# Features Documentation

## Overview

The Import-Export Qt5 Data Management Tool is a desktop application built with PyQt5 that provides comprehensive data import, export, and management capabilities.

## Core Features

### 1. CSV File Operations

#### Import CSV
- **Location**: Main window → "Import from CSV" button
- **Supported Format**: Comma-separated values (.csv)
- **Features**:
  - Automatic delimiter detection
  - Header row detection
  - Encoding support (UTF-8, Latin-1, etc.)
- **Usage**:
  1. Click "Import from CSV"
  2. Select CSV file from file dialog
  3. Data appears in table view

#### Export CSV
- **Location**: Main window → "Export to CSV" button
- **Features**:
  - Preserves data types
  - Excludes index by default
  - UTF-8 encoding
- **Usage**:
  1. Load data into the application
  2. Click "Export to CSV"
  3. Choose save location and filename

### 2. Excel File Operations

#### Import Excel
- **Location**: Main window → "Import from Excel" button
- **Supported Formats**: .xlsx, .xls
- **Features**:
  - Reads first sheet by default
  - Handles merged cells
  - Preserves formatting information
- **Usage**:
  1. Click "Import from Excel"
  2. Select Excel file from file dialog
  3. Data appears in table view

#### Export Excel
- **Location**: Main window → "Export to Excel" button
- **Supported Format**: .xlsx
- **Features**:
  - Creates formatted Excel workbook
  - Preserves data types
  - Clean, professional output
- **Usage**:
  1. Load data into the application
  2. Click "Export to Excel"
  3. Choose save location and filename

### 3. Database Operations

#### Database Support
- **Current Support**: SQLite
- **Future Plans**: PostgreSQL, MySQL, MariaDB

#### Import from Database
- **Location**: Main window → "Database Operations" → "Import from DB"
- **Features**:
  - SQL query execution
  - Table browsing
  - Connection string support
- **Configuration**:
  - Database Type: sqlite (default)
  - Database Name: Path to .db file
  - Table Name: Name of table to query
- **Usage**:
  1. Click "Database Operations"
  2. Enter database details
  3. Click "Import from DB"
  4. Data from table appears in table view

#### Export to Database
- **Location**: Main window → "Database Operations" → "Export to DB"
- **Features**:
  - Table creation
  - Data insertion
  - Replace or append modes
- **Configuration**: Same as import
- **Usage**:
  1. Load data into the application
  2. Click "Database Operations"
  3. Enter database details
  4. Click "Export to DB"
  5. Data is saved to specified table

### 4. API Data Fetching

#### REST API Integration
- **Location**: Main window → "Fetch from API (JSONPlaceholder)"
- **Default API**: JSONPlaceholder (https://jsonplaceholder.typicode.com/users)
- **Features**:
  - JSON parsing
  - Nested data normalization
  - Error handling
  - HTTP status code checking
- **Usage**:
  1. Click "Fetch from API (JSONPlaceholder)"
  2. Data is automatically fetched and displayed
  3. Modify the URL in code for other APIs

#### Customizing API Endpoint
To fetch from a different API:
1. Open main.py
2. Find the `fetch_from_api` method
3. Change the URL variable to your API endpoint
4. Adjust JSON parsing if needed

### 5. Data Viewing

#### Table View
- **Features**:
  - Scrollable table interface
  - Column headers
  - Row numbers
  - Resizable columns
- **Capabilities**:
  - View large datasets
  - Scroll horizontally and vertically
  - Column width adjustment

## Technical Features

### Data Handling
- **Library**: pandas DataFrame
- **Benefits**:
  - Efficient memory usage
  - Fast operations
  - Type preservation
  - Missing data handling

### User Interface
- **Framework**: PyQt5
- **Features**:
  - Native look and feel
  - Cross-platform compatibility
  - Responsive design
  - Dialog-based workflows

### Error Handling
- **User-Friendly Messages**: All errors are caught and displayed with clear messages
- **Exception Types Handled**:
  - File I/O errors
  - Database connection errors
  - Network errors
  - Data parsing errors
  - Invalid file format errors

## Feature Comparison

| Feature | CSV | Excel | Database | API |
|---------|-----|-------|----------|-----|
| Import | ✅ | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ | ❌ |
| Data Types | Basic | Rich | Rich | JSON |
| File Size | Large | Medium | Large | N/A |
| Speed | Fast | Medium | Fast | Network-dependent |

## Planned Features

### Short Term
- [ ] Multi-sheet Excel support
- [ ] JSON import/export
- [ ] XML import/export
- [ ] Filter and sort in table view

### Medium Term
- [ ] PostgreSQL support
- [ ] MySQL support
- [ ] Data visualization
- [ ] Export to PDF

### Long Term
- [ ] Batch operations
- [ ] Scheduled operations
- [ ] Cloud storage integration
- [ ] Advanced data transformations

## Performance Considerations

### Large Files
- CSV files > 100MB may take time to load
- Excel files > 50MB may cause delays
- Consider chunking for very large datasets

### Memory Usage
- All data is loaded into memory
- Monitor memory usage for large files
- Close application and restart for fresh memory state

### Network Operations
- API calls require internet connection
- Timeout settings: 30 seconds default
- Retry logic: Manual retry required

## Troubleshooting

### Import Issues
- **Problem**: File won't import
- **Solutions**:
  - Check file format
  - Verify file is not corrupted
  - Ensure file is not open in another application
  - Check file permissions

### Export Issues
- **Problem**: Cannot save file
- **Solutions**:
  - Check write permissions
  - Ensure target directory exists
  - Verify disk space
  - Close file if open in another application

### Database Issues
- **Problem**: Cannot connect to database
- **Solutions**:
  - Verify database file exists
  - Check database file permissions
  - Ensure database is not locked
  - Verify table name is correct

### API Issues
- **Problem**: Cannot fetch data
- **Solutions**:
  - Check internet connection
  - Verify API endpoint URL
  - Check API service status
  - Review API response format

## Support

For feature requests, bug reports, or questions, please:
1. Check existing documentation
2. Search existing issues on GitHub
3. Open a new issue with detailed information

## Version History

### Current Version
- All core features implemented
- Stable and tested
- Cross-platform support

### Future Versions
- See planned features above
- Community-driven development
- Regular updates and improvements
