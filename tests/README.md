# Test Suite

This directory contains all tests for the mise-en-place repository.

## Structure

- **unit/**: Unit tests for individual components
  - `t_config_parser.py`: Tests for the Python configuration parser including CLI options
  - `t_install_functions.py`: Tests for shell functions in install.sh
  - `t_security_features.py`: Tests for security features (template detection, env validation, injection prevention)
  - `t_template_processing.py`: Tests for template processing workflow and environment handling

- **smoke/**: Smoke tests for end-to-end functionality
  - `t_sync_config.py`: Tests for configuration sync operations with security edge cases
  - `t_end_to_end.py`: Full workflow integration tests including quick_install and error recovery

## Running Tests

### Run all tests:
```bash
python3 tests/run_all_tests.py
```

### Run specific test category:
```bash
# Unit tests only
python3 -m pytest tests/unit/

# Smoke tests only
python3 -m pytest tests/smoke/
```

### Run specific test file:
```bash
python3 tests/unit/t_config_parser.py
```

### Run with verbose output:
```bash
python3 tests/unit/t_config_parser.py -v
```

### Run security-focused tests:
```bash
python3 tests/unit/t_security_features.py
python3 tests/unit/t_template_processing.py
```

## Test Coverage

### Security Features
- Shell injection prevention in subprocess calls
- Environment file validation for malicious content
- Secure temporary file handling with atomic operations
- Template variable detection and validation
- Rollback functionality for failed operations

### Template Processing
- End-to-end template processing workflow
- Environment file precedence (`.env` vs `~/.config/dotfiles/.env`)
- Missing variable detection and warnings
- `envsubst` integration and error handling
- Automatic template processing during sync

### Integration Testing
- Complete `quick_install` workflow
- Sync operations with automatic template processing
- Error recovery and user interaction
- Cross-shell compatibility
- Security edge cases and attack scenarios

## Test Naming Convention

All test files follow the pattern `t_<module_name>.py` for easy identification and discovery.