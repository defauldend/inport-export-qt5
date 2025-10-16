# Development Guide

This guide will help you set up your development environment and contribute to the Import-Export Qt5 Data Management Tool.

## Table of Contents
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Building](#building)
- [Common Tasks](#common-tasks)

## Development Setup

### Prerequisites
- Python 3.7 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Code editor (VS Code, PyCharm, or similar)

### Initial Setup

1. **Fork and Clone**
   ```bash
   # Fork on GitHub first
   git clone https://github.com/YOUR-USERNAME/inport-export-qt5.git
   cd inport-export-qt5
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Development Tools**
   ```bash
   pip install flake8 black isort pylint pytest mypy bandit
   ```

5. **Configure Git**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

### IDE Setup

#### VS Code
1. Install Python extension
2. Install PyQt5 extension (optional)
3. Configure settings:
   ```json
   {
       "python.linting.enabled": true,
       "python.linting.flake8Enabled": true,
       "python.formatting.provider": "black",
       "python.formatting.blackArgs": ["--line-length", "127"],
       "editor.formatOnSave": true
   }
   ```

#### PyCharm
1. Open project
2. Configure Python interpreter to use venv
3. Enable code inspections
4. Configure code style to match PEP 8

## Project Structure

```
inport-export-qt5/
├── .github/
│   ├── workflows/          # CI/CD workflows
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── src/                    # Additional source files
├── pyqt_data_app/         # App versions
├── main.py                # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── CONTRIBUTING.md       # Contribution guidelines
├── FEATURES.md          # Features documentation
├── QUICKSTART.md        # Quick start guide
├── SECURITY.md          # Security policy
├── CHANGELOG.md         # Version history
└── LICENSE              # MIT License
```

## Development Workflow

### Creating a New Feature

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add docstrings
   - Update documentation
   - Add tests if applicable

3. **Test Your Changes**
   ```bash
   # Run the application
   python main.py
   
   # Run linters
   flake8 main.py
   black --check main.py
   isort --check-only main.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### Fixing a Bug

1. **Create a Branch**
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Reproduce the Bug**
   - Document steps to reproduce
   - Identify root cause
   - Write test case (if possible)

3. **Fix the Bug**
   - Make minimal changes
   - Test thoroughly
   - Update documentation if needed

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "Fix: bug description"
   git push origin fix/bug-description
   ```

## Testing

### Manual Testing

1. **Test All Features**
   ```bash
   python main.py
   ```
   - Test CSV import/export
   - Test Excel import/export
   - Test database operations
   - Test API fetching

2. **Test Error Cases**
   - Invalid file formats
   - Missing files
   - Network errors
   - Database errors

3. **Test on Different Platforms**
   - Test on your OS
   - Ask others to test on different OS

### Automated Testing (Future)

```python
# Example test structure
def test_csv_import():
    # Test CSV import functionality
    pass

def test_excel_export():
    # Test Excel export functionality
    pass
```

### Testing Checklist
- [ ] Application starts without errors
- [ ] CSV import works
- [ ] CSV export works
- [ ] Excel import works
- [ ] Excel export works
- [ ] Database import works
- [ ] Database export works
- [ ] API fetch works
- [ ] Error messages are clear
- [ ] UI is responsive

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

1. **Line Length**: 127 characters
2. **Indentation**: 4 spaces
3. **Imports**: Organized in groups
4. **Naming**:
   - Classes: PascalCase
   - Functions/Methods: snake_case
   - Constants: UPPER_SNAKE_CASE

### Example Code Style

```python
import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Initialize the class."""
        self.value = 0
    
    def my_method(self, param: str) -> Optional[str]:
        """
        Method docstring.
        
        Args:
            param: Parameter description
            
        Returns:
            Return value description
        """
        return param.upper()
```

### Linting Commands

```bash
# Check style
flake8 main.py --max-line-length=127

# Format code
black main.py --line-length=127

# Sort imports
isort main.py --profile black

# Type checking
mypy main.py

# Security check
bandit -r .
```

## Debugging

### Using Print Statements

```python
print(f"Debug: variable value = {variable}")
```

### Using Python Debugger

```python
import pdb

# Add breakpoint
pdb.set_trace()
```

### Using VS Code Debugger

1. Create `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Current File",
               "type": "python",
               "request": "launch",
               "program": "${file}",
               "console": "integratedTerminal"
           }
       ]
   }
   ```

2. Set breakpoints
3. Press F5 to start debugging

### Common Debugging Tips

- Use `try-except` blocks to catch errors
- Add logging for important operations
- Check variable types and values
- Verify file paths are correct
- Test with small datasets first

## Building

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name data-management-tool main.py

# Executable will be in dist/ folder
```

### Building for Distribution

```bash
# Create source distribution
python setup.py sdist

# Create wheel
python setup.py bdist_wheel
```

## Common Tasks

### Adding a New Import Format

1. Add button to MainWindow
2. Create import method
3. Use pandas for file reading
4. Handle errors
5. Update documentation

Example:
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

### Adding a New Export Format

Similar to import, but use pandas export methods:
```python
def export_json(self):
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save JSON File", "", "JSON Files (*.json)"
    )
    if file_path:
        try:
            self.df.to_json(file_path, orient='records')
            self.show_message("Success", f"Data exported to {file_path}")
        except Exception as e:
            self.show_message("Error", f"Could not export to JSON:\n{e}")
```

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade pandas

# Update requirements.txt
pip freeze > requirements.txt
```

### Running CI/CD Locally

```bash
# Install act (GitHub Actions locally)
# https://github.com/nektos/act

# Run workflows
act push
```

## Performance Tips

### Optimizing for Large Files

1. Use chunking for very large files
2. Show progress indicators
3. Use background threads
4. Implement pagination

### Memory Management

1. Clear data when not needed
2. Use generators for large datasets
3. Monitor memory usage
4. Close file handles properly

## Resources

- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Git Best Practices](https://www.git-scm.com/doc)

## Getting Help

- Check existing documentation
- Search GitHub issues
- Ask in discussions
- Contact maintainers

## Code Review Process

1. Submit PR with clear description
2. Wait for review feedback
3. Address feedback
4. Get approval
5. Merge

## Release Process

1. Update CHANGELOG.md
2. Update version number
3. Create git tag
4. Push tag
5. CI/CD creates release

---

Happy coding! 🚀
