# API Documentation

This document provides technical API documentation for developers who want to understand, extend, or integrate with the Import-Export Qt5 Data Management Tool.

## Table of Contents
- [Core Classes](#core-classes)
- [Models](#models)
- [Dialogs](#dialogs)
- [Main Application](#main-application)
- [Extension Points](#extension-points)
- [Events and Signals](#events-and-signals)

## Core Classes

### PandasModel

**Purpose**: Qt model for displaying pandas DataFrames in QTableView.

**Location**: `main.py`

**Class Definition**:
```python
class PandasModel(QAbstractTableModel):
    """A model to interface a pandas DataFrame with a QTableView."""
```

**Methods**:

#### `__init__(dataframe: pd.DataFrame = pd.DataFrame())`
Initialize the model with a DataFrame.

**Parameters**:
- `dataframe` (pd.DataFrame): Initial DataFrame to display

**Returns**: None

**Example**:
```python
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
model = PandasModel(df)
```

#### `rowCount(parent=None) -> int`
Return the number of rows in the DataFrame.

**Parameters**:
- `parent` (QModelIndex, optional): Parent index

**Returns**: Number of rows

#### `columnCount(parent=None) -> int`
Return the number of columns in the DataFrame.

**Parameters**:
- `parent` (QModelIndex, optional): Parent index

**Returns**: Number of columns

#### `data(index, role=Qt.DisplayRole) -> Any`
Return data for the given index and role.

**Parameters**:
- `index` (QModelIndex): Cell index
- `role` (Qt.ItemDataRole): Data role

**Returns**: Cell data as string or None

#### `headerData(section, orientation, role=Qt.DisplayRole) -> str`
Return header data for the given section and orientation.

**Parameters**:
- `section` (int): Header section index
- `orientation` (Qt.Orientation): Horizontal or vertical
- `role` (Qt.ItemDataRole): Data role

**Returns**: Header text

#### `setDataFrame(dataframe: pd.DataFrame)`
Update the model with a new DataFrame.

**Parameters**:
- `dataframe` (pd.DataFrame): New DataFrame to display

**Returns**: None

**Example**:
```python
new_df = pd.DataFrame({'X': [5, 6], 'Y': [7, 8]})
model.setDataFrame(new_df)
```

## Dialogs

### DbDialog

**Purpose**: Dialog for configuring database connections.

**Location**: `main.py`

**Class Definition**:
```python
class DbDialog(QDialog):
    """A dialog to get database connection details from the user."""
```

**Signals**:

#### `db_import_requested = pyqtSignal(dict)`
Emitted when user requests database import.

**Payload**: Dictionary with connection details

#### `db_export_requested = pyqtSignal(dict)`
Emitted when user requests database export.

**Payload**: Dictionary with connection details

**Methods**:

#### `__init__(parent=None)`
Initialize the database dialog.

**Parameters**:
- `parent` (QWidget, optional): Parent widget

#### `get_db_info() -> dict`
Get database connection information from form fields.

**Returns**: Dictionary with keys:
- `db_type` (str): Database type (e.g., 'sqlite')
- `db_name` (str): Database name/path
- `table_name` (str): Table name

**Example**:
```python
dialog = DbDialog()
if dialog.exec_():
    info = dialog.get_db_info()
    print(f"Database: {info['db_name']}")
```

#### `on_import()`
Handle import button click.

**Returns**: None

#### `on_export()`
Handle export button click.

**Returns**: None

## Main Application

### MainWindow

**Purpose**: Main application window with all UI components.

**Location**: `main.py`

**Class Definition**:
```python
class MainWindow(QMainWindow):
    """Main application window."""
```

**Attributes**:

- `central_widget` (QWidget): Central widget
- `layout` (QVBoxLayout): Main layout
- `table_view` (QTableView): Table for displaying data
- `df` (pd.DataFrame): Current DataFrame
- `model` (PandasModel): Table model
- `btn_*` (QPushButton): Various buttons

**Methods**:

#### `__init__()`
Initialize the main window and UI components.

#### `show_message(title: str, message: str)`
Display a message dialog to the user.

**Parameters**:
- `title` (str): Dialog title
- `message` (str): Message content

**Example**:
```python
self.show_message("Success", "Operation completed successfully.")
```

#### `import_csv()`
Import data from a CSV file.

**Process**:
1. Show file dialog
2. Read CSV with pandas
3. Update table view
4. Show success/error message

**Returns**: None

#### `import_excel()`
Import data from an Excel file.

**Process**:
1. Show file dialog
2. Read Excel with pandas
3. Update table view
4. Show success/error message

**Returns**: None

#### `export_csv()`
Export current data to a CSV file.

**Process**:
1. Show save dialog
2. Write DataFrame to CSV
3. Show success/error message

**Returns**: None

#### `export_excel()`
Export current data to an Excel file.

**Process**:
1. Show save dialog
2. Write DataFrame to Excel
3. Show success/error message

**Returns**: None

#### `open_db_dialog()`
Open the database operations dialog.

**Returns**: None

#### `import_from_db(db_info: dict)`
Import data from a database.

**Parameters**:
- `db_info` (dict): Database connection details

**Process**:
1. Create database engine
2. Execute SQL query
3. Load data into DataFrame
4. Update table view
5. Show success/error message

**Returns**: None

#### `export_to_db(db_info: dict)`
Export data to a database.

**Parameters**:
- `db_info` (dict): Database connection details

**Process**:
1. Create database engine
2. Write DataFrame to database table
3. Show success/error message

**Returns**: None

#### `fetch_from_api()`
Fetch data from a REST API.

**Process**:
1. Make HTTP GET request
2. Parse JSON response
3. Normalize nested data
4. Update table view
5. Show success/error message

**Returns**: None

## Extension Points

### Adding New Import Formats

To add a new import format:

1. **Add a button**:
```python
self.btn_import_json = QPushButton("Import from JSON")
self.layout.addWidget(self.btn_import_json)
self.btn_import_json.clicked.connect(self.import_json)
```

2. **Implement the import method**:
```python
def import_json(self):
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Open JSON File", "", "JSON Files (*.json)"
    )
    if file_path:
        try:
            self.df = pd.read_json(file_path)
            self.model.setDataFrame(self.df)
            self.show_message("Success", "JSON file imported successfully.")
        except Exception as e:
            self.show_message("Error", f"Could not import JSON file:\n{e}")
```

### Adding New Export Formats

Similar process to import:

```python
def export_json(self):
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save JSON File", "", "JSON Files (*.json)"
    )
    if file_path:
        try:
            self.df.to_json(file_path, orient='records', indent=2)
            self.show_message("Success", f"Data exported to {file_path}")
        except Exception as e:
            self.show_message("Error", f"Could not export to JSON:\n{e}")
```

### Adding Database Support

To add PostgreSQL support:

1. **Update DbDialog**:
```python
self.db_type_input = QComboBox()
self.db_type_input.addItems(['sqlite', 'postgresql', 'mysql'])
```

2. **Update connection string logic**:
```python
if db_type == 'postgresql':
    engine = create_engine(f"postgresql://{user}:{password}@{host}/{db_name}")
elif db_type == 'sqlite':
    engine = create_engine(f"sqlite:///{db_name}")
```

### Adding Data Transformations

Add a new menu or buttons for transformations:

```python
def transform_data(self):
    """Apply data transformations."""
    try:
        # Example: Remove duplicates
        self.df = self.df.drop_duplicates()
        # Example: Fill missing values
        self.df = self.df.fillna(0)
        # Update view
        self.model.setDataFrame(self.df)
        self.show_message("Success", "Data transformed successfully.")
    except Exception as e:
        self.show_message("Error", f"Transformation failed:\n{e}")
```

## Events and Signals

### PyQt5 Signals

#### Button Click Events

All buttons use the `clicked` signal:

```python
button.clicked.connect(handler_method)
```

#### Custom Signals

The DbDialog class defines custom signals:

```python
db_import_requested = pyqtSignal(dict)
db_export_requested = pyqtSignal(dict)
```

**Usage**:
```python
dialog = DbDialog()
dialog.db_import_requested.connect(self.import_from_db)
dialog.db_export_requested.connect(self.export_to_db)
```

### Model Events

The PandasModel uses standard Qt model signals:

- `dataChanged`: Emitted when data changes
- `layoutChanged`: Emitted when layout changes
- `modelReset`: Emitted when model is reset

**Example**:
```python
model.dataChanged.connect(on_data_changed)
```

## Data Flow

### Import Flow

```
User Action → File Dialog → pandas.read_*() → DataFrame → 
PandasModel.setDataFrame() → QTableView.setModel() → Display
```

### Export Flow

```
User Action → Save Dialog → DataFrame.to_*() → File → Success Message
```

### Database Flow

```
User Action → DbDialog → Connection String → SQLAlchemy Engine → 
pandas.read_sql() or DataFrame.to_sql() → Success Message
```

## Error Handling

All methods use try-except blocks:

```python
try:
    # Operation
    self.show_message("Success", "Operation completed.")
except Exception as e:
    self.show_message("Error", f"Operation failed:\n{e}")
```

## Dependencies

### Required Libraries

- **PyQt5**: GUI framework
  - `QtWidgets`: UI components
  - `QtCore`: Core functionality

- **pandas**: Data manipulation
  - `read_csv()`, `read_excel()`: Import
  - `to_csv()`, `to_excel()`: Export
  - `DataFrame`: Data structure

- **SQLAlchemy**: Database abstraction
  - `create_engine()`: Connection
  - `Engine.connect()`: Execution

- **requests**: HTTP library
  - `get()`: HTTP requests
  - `Response.json()`: JSON parsing

- **openpyxl**: Excel support (pandas backend)

## Configuration

### Customizing the Application

#### Default Database Type

Change in `DbDialog.__init__()`:
```python
self.db_type_input = QLineEdit("postgresql")  # Instead of "sqlite"
```

#### Default API Endpoint

Change in `MainWindow.fetch_from_api()`:
```python
url = "https://your-api.com/endpoint"  # Instead of JSONPlaceholder
```

#### Window Size

Change in `MainWindow.__init__()`:
```python
self.setGeometry(100, 100, 1200, 800)  # Larger window
```

## Testing API

### Unit Testing Example

```python
import unittest
from PyQt5.QtWidgets import QApplication
from main import PandasModel
import pandas as pd

class TestPandasModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])
    
    def test_row_count(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        model = PandasModel(df)
        self.assertEqual(model.rowCount(), 3)
    
    def test_column_count(self):
        df = pd.DataFrame({'A': [1], 'B': [2]})
        model = PandasModel(df)
        self.assertEqual(model.columnCount(), 2)

if __name__ == '__main__':
    unittest.main()
```

## Performance Considerations

### Large DataFrames

For DataFrames with > 100,000 rows, consider:

1. **Pagination**: Display subset of rows
2. **Lazy Loading**: Load data on demand
3. **Indexing**: Use pandas indexing for faster access

### Memory Management

```python
# Clear DataFrame when not needed
self.df = pd.DataFrame()

# Use garbage collection
import gc
gc.collect()
```

## Future API Enhancements

Planned additions:

1. **Filtering API**: Filter data in table view
2. **Sorting API**: Sort data by columns
3. **Plugin System**: Load external plugins
4. **Scripting API**: Automate operations
5. **REST API**: Control via HTTP requests

---

For more information, see:
- [DEVELOPMENT.md](DEVELOPMENT.md)
- [EXAMPLES.md](EXAMPLES.md)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
