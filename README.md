# Mise-en-Place - Dotfiles Management Framework

A macOS dotfiles configuration management system with centralized sync and modern tooling. 

## Overview

This repository provides a framework for managing configuration files across multiple applications and development tools using a hybrid Python + Shell approach for maximum compatibility and maintainability. It is configured for macOS systems, but can be adapted for other Unix-based systems. It is intended to be simple and intuitive to use with very deterministic results. Use it to get your IDE or LLM config set up quickly & easily. 

**Key Features:**
- 🔄 Bidirectional sync between repository and system
- 🐍 Python-powered configuration parsing with shell file operations
- 🛡️ Automatic backups before changes with rollback capability
- 📱 Cross-shell compatibility (bash/zsh) with POSIX compliance
- 🔍 Interactive diff preview before syncing
- ✨ Multiple sync strategies (ask, replace, skip)
- 🎯 Safe by default - always preview changes first
- 🚀 Quick install for zero-to-functional setup
- 🔧 Automated template processing with secure environment variable substitution
- 🔒 Security hardened - shell injection protection and environment file validation
- 📍 Repository-agnostic design - works with any project name/location

## Documentation

- **[IDE.md](docs/IDE.md)** - IDE configurations for VS Code, Cursor, and Windsurf
- **[LLM.md](docs/LLM.md)** - LLM tool configurations for Claude
- **[CLAUDE.md](CLAUDE.md)** - Detailed repository structure and implementation notes
- **[Claude Desktop Setup](llm/claude_desktop/README.md)** - Specific instructions for Claude Desktop configuration
- **[Claude Code Guide](llm/claude_code/README.md)** - Comprehensive guide to using Claude Code
- **[Test Suite](tests/README.md)** - Information about running tests


## Quick Start - Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/andisab/mise-en-place.git
cd mise-en-place

# Run automated setup
./install.sh

# When prompted "Run quick install? [Y/n]", press Enter to:
# • Validate configuration
# • Preview files to be synced
# • Sync dotfiles to your system with automatic template processing
# • Install shell integration

# That's it. You should be good to go! 
```
The quick install handles everything automatically. For manual control or customization, follow these steps instead: 


## Manual Setup (Advanced)

If you prefer to control each step or need to customize before syncing:

```bash
# Clone repository
git clone https://github.com/andisab/mise-en-place.git
cd mise-en-place

# Review and customize dotfiles.conf. Uncomment only the files you want to import and manage. 
vim | emacs | nano dotfiles.conf

# Source the installation script
source install.sh

# If you plan on using sync functionality regularly, consider installing shell integration (one-time setup):
install_shell_integration

# Test configuration (safe - no file changes)
test_config

# Sync dotfiles from repository to system (with preview)
sync_dotfiles_from_git
```


## Configuration

All managed files are defined in `dotfiles.conf` using simple `repo_path:system_path` format:

```
# LLM & AI Assistant configs
llm/claude_code/CLAUDE.md:.claude/CLAUDE.md
llm/claude_desktop/claude_desktop_config_basic.json:Library/Application Support/Claude/claude_desktop_config.json
```


## Template Processing & Environment Variables

The framework includes automated template processing with secure environment variable substitution:
- **Automatic Processing**: Templates are processed automatically after successful sync operations
- **Secure Substitution**: Uses `envsubst` for safe, reliable environment variable import & expansion with shell injection protection
- **Variable Detection**: Automatically discovers required variables from templates using regex analysis
- **Missing Variable Warnings**: Alerts you to undefined variables that may cause issues
- **Environment File Validation**: Validates `.env` files for security before processing
- **Atomic Operations**: Template processing uses secure temporary files with rollback capability
- **Cross-Platform**: Works on macOS (in rare cases, may require `brew install gettext`) and Linux systems

### Environment Setup
```bash
# 1. Copy the environment template (done automatically during sync)
cp ~/.config/dotfiles/.env.example ~/.config/dotfiles/.env

# 2. Edit and add your API keys/secrets (or just use your existing .env file, if you prefer, as configured in config_parser.py)
vim | emacs | nano ~/.config/dotfiles/.env

# 3. Templates are processed automatically during sync
sync_dotfiles_from_git  # Automatically processes templates after sync
```

### Requirements
The template processing feature requires `envsubst`. Check if you have it:
```bash
which envsubst || echo "envsubst not found"
```

On Mac OS & Linux, it's usually pre-installed with the `gettext` package.

If not found, install on macOS:
```bash
brew install gettext
brew link --force gettext  # May be needed if envsubst isn't in PATH
```

### Environment Variable Hierarchy

The system follows a clear precedence order when resolving environment variables (from lowest to highest priority):

1. **System Environment Variables** (lowest priority)
   - Variables already set in your shell (e.g., via `export VAR=value`)
   - These are checked first but can be overridden by any .env file

2. **~/.env** (middle priority)
   - Traditional location for global environment variables
   - Overrides system environment variables

3. **~/.config/dotfiles/.env** (highest priority)
   - Repository-specific location for this dotfiles system
   - Overrides both system variables and ~/.env

**How it works**: The system uses a "last-wins" approach where later files override earlier ones. When processing templates:
- First checks system environment
- Then sources ~/.env (if it exists and passes security validation)
- Finally sources ~/.config/dotfiles/.env (if it exists and passes validation)
- All environment loading happens in an isolated subshell for security

**Example**:
```bash
# System environment
export API_KEY="system_key"

# ~/.env
API_KEY="global_key"
DATABASE_URL="postgres://global"

# ~/.config/dotfiles/.env
API_KEY="local_key"

# Result: ${API_KEY} → "local_key" (highest priority wins)
#         ${DATABASE_URL} → "postgres://global" (from ~/.env)
```


## Additional Setup & Customization

### 1. Personal Information
- Update `llm/claude_code/CLAUDE.md` with your preferences and profile
- Configure git with your name and email using `git config`

### 2. Shell Configuration
- Your existing shell configuration files will remain untouched
- Use the custom overlay feature (below) if you want to manage shell configs through this repo

### 3. Choose What to Manage
- Edit `dotfiles.conf` and uncomment any additional files you want to import and manage
- Add new entries for any additional configuration or customized files you want to track

### 4. IDE and Tool Configurations
- The `ide/` directory contains templates for VS Code, Cursor, and Windsurf
- The `llm/` directory contains templates for Claude Desktop and Claude Code
- Customize these based on your preferences

### 5. Custom File Overlays

The framework also supports personal dotfile customization that will take precedence over repository files:

```bash
# Custom files are stored in ~/.config/dotfiles.custom/
# Add custom overlay entries to dotfiles.conf using "custom:" prefix

# Example in dotfiles.conf:
llm/claude_code/CLAUDE.md:.claude/CLAUDE.md        # Standard mapping
custom:my-claude.md:.claude/CLAUDE.md              # Custom overlay

# Create your custom file:
mkdir -p ~/.config/dotfiles.custom
cp ~/.claude/CLAUDE.md ~/.config/dotfiles.custom/my-claude.md
# Edit the custom file with your personal settings

# When syncing, custom files take precedence over repository versions
sync_dotfiles_from_git  # Will use custom file if it exists
```

This allows you to maintain personal configurations and sync without concern for being overwritten by repository updates. 


## More Detailed Information

After sourcing `install.sh`:

- `quick_install` - Run the automated setup wizard (recommended for first time)
- `test_config` - Test configuration safely (no file changes)
- `validate_config` - Run detailed validation
- `sync_dotfiles_from_git` - Deploy repo configs to system (with preview + automatic template processing!)
- `collect_dotfiles` - Collect system configs to repo
- `process_env_templates` - Process configuration templates with environment variable substitution
- `install_shell_integration` - Add commands to your shell startup file
- `remove_shell_integration` - Remove commands from shell startup file

### Enhanced Sync Options

The `sync_dotfiles_from_git` command now includes automatic template processing and defaults to a safe preview mode:

```bash
# Default: Preview changes with interactive prompts + automatic template processing
sync_dotfiles_from_git

# Or use Python directly with more options:
python3 config_parser.py --sync-from-repo              # Interactive mode (default)
python3 config_parser.py --sync-from-repo --force      # Skip preview, apply all changes
python3 config_parser.py --sync-from-repo --strategy replace  # Replace all without asking
python3 config_parser.py --sync-from-repo --strategy skip     # Preview only, skip all changes
```

### Repository Structure

```
├── HOME/            # Dotfiles that mirror ${HOME} directory structure
│   ├── .env.example # → ~/.config/dotfiles/.env.example
│   └── config/      # → ~/.config/
├── docs/            # Documentation
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
├── tests/           # Test suite
│   ├── unit/        # Unit tests
│   └── smoke/       # Integration tests
├── dotfiles.conf    # Configuration manifest
├── config_parser.py # Python configuration parser
├── install.sh       # Main installation interface script
└── CLAUDE.md        # Repository structure documentation
```


## Safety Features

- All operations preview changes before applying them
- Existing files are backed up to `~/.config/dotfiles.bak`
- Use `--force` flag to skip previews (use with caution)
- Python-based diff visualization using built-in `difflib`
- **Security Hardening**:
  - Shell injection prevention through proper subprocess argument handling
  - Environment file validation to prevent execution of malicious code
  - Secure temporary file operations with atomic updates
  - Rollback capability for failed template processing operations


## Requirements

- **macOS 10.15+** or Linux
- **Python 3.8+** (ships with macOS 10.15+)
- **Git** (see First Time macOS Setup above)
- **envsubst** (for template processing - see [Template Processing](#requirements-1) section)

### First Time macOS Setup

<details>
<summary>Click here if you need to install Git or Homebrew</summary>

### Install Xcode Command Line Tools (includes Git)
```bash
xcode-select --install
```

### Or install Homebrew (optional, includes Git)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Git via Homebrew
brew install git
```

</details>

## License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 Andis A. Blukis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```