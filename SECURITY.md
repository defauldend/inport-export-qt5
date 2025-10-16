# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Reporting a Vulnerability

We take the security of Import-Export Qt5 seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (Preferred)
   - Go to the repository's Security tab
   - Click "Report a vulnerability"
   - Fill in the details

2. **Email**
   - Contact the repository maintainers privately
   - Include detailed information about the vulnerability

### What to Include in Your Report

Please include as much of the following information as possible:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability
- Suggested fix (if you have one)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Status Updates**: Every 7 days
- **Resolution**: Varies by severity

### Vulnerability Handling Process

1. **Report Received**: We acknowledge receipt
2. **Investigation**: We investigate and validate the report
3. **Fix Development**: We develop a fix
4. **Testing**: We test the fix thoroughly
5. **Release**: We release a patch
6. **Disclosure**: We publicly disclose the vulnerability (with credit to reporter if desired)

## Security Best Practices for Users

### Using the Application Securely

1. **Keep Updated**
   - Always use the latest version
   - Check for updates regularly
   - Subscribe to release notifications

2. **Database Security**
   - Use strong passwords for database connections
   - Don't share database credentials
   - Restrict database file permissions

3. **File Operations**
   - Verify file sources before importing
   - Be cautious with untrusted CSV/Excel files
   - Check file permissions before export

4. **API Operations**
   - Use HTTPS endpoints when possible
   - Validate API responses
   - Don't expose API keys in code
   - Use environment variables for sensitive data

5. **Network Security**
   - Use secure networks for API operations
   - Be cautious on public Wi-Fi
   - Consider VPN for sensitive data

### Development Security

If you're contributing to the project:

1. **Code Review**
   - All code changes are reviewed
   - Security implications are considered
   - Dependencies are checked

2. **Dependencies**
   - Keep dependencies updated
   - Review dependency security advisories
   - Use `pip-audit` or `safety` to check vulnerabilities

3. **Input Validation**
   - Validate all user inputs
   - Sanitize database queries
   - Check file formats

4. **Error Handling**
   - Don't expose sensitive information in errors
   - Log security events appropriately
   - Handle exceptions gracefully

## Known Security Considerations

### Current Architecture

1. **SQL Injection Prevention**
   - We use SQLAlchemy parameterized queries
   - No direct SQL string concatenation
   - Table names are user-provided (use with caution)

2. **File Operations**
   - File paths are sanitized
   - File operations use safe Python libraries
   - No arbitrary code execution from files

3. **API Security**
   - API calls use requests library
   - SSL/TLS verification enabled by default
   - No credential storage in code

### Potential Risks

1. **Malicious Files**
   - CSV/Excel files could contain malicious data
   - Always verify file sources
   - Use antivirus software

2. **Database Access**
   - Direct database file access required
   - User responsible for database security
   - No built-in access controls

3. **Network Operations**
   - API calls transmit data over network
   - Use secure networks
   - Consider data sensitivity

## Security Features

### Built-in Security

1. **No Credential Storage**
   - Application doesn't store credentials
   - No persistent authentication

2. **Safe Libraries**
   - Uses well-maintained, secure libraries
   - Regular dependency updates
   - Security scanning in CI/CD

3. **Error Handling**
   - Errors don't expose system information
   - User-friendly error messages
   - Proper exception handling

### CI/CD Security

1. **Automated Scanning**
   - Bandit security linter
   - Safety dependency checker
   - Code quality checks

2. **Multi-platform Testing**
   - Tests on multiple OS
   - Tests on multiple Python versions
   - Continuous integration

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible
5. Credit the reporter (if they wish) in release notes

### Public Disclosure Timing

- **Critical vulnerabilities**: Immediate patch and disclosure
- **High severity**: 7 days after patch release
- **Medium/Low severity**: 14 days after patch release

## Hall of Fame

We recognize and thank security researchers who help us keep the project secure:

*(No reports yet)*

## Contact

For security concerns, please use:
- GitHub Security Advisories (preferred)
- Repository maintainer email (check repository)

## Updates to This Policy

This policy may be updated periodically. Check the repository for the latest version.

**Last Updated**: 2024
