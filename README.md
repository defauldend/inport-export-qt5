# Import-Export Qt5 Data Management Tool

A comprehensive PyQt5-based desktop application for managing, importing, and exporting data across multiple formats and sources.

## 🚀 Features

### Data Import
- **CSV Files**: Import comma-separated value files
- **Excel Files**: Import Excel spreadsheets (.xlsx, .xls)
- **SQLite Database**: Load data from SQLite database tables
- **REST API**: Fetch data from REST APIs (includes JSONPlaceholder example)

### Data Export
- **CSV Files**: Export data to comma-separated value format
- **Excel Files**: Export data to Excel spreadsheets (.xlsx)
- **SQLite Database**: Save data to SQLite database tables

### Data Management
- **Interactive Table View**: View and manage data in a user-friendly table interface
- **Real-time Updates**: See changes immediately in the table view
- **Multiple Operations**: Perform multiple import/export operations in a single session

## 📋 Requirements

- Python 3.7 or higher
- PyQt5
- pandas
- openpyxl (for Excel support)
- SQLAlchemy (for database operations)
- requests (for API operations)

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/defauldend/inport-export-qt5.git
cd inport-export-qt5
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Running the Application
```bash
python3 main.py
```

### Basic Operations

#### Importing Data from CSV
1. Click the "Import from CSV" button
2. Select your CSV file from the file dialog
3. Data will be displayed in the table view

#### Exporting Data to Excel
1. Load data into the application (via CSV, Excel, or Database)
2. Click the "Export to Excel" button
3. Choose a location and filename
4. Your data will be saved as an Excel file

#### Database Operations
1. Click the "Database Operations" button
2. Enter database details:
   - Database Type: sqlite (default)
   - Database Name: Your database filename (e.g., data.db)
   - Table Name: The table to import from or export to
3. Choose "Import from DB" or "Export to DB"

#### Fetching Data from API
1. Click the "Fetch from API (JSONPlaceholder)" button
2. Data will be automatically fetched and displayed
3. Modify the API URL in the code to fetch from other endpoints

## 🏗️ Project Structure

```
inport-export-qt5/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore patterns
├── scrip.sh            # Setup script
├── pyqt_data_app/      # Additional application versions
└── src/                # Source files
```

## 🔬 Development

### Code Structure

The application follows a modular design:

- **PandasModel**: Custom Qt model for displaying pandas DataFrames
- **DbDialog**: Dialog for database connection configuration
- **MainWindow**: Main application window with all UI components

### Adding New Import/Export Formats

To add support for new file formats:

1. Add a new button in the `MainWindow.__init__` method
2. Create a corresponding import/export method
3. Use pandas' built-in I/O functions for common formats
4. Handle exceptions and show user-friendly error messages

## 🧪 Testing

### Manual Testing
1. Prepare test data files (CSV, Excel)
2. Run the application
3. Test each import/export operation
4. Verify data integrity after operations

### Testing Database Operations
```bash
# Create a test database
python3 -c "import sqlite3; conn = sqlite3.connect('test.db'); conn.execute('CREATE TABLE test_table (id INTEGER, name TEXT)'); conn.execute('INSERT INTO test_table VALUES (1, \"Test\")'); conn.commit(); conn.close()"
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to classes and methods
- Comment complex logic

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Known Issues

- Large datasets may cause UI lag
- API fetching requires internet connection
- SQLite is the only supported database type currently

## 🔮 Future Enhancements

- [ ] Support for PostgreSQL and MySQL databases
- [ ] Data filtering and sorting in the table view
- [ ] Data visualization features
- [ ] Multi-sheet Excel support
- [ ] JSON import/export
- [ ] Data validation and cleaning tools
- [ ] Batch operations
- [ ] Command-line interface

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- PyQt5 for the GUI framework
- pandas for data manipulation
- SQLAlchemy for database abstraction
- JSONPlaceholder for the test API
