# Test Data for Data Management Tool

This directory contains sample data files for testing the Data Management Tool.

## Sample CSV

```csv
id,name,email,age,city
1,John Doe,john@example.com,30,New York
2,Jane Smith,jane@example.com,25,Los Angeles
3,Bob Johnson,bob@example.com,35,Chicago
4,Alice Brown,alice@example.com,28,Houston
5,Charlie Davis,charlie@example.com,32,Phoenix
```

## Sample JSON

```json
[
  {
    "id": 1,
    "name": "Product A",
    "price": 29.99,
    "stock": 100,
    "category": "Electronics"
  },
  {
    "id": 2,
    "name": "Product B",
    "price": 49.99,
    "stock": 50,
    "category": "Clothing"
  },
  {
    "id": 3,
    "name": "Product C",
    "price": 19.99,
    "stock": 200,
    "category": "Books"
  }
]
```

## Testing Instructions

1. **Test Import CSV**:
   - Save the sample CSV data above to a file named `test_data.csv`
   - Click "Import from CSV" and select the file
   - Verify the data appears in the table

2. **Test Search/Filter**:
   - After importing data, type in the search box
   - Try searching for "John", "New York", or any value in the data
   - Verify the table filters correctly

3. **Test Sorting**:
   - Click on any column header
   - Verify the data sorts ascending/descending

4. **Test JSON Import**:
   - Save the sample JSON data to `test_products.json`
   - Click "Import from JSON" and select the file
   - Verify the data loads correctly

5. **Test Export**:
   - After importing data, try exporting to CSV, Excel, or JSON
   - Verify the exported file contains the correct data

6. **Test Performance Metrics**:
   - After performing several operations
   - Go to Help > Performance Metrics
   - Verify you see operation counts and timing

7. **Test API Fetch**:
   - Click "Fetch from API (JSONPlaceholder)"
   - Verify data from the API loads
   - Check the status bar for feedback

8. **Test Database Operations**:
   - Click "Database Operations"
   - Try exporting to a SQLite database
   - Then try importing from the same database
