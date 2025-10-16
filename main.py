import sys
import os
import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine, text

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QDialog, QLineEdit, QGridLayout, QLabel,
    QMessageBox, QDialogButtonBox, QStatusBar, QProgressDialog, QMenuBar,
    QMenu, QAction
)
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal, QSortFilterProxyModel

# Import DebugManager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.debug import DebugManager, OperationMetrics

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
    # Signal to send db info back to the main window
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
        self.setGeometry(100, 100, 900, 700)
        
        # Initialize Debug Manager
        self.debug_manager = DebugManager()
        self.debug_manager.logger.info("Application started")

        # --- Menu Bar ---
        self._create_menu_bar()

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- Search/Filter Bar ---
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter data...")
        self.search_input.textChanged.connect(self.filter_data)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.layout.addLayout(self.search_layout)

        # --- Table View for DataFrame ---
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)  # Enable sorting
        self.df = pd.DataFrame({
            'Welcome': ['This is a data management tool'],
            'Info': ['You can import/export files or connect to a database.']
        })
        self.model = PandasModel(self.df)
        
        # Create proxy model for filtering and sorting
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns
        
        self.table_view.setModel(self.proxy_model)
        self.layout.addWidget(self.table_view)

        # --- Buttons ---
        self.btn_import_csv = QPushButton("Import from CSV")
        self.btn_import_excel = QPushButton("Import from Excel")
        self.btn_import_json = QPushButton("Import from JSON")
        self.btn_export_csv = QPushButton("Export to CSV")
        self.btn_export_excel = QPushButton("Export to Excel")
        self.btn_export_json = QPushButton("Export to JSON")
        self.btn_db_ops = QPushButton("Database Operations")
        self.btn_fetch_api = QPushButton("Fetch from API (JSONPlaceholder)")

        # Add buttons to the layout
        self.layout.addWidget(self.btn_import_csv)
        self.layout.addWidget(self.btn_import_excel)
        self.layout.addWidget(self.btn_import_json)
        self.layout.addWidget(self.btn_export_csv)
        self.layout.addWidget(self.btn_export_excel)
        self.layout.addWidget(self.btn_export_json)
        self.layout.addWidget(self.btn_db_ops)
        self.layout.addWidget(self.btn_fetch_api)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # --- Connect Signals to Slots ---
        self.btn_import_csv.clicked.connect(self.import_csv)
        self.btn_import_excel.clicked.connect(self.import_excel)
        self.btn_import_json.clicked.connect(self.import_json)
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_excel.clicked.connect(self.export_excel)
        self.btn_export_json.clicked.connect(self.export_json)
        self.btn_db_ops.clicked.connect(self.open_db_dialog)
        self.btn_fetch_api.clicked.connect(self.fetch_from_api)

    def _create_menu_bar(self):
        """Create menu bar with File and Help menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        clear_action = QAction('Clear Data', self)
        clear_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        metrics_action = QAction('Performance &Metrics', self)
        metrics_action.triggered.connect(self.show_metrics)
        help_menu.addAction(metrics_action)
    
    def filter_data(self):
        """Filter table data based on search input."""
        search_text = self.search_input.text()
        self.proxy_model.setFilterFixedString(search_text)
        self.status_bar.showMessage(f"Filtering: '{search_text}'")
    
    def clear_data(self):
        """Clear all data from the table."""
        self.df = pd.DataFrame()
        self.model.setDataFrame(self.df)
        self.search_input.clear()
        self.status_bar.showMessage("Data cleared")
        self.debug_manager.logger.info("Data cleared by user")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Data Management Tool",
                         "Data Management Tool v1.1\n\n"
                         "A PyQt5 application for managing data with support for:\n"
                         "- CSV, Excel, and JSON files\n"
                         "- Database operations\n"
                         "- API data fetching\n"
                         "- Data filtering and sorting\n"
                         "- Performance monitoring")
    
    def show_metrics(self):
        """Show performance metrics dialog."""
        summary = self.debug_manager.get_performance_summary()
        if isinstance(summary, str):
            QMessageBox.information(self, "Performance Metrics", summary)
        else:
            metrics_text = (
                f"Total Operations: {summary['total_operations']}\n"
                f"Successful: {summary['successful_operations']}\n"
                f"Failed: {summary['failed_operations']}\n"
                f"Average Duration: {summary['average_duration']:.3f}s\n"
                f"Current Memory: {summary['current_memory'] / 1024 / 1024:.2f} MB"
            )
            QMessageBox.information(self, "Performance Metrics", metrics_text)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
        self.status_bar.showMessage(f"{title}: {message[:50]}...")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df = pd.read_csv(file_path)
                self.model.setDataFrame(self.df)
                
                # Record metrics
                metrics = OperationMetrics(
                    operation_name="Import CSV",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"CSV file imported successfully. {len(self.df)} rows loaded.")
                self.status_bar.showMessage(f"Loaded {len(self.df)} rows from CSV")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Import CSV",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not import CSV file:\n{e}")
                self.status_bar.showMessage("Import failed")

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df = pd.read_excel(file_path)
                self.model.setDataFrame(self.df)
                
                metrics = OperationMetrics(
                    operation_name="Import Excel",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"Excel file imported successfully. {len(self.df)} rows loaded.")
                self.status_bar.showMessage(f"Loaded {len(self.df)} rows from Excel")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Import Excel",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not import Excel file:\n{e}")
                self.status_bar.showMessage("Import failed")

    def import_json(self):
        """Import data from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df = pd.read_json(file_path)
                self.model.setDataFrame(self.df)
                
                metrics = OperationMetrics(
                    operation_name="Import JSON",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"JSON file imported successfully. {len(self.df)} rows loaded.")
                self.status_bar.showMessage(f"Loaded {len(self.df)} rows from JSON")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Import JSON",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not import JSON file:\n{e}")
                self.status_bar.showMessage("Import failed")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df.to_csv(file_path, index=False)
                
                metrics = OperationMetrics(
                    operation_name="Export CSV",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"Data exported to {file_path}")
                self.status_bar.showMessage(f"Exported {len(self.df)} rows to CSV")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Export CSV",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not export to CSV:\n{e}")
                self.status_bar.showMessage("Export failed")

    def export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df.to_excel(file_path, index=False)
                
                metrics = OperationMetrics(
                    operation_name="Export Excel",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"Data exported to {file_path}")
                self.status_bar.showMessage(f"Exported {len(self.df)} rows to Excel")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Export Excel",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not export to Excel:\n{e}")
                self.status_bar.showMessage("Export failed")

    def export_json(self):
        """Export data to JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            start_time = datetime.now()
            mem_before = self.debug_manager.get_memory_usage()
            try:
                self.df.to_json(file_path, orient='records', indent=2)
                
                metrics = OperationMetrics(
                    operation_name="Export JSON",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"Data exported to {file_path}")
                self.status_bar.showMessage(f"Exported {len(self.df)} rows to JSON")
            except Exception as e:
                metrics = OperationMetrics(
                    operation_name="Export JSON",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=False,
                    error_message=str(e),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                self.show_message("Error", f"Could not export to JSON:\n{e}")
                self.status_bar.showMessage("Export failed")
                
    def open_db_dialog(self):
        dialog = DbDialog(self)
        # Connect the dialog's custom signals to the main window's methods
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

        start_time = datetime.now()
        mem_before = self.debug_manager.get_memory_usage()
        try:
            # For SQLite, the connection string is 'sqlite:///database_name.db'
            engine = create_engine(f"{db_type}:///{db_name}")
            with engine.connect() as connection:
                self.df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
                self.model.setDataFrame(self.df)
                
                metrics = OperationMetrics(
                    operation_name="Import from Database",
                    start_time=start_time,
                    end_time=datetime.now(),
                    success=True,
                    rows_affected=len(self.df),
                    memory_before=mem_before,
                    memory_after=self.debug_manager.get_memory_usage()
                )
                self.debug_manager.record_metrics(metrics)
                
                self.show_message("Success", f"Data imported from table '{table_name}'. {len(self.df)} rows loaded.")
                self.status_bar.showMessage(f"Loaded {len(self.df)} rows from database")
        except Exception as e:
            metrics = OperationMetrics(
                operation_name="Import from Database",
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                error_message=str(e),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            self.show_message("Error", f"Could not import from database:\n{e}")
            self.status_bar.showMessage("Database import failed")

    def export_to_db(self, db_info):
        db_type = db_info['db_type']
        db_name = db_info['db_name']
        table_name = db_info['table_name']

        if not all([db_type, db_name, table_name]):
            self.show_message("Error", "Database details cannot be empty.")
            return

        start_time = datetime.now()
        mem_before = self.debug_manager.get_memory_usage()
        try:
            engine = create_engine(f"{db_type}:///{db_name}")
            # Use 'if_exists='replace'' to overwrite the table.
            # Use 'append' to add data, or 'fail' to do nothing if the table exists.
            self.df.to_sql(table_name, engine, if_exists='replace', index=False)
            
            metrics = OperationMetrics(
                operation_name="Export to Database",
                start_time=start_time,
                end_time=datetime.now(),
                success=True,
                rows_affected=len(self.df),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            
            self.show_message("Success", f"Data exported to table '{table_name}'. {len(self.df)} rows saved.")
            self.status_bar.showMessage(f"Exported {len(self.df)} rows to database")
        except Exception as e:
            metrics = OperationMetrics(
                operation_name="Export to Database",
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                error_message=str(e),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            self.show_message("Error", f"Could not export to database:\n{e}")
            self.status_bar.showMessage("Database export failed")
            
    def fetch_from_api(self):
        # Example API: JSONPlaceholder, which provides fake API for testing
        url = "https://jsonplaceholder.typicode.com/users"
        start_time = datetime.now()
        mem_before = self.debug_manager.get_memory_usage()
        
        # Show progress dialog for API call
        progress = QProgressDialog("Fetching data from API...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            
            # Normalize the nested JSON structure if necessary
            self.df = pd.json_normalize(data)
            
            self.model.setDataFrame(self.df)
            
            metrics = OperationMetrics(
                operation_name="Fetch from API",
                start_time=start_time,
                end_time=datetime.now(),
                success=True,
                rows_affected=len(self.df),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            
            progress.close()
            self.show_message("Success", f"Data fetched from API successfully. {len(self.df)} rows loaded.")
            self.status_bar.showMessage(f"Loaded {len(self.df)} rows from API")
        except requests.exceptions.RequestException as e:
            metrics = OperationMetrics(
                operation_name="Fetch from API",
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                error_message=str(e),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            
            progress.close()
            self.show_message("API Error", f"Could not fetch data from API:\n{e}")
            self.status_bar.showMessage("API fetch failed")
        except Exception as e:
            metrics = OperationMetrics(
                operation_name="Fetch from API",
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                error_message=str(e),
                memory_before=mem_before,
                memory_after=self.debug_manager.get_memory_usage()
            )
            self.debug_manager.record_metrics(metrics)
            
            progress.close()
            self.show_message("Error", f"An error occurred:\n{e}")
            self.status_bar.showMessage("Operation failed")

    def closeEvent(self, event):
        """Handle application close event."""
        self.debug_manager.logger.info("Application closing")
        event.accept()

# --- Application Execution ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
