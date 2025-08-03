#!/usr/bin/env python3
"""
Data Master Pro with Analytics
A comprehensive data analysis and visualization tool built with PyQt5
"""

import sys
import pandas as pd
import requests
from sqlalchemy import create_engine
from collections import deque
from io import StringIO

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QDialog, QLineEdit, QGridLayout, QLabel,
    QMessageBox, QDialogButtonBox, QAction, QTextEdit, QListWidget, QListWidgetItem,
    QGroupBox, QComboBox, QTabWidget, QMenu
)
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal, QModelIndex
from PyQt5.QtGui import QKeySequence, QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns

# Set the plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class Command:
    """Base class for implementing the Command pattern for undo/redo functionality"""
    def __init__(self, model):
        self.model = model
    
    def undo(self):
        pass
    
    def redo(self):
        pass
    
    def __str__(self):
        return "Generic Command"

class EditCommand(Command):
    """Command for cell editing operations"""
    def __init__(self, model, row, col, old_value, new_value):
        super().__init__(model)
        self.row, self.col = row, col
        self.old_value, self.new_value = old_value, new_value
    
    def undo(self):
        self.model.silent_update(self.row, self.col, self.old_value)
    
    def redo(self):
        self.model.silent_update(self.row, self.col, self.new_value)
    
    def __str__(self):
        col_name = self.model._dataframe.columns[self.col]
        return f"Edit cell ({self.row}, '{col_name}') to '{self.new_value}'"

class RowCommand(Command):
    """Command for row operations (add/delete)"""
    def __init__(self, model, index, row_data=None):
        super().__init__(model)
        self.index = index
        self.row_data = row_data
    
    def undo(self):
        if self.row_data is not None:
            self.model.insert_row(self.index, self.row_data)
        else:
            self.model.delete_row(self.index, create_command=False)
    
    def redo(self):
        if self.row_data is not None:
            self.model.delete_row(self.index, create_command=False)
        else:
            self.model.add_row(create_command=False)
    
    def __str__(self):
        return f"Delete row at index {self.index}" if self.row_data is not None else "Add new row"

class PandasModel(QAbstractTableModel):
    """Qt Model for displaying pandas DataFrames in QTableView"""
    editCommitted = pyqtSignal(Command)
    
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._dataframe = df
    
    def rowCount(self, parent=None):
        return self._dataframe.shape[0]
    
    def columnCount(self, parent=None):
        return self._dataframe.shape[1]
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self._dataframe.iloc[index.row(), index.column()])
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])
    
    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable
    
    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False
        
        row, col = index.row(), index.column()
        old_value = self._dataframe.iloc[row, col]
        
        try:
            # Try to maintain the original data type
            dtype = self._dataframe.iloc[:, col].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                if pd.api.types.is_integer_dtype(dtype):
                    value = int(float(value))
                else:
                    value = float(value)
        except (ValueError, TypeError):
            return False
        
        self._dataframe.iloc[row, col] = value
        self.dataChanged.emit(index, index, [role])
        self.editCommitted.emit(EditCommand(self, row, col, old_value, value))
        return True
    
    def setDataFrame(self, df):
        self.beginResetModel()
        self._dataframe = df.copy()
        self.endResetModel()
    
    def silent_update(self, row, col, value):
        """Update cell without emitting signals"""
        self._dataframe.iloc[row, col] = value
        index = self.createIndex(row, col)
        self.dataChanged.emit(index, index)
    
    def add_row(self, create_command=True):
        """Add a new row to the DataFrame"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        new_row = pd.Series([pd.NA] * len(self._dataframe.columns), 
                           index=self._dataframe.columns)
        self._dataframe = pd.concat([self._dataframe, new_row.to_frame().T], 
                                  ignore_index=True)
        self.endInsertRows()
        
        if create_command:
            self.editCommitted.emit(RowCommand(self, self.rowCount() - 1))
    
    def delete_row(self, row_idx, create_command=True):
        """Delete a row from the DataFrame"""
        if create_command:
            row_data = self._dataframe.iloc[row_idx].copy()
        
        self.beginRemoveRows(QModelIndex(), row_idx, row_idx)
        self._dataframe.drop(self._dataframe.index[row_idx], inplace=True)
        self._dataframe.reset_index(drop=True, inplace=True)
        self.endRemoveRows()
        
        if create_command:
            self.editCommitted.emit(RowCommand(self, row_idx, row_data))
    
    def insert_row(self, idx, data):
        """Insert a row at a specific index"""
        self.beginInsertRows(QModelIndex(), idx, idx)
        part1 = self._dataframe.iloc[:idx]
        part2 = self._dataframe.iloc[idx:]
        new_row = pd.DataFrame([data.values], columns=self._dataframe.columns)
        self._dataframe = pd.concat([part1, new_row, part2]).reset_index(drop=True)
        self.endInsertRows()

class HistoryManager:
    """Manages undo/redo history using the Command pattern"""
    historyChanged = pyqtSignal()
    
    def __init__(self):
        self.history = []
        self.current_index = -1
    
    def add_command(self, command):
        # Remove any commands after current index
        if self.current_index + 1 < len(self.history):
            self.history = self.history[:self.current_index + 1]
        
        self.history.append(command)
        self.current_index += 1
        self.historyChanged.emit()
    
    def undo(self):
        if self.can_undo():
            self.history[self.current_index].undo()
            self.current_index -= 1
            self.historyChanged.emit()
    
    def redo(self):
        if self.can_redo():
            self.current_index += 1
            self.history[self.current_index].redo()
            self.historyChanged.emit()
    
    def jump_to_state(self, target_index):
        """Jump to a specific state in the history"""
        while self.current_index > target_index:
            self.undo()
        while self.current_index < target_index:
            self.redo()
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.current_index = -1
        self.historyChanged.emit()
    
    def can_undo(self):
        return self.current_index >= 0
    
    def can_redo(self):
        return self.current_index + 1 < len(self.history)

class StatisticsDialog(QDialog):
    """Dialog for displaying statistical analysis and visualizations"""
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df.select_dtypes(include='number')
        self.setWindowTitle("Statistical Analysis")
        self.setMinimumSize(1000, 800)
        
        main_layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        
        # Add tabs for different types of analysis
        tab_widget.addTab(self.create_distribution_tab(), "Distributions")
        tab_widget.addTab(self.create_pairplot_tab(), "Relationships")
        tab_widget.addTab(self.create_heatmap_tab(), "Correlation Heatmap")
        
        main_layout.addWidget(tab_widget)
    
    def create_distribution_tab(self):
        """Create tab with distribution plots"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Histograms
        fig_hist = plt.figure(figsize=(10, 6))
        if not self.df.empty:
            self.df.hist(ax=fig_hist.gca(), bins=20, alpha=0.7)
            fig_hist.suptitle('Distribution of Numeric Variables', fontsize=14)
        fig_hist.tight_layout()
        canvas_hist = FigureCanvas(fig_hist)
        
        # Box plots
        fig_box = plt.figure(figsize=(10, 4))
        if not self.df.empty:
            sns.boxplot(data=self.df, orient='h', ax=fig_box.gca())
            fig_box.gca().set_title('Box Plot Comparison')
        fig_box.tight_layout()
        canvas_box = FigureCanvas(fig_box)
        
        layout.addWidget(QLabel("<h3>Histograms of Numeric Columns</h3>"))
        layout.addWidget(canvas_hist)
        layout.addWidget(QLabel("<h3>Box Plot Comparison</h3>"))
        layout.addWidget(canvas_box)
        
        return tab
    
    def create_pairplot_tab(self):
        """Create tab with pair plot"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        try:
            if len(self.df.columns) > 1:
                pair_plot = sns.pairplot(self.df, diag_kind='kde')
                canvas = FigureCanvas(pair_plot.fig)
                layout.addWidget(canvas)
            else:
                layout.addWidget(QLabel("Need at least 2 numeric columns for pair plot."))
        except Exception as e:
            layout.addWidget(QLabel(f"Could not generate pair plot.\nError: {e}"))
        
        return tab
    
    def create_heatmap_tab(self):
        """Create tab with correlation heatmap"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if len(self.df.columns) > 1:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111)
            
            correlation_matrix = self.df.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', 
                       fmt=".2f", ax=ax, center=0)
            ax.set_title('Correlation Matrix', fontsize=14)
            
            fig.tight_layout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
        else:
            layout.addWidget(QLabel("Need at least 2 numeric columns for correlation analysis."))
        
        return tab

class ChartDialog(QDialog):
    """Dialog for creating custom charts"""
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df
        self.setWindowTitle("Create Chart from Selection")
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        
        # Chart options
        options_layout = QHBoxLayout()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Bar Chart", "Line Chart", "Histogram", 
            "Scatter Plot", "Pie Chart", "Box Plot"
        ])
        
        self.x_axis_combo = QComboBox()
        self.y_axis_combo = QComboBox()
        self.btn_generate = QPushButton("Generate Chart")
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        options_layout.addWidget(QLabel("Chart Type:"))
        options_layout.addWidget(self.chart_type_combo)
        options_layout.addWidget(QLabel("X-Axis:"))
        options_layout.addWidget(self.x_axis_combo)
        options_layout.addWidget(QLabel("Y-Axis:"))
        options_layout.addWidget(self.y_axis_combo)
        options_layout.addWidget(self.btn_generate)
        
        main_layout.addLayout(options_layout)
        
        # Chart display
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)
        
        # Connect signals
        self.chart_type_combo.currentTextChanged.connect(self.update_axis_options)
        self.btn_generate.clicked.connect(self.generate_chart)
        
        # Initialize
        self.populate_initial_options()
        self.update_axis_options()
    
    def populate_initial_options(self):
        """Populate column options based on data types"""
        self.numeric_cols = self.df.select_dtypes(include='number').columns.tolist()
        self.categorical_cols = self.df.select_dtypes(exclude='number').columns.tolist()
    
    def update_axis_options(self):
        """Update axis options based on selected chart type"""
        chart_type = self.chart_type_combo.currentText()
        self.x_axis_combo.clear()
        self.y_axis_combo.clear()
        
        if chart_type in ["Bar Chart", "Line Chart"]:
            self.x_axis_combo.addItems(self.categorical_cols + self.numeric_cols)
            self.y_axis_combo.addItems(self.numeric_cols)
            self.y_axis_combo.setEnabled(True)
        elif chart_type == "Histogram":
            self.x_axis_combo.addItems(self.numeric_cols)
            self.y_axis_combo.setEnabled(False)
        elif chart_type in ["Scatter Plot", "Box Plot"]:
            self.x_axis_combo.addItems(self.numeric_cols + self.categorical_cols)
            self.y_axis_combo.addItems(self.numeric_cols)
            self.y_axis_combo.setEnabled(True)
        elif chart_type == "Pie Chart":
            self.x_axis_combo.addItems(self.categorical_cols)
            self.y_axis_combo.addItems(self.numeric_cols)
            self.y_axis_combo.setEnabled(True)
    
    def generate_chart(self):
        """Generate the selected chart type"""
        chart_type = self.chart_type_combo.currentText()
        x_col = self.x_axis_combo.currentText()
        y_col = self.y_axis_combo.currentText()
        
        if not x_col:
            QMessageBox.warning(self, "Input Error", "Please select a column for the X-axis.")
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            if chart_type == "Bar Chart":
                if not y_col:
                    return
                grouped_data = self.df.groupby(x_col)[y_col].sum().nlargest(20)
                grouped_data.plot(kind='bar', ax=ax, color='skyblue')
                ax.set_ylabel(f"Sum of {y_col}")
                ax.set_title(f"Bar Chart: {y_col} by {x_col}")
                
            elif chart_type == "Line Chart":
                if not y_col:
                    return
                self.df.plot(x=x_col, y=y_col, ax=ax, marker='o')
                ax.set_title(f"Line Chart: {y_col} vs {x_col}")
                
            elif chart_type == "Histogram":
                self.df[x_col].plot(kind='hist', ax=ax, bins=20, alpha=0.7, color='lightgreen')
                ax.set_xlabel(x_col)
                ax.set_title(f"Histogram of {x_col}")
                
            elif chart_type == "Scatter Plot":
                if not y_col:
                    return
                self.df.plot(kind='scatter', x=x_col, y=y_col, ax=ax, alpha=0.6)
                ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
                
            elif chart_type == "Box Plot":
                if not y_col:
                    return
                sns.boxplot(data=self.df, x=x_col, y=y_col, ax=ax)
                ax.set_title(f"Box Plot: {y_col} by {x_col}")
                
            elif chart_type == "Pie Chart":
                if not y_col:
                    return
                pie_data = self.df.groupby(x_col)[y_col].sum().nlargest(10)
                pie_data.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90)
                ax.set_ylabel('')
                ax.set_title(f"Pie Chart: {y_col} by {x_col}")
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Chart Error", f"Could not generate chart:\n{e}")

class TimelineDialog(QDialog):
    """Dialog for showing edit history timeline"""
    stateSelected = pyqtSignal(int)
    
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle("Edit History Timeline")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(
            lambda item: self.stateSelected.emit(self.list_widget.row(item) - 1) or self.accept()
        )
        
        layout.addWidget(QLabel("Double-click to jump to a state:"))
        layout.addWidget(self.list_widget)
        
        self.update_list()
    
    def update_list(self):
        """Update the timeline list"""
        self.list_widget.clear()
        self.list_widget.addItem(QListWidgetItem("--- Original Loaded Data ---"))
        
        for i, command in enumerate(self.history_manager.history):
            self.list_widget.addItem(QListWidgetItem(f"{i+1:03d}: {command}"))
        
        # Highlight current state
        current_row = self.history_manager.current_index + 1
        self.list_widget.setCurrentRow(current_row)
        
        if current_row < self.list_widget.count():
            font = self.list_widget.item(current_row).font()
            font.setBold(True)
            self.list_widget.item(current_row).setFont(font)

class FindDialog(QDialog):
    """Dialog for finding values in the dataset"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find Value")
        
        layout = QGridLayout(self)
        layout.addWidget(QLabel("Find what:"), 0, 0)
        
        self.find_input = QLineEdit()
        layout.addWidget(self.find_input, 0, 1)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 1, 0, 1, 2)
    
    def get_text(self):
        return self.find_input.text()

class InfoDialog(QDialog):
    """Dialog for displaying DataFrame information"""
    def __init__(self, info_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DataFrame Info")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(info_text)
        text_edit.setFontFamily("Courier New")
        
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class DatabaseDialog(QDialog):
    """Dialog for database operations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Operations")
        
        layout = QGridLayout(self)
        layout.addWidget(QLabel("Database Name:"), 0, 0)
        self.db_name = QLineEdit("data.db")
        layout.addWidget(self.db_name, 0, 1)
        
        layout.addWidget(QLabel("Table Name:"), 1, 0)
        self.table_name = QLineEdit("my_table")
        layout.addWidget(self.table_name, 1, 1)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, 2, 0, 1, 2)
    
    def get_info(self):
        return {
            "db_name": self.db_name.text(),
            "table_name": self.table_name.text()
        }

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Master Pro with Analytics")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize components
        self.history_manager = HistoryManager()
        self.original_df = pd.DataFrame()
        
        self._create_actions()
        self._setup_ui()
        self._connect_signals()
        self.update_action_states()
    
    def _create_actions(self):
        """Create keyboard shortcuts and actions"""
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        
        self.find_action = QAction("Find...", self)
        self.find_action.setShortcut(QKeySequence.Find)
        
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.find_action)
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Table view
        self.table_view = QTableView()
        self.model = PandasModel(pd.DataFrame({'Welcome': ['Load data to begin analysis']}))
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.main_layout.addWidget(self.table_view, 4)
        
        # Button panel
        self.button_panel = QWidget()
        self.button_panel.setFixedWidth(250)
        self.panel_layout = QVBoxLayout(self.button_panel)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        self.btn_import = QPushButton("📁 Import File...")
        self.btn_export = QPushButton("💾 Export File...")
        file_layout.addWidget(self.btn_import)
        file_layout.addWidget(self.btn_export)
        file_group.setLayout(file_layout)
        
        # Data sources group
        source_group = QGroupBox("Data Sources")
        source_layout = QVBoxLayout()
        self.btn_db_import = QPushButton("🗄️ Import from DB")
        self.btn_db_export = QPushButton("🗄️ Export to DB")
        self.btn_api_fetch = QPushButton("🌐 Fetch from API")
        source_layout.addWidget(self.btn_db_import)
        source_layout.addWidget(self.btn_db_export)
        source_layout.addWidget(self.btn_api_fetch)
        source_group.setLayout(source_layout)
        
        # Row operations group
        row_group = QGroupBox("Row Operations")
        row_layout = QVBoxLayout()
        self.btn_add_row = QPushButton("➕ Add Row")
        self.btn_del_row = QPushButton("➖ Delete Selected Row(s)")
        row_layout.addWidget(self.btn_add_row)
        row_layout.addWidget(self.btn_del_row)
        row_group.setLayout(row_layout)
        
        # History group
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout()
        self.btn_undo = QPushButton("↶ Undo")
        self.btn_redo = QPushButton("↷ Redo")
        self.btn_timeline = QPushButton("📋 Show Timeline...")
        self.btn_restart = QPushButton("🔄 Restart All Edits")
        self.btn_restart.setStyleSheet("background-color: #ff9800; color: white;")
        history_layout.addWidget(self.btn_undo)
        history_layout.addWidget(self.btn_redo)
        history_layout.addWidget(self.btn_timeline)
        history_layout.addWidget(self.btn_restart)
