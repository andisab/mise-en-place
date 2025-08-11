# Claude Desktop Configuration

This directory contains the configuration for Claude Desktop's MCP (Model Context Protocol) servers.

## Overview

Claude Desktop requires a configuration file to define MCP servers, but JSON doesn't support environment variables or dynamic values. This creates challenges for:
- Hardcoded home directory paths that vary between systems
- API keys that shouldn't be committed to version control

## Solution

This repo advocates for a template-based approach if you would like to use MCP servers that require API keys. You won't need to do any of this for initial setup on the claude_desktop_config.json file. 

1. **`claude_desktop_config.template.json`** - Template with placeholders like `${HOME}` and `${API_KEY}`
2. **`.env.example`** - Example environment file showing required variables
3. **`~/.claude_secrets`** - Your actual secrets file (never committed)
4. **`generate_claude_config`** - Shell function that processes the template

If you don't need to use MCP servers that require API keys, you can skip this step! 

## Setup Instructions

### 1. Create your secrets file

```bash
# Copy the example file
cp ~/.env.example ~/.claude_secrets

# Edit the file and add your actual API keys
vim ~/.claude_secrets
```

### 2. Generate the configuration

```bash
# Source the install script first
source ~/Projects/mise-en-place/install.sh

# Then generate the config
generate_claude_config
```

This will:
- Read the template file
- Replace `${HOME}` with your actual home directory
- Replace `${API_KEY}` placeholders with values from `~/.claude_secrets`
- Generate the config at `~/Library/Application Support/Claude/claude_desktop_config.json`

### 3. Restart Claude Desktop

The new configuration will be loaded when Claude Desktop starts.

## Adding New MCP Servers

1. Edit `claude_desktop_config.template.json`
2. Add any new API keys to `.env.example` (as examples)
3. Update the `generate_claude_config` function in `profile` if needed
4. Regenerate your config with `generate_claude_config`

## Security Notes

- Never commit `~/.claude_secrets` or the generated config file
- Both are already in `.gitignore` for safety
- The template file can be safely committed as it contains no secrets

## Troubleshooting

If the function isn't available:
```bash
source ~/Projects/mise-en-place/install.sh
```

If you get path errors, ensure your dotfiles are synced:
```bash
source ~/Projects/mise-en-place/install.sh
sync_dotfiles_from_git
```