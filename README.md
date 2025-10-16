# inport-export-qt5

A comprehensive PyQt5-based data management application with support for multiple file formats, database operations, and performance monitoring.

## Features

### Data Import/Export
- **CSV Files**: Import and export CSV files
- **Excel Files**: Import and export Excel files (.xlsx, .xls)
- **JSON Files**: Import and export JSON files with proper formatting
- **Database Operations**: Connect to SQLite databases for import/export
- **API Integration**: Fetch data from REST APIs (JSONPlaceholder example included)

### Data Management
- **Search/Filter**: Real-time data filtering across all columns
- **Sorting**: Click column headers to sort data
- **Clear Data**: Clear all data from the table view

### Performance Monitoring
- **Debug Manager**: Comprehensive logging and performance tracking
- **Operation Metrics**: Track success/failure rates, duration, and memory usage
- **Performance Summary**: View detailed metrics via Help menu

### User Interface
- **Menu Bar**: File and Help menus for easy navigation
- **Status Bar**: Real-time feedback on operations
- **Progress Dialog**: Visual feedback for long-running operations
- **Responsive Layout**: Clean and intuitive Qt5 interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/defauldend/inport-export-qt5.git
cd inport-export-qt5
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python3 main.py
```

## Requirements

- Python 3.7+
- PyQt5 5.15.0+
- pandas 1.3.0+
- openpyxl 3.0.0+
- SQLAlchemy 1.4.0+
- requests 2.26.0+
- psutil 5.8.0+

## License

This project is open source and available under the MIT License.

