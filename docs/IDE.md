## Table of Contents
- [IDE Set-up](#ide-set-up)
  - [VS Code Set-up](#vs-code-set-up)
  - [Cursor Set-up](#cursor-set-up)
  - [Windsurf Set-up](#windsurf-set-up)

# IDE Set-up
## VSCode Set-up

#### Configuration Files
VSCode settings are stored in `ide/vscode/`:
- `settings.json` - User settings with Vim integration
- `extensions.json` - Recommended extensions list
- `aab_settings.json` - Additional custom settings
- `VSCode_default_keybindings.json` - Keybinding reference

#### Installation
1. **Install VS Code**: Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. **Link settings**:
   ```bash
   ln -sf ~/Projects/mise-en-place/ide/vscode/settings.json ~/Library/Application\ Support/Code/User/settings.json
   ```
3. **Install extensions**: Open `extensions.json` and install recommended extensions

#### Extensions
**Essential:**
- **Vim** - Vim keybindings
  - https://github.com/VSCodeVim/Vim?tab=readme-ov-file : VIM-style key bindings for VSCode.
  - https://www.barbarianmeetscoding.com/blog/boost-your-coding-fu-with-vscode-and-vim
- **GitLens** - Enhanced Git capabilities
- **Auto Rename Tag** - HTML/XML tag sync
- **Bracket Pair Colorizer** - Visual bracket matching

**Language Support:**
- **Python** - Python development
- **TypeScript** - TypeScript/JavaScript
- **Rust** - Rust language support
- **Go** - Go development


&nbsp;
## Cursor Set-up
#### Configuration Files
Cursor settings are stored in `ide/cursor/`.

#### Installation
1. **Install Cursor**: Download from [cursor.sh](https://cursor.sh/)
2. **Link settings** (Cursor uses similar paths to VS Code):
   ```bash
   ln -sf ~/Projects/mise-en-place/ide/cursor/settings.json ~/Library/Application\ Support/Cursor/User/settings.json
   ```

#### Key Features
- AI-powered code completion
- Built on VS Code, supports same extensions
- Enhanced with LLM capabilities


&nbsp;
## Windsurf Set-up

#### Configuration Files
Windsurf settings are stored in `ide/windsurf/`.

#### Installation
1. **Install Windsurf**: Download from [codeium.com/windsurf](https://codeium.com/windsurf)
2. **Link settings**:
   ```bash
   ln -sf ~/Projects/mise-en-place/ide/windsurf/settings.json ~/Library/Application\ Support/Windsurf/User/settings.json
   ```

#### Key Features
- AI-native IDE with advanced code generation
- Multi-file editing capabilities
- Built-in AI chat and commands



