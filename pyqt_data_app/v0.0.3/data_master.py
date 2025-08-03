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
    QGroupBox, QComboBox
)
from PyQt5.QtCore import QObject, QAbstractTableModel, Qt, pyqtSignal, QModelIndex
from PyQt5.QtGui import QKeySequence

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
plt.style.use('seaborn-v0_8-whitegrid') # Use a nice style for the charts

# --- Command Classes for Temporal History ---
class Command:
    """Base class for an undoable command."""
    def __init__(self, model): self.model = model
    def undo(self): pass
    def redo(self): pass
    def __str__(self): return "Generic Command"

class EditCommand(Command):
    def __init__(self, model, row, col, old_value, new_value):
        super().__init__(model); self.row, self.col = row, col
        self.old_value, self.new_value = old_value, new_value
    def undo(self): self.model.silent_update(self.row, self.col, self.old_value)
    def redo(self): self.model.silent_update(self.row, self.col, self.new_value)
    def __str__(self):
        col_name = self.model._dataframe.columns[self.col]
        return f"Edit cell ({self.row}, '{col_name}') to '{self.new_value}'"

class RowCommand(Command):
    def __init__(self, model, index, row_data=None):
        super().__init__(model); self.index = index; self.row_data = row_data
    def undo(self):
        if self.row_data is not None: self.model.insert_row(self.index, self.row_data) # Undo delete
        else: self.model.delete_row(self.index, create_command=False) # Undo add
    def redo(self):
        if self.row_data is not None: self.model.delete_row(self.index, create_command=False) # Redo delete
        else: self.model.add_row(create_command=False) # Redo add
    def __str__(self):
        return f"Delete row at index {self.index}" if self.row_data is not None else "Add new row"

# --- Pandas Model ---
class PandasModel(QAbstractTableModel):
    editCommitted = pyqtSignal(Command)
    def __init__(self, df=pd.DataFrame()): super().__init__(); self._dataframe = df
    def rowCount(self, p=None): return self._dataframe.shape[0]
    def columnCount(self, p=None): return self._dataframe.shape[1]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid() or r!=Qt.DisplayRole: return None
        return str(self._dataframe.iloc[i.row(), i.column()])
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r==Qt.DisplayRole:
            if o==Qt.Horizontal: return str(self._dataframe.columns[s])
            if o==Qt.Vertical: return str(self._dataframe.index[s])
    def flags(self, i): return super().flags(i)|Qt.ItemIsEditable
    def setData(self, i, v, r=Qt.EditRole):
        if r!=Qt.EditRole: return False
        row,col = i.row(),i.column(); old=self._dataframe.iloc[row,col]
        try:
            dtype=self._dataframe.iloc[:,col].dtype
            if pd.api.types.is_numeric_dtype(dtype): v=int(float(v)) if pd.api.types.is_integer_dtype(dtype) else float(v)
        except: return False
        self._dataframe.iloc[row,col]=v; self.dataChanged.emit(i,i,[r])
        self.editCommitted.emit(EditCommand(self,row,col,old,v)); return True
    def setDataFrame(self,df): self.beginResetModel(); self._dataframe=df.copy(); self.endResetModel()
    def silent_update(self,r,c,v): self._dataframe.iloc[r,c]=v; self.dataChanged.emit(self.createIndex(r,c),self.createIndex(r,c))
    def add_row(self,create_command=True):
        self.beginInsertRows(QModelIndex(),self.rowCount(),self.rowCount())
        self._dataframe.loc[self.rowCount()]=[pd.NA]*len(self._dataframe.columns)
        self.endInsertRows()
        if create_command: self.editCommitted.emit(RowCommand(self, self.rowCount()-1))
    def delete_row(self,row_idx,create_command=True):
        if create_command: row_data=self._dataframe.iloc[row_idx].copy()
        self.beginRemoveRows(QModelIndex(),row_idx,row_idx)
        self._dataframe.drop(self._dataframe.index[row_idx],inplace=True)
        self._dataframe.reset_index(drop=True,inplace=True); self.endRemoveRows()
        if create_command: self.editCommitted.emit(RowCommand(self,row_idx,row_data))
    def insert_row(self,idx,data):
        self.beginInsertRows(QModelIndex(),idx,idx)
        part1=self._dataframe.iloc[:idx]; part2=self._dataframe.iloc[idx:]
        self._dataframe=pd.concat([part1,pd.DataFrame([data.values],columns=self._dataframe.columns),part2]).reset_index(drop=True)
        self.endInsertRows()

# --- History Manager ---
class HistoryManager(QObject):
    historyChanged = pyqtSignal()
    def __init__(self): super().__init__(); self.history=[]; self.current_index=-1
    def add_command(self,command):
        if self.current_index+1<len(self.history): self.history=self.history[:self.current_index+1]
        self.history.append(command); self.current_index+=1; self.historyChanged.emit()
    def undo(self):
        if self.can_undo(): self.history[self.current_index].undo(); self.current_index-=1; self.historyChanged.emit()
    def redo(self):
        if self.can_redo(): self.current_index+=1; self.history[self.current_index].redo(); self.historyChanged.emit()
    def jump_to_state(self,idx):
        while self.current_index>idx: self.undo()
        while self.current_index<idx: self.redo()
    def clear(self): self.history.clear(); self.current_index=-1; self.historyChanged.emit()
    def can_undo(self): return self.current_index>-1
    def can_redo(self): return self.current_index+1<len(self.history)

# --- Dialogs ---
class ChartDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent); self.df = df; self.setWindowTitle("Create Chart from Selection"); self.setMinimumSize(800, 600)
        main_layout=QVBoxLayout(self); options_layout=QHBoxLayout(); self.chart_type_combo=QComboBox()
        self.chart_type_combo.addItems(["Bar Chart", "Line Chart", "Histogram", "Scatter Plot", "Pie Chart"])
        self.x_axis_combo=QComboBox(); self.y_axis_combo=QComboBox(); self.btn_generate=QPushButton("Generate Chart")
        options_layout.addWidget(QLabel("Chart Type:")); options_layout.addWidget(self.chart_type_combo)
        options_layout.addWidget(QLabel("X-Axis:")); options_layout.addWidget(self.x_axis_combo)
        options_layout.addWidget(QLabel("Y-Axis:")); options_layout.addWidget(self.y_axis_combo); options_layout.addWidget(self.btn_generate)
        main_layout.addLayout(options_layout); self.figure=plt.figure(); self.canvas=FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas); self.chart_type_combo.currentTextChanged.connect(self.update_axis_options)
        self.btn_generate.clicked.connect(self.generate_chart); self.populate_initial_options(); self.update_axis_options()
    def populate_initial_options(self):
        self.numeric_cols=self.df.select_dtypes(include='number').columns.tolist()
        self.categorical_cols=self.df.select_dtypes(exclude='number').columns.tolist()
    def update_axis_options(self):
        chart_type=self.chart_type_combo.currentText(); self.x_axis_combo.clear(); self.y_axis_combo.clear()
        if chart_type in ["Bar Chart", "Line Chart"]:
            self.x_axis_combo.addItems(self.categorical_cols+self.numeric_cols); self.y_axis_combo.addItems(self.numeric_cols); self.y_axis_combo.setEnabled(True)
        elif chart_type=="Histogram":
            self.x_axis_combo.addItems(self.numeric_cols); self.y_axis_combo.setEnabled(False)
        elif chart_type=="Scatter Plot":
            self.x_axis_combo.addItems(self.numeric_cols); self.y_axis_combo.addItems(self.numeric_cols); self.y_axis_combo.setEnabled(True)
        elif chart_type=="Pie Chart":
            self.x_axis_combo.addItems(self.categorical_cols); self.y_axis_combo.addItems(self.numeric_cols); self.y_axis_combo.setEnabled(True)
    def generate_chart(self):
        chart_type=self.chart_type_combo.currentText(); x_col=self.x_axis_combo.currentText(); y_col=self.y_axis_combo.currentText()
        if not x_col: QMessageBox.warning(self,"Input Error","Please select a column for the X-axis."); return
        self.figure.clear(); ax=self.figure.add_subplot(111)
        try:
            if chart_type=="Bar Chart":
                if not y_col: return
                self.df.groupby(x_col)[y_col].sum().nlargest(20).plot(kind='bar',ax=ax); ax.set_ylabel(f"Sum of {y_col}")
            elif chart_type=="Line Chart":
                if not y_col: return
                self.df.plot(x=x_col,y=y_col,ax=ax)
            elif chart_type=="Histogram":
                self.df[x_col].plot(kind='hist',ax=ax,bins=15); ax.set_xlabel(x_col)
            elif chart_type=="Scatter Plot":
                if not y_col: return
                self.df.plot(kind='scatter',x=x_col,y=y_col,ax=ax)
            elif chart_type=="Pie Chart":
                if not y_col: return
                self.df.groupby(x_col)[y_col].sum().nlargest(10).plot(kind='pie',ax=ax,autopct='%1.1f%%',startangle=90); ax.set_ylabel('')
            ax.set_title(f"{chart_type} of {y_col if y_col else ''} by {x_col}"); self.figure.tight_layout(); self.canvas.draw()
        except Exception as e: QMessageBox.critical(self,"Chart Error",f"Could not generate chart:\n{e}")
class TimelineDialog(QDialog):
    stateSelected=pyqtSignal(int)
    def __init__(self,hist_mgr,parent=None):
        super().__init__(parent);self.hist_mgr=hist_mgr;self.setWindowTitle("Edit History Timeline");self.setMinimumSize(600,400)
        self.layout=QVBoxLayout(self);self.list_widget=QListWidget()
        self.list_widget.itemDoubleClicked.connect(lambda item:self.stateSelected.emit(self.list_widget.row(item)-1) or self.accept())
        self.layout.addWidget(QLabel("Double-click to jump to a state:"));self.layout.addWidget(self.list_widget);self.update_list()
    def update_list(self):
        self.list_widget.clear();self.list_widget.addItem(QListWidgetItem("--- Original Loaded Data ---"))
        for i,cmd in enumerate(self.hist_mgr.history):self.list_widget.addItem(QListWidgetItem(f"{i+1:03d}: {cmd}"))
        curr_row=self.hist_mgr.current_index+1;self.list_widget.setCurrentRow(curr_row)
        font=self.list_widget.item(curr_row).font();font.setBold(True);self.list_widget.item(curr_row).setFont(font)
class FindDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle("Find Value");self.layout=QGridLayout(self);self.layout.addWidget(QLabel("Find what:"),0,0)
        self.find_input=QLineEdit();self.layout.addWidget(self.find_input,0,1)
        btns=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);btns.accepted.connect(self.accept);btns.rejected.connect(self.reject)
        self.layout.addWidget(btns,1,0,1,2)
    def get_text(self):return self.find_input.text()
class InfoDialog(QDialog):
    def __init__(self,info_txt,parent=None):
        super().__init__(parent);self.setWindowTitle("DataFrame Info");self.setMinimumSize(600,500);layout=QVBoxLayout(self)
        text_edit=QTextEdit();text_edit.setReadOnly(True);text_edit.setText(info_txt);text_edit.setFontFamily("monospace")
        layout.addWidget(text_edit);btns=QDialogButtonBox(QDialogButtonBox.Ok);btns.accepted.connect(self.accept);layout.addWidget(btns)
class DbDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle("Database Operations");self.layout=QGridLayout(self)
        self.layout.addWidget(QLabel("DB Name:"),0,0);self.db_name=QLineEdit("data.db");self.layout.addWidget(self.db_name,0,1)
        self.layout.addWidget(QLabel("Table Name:"),1,0);self.table_name=QLineEdit("my_table");self.layout.addWidget(self.table_name,1,1)
    def get_info(self):return {"db_name":self.db_name.text(),"table_name":self.table_name.text()}

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle("Data Master Pro with Analytics");self.setGeometry(100,100,1200,700)
        self.history_manager=HistoryManager();self.original_df=pd.DataFrame()
        self._create_actions_for_shortcuts();self._setup_ui();self._connect_signals();self.update_action_states()
    def _create_actions_for_shortcuts(self):
        self.undo_action=QAction("Undo",self);self.undo_action.setShortcut(QKeySequence.Undo)
        self.redo_action=QAction("Redo",self);self.redo_action.setShortcut(QKeySequence.Redo)
        self.find_action=QAction("Find...",self);self.find_action.setShortcut(QKeySequence.Find)
        self.addAction(self.undo_action);self.addAction(self.redo_action);self.addAction(self.find_action)
    def _setup_ui(self):
        self.central_widget=QWidget();self.setCentralWidget(self.central_widget);self.main_layout=QHBoxLayout(self.central_widget)
        self.table_view=QTableView();self.model=PandasModel(pd.DataFrame({'Hint':['Select columns, then click "Create Chart..."']}))
        self.table_view.setModel(self.model);self.table_view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_layout.addWidget(self.table_view,4);self.button_panel=QWidget();self.button_panel.setFixedWidth(220)
        self.panel_layout=QVBoxLayout(self.button_panel)
        file_group=QGroupBox("File I/O");file_layout=QVBoxLayout();self.btn_import=QPushButton("Import File...");self.btn_export=QPushButton("Export File...")
        file_layout.addWidget(self.btn_import);file_layout.addWidget(self.btn_export);file_group.setLayout(file_layout)
        source_group=QGroupBox("Data Sources");source_layout=QVBoxLayout()
        self.btn_db_import=QPushButton("Import from DB");self.btn_db_export=QPushButton("Export to DB");self.btn_api_fetch=QPushButton("Fetch from API")
        source_layout.addWidget(self.btn_db_import);source_layout.addWidget(self.btn_db_export);source_layout.addWidget(self.btn_api_fetch)
        source_group.setLayout(source_layout)
        row_group=QGroupBox("Row Operations");row_layout=QVBoxLayout();self.btn_add_row=QPushButton("Add Row");self.btn_del_row=QPushButton("Delete Selected Row(s)")
        row_layout.addWidget(self.btn_add_row);row_layout.addWidget(self.btn_del_row);row_group.setLayout(row_layout)
        history_group=QGroupBox("History");history_layout=QVBoxLayout();self.btn_undo=QPushButton("Undo");self.btn_redo=QPushButton("Redo")
        self.btn_timeline=QPushButton("Show Timeline...");self.btn_restart=QPushButton("Restart All Edits");self.btn_restart.setStyleSheet("background-color:#ffc107;")
        history_layout.addWidget(self.btn_undo);history_layout.addWidget(self.btn_redo);history_layout.addWidget(self.btn_timeline);history_layout.addWidget(self.btn_restart)
        history_group.setLayout(history_layout)
        tools_group=QGroupBox("Tools & Analytics");tools_layout=QVBoxLayout();self.btn_find=QPushButton("Find Value...");self.btn_info=QPushButton("Get DataFrame Info")
        self.btn_chart=QPushButton("Create Chart...");self.btn_chart.setStyleSheet("background-color:#cce5ff;")
        tools_layout.addWidget(self.btn_find);tools_layout.addWidget(self.btn_info);tools_layout.addWidget(self.btn_chart)
        tools_group.setLayout(tools_layout)
        self.panel_layout.addWidget(file_group);self.panel_layout.addWidget(source_group);self.panel_layout.addWidget(row_group);self.panel_layout.addWidget(history_group)
        self.panel_layout.addWidget(tools_group);self.panel_layout.addStretch();self.main_layout.addWidget(self.button_panel)
    def _connect_signals(self):
        self.btn_import.clicked.connect(self.import_file);self.btn_export.clicked.connect(self.export_file)
        self.btn_db_import.clicked.connect(self.db_import);self.btn_db_export.clicked.connect(self.db_export)
        self.btn_api_fetch.clicked.connect(self.fetch_from_api);self.btn_add_row.clicked.connect(self.model.add_row)
        self.btn_del_row.clicked.connect(self.delete_selected_rows);self.btn_undo.clicked.connect(self.history_manager.undo)
        self.btn_redo.clicked.connect(self.history_manager.redo);self.btn_timeline.clicked.connect(self.show_timeline)
        self.btn_restart.clicked.connect(self.restart_edits);self.btn_find.clicked.connect(self.find_value);self.btn_info.clicked.connect(self.get_info)
        self.btn_chart.clicked.connect(self.create_chart_from_selection);self.model.editCommitted.connect(self.history_manager.add_command)
        self.history_manager.historyChanged.connect(self.update_action_states);self.undo_action.triggered.connect(self.history_manager.undo)
        self.redo_action.triggered.connect(self.history_manager.redo);self.find_action.triggered.connect(self.find_value)
        self.table_view.horizontalHeader().customContextMenuRequested.connect(self.header_context_menu)
    def update_action_states(self):
        has_data=not self.model._dataframe.empty
        for btn in [self.btn_export,self.btn_db_export,self.btn_add_row,self.btn_del_row,self.btn_find,self.btn_info,self.btn_chart]: btn.setEnabled(has_data)
        self.btn_undo.setEnabled(self.history_manager.can_undo());self.btn_redo.setEnabled(self.history_manager.can_redo())
        self.btn_restart.setEnabled(not self.original_df.empty and not self.model._dataframe.equals(self.original_df))
        self.btn_timeline.setEnabled(bool(self.history_manager.history))
    def _load_data(self,df):
        self.model.setDataFrame(df);self.original_df=df.copy();self.history_manager.clear()
        QMessageBox.information(self,"Success","Data loaded successfully.")
    def import_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Open File","","CSV/Excel Files (*.csv *.xlsx *.xls)")
        if not path: return
        try:self._load_data(pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path))
        except Exception as e:QMessageBox.critical(self,"Import Error",f"Could not load file:\n{e}")
    def export_file(self):
        if self.model._dataframe.empty:return
        path,_=QFileDialog.getSaveFileName(self,"Export File","","CSV (*.csv);;Excel (*.xlsx)")
        if not path:return
        try:
            if path.endswith('.csv'):self.model._dataframe.to_csv(path,index=False)
            else:self.model._dataframe.to_excel(path,index=False)
        except Exception as e:QMessageBox.critical(self,"Export Error",f"Could not export file:\n{e}")
    def db_import(self):
        dialog=DbDialog(self)
        if dialog.exec_():
            info=dialog.get_info()
            try:engine=create_engine(f"sqlite:///{info['db_name']}");self._load_data(pd.read_sql(f"SELECT * FROM {info['table_name']}",engine))
            except Exception as e:QMessageBox.critical(self,"DB Import Error",f"Could not import from DB:\n{e}")
    def db_export(self):
        if self.model._dataframe.empty:return
        dialog=DbDialog(self)
        if dialog.exec_():
            info=dialog.get_info()
            try:engine=create_engine(f"sqlite:///{info['db_name']}");self.model._dataframe.to_sql(info['table_name'],engine,if_exists='replace',index=False)
            except Exception as e:QMessageBox.critical(self,"DB Export Error",f"Could not export to DB:\n{e}")
    def fetch_from_api(self):
        try:r=requests.get("https://jsonplaceholder.typicode.com/users",timeout=5);r.raise_for_status();self._load_data(pd.json_normalize(r.json()))
        except Exception as e:QMessageBox.critical(self,"API Error",f"Could not fetch from API:\n{e}")
    def delete_selected_rows(self):
        rows=sorted(set(index.row() for index in self.table_view.selectedIndexes()),reverse=True)
        if not rows:return
        for row_idx in rows:self.model.delete_row(row_idx)
    def restart_edits(self):
        if not self.btn_restart.isEnabled():return
        reply=QMessageBox.question(self,"Confirm Restart","Discard all changes made in this session?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if reply==QMessageBox.Yes:self._load_data(self.original_df)
    def show_timeline(self):
        dialog=TimelineDialog(self.history_manager,self);dialog.stateSelected.connect(self.history_manager.jump_to_state);dialog.exec_()
    def find_value(self):
        dialog=FindDialog(self)
        if dialog.exec_():
            text=dialog.get_text()
            if not text:return
            matches=self.model._dataframe.astype(str).apply(lambda x:x.str.contains(text,case=False,na=False))
            match_indices=matches.stack()[matches.stack()]
            if not match_indices.empty:
                row,col_name=match_indices.index[0];col=self.model._dataframe.columns.get_loc(col_name)
                self.table_view.setCurrentIndex(self.model.createIndex(row,col))
            else:QMessageBox.information(self,"Not Found",f"Value '{text}' not found.")
    def get_info(self):
        if self.model._dataframe.empty:return
        with StringIO() as buffer:self.model._dataframe.info(buf=buffer);info=buffer.getvalue()
        desc=self.model._dataframe.describe(include='all').to_string()
        InfoDialog(f"--- Info ---\n{info}\n\n--- Description ---\n{desc}",self).exec_()
    def header_context_menu(self,pos):
        menu=QMenu();col=self.table_view.horizontalHeader().logicalIndexAt(pos)
        sort_asc=menu.addAction("Sort Ascending");sort_desc=menu.addAction("Sort Descending")
        action=menu.exec_(self.table_view.horizontalHeader().mapToGlobal(pos))
        if action==sort_asc:self.table_view.sortByColumn(col,Qt.AscendingOrder)
        elif action==sort_desc:self.table_view.sortByColumn(col,Qt.DescendingOrder)
    def create_chart_from_selection(self):
        selected_indexes=self.table_view.selectionModel().selectedIndexes()
        if not selected_indexes:QMessageBox.information(self,"Selection Required","Please select one or more columns to create a chart.");return
        selected_columns_indices=sorted(list(set(index.column() for index in selected_indexes)))
        column_names=[self.model._dataframe.columns[i] for i in selected_columns_indices]
        chart_df=self.model._dataframe[column_names].copy();dialog=ChartDialog(chart_df,self);dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())