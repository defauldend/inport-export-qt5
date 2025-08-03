#!/bin/bash

# This script creates a directory for the PyQt5 data application,
# generates the Python source code file, and the requirements.txt file.

# --- Configuration ---
PROJECT_DIR="pyqt_data_app"

# --- Script Start ---
echo "Creating project directory: $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "Creating Python application file: data_app.py..."

# Use a 'here document' to write the Python code to data_app.py
# The 'EOF' marker prevents the shell from expanding variables like $ in the code.
cat << 'EOF' > data_app.py
import sys
import pandas as pd
import requests
from sqlalchemy import create_engine, text

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QDialog, QLineEdit, QGridLayout, QLabel,
    QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal

# --- Model to link pandas DataFrame to QTableView ---
class PandasModel(QAbstractTableModel):
    """A model to interface a pandas DataFrame with a QTableView."""
    def __init__(self, dataframe: pd.DataFrame = pd.DataFrame()):
        super().__init__()
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        return self._dataframe.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])
        return None

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()

# --- Database Connection Dialog ---
class DbDialog(QDialog):
    """A dialog to get database connection details from the user."""
    db_import_requested = pyqtSignal(dict)
    db_export_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Operations")
        self.layout = QGridLayout(self)

        # Create widgets
        self.db_type_label = QLabel("Database Type:")
        self.db_type_input = QLineEdit("sqlite")
        self.db_type_input.setDisabled(True) # For this example, we'll stick to SQLite

        self.db_name_label = QLabel("Database Name:")
        self.db_name_input = QLineEdit("data.db")

        self.table_name_label = QLabel("Table Name:")
        self.table_name_input = QLineEdit("my_table")

        # Buttons
        self.button_box = QDialogButtonBox()
        self.import_button = self.button_box.addButton("Import from DB", QDialogButtonBox.ActionRole)
        self.export_button = self.button_box.addButton("Export to DB", QDialogButtonBox.ActionRole)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.Cancel)

        # Add widgets to layout
        self.layout.addWidget(self.db_type_label, 0, 0)
        self.layout.addWidget(self.db_type_input, 0, 1)
        self.layout.addWidget(self.db_name_label, 1, 0)
        self.layout.addWidget(self.db_name_input, 1, 1)
        self.layout.addWidget(self.table_name_label, 2, 0)
        self.layout.addWidget(self.table_name_input, 2, 1)
        self.layout.addWidget(self.button_box, 3, 0, 1, 2)

        # Connect signals
        self.import_button.clicked.connect(self.on_import)
        self.export_button.clicked.connect(self.on_export)
        self.cancel_button.clicked.connect(self.reject)

    def get_db_info(self):
        """Returns a dictionary with the connection details."""
        return {
            "db_type": self.db_type_input.text(),
            "db_name": self.db_name_input.text(),
            "table_name": self.table_name_input.text()
        }

    def on_import(self):
        self.db_import_requested.emit(self.get_db_info())
        self.accept()

    def on_export(self):
        self.db_export_requested.emit(self.get_db_info())
        self.accept()

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Management Tool")
        self.setGeometry(100, 100, 800, 600)

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- Table View for DataFrame ---
        self.table_view = QTableView()
        self.df = pd.DataFrame({
            'Welcome': ['This is a data management tool'],
            'Info': ['You can import/export files or connect to a database.']
        })
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)
        self.layout.addWidget(self.table_view)

        # --- Buttons ---
        self.btn_import_csv = QPushButton("Import from CSV")
        self.btn_import_excel = QPushButton("Import from Excel")
        self.btn_export_csv = QPushButton("Export to CSV")
        self.btn_export_excel = QPushButton("Export to Excel")
        self.btn_db_ops = QPushButton("Database Operations")
        self.btn_fetch_api = QPushButton("Fetch from API (JSONPlaceholder)")

        # Add buttons to the layout
        self.layout.addWidget(self.btn_import_csv)
        self.layout.addWidget(self.btn_import_excel)
        self.layout.addWidget(self.btn_export_csv)
        self.layout.addWidget(self.btn_export_excel)
        self.layout.addWidget(self.btn_db_ops)
        self.layout.addWidget(self.btn_fetch_api)

        # --- Connect Signals to Slots ---
        self.btn_import_csv.clicked.connect(self.import_csv)
        self.btn_import_excel.clicked.connect(self.import_excel)
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_excel.clicked.connect(self.export_excel)
        self.btn_db_ops.clicked.connect(self.open_db_dialog)
        self.btn_fetch_api.clicked.connect(self.fetch_from_api)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.model.setDataFrame(self.df)
                self.show_message("Success", "CSV file imported successfully.")
            except Exception as e:
                self.show_message("Error", f"Could not import CSV file:\n{e}")

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)")
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.model.setDataFrame(self.df)
                self.show_message("Success", "Excel file imported successfully.")
            except Exception as e:
                self.show_message("Error", f"Could not import Excel file:\n{e}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                self.show_message("Success", f"Data exported to {file_path}")
            except Exception as e:
                self.show_message("Error", f"Could not export to CSV:\n{e}")

    def export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)")
        if file_path:
            try:
                self.df.to_excel(file_path, index=False)
                self.show_message("Success", f"Data exported to {file_path}")
            except Exception as e:
                self.show_message("Error", f"Could not export to Excel:\n{e}")
                
    def open_db_dialog(self):
        dialog = DbDialog(self)
        dialog.db_import_requested.connect(self.import_from_db)
        dialog.db_export_requested.connect(self.export_to_db)
        dialog.exec_()

    def import_from_db(self, db_info):
        db_type = db_info['db_type']
        db_name = db_info['db_name']
        table_name = db_info['table_name']

        if not all([db_type, db_name, table_name]):
            self.show_message("Error", "Database details cannot be empty.")
            return

        try:
            engine = create_engine(f"{db_type}:///{db_name}")
            with engine.connect() as connection:
                self.df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
                self.model.setDataFrame(self.df)
                self.show_message("Success", f"Data imported from table '{table_name}'.")
        except Exception as e:
            self.show_message("Error", f"Could not import from database:\n{e}")

    def export_to_db(self, db_info):
        db_type = db_info['db_type']
        db_name = db_info['db_name']
        table_name = db_info['table_name']

        if not all([db_type, db_name, table_name]):
            self.show_message("Error", "Database details cannot be empty.")
            return

        try:
            engine = create_engine(f"{db_type}:///{db_name}")
            self.df.to_sql(table_name, engine, if_exists='replace', index=False)
            self.show_message("Success", f"Data exported to table '{table_name}'.")
        except Exception as e:
            self.show_message("Error", f"Could not export to database:\n{e}")
            
    def fetch_from_api(self):
        url = "https://jsonplaceholder.typicode.com/users"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            self.df = pd.json_normalize(data)
            
            self.model.setDataFrame(self.df)
            self.show_message("Success", "Data fetched from API successfully.")
        except requests.exceptions.RequestException as e:
            self.show_message("API Error", f"Could not fetch data from API:\n{e}")
        except Exception as e:
            self.show_message("Error", f"An error occurred:\n{e}")

# --- Application Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
EOF

echo "Creating dependency file: requirements.txt..."

# Use a 'here document' to write the requirements
cat << EOF > requirements.txt
PyQt5
pandas
openpyxl
SQLAlchemy
requests
EOF

echo ""
echo "--------------------------------------------------"
echo "Project setup complete!"
echo ""
echo "To run the application, follow these steps:"
echo "1. Navigate to the project directory:"
echo "   cd $PROJECT_DIR"
echo ""
echo "2. Create a virtual environment (recommended):"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo ""
echo "3. Install the required packages:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Run the application:"
echo "   python3 data_app.py"
echo "--------------------------------------------------"
