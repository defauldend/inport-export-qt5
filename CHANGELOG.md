# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README.md with installation and usage instructions
- CI/CD pipeline with GitHub Actions
  - Python linting workflow
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Multi-version Python testing (3.8, 3.9, 3.10, 3.11, 3.12)
  - Code quality checks (Black, isort, Pylint, Bandit)
  - Security vulnerability scanning
  - Build verification
  - Release automation
- CONTRIBUTING.md with contribution guidelines
- LICENSE file (MIT License)
- FEATURES.md with detailed feature documentation
- CHANGELOG.md (this file)
- requirements.txt in root directory
- Dependency caching in CI/CD workflows

### Changed
- Enhanced README with comprehensive documentation
- Improved project structure documentation

### Fixed
- N/A

## [0.0.2] - Previous Version

### Added
- DebugManager class for logging and performance monitoring
- Enhanced debugging capabilities

### Changed
- Improved code organization

### Fixed
- Various bug fixes

## [Initial] - Initial Release

### Added
- CSV file import and export
- Excel file import and export
- SQLite database import and export
- REST API data fetching
- Interactive table view for data management
- PyQt5 GUI application
- Basic error handling
- File dialog integration
- Database connection dialog

### Features
- PandasModel for DataFrame display
- DbDialog for database operations
- MainWindow with all UI components
- Support for multiple data formats

## Future Releases

### Planned for Next Version
- [ ] Multi-sheet Excel support
- [ ] JSON and XML import/export
- [ ] Table filtering and sorting
- [ ] PostgreSQL and MySQL support
- [ ] Data visualization

### Long-term Plans
- [ ] Batch operations
- [ ] Cloud storage integration
- [ ] Advanced data transformations
- [ ] Command-line interface
- [ ] Plugin system

---

## Version Numbering

- Major version: Breaking changes
- Minor version: New features, backward compatible
- Patch version: Bug fixes, backward compatible

## Release Process

1. Update CHANGELOG.md
2. Update version in code
3. Create GitHub release
4. CI/CD automatically builds and publishes artifacts

## Links

- [Repository](https://github.com/defauldend/inport-export-qt5)
- [Issues](https://github.com/defauldend/inport-export-qt5/issues)
- [Pull Requests](https://github.com/defauldend/inport-export-qt5/pulls)
