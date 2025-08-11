# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status Summary & To Do's
**Updated**: *August 11th, 2025*

**Current Status**: Self-maintaining dotfiles system with comprehensive security and template processing
- ✅ Quick install automation
- ✅ Hybrid Python + Shell architecture implemented with config_parser.py and install.sh
- ✅ Interactive diff/merge functionality
- ✅ Custom overlay features for highly personalized configurations
- ✅ Automated environment template processing with validation and error handling
- ✅ **Security Hardening Complete** (February 2025):
  - Fixed shell injection vulnerabilities with proper subprocess handling
  - Added environment file validation to prevent malicious code execution
  - Implemented secure temporary file operations with atomic updates
  - Added rollback capability for template processing failures
  - Converted shell functions to thin Python wrappers for better security control
  - Enhanced POSIX compliance across all shell variants

**To Do**: Framework mature - focusing on expansion and polish
- ✨ **Config/LLM Context To Add**: Expand command library and IDE support
  - Add more common AI development tasks to /commands directory
  - Refine existing /commands for better functionality
  - Add more comprehensive IDE configuration files (Cursor, Windsurf, et al.)
- 🔧 **Nice-to-Have's**: Minor improvements and optimization
  - Add pre-commit hooks for linting and validation
  - Improve installation instructions for docs/LLM.md et al.


## Repository Overview

This is a dotfiles repository template for macOS that manages configuration files across multiple tools and applications. The repository uses a **hybrid Python + Shell architecture** for maximum compatibility and maintainability across different macOS versions and shells. It is theoretically extensible to other operating systems as well. 

## Core Architecture

### Hybrid Management System
- **config_parser.py**: Python script that handles all configuration parsing, validation, file operations, and diff/merge functionality
- **install.sh**: Simple shell wrapper that provides convenient functions calling Python commands
- **dotfiles.conf**: Single source of truth configuration file using `repo_path:system_path` format
- **docs/**: Structured documentation split by purpose (installation, tools, setup)

### Key Design Principles
- **Python handles everything complex**: Configuration parsing, validation, file operations, diff/merge, and safety checks
- **Shell provides simple interface**: Easy-to-use, CLI-accessible wrapper functions that call Python commands
- **Single configuration source**: `dotfiles.conf` eliminates manual sync issues
- **No shell arrays needed**: Python manages all data structures internally
- **True cross-shell compatibility**: Shell script only uses basic commands that (...should!) work identically everywhere
- **Safe by default**: Preview mode shows diffs before making any changes
- **Pure Python diff**: Uses built-in `difflib` - no external diff command dependencies

### Repository Structure
```
├── HOME/            # Dotfiles that mirror home directory structure
│   ├── .env.example # → ~/.config/dotfiles/.env.example
│   └── config/      # → ~/.config/
├── docs/            # Focused documentation
│   ├── IDE.md       # IDE configurations
│   ├── LLM.md       # LLM tool configurations
│   └── img/         # Documentation images
├── ide/             # IDE configurations
│   ├── vscode/      # VS Code settings
│   ├── cursor/      # Cursor IDE settings
│   └── windsurf/    # Windsurf IDE settings
├── llm/             # LLM tool configurations
│   ├── claude_code/    # Claude Code configuration
│   └── claude_desktop/ # Claude Desktop configuration
├── dotfiles.conf        # Configuration manifest
├── config_parser.py     # Python configuration parser
├── install.sh           # Main installation script
└── tests/               # Test suite
    ├── run_all_tests.py # Test runner script
    ├── unit/            # Unit tests
    │   ├── t_config_parser.py      # Tests for config parser
    │   └── t_install_functions.py  # Tests for shell functions
    └── smoke/           # Smoke tests
        └── t_sync_config.py        # End-to-end sync tests
```

## Getting Started

```bash
# Clone repository
git clone https://github.com/andisab/mise-en-place.git
cd mise-en-place

# Quick automated setup (recommended for starting out)
./install.sh

# Manual setup (advanced use)
source install.sh
test_config                    # Validate configuration safely
sync_dotfiles                  # Deploy dotfiles.conf-designated configs with preview
install_shell_integration      # Add commands to shell

# Run test suite to verify installation
python3 tests/run_all_tests.py
```

## Common Commands

### Modern Dotfiles Management
```bash
# Source the installation script
source ~/Projects/mise-en-place/install.sh

# Quick install (NEW) - Automated happy path installation
quick_install

# Test configuration safely (no file changes)
test_config

# Run detailed validation
validate_config

# Sync dotfiles from repository to system (NOW WITH AUTOMATIC TEMPLATE PROCESSING!)
sync_dotfiles

# Collect system files back to repository
collect_dotfiles

# Process configuration templates with environment variables (automatic during sync)
process_env_templates

# Process Claude Desktop basic config - Expand ${HOME} variables only
process_claude_basic_config

# Manage shell integration
install_shell_integration
remove_shell_integration
```

### Configuration Management
```bash
# Edit managed files list
vim dotfiles.conf

# Validate configuration with Python
python3 config_parser.py --validate-only --verbose

# List all managed files
python3 config_parser.py --list

# Enhanced sync operations with diff/merge
python3 config_parser.py --sync-from-repo              # Interactive preview (default)
python3 config_parser.py --sync-from-repo --force      # Direct sync, no preview
python3 config_parser.py --sync-from-repo --strategy replace  # Replace all
python3 config_parser.py --sync-from-repo --strategy skip     # Preview only
python3 config_parser.py --sync-to-repo                # Collect back to repo
```

### Testing and Validation
```bash
# Run complete test suite
python3 tests/run_all_tests.py

# Run specific test categories
python3 -m pytest tests/unit/              # Unit tests only
python3 -m pytest tests/smoke/             # Smoke tests only

# Run individual test files
python3 -m pytest tests/unit/t_config_parser.py -v
python3 -m pytest tests/smoke/t_sync_config.py -v

# Validate configuration without file changes
test_config
validate_config
```

### Interactive Sync Features (NEW)
- **Preview by default**: See all changes before applying them
- **Color-coded diffs**: Green for additions, red for deletions, cyan for line numbers
- **Interactive prompts**: Choose action for each modified file
  - [K]eep current file (skip)
  - [R]eplace with repository version
  - [B]ackup current and replace
  - [V]iew diff again
  - [Q]uit
- **Summary reports**: Know exactly what changed
- **Safe backups**: Modified files are backed up to `~/.config/dotfiles.bak`

## Configuration Files

### Core Configuration
- **dotfiles.conf**: Master configuration using `repo_path:system_path` format
- **config_parser.py**: Python parser with command-line interface, validation, and diff/merge functionality
- **install.sh**: Shell functions for file operations and system integration (no changes needed!)

### Shell Configuration  
- Shell configurations are not managed by default
- Users can use the custom overlay feature to manage their own shell configs
- The framework focuses on LLM and IDE configurations


## Development Environment

### Tools & Technologies
- **Python**: Python 3.8+ (ships with macOS 10.15+, ensuring compatibility)
- **Shell**: zsh/bash with vim-style keybindings (`bindkey -v`)
- **Terminal**: Compatible with any terminal emulator
- **Editor**: Supports various editors (VS Code, Cursor, Windsurf)
- **Version Control**: Git
- **Package Management**: Homebrew (system)
- **Testing Framework**: pytest-based test suite with unit and smoke tests
- **Build Tools**: Python pathlib and difflib for file operations

### Configuration Files
- **dotfiles.conf**: Master configuration using `repo_path:system_path` format
- **config_parser.py**: Python parser with command-line interface and validation
- **install.sh**: Shell functions for file operations and system integration
- **tests/**: Comprehensive test suite with unit and smoke tests

### Environment Setup
```bash
# Ensure Python 3.8+ is available (should be pre-installed on macOS 10.15+)
python3 --version

# Clone and setup repository
git clone https://github.com/andisab/mise-en-place.git
cd mise-en-place

# Run quick install or manual setup
./install.sh
```

### Documentation Structure
- **README.md**: Overview, quick start, and installation guide
- **CLAUDE.md**: Repository structure and implementation guidance (this file)
- **docs/IDE.md**: IDE-specific configurations (VS Code, Cursor, Windsurf)
- **docs/LLM.md**: LLM tool configurations (Claude Desktop, Claude Code)
- **llm/claude_code/.claude/specs/**: Code standards and development guidelines

## Implementation Notes

### Hybrid Architecture Benefits
- **Stability**: Python 3.8+ ships with macOS 10.15+, ensuring compatibility
- **Maintainability**: Complex logic in Python, file operations in shell
- **Cross-shell**: Auto-detects and generates bash/zsh compatible syntax
- **Error handling**: Robust validation and detailed error messages

### Configuration Management
- **Single source**: `dotfiles.conf` as the only place to define file mappings
- **Python-based operations**: All file operations handled by Python's robust libraries
- **No shell complexity**: Eliminated all shell array handling and compatibility issues
- **Validation**: Python script validates file existence, syntax, and consistency
- **Testing**: Safe test functions that don't modify system files
- **Backup**: Automatic backup to `~/.config/dotfiles.bak` before changes
- **Diff/Merge**: Interactive diff preview using Python's built-in `difflib`
- **Safe defaults**: Preview mode is default, requires confirmation before changes

### Implementation History
- **Original**: Manual dual-array approach prone to sync errors
- **Attempted #1**: Associative arrays with slash-containing keys (bash arithmetic evaluation issues)
- **Attempted #2**: Synchronized arrays with index-based access (shell compatibility issues)
- **Current**: Python handles all operations, shell just provides simple wrapper functions
- **Latest Enhancement**: Added diff/merge functionality with interactive preview (inspired by LLMConfigMCP)
- **Recent Updates (January 2025)**:
  - Added custom overlay support with `custom:` prefix in dotfiles.conf
  - Added `quick_install()` function for streamlined Claude Desktop setup
  - Added `process_claude_basic_config()` to expand ${HOME} variables
  - Moved .env.example to ~/.config/dotfiles/ for better organization
  - Enhanced command structure with /prime, /docs, /prd, /commit slash commands
  - Reorganized test suite into proper unit/smoke test structure
  - Added comprehensive code standards documentation (JavaScript, Node.js, TypeScript specs)
  - Improved documentation structure and cross-references
  - **Shell Integration Improvements**: Non-intrusive startup behavior with directory-based detection
  - **Dynamic Repository Support**: Repository-agnostic design works with any directory name
  - **Automated Template Processing**: `sync_dotfiles` now automatically processes environment templates
  - **Advanced Environment Validation**: Template-first parsing with missing variable warnings and envsubst integration
- **Result**: Robust solution that eliminates all shell complexity and compatibility issues while providing modern diff/merge capabilities and comprehensive development tooling

### Custom Overlay Feature
- Files can be prefixed with `custom:` in dotfiles.conf to override repository versions
- Custom files are stored in `~/.config/dotfiles.custom/` (CUSTOM_DIR)
- Format: `custom:filename:destination` (filename can contain colons, destination cannot)
- Custom files take precedence when they exist, with graceful fallback to repository versions