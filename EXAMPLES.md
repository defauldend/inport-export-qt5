# Examples and Use Cases

This document provides practical examples and common use cases for the Import-Export Qt5 Data Management Tool.

## Table of Contents
- [Basic Examples](#basic-examples)
- [Advanced Use Cases](#advanced-use-cases)
- [Automation Examples](#automation-examples)
- [Integration Examples](#integration-examples)
- [Real-World Scenarios](#real-world-scenarios)

## Basic Examples

### Example 1: Convert CSV to Excel

**Scenario**: You have a CSV file and need to convert it to Excel format.

**Steps**:
1. Launch the application: `python main.py`
2. Click "Import from CSV"
3. Select your CSV file (e.g., `data.csv`)
4. Click "Export to Excel"
5. Save as `data.xlsx`

**Sample CSV** (`data.csv`):
```csv
Name,Department,Salary
John Doe,Engineering,75000
Jane Smith,Marketing,65000
Bob Johnson,Sales,70000
```

### Example 2: Fetch API Data and Save to Database

**Scenario**: Fetch user data from an API and save it to a local database for offline access.

**Steps**:
1. Launch the application
2. Click "Fetch from API (JSONPlaceholder)"
3. Wait for data to load
4. Click "Database Operations"
5. Enter:
   - Database Name: `users.db`
   - Table Name: `api_users`
6. Click "Export to DB"

### Example 3: Database Backup to CSV

**Scenario**: Create a CSV backup of your database.

**Steps**:
1. Launch the application
2. Click "Database Operations"
3. Enter your database details
4. Click "Import from DB"
5. Click "Export to CSV"
6. Save as `backup_YYYYMMDD.csv`

## Advanced Use Cases

### Use Case 1: Data Migration

**Scenario**: Migrate data from one database to another.

**Steps**:
1. Import from source database
2. Verify data in table view
3. Export to target database

**Example**:
```python
# Source: old_database.db, table: old_data
# Target: new_database.db, table: new_data
```

### Use Case 2: Data Consolidation

**Scenario**: Combine multiple CSV files into one Excel workbook.

**Process**:
1. Import first CSV → Export to Excel (Sheet1)
2. Import second CSV → Append to Excel (manual)
3. Continue for all files

**Note**: Currently supports single sheet; multi-sheet support planned.

### Use Case 3: Data Validation

**Scenario**: Load data, validate it externally, and save cleaned version.

**Workflow**:
1. Import CSV data
2. Export to Excel
3. Review/clean in Excel
4. Import cleaned Excel
5. Export to database

## Automation Examples

### Example 1: Scheduled Database Backups

**Script**: Create a scheduled task to backup database.

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d)
BACKUP_FILE="backup_${DATE}.csv"

# Note: Requires CLI support (future enhancement)
# For now, manual process required
```

### Example 2: Batch File Conversion

**Scenario**: Convert multiple CSV files to Excel.

**Manual Process**:
1. Import first CSV
2. Export as Excel
3. Repeat for each file

**Future**: Batch processing support planned.

## Integration Examples

### Example 1: Integration with Data Analysis Pipeline

**Workflow**:
```
API → Import-Export Tool → CSV → Python Analysis → Results
```

**Steps**:
1. Fetch data from API
2. Export to CSV
3. Process with pandas/numpy in separate script
4. Import results back into tool
5. Export to database or Excel for reporting

### Example 2: Integration with Business Intelligence Tools

**Workflow**:
```
Database → Import-Export Tool → Excel → BI Tool (Tableau/PowerBI)
```

**Steps**:
1. Import from database
2. Export to Excel
3. Import Excel into BI tool
4. Create visualizations

### Example 3: API Data Collection

**Workflow**:
```
API → Import-Export Tool → Database → Regular Updates
```

**Process**:
1. Configure API endpoint in code
2. Fetch data regularly
3. Save to database
4. Track historical data

## Real-World Scenarios

### Scenario 1: Sales Data Management

**Context**: Small business needs to manage sales data from multiple sources.

**Solution**:
1. **Daily**: 
   - Fetch orders from online API
   - Export to daily CSV for records
   - Append to master database

2. **Weekly**:
   - Import master database
   - Export to Excel for reporting
   - Share with management

3. **Monthly**:
   - Create database backup
   - Archive old data

### Scenario 2: Research Data Collection

**Context**: Researcher collecting data from various sources.

**Solution**:
1. **Data Collection**:
   - Import CSV files from experiments
   - Import Excel files from surveys
   - Fetch data from public APIs

2. **Data Organization**:
   - Consolidate in single database
   - Export subsets for analysis
   - Create backups regularly

3. **Data Sharing**:
   - Export to Excel for collaborators
   - Generate CSV for publication

### Scenario 3: Inventory Management

**Context**: Store manager tracking inventory.

**Solution**:
1. **Daily Operations**:
   - Import inventory from supplier (CSV)
   - Update local database
   - Export daily report (Excel)

2. **Stock Analysis**:
   - Import historical data
   - Export to Excel for trend analysis
   - Update ordering decisions

3. **Reporting**:
   - Generate weekly reports
   - Export to CSV for accounting
   - Archive historical data

### Scenario 4: Academic Grade Management

**Context**: Teacher managing student grades.

**Solution**:
1. **Data Entry**:
   - Import student list (CSV)
   - Export to Excel for grade entry
   - Import completed grades

2. **Database Storage**:
   - Save grades to database
   - Track over multiple semesters
   - Easy retrieval

3. **Reporting**:
   - Export class statistics
   - Generate individual reports
   - Archive historical data

## Sample Data Sets

### Sample 1: Employee Data

```csv
EmployeeID,FirstName,LastName,Department,HireDate,Salary
1001,John,Doe,Engineering,2020-01-15,75000
1002,Jane,Smith,Marketing,2019-06-20,65000
1003,Bob,Johnson,Sales,2021-03-10,70000
1004,Alice,Williams,Engineering,2020-11-05,80000
```

### Sample 2: Product Inventory

```csv
ProductID,ProductName,Category,Price,StockQuantity
P001,Laptop,Electronics,999.99,15
P002,Mouse,Electronics,29.99,50
P003,Keyboard,Electronics,79.99,30
P004,Monitor,Electronics,299.99,20
```

### Sample 3: Sales Transactions

```csv
TransactionID,Date,ProductID,Quantity,TotalAmount
T001,2024-01-15,P001,1,999.99
T002,2024-01-16,P002,2,59.98
T003,2024-01-16,P003,1,79.99
T004,2024-01-17,P001,1,999.99
```

## API Examples

### Example 1: Custom API Integration

To fetch from your own API, modify the `fetch_from_api` method:

```python
def fetch_from_api(self):
    # Change this URL to your API endpoint
    url = "https://your-api.com/data"
    
    # Add authentication if needed
    headers = {
        "Authorization": "Bearer YOUR_TOKEN"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        self.df = pd.json_normalize(data)
        self.model.setDataFrame(self.df)
        self.show_message("Success", "Data fetched successfully.")
    except Exception as e:
        self.show_message("Error", str(e))
```

### Example 2: API with Parameters

```python
def fetch_weather_data(self, city):
    url = f"https://api.weather.com/v1/data?city={city}"
    # ... rest of implementation
```

## Best Practices

### Data Management Best Practices

1. **Regular Backups**: Export important data regularly
2. **Version Control**: Name files with dates (data_20240101.csv)
3. **Validation**: Always verify data after import
4. **Testing**: Test with sample data first
5. **Documentation**: Keep notes on data sources

### File Organization

```
project/
├── raw_data/          # Original data files
├── processed_data/    # Cleaned data
├── backups/          # Regular backups
├── reports/          # Generated reports
└── archives/         # Historical data
```

### Database Best Practices

1. Use meaningful table names
2. Regular backups
3. Test queries with small datasets
4. Document schema
5. Use transactions for important operations

## Troubleshooting Examples

### Problem: Large File Import Slow

**Solution**:
```python
# For very large files, consider chunking
chunks = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in chunks:
    # Process each chunk
    pass
```

### Problem: Memory Issues

**Solution**:
- Import data in smaller batches
- Close and restart application between operations
- Use 64-bit Python for large datasets

### Problem: Encoding Issues

**Solution**:
```python
# Specify encoding
df = pd.read_csv('file.csv', encoding='utf-8')
# or
df = pd.read_csv('file.csv', encoding='latin-1')
```

## Future Examples

Once new features are added, this section will include:
- Multi-sheet Excel examples
- PostgreSQL integration examples
- Data filtering examples
- Batch operation examples
- Visualization examples

---

For more examples and questions, please check:
- GitHub Issues
- Discussions
- Documentation

Have an example to share? Contribute it via pull request!
