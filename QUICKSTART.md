# Quick Start Guide

This guide will help you get started with the Import-Export Qt5 Data Management Tool in just a few minutes.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Basic knowledge of CSV/Excel files (helpful but not required)

## Installation Steps

### Step 1: Download the Project

```bash
# Clone the repository
git clone https://github.com/defauldend/inport-export-qt5.git

# Navigate to the project directory
cd inport-export-qt5
```

### Step 2: Set Up Virtual Environment (Recommended)

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

## First-Time Usage

### Example 1: Import a CSV File

1. Launch the application
2. Click the "Import from CSV" button
3. Navigate to a CSV file on your computer
4. Select the file
5. View the data in the table

### Example 2: Fetch Data from API

1. Launch the application
2. Click "Fetch from API (JSONPlaceholder)"
3. Wait a moment while data is fetched
4. View the API data in the table
5. Export it if needed

### Example 3: Export to Excel

1. Import data (using CSV or API)
2. Click "Export to Excel"
3. Choose a save location
4. Enter a filename (e.g., "my_data.xlsx")
5. Click Save
6. Your Excel file is ready!

### Example 4: Database Operations

1. Click "Database Operations"
2. Keep default values or enter your own:
   - Database Name: `test.db`
   - Table Name: `my_table`
3. To import: Click "Import from DB" (if table exists)
4. To export: Click "Export to DB" (creates table if needed)

## Sample Data

### Create Sample CSV

Create a file named `sample.csv` with this content:
```csv
Name,Age,City
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago
```

### Create Sample Database

```bash
# Run this Python script to create a sample database
python3 << EOF
import sqlite3
import pandas as pd

# Create database
conn = sqlite3.connect('sample.db')

# Create sample data
data = {
    'Product': ['Laptop', 'Mouse', 'Keyboard'],
    'Price': [999.99, 29.99, 79.99],
    'Stock': [15, 50, 30]
}
df = pd.DataFrame(data)

# Save to database
df.to_sql('products', conn, if_exists='replace', index=False)
conn.close()
print("Sample database created: sample.db")
EOF
```

## Common Tasks

### Task 1: Convert CSV to Excel
1. Import CSV file
2. Export to Excel
3. Done!

### Task 2: Backup Database to CSV
1. Open Database Operations
2. Import from database
3. Export to CSV
4. Your database is backed up!

### Task 3: Merge API Data with Local Data
1. Fetch from API
2. Export to CSV (save as `api_data.csv`)
3. Use external tools to merge with your data
4. Import merged CSV back

## Tips and Tricks

### Keyboard Shortcuts
- The application uses standard Qt keyboard shortcuts
- Copy: Ctrl+C (Cmd+C on macOS)
- Select All: Ctrl+A (Cmd+A on macOS)

### Working with Large Files
- For files > 100MB, be patient during import
- Consider splitting large files into chunks
- Close and restart the app to free memory

### Database Tips
- Always use meaningful table names
- Test with a copy of important databases
- SQLite files are portable across platforms

### API Tips
- Ensure you have internet connection
- Check API documentation for rate limits
- Some APIs require authentication (modify code)

## Troubleshooting

### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.7+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Try running with verbose output
python -v main.py
```

### Import Errors
```bash
# Check if file exists
ls -l your_file.csv  # Unix/Linux/macOS
dir your_file.csv     # Windows

# Verify file permissions
# Make sure the file is readable
```

### Display Issues
```bash
# On Linux, install Qt platform plugin
sudo apt-get install libxcb-xinerama0

# Check Qt installation
python -c "from PyQt5 import QtCore; print(QtCore.PYQT_VERSION_STR)"
```

## Next Steps

After getting started, you might want to:

1. **Read the Full Documentation**
   - Check README.md for detailed features
   - Review FEATURES.md for in-depth feature guide

2. **Customize the Application**
   - Modify API endpoints in `main.py`
   - Add custom data transformations
   - Create your own import/export formats

3. **Contribute**
   - See CONTRIBUTING.md
   - Report bugs or request features
   - Submit pull requests

4. **Share**
   - Share the project with colleagues
   - Use it in your workflows
   - Provide feedback

## Example Workflows

### Workflow 1: Data Analysis Pipeline
1. Fetch data from API
2. Export to CSV for processing
3. Process with external tools
4. Import processed CSV
5. Export to Excel for reporting

### Workflow 2: Database Migration
1. Import from old SQLite database
2. Review data in table view
3. Export to new database with different table name
4. Verify migration

### Workflow 3: Format Conversion
1. Import from any supported format
2. Export to desired format
3. Done - quick and easy!

## Getting Help

- **Documentation**: Check README.md and FEATURES.md
- **Issues**: Open issue on GitHub
- **Community**: Join discussions on GitHub
- **Email**: Contact maintainers (see repository)

## Resources

- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## System Requirements

### Minimum Requirements
- CPU: 1 GHz or faster
- RAM: 512 MB (1 GB recommended)
- Disk: 100 MB free space
- OS: Windows 7+, macOS 10.12+, Linux (any recent distribution)

### Recommended Requirements
- CPU: 2 GHz dual-core
- RAM: 2 GB or more
- Disk: 500 MB free space
- OS: Latest stable version of your OS

## Version Information

To check which version you're running:
```bash
git log --oneline -1
```

---

**Congratulations!** You're now ready to use the Import-Export Qt5 Data Management Tool. Happy data managing! 🎉
