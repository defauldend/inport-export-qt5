#!/bin/bash

# This script creates a complete project structure for the PyQt5 data application,
# including the Python source code, dependencies file, and sample data files.

# --- Configuration ---
PROJECT_DIR="pyqt_data_master"
SAMPLE_DIR="$PROJECT_DIR/sample_data"

# --- Script Start ---
echo "Creating project directory: $PROJECT_DIR..."
mkdir -p "$SAMPLE_DIR"

# Change into the project directory to create files there
cd "$PROJECT_DIR"

echo "Creating Python application file: data_master_app.py..."
# Use a 'here document' with a quoted EOF to prevent shell variable expansion
cat << 'EOF' > data_master_app.py
import sys
import pandas as pd
import requests
from sqlalchemy import create_engine
from collections import deque

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QDialog, QLineEdit, QGridLayout, QLabel,
    QMessageBox, QDialogButtonBox, QAction
)
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal, QModelIndex
from PyQt5.QtGui import QKeySequence

# --- Command Class for Undo/Redo Pattern ---
class EditCommand:
    """Encapsulates a cell edit to support undo/redo."""
    def __init__(self, model, row, col, old_value, new_value):
        self.model = model
        self.row, self.col = row, col
        self.old_value, self.new_value = old_value, new_value
    def undo(self):
        self.model.silent_update(self.row, self.col, self.old_value)
    def redo(self):
        self.model.silent_update(self.row, self.col, self.new_value)

# --- The Pandas Model for the QTableView ---
class PandasModel(QAbstractTableModel):
    editCommitted = pyqtSignal(object)
    def __init__(self, dataframe: pd.DataFrame = pd.DataFrame()):
        super().__init__()
        self._dataframe = dataframe
    def rowCount(self, parent=None): return self._dataframe.shape[0]
    def columnCount(self, parent=None): return self._dataframe.shape[1]
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole: return None
        return str(self._dataframe.iloc[index.row(), index.column()])
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal: return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical: return str(self._dataframe.index[section])
        return None
    def flags(self, index): return super().flags(index) | Qt.ItemIsEditable
    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole: return False
        row, col = index.row(), index.column()
        old_value = self._dataframe.iloc[row, col]
        try:
            original_dtype = self._dataframe.iloc[:, col].dtype
            if pd.api.types.is_numeric_dtype(original_dtype):
                value = int(float(value)) if pd.api.types.is_integer_dtype(original_dtype) else float(value)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Type Error", f"Could not convert input to type {original_dtype}.")
            return False
        self._dataframe.iloc[row, col] = value
        self.dataChanged.emit(index, index, [Qt.EditRole])
        command = EditCommand(self, row, col, old_value, value)
        self.editCommitted.emit(command)
        return True
    def setDataFrame(self, dataframe):
        self.beginResetModel(); self._dataframe = dataframe.copy(); self.endResetModel()
    def silent_update(self, row, col, value):
        self._dataframe.iloc[row, col] = value
        index = self.createIndex(row, col)
        self.dataChanged.emit(index, index, [Qt.EditRole])

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Editor with Temporal Memory")
        self.setGeometry(100, 100, 1100, 700)
        self.undo_stack = deque(maxlen=100)
        self.redo_stack = deque(maxlen=100)
        self._setup_ui()
        self._create_actions()
        self._create_menu_bar()
        self._connect_signals()
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.table_view = QTableView()
        self.df = pd.DataFrame({'Hint': ['Use the buttons or File menu to load data.']})
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)
        self.main_layout.addWidget(self.table_view, 4)
        self.button_panel = QWidget()
        self.button_layout = QVBoxLayout(self.button_panel)
        self.btn_import_csv = QPushButton("Import CSV")
        self.btn_import_excel = QPushButton("Import Excel")
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_excel = QPushButton("Export Excel")
        self.button_layout.addWidget(self.btn_import_csv); self.button_layout.addWidget(self.btn_import_excel)
        self.button_layout.addSpacing(20); self.button_layout.addWidget(self.btn_export_csv); self.button_layout.addWidget(self.btn_export_excel)
        self.button_layout.addStretch()
        self.button_panel.setFixedWidth(200)
        self.main_layout.addWidget(self.button_panel)
    def _create_actions(self):
        self.undo_action = QAction("Undo", self, shortcut=QKeySequence.Undo, enabled=False)
        self.redo_action = QAction("Redo", self, shortcut=QKeySequence.Redo, enabled=False)
    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        # You can add actions like open, save here
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
    def _connect_signals(self):
        self.btn_import_csv.clicked.connect(self.import_csv)
        self.btn_import_excel.clicked.connect(self.import_excel)
        self.btn_export_csv.clicked.connect(lambda: self.export_file('.csv', 'CSV Files (*.csv)'))
        self.btn_export_excel.clicked.connect(lambda: self.export_file('.xlsx', 'Excel Files (*.xlsx)'))
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.model.editCommitted.connect(self.add_to_undo_stack)
    def add_to_undo_stack(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.update_action_states()
    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop(); command.undo(); self.redo_stack.append(command)
            self.update_action_states()
    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop(); command.redo(); self.undo_stack.append(command)
            self.update_action_states()
    def update_action_states(self):
        self.undo_action.setEnabled(bool(self.undo_stack))
        self.redo_action.setEnabled(bool(self.redo_stack))
    def clear_history(self):
        self.undo_stack.clear(); self.redo_stack.clear()
        self.update_action_states()
    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path: self._load_file(pd.read_csv, path)
    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Excel", "", "Excel Files (*.xlsx *.xls)")
        if path: self._load_file(pd.read_excel, path)
    def _load_file(self, read_func, path):
        try:
            self.model.setDataFrame(read_func(path))
            self.show_message("Success", "File loaded successfully.")
            self.clear_history()
        except Exception as e:
            self.show_message("Error", f"Could not load file:\n{e}")
    def export_file(self, extension, file_filter):
        if self.model._dataframe.empty:
            self.show_message("Info", "There is no data to export."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", file_filter)
        if path:
            try:
                if extension == '.csv': self.model._dataframe.to_csv(path, index=False)
                elif extension == '.xlsx': self.model._dataframe.to_excel(path, index=False)
                self.show_message("Success", f"Data exported to {path}")
            except Exception as e:
                self.show_message("Error", f"Could not export file:\n{e}")
    def show_message(self, title, msg):
        QMessageBox.information(self, title, msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
EOF

echo "Creating dependency file: requirements.txt..."
# Use a standard 'here document' for the requirements
cat << EOF > requirements.txt
PyQt5
pandas
openpyxl
SQLAlchemy
requests
EOF

echo "Creating sample CSV file: sample_data/sample_products.csv..."
cat << EOF > sample_data/sample_products.csv
ProductID,ProductName,Category,UnitPrice,UnitsInStock
1,Chai,Beverages,18.00,39
2,Chang,Beverages,19.50,17
3,Aniseed Syrup,Condiments,10.00,13
4,Chef Anton's Cajun Seasoning,Condiments,22.00,53
5,Grandma's Boysenberry Spread,Condiments,25.55,120
EOF

# Go back to the parent directory
cd ..

echo ""
echo "--------------------------------------------------"
echo "Project setup complete!"
echo "Created directory: $PROJECT_DIR"
echo "--------------------------------------------------"
echo ""
echo "To run the application, follow these steps:"
echo ""
echo "1. Navigate to the project directory:"
echo "   cd $PROJECT_DIR"
echo ""
echo "2. Create and activate a Python virtual environment (recommended):"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   (On Windows, use: venv\\Scripts\\activate)"
echo ""
echo "3. Install the required packages from requirements.txt:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Generate the sample Excel file with this command:"
echo '   python3 -c "import pandas as pd; pd.DataFrame({\"CustomerID\": [101, 102, 103], \"Name\": [\"Alfreds Futterkiste\", \"Ana Trujillo\", \"Antonio Moreno\"], \"City\": [\"Berlin\", \"México D.F.\", \"México D.F.\"], \"Country\": [\"Germany\", \"Mexico\", \"Mexico\"]}).to_excel(\"sample_data/sample_customers.xlsx\", index=False)"'
echo ""
echo "5. Run the application:"
echo "   python3 data_master_app.py"
echo ""
echo "You can now use the 'Import CSV' and 'Import Excel' buttons to load the sample data."
echo ""
