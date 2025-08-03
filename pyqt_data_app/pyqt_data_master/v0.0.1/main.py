import sys
import os
import pandas as pd
import requests
from sqlalchemy import create_engine
from collections import deque
from io import StringIO

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QDialog, QLineEdit, QGridLayout, QLabel,
    QMessageBox, QDialogButtonBox, QAction
)
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence

# --- Command & Model Classes (Unchanged from previous version) ---
class EditCommand:
    def __init__(self, model, row, col, old_value, new_value):
        self.model, self.row, self.col = model, row, col
        self.old_value, self.new_value = old_value, new_value
    def undo(self): self.model.silent_update(self.row, self.col, self.old_value)
    def redo(self): self.model.silent_update(self.row, self.col, self.new_value)

class PandasModel(QAbstractTableModel):
    editCommitted = pyqtSignal(object)
    def __init__(self, dataframe: pd.DataFrame = pd.DataFrame()):
        super().__init__(); self._dataframe = dataframe
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
        except (ValueError, TypeError): return False
        self._dataframe.iloc[row, col] = value
        self.dataChanged.emit(index, index, [Qt.EditRole])
        self.editCommitted.emit(EditCommand(self, row, col, old_value, value))
        return True
    def setDataFrame(self, dataframe):
        self.beginResetModel(); self._dataframe = dataframe.copy(); self.endResetModel()
    def silent_update(self, row, col, value):
        self._dataframe.iloc[row, col] = value
        self.dataChanged.emit(self.createIndex(row, col), self.createIndex(row, col), [Qt.EditRole])

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Editor with Restart")
        self.setGeometry(100, 100, 1100, 700)
        
        # --- State Management ---
        self.undo_stack = deque(maxlen=100)
        self.redo_stack = deque(maxlen=100)
        self.original_df = pd.DataFrame() # To store the pristine copy of the data

        self._setup_ui()
        self._create_actions()
        self._create_menu_bar()
        self._connect_signals()
        self.update_action_states() # Initial UI state

    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.table_view = QTableView()
        self.df = pd.DataFrame({'Hint': ['Use the buttons to load data.']})
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)
        self.main_layout.addWidget(self.table_view, 4)
        
        self.button_panel = QWidget()
        self.button_layout = QVBoxLayout(self.button_panel)
        self.btn_import_csv = QPushButton("Import CSV")
        self.btn_import_excel = QPushButton("Import Excel")
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_excel = QPushButton("Export Excel")
        
        # New Restart Button
        self.btn_restart_edits = QPushButton("Restart Edits")
        self.btn_restart_edits.setStyleSheet("background-color: #ffc107;") # A warning yellow

        self.button_layout.addWidget(self.btn_import_csv); self.button_layout.addWidget(self.btn_import_excel)
        self.button_layout.addSpacing(20); self.button_layout.addWidget(self.btn_export_csv); self.button_layout.addWidget(self.btn_export_excel)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_restart_edits)
        self.button_panel.setFixedWidth(200)
        self.main_layout.addWidget(self.button_panel)

    def _create_actions(self):
        self.undo_action = QAction("Undo", self, shortcut=QKeySequence.Undo)
        self.redo_action = QAction("Redo", self, shortcut=QKeySequence.Redo)
        self.restart_action = QAction("Restart All Edits...", self)
        self.restart_action.setToolTip("Revert all changes to the last loaded state")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.restart_action)

    def _connect_signals(self):
        self.btn_import_csv.clicked.connect(self.import_csv)
        self.btn_import_excel.clicked.connect(self.import_excel)
        self.btn_export_csv.clicked.connect(lambda: self.export_file('.csv', 'CSV Files (*.csv)'))
        self.btn_export_excel.clicked.connect(lambda: self.export_file('.xlsx', 'Excel Files (*.xlsx)'))
        self.btn_restart_edits.clicked.connect(self.restart_edits)
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.restart_action.triggered.connect(self.restart_edits)
        self.model.editCommitted.connect(self.add_to_undo_stack)

    # --- Core Logic ---
    def add_to_undo_stack(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.update_action_states()

    def undo(self):
        if self.undo_stack:
            cmd = self.undo_stack.pop(); cmd.undo(); self.redo_stack.append(cmd)
            self.update_action_states()

    def redo(self):
        if self.redo_stack:
            cmd = self.redo_stack.pop(); cmd.redo(); self.undo_stack.append(cmd)
            self.update_action_states()

    def restart_edits(self):
        """Reverts the DataFrame to its original state and clears history."""
        if self.original_df.empty or self.model._dataframe.equals(self.original_df):
            self.show_message("Info", "There are no edits to restart.")
            return

        reply = QMessageBox.question(self, "Confirm Restart",
                                     "Are you sure you want to discard all changes made in this session?\nThis action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.model.setDataFrame(self.original_df)
            self.clear_history()
            self.show_message("Success", "All edits have been reverted to the last loaded state.")
            
    def update_action_states(self):
        """Enables or disables all actions based on the current state."""
        self.undo_action.setEnabled(bool(self.undo_stack))
        self.redo_action.setEnabled(bool(self.redo_stack))
        
        # Enable restart only if an original exists and it's different from the current state
        can_restart = not self.original_df.empty and not self.model._dataframe.equals(self.original_df)
        self.restart_action.setEnabled(can_restart)
        self.btn_restart_edits.setEnabled(can_restart)

    def clear_history(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_action_states()

    def _load_file(self, read_func, path):
        if not path: return
        try:
            df = read_func(path)
            self.model.setDataFrame(df)
            # Store the pristine copy
            self.original_df = df.copy()
            self.show_message("Success", "File loaded successfully.")
            self.clear_history()
        except Exception as e:
            self.original_df = pd.DataFrame() # Clear original on failure
            self.model.setDataFrame(pd.DataFrame()) # Clear model on failure
            self.show_message("Error", f"Could not load file:\n{e}")
            self.clear_history()

    # --- Helper Methods ---
    def import_csv(self): self._load_file(pd.read_csv, QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")[0])
    def import_excel(self): self._load_file(pd.read_excel, QFileDialog.getOpenFileName(self, "Open Excel", "", "Excel Files (*.xlsx *.xls)")[0])
    def export_file(self, ext, filt):
        if self.model._dataframe.empty: self.show_message("Info", "No data to export."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", filt)
        if path:
            try:
                if ext == '.csv': self.model._dataframe.to_csv(path, index=False)
                elif ext == '.xlsx': self.model._dataframe.to_excel(path, index=False)
                self.show_message("Success", f"Data exported to {path}")
            except Exception as e: self.show_message("Error", f"Could not export file:\n{e}")
    def show_message(self, title, msg): QMessageBox.information(self, title, msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
