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
        """Reverts the change by setting the cell to the old value."""
        self.model.silent_update(self.row, self.col, self.old_value)

    def redo(self):
        """Re-applies the change by setting the cell to the new value."""
        self.model.silent_update(self.row, self.col, self.new_value)


# --- Modified Pandas Model ---
class PandasModel(QAbstractTableModel):
    # Signal that emits a command object after a successful edit
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

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def setData(self, index, value, role=Qt.EditRole):
        """This is called when a user edits a cell."""
        if role != Qt.EditRole: return False

        row, col = index.row(), index.column()
        old_value = self._dataframe.iloc[row, col]

        # --- Data Validation ---
        try:
            original_dtype = self._dataframe.iloc[:, col].dtype
            if pd.api.types.is_numeric_dtype(original_dtype):
                value = int(float(value)) if pd.api.types.is_integer_dtype(original_dtype) else float(value)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Type Error", f"Could not convert input to type {original_dtype}.")
            return False

        # Update DataFrame
        self._dataframe.iloc[row, col] = value
        self.dataChanged.emit(index, index, [Qt.EditRole])

        # Create a command and emit it for the undo stack
        command = EditCommand(self, row, col, old_value, value)
        self.editCommitted.emit(command)

        return True

    def silent_update(self, row, col, value):
        """Updates the DataFrame without creating an undo command."""
        self._dataframe.iloc[row, col] = value
        index = self.createIndex(row, col)
        self.dataChanged.emit(index, index, [Qt.EditRole])


# --- Dialogs (Unchanged) ---
class DbDialog(QDialog): pass # Omitted for brevity
class InfoDialog(QDialog): pass # Omitted for brevity

# --- Main Application Window with Undo/Redo Logic ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Editor with Temporal Memory")
        self.setGeometry(100, 100, 1100, 700)

        # --- Undo/Redo Stacks ---
        self.undo_stack = deque(maxlen=100) # Limit history to 100 steps
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
        self.df = pd.DataFrame({'Hint': ['Use Ctrl+Z to Undo and Ctrl+Y to Redo edits.']})
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)
        self.main_layout.addWidget(self.table_view, 4)

        # Button panel setup (same as before)
        self.button_panel = QWidget()
        self.button_layout = QVBoxLayout(self.button_panel)
        self.btn_import_csv = QPushButton("Import from CSV")
        self.btn_export_csv = QPushButton("Export to CSV")
        # ... other buttons
        self.button_layout.addWidget(self.btn_import_csv)
        self.button_layout.addWidget(self.btn_export_csv)
        self.button_layout.addStretch()
        self.button_panel.setFixedWidth(200)
        self.main_layout.addWidget(self.button_panel)

    def _create_actions(self):
        """Create QAction objects for the menu."""
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo) # Ctrl+Z
        self.undo_action.setEnabled(False)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo) # Ctrl+Y
        self.redo_action.setEnabled(False)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

    def _connect_signals(self):
        # Connect button signals
        self.btn_import_csv.clicked.connect(self.import_csv)
        # ... other button connections

        # Connect action triggers
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)

        # Connect the model's custom signal to our handler
        self.model.editCommitted.connect(self.add_to_undo_stack)

    def add_to_undo_stack(self, command):
        """Adds a new command to the undo stack."""
        self.undo_stack.append(command)
        # A new action clears the redo stack
        self.redo_stack.clear()
        self.update_action_states()

    def undo(self):
        if not self.undo_stack: return
        # Pop the last command, execute its undo method, and move it to the redo stack
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        self.update_action_states()

    def redo(self):
        if not self.redo_stack: return
        # Pop the last undone command, execute its redo method, and move it back
        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        self.update_action_states()

    def update_action_states(self):
        """Enables or disables the Undo/Redo menu actions."""
        self.undo_action.setEnabled(bool(self.undo_stack))
        self.redo_action.setEnabled(bool(self.redo_stack))

    def clear_history(self):
        """Clears both stacks, e.g., when a new file is loaded."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_action_states()

    def import_csv(self):
        """Example of a data-loading function that clears history."""
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                self.model.setDataFrame(pd.read_csv(path))
                self.show_message("Success", "CSV file imported.")
                self.clear_history() # Crucial step!
            except Exception as e:
                self.show_message("Error", f"Could not import CSV:\n{e}")

    def show_message(self, title, msg):
        QMessageBox.information(self, title, msg)


# --- Application Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
