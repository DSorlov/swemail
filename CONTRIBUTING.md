# Contributing to SWE Mail Integration

Thank you for your interest in contributing to the Swedish Mail Delivery integration for Home Assistant!

## Development Setup

### Prerequisites
- Python 3.11 or newer
- Home Assistant development environment
- Git

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DSorlov/swemail.git
   cd swemail
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run tests and validation:**
   ```bash
   # Validate Python syntax
   python -m py_compile custom_components/swemail/*.py
   
   # Run linting
   black --check custom_components/
   isort --check-only custom_components/
   flake8 custom_components/
   
   # Type checking
   mypy custom_components/swemail/
   ```

## Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Pre-commit**: Git hooks for code quality

### Running Code Quality Checks

```bash
# Format code
black custom_components/
isort custom_components/

# Check formatting
black --check custom_components/
isort --check-only custom_components/

# Lint code
flake8 custom_components/

# Type checking
mypy custom_components/swemail/
```

## Testing

### Automated Testing

The project includes GitHub Actions workflows that run:

1. **hassfest**: Validates Home Assistant integration requirements
2. **HACS**: Validates HACS compatibility
3. **CI**: Runs linting, formatting checks, and Python validation
4. **Translation validation**: Ensures all translation files are consistent

### Manual Testing

1. **Install in Home Assistant:**
   - Copy `custom_components/swemail` to your HA `custom_components` folder
   - Restart Home Assistant
   - Add the integration through the UI

2. **Test different scenarios:**
   - Valid Swedish postal codes
   - Invalid postal codes
   - Network connectivity issues
   - Different provider combinations

## Adding Translations

To add a new language translation:

1. **Create translation file:**
   ```bash
   cp custom_components/swemail/translations/en.json custom_components/swemail/translations/[language_code].json
   ```

2. **Translate all strings** in the new file

3. **Validate translation:**
   ```bash
   python -c "import json; json.load(open('custom_components/swemail/translations/[language_code].json', encoding='utf-8'))"
   ```

4. **Test the translation** by changing your Home Assistant language

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code quality guidelines
3. **Add tests** for new functionality (if applicable)
4. **Update documentation** if needed
5. **Run all quality checks** before submitting
6. **Create a pull request** with a clear description

### Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] Documentation has been updated
- [ ] Translation files are consistent (if modified)
- [ ] Commit messages are clear and descriptive
- [ ] Pre-commit hooks pass

## Release Process

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Getting Help

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Code Review**: Submit PRs for community review

## Code of Conduct

Please be respectful and constructive in all interactions. This project welcomes contributions from everyone regardless of background or experience level.