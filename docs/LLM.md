## Table of Contents
- [LLM Set-up](#llm-set-up)
  - [Claude Desktop Set-up](#claude-desktop-set-up)
  - [Claude Code Set-up](#claude-code-set-up)
  - [Chat GPT Code Set-up](#chat-gpt-code-set-up)

&nbsp;
## LLM Set-up

This document covers configuration for LLM-based development tools.

&nbsp;
## Claude Desktop Set-up
Claude Desktop and Claude Code have slightly different configurations and built-in capabilities. Claude Desktop is a desktop application that provides a more traditional UI-driven experience, while Claude Code is a command-line tool that provides a more modern, terminal-based experience, with corresponding functionality and permissions for dev work. I would recommend familiarizing yourself with Claude Desktop setup and functionality first, and then moving to the more advanced features of Claude Code from there. It is also somewhat straightforward to import MCP functionality from Claude Desktop to Claude Code. 

#### Configuration Files
Claude Desktop settings are stored in `llm/claude_desktop/`:
- `claude_desktop_config.template.json` - Configuration template
- `claude_desktop_config_ref.jsonc` - Configuration reference with all options
- `README.md` - Detailed setup instructions
- `profile_settings.md` - Profile configuration guide

#### Installation
1. **Install Claude Desktop**: Download from [claude.ai](https://claude.ai/download)
2. **Configure MCP servers**:
   ```bash
   cp ~/Projects/mise-en-place/llm/claude_desktop/claude_desktop_config.template.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
3. **Edit configuration**: Add your MCP server configurations

#### Key Features
- Model Context Protocol (MCP) support
- Multiple server integrations
- Custom tool configurations



&nbsp;
## Claude Code Set-up

#### Configuration Files
Claude Code settings are stored in `llm/claude_code/`:
- `CLAUDE.md` - Custom instructions for Claude Code behavior

#### Installation
1. **Install Claude Code**: 
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
2. **Set up custom instructions**:
   ```bash
   mkdir -p ~/.claude
   ln -sf ~/Projects/mise-en-place/llm/claude_code/CLAUDE.md ~/.claude/CLAUDE.md
   ```

#### Key Features
- Terminal-based AI coding assistant
- Custom behavior instructions
- File system access and code generation
- Git integration



&nbsp;
## Chat GPT Code Set-up

#### Installation
1. **Install via npm**:
   ```bash
   npm install -g chatgpt-cli
   ```
2. **Configure API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

#### Key Features
- Command-line interface to ChatGPT
- Code generation and explanation
- Multiple model support
