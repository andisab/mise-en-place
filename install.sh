#!/usr/bin/env bash

# Dotfiles Installation Script (Python-based)
# All heavy lifting is done by Python, shell just provides convenient functions

# Configuration
home_dir="${1:-$HOME}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_name="$(basename "$script_dir")"
config_parser="$script_dir/config_parser.py"

# Load secrets file locations from Python configuration
SECRETS_FILES=($(python3 "$config_parser" --get-secrets-files))

# Test configuration
test_config() {
    echo "Testing configuration..."
    python3 "$config_parser" --list
}

# Validate configuration
validate_config() {
    echo "Validating configuration..."
    python3 "$config_parser" --validate-only --verbose
}

# Sync dotfiles from repository to system
sync_dotfiles() {
    echo "Syncing dotfiles from repository to system..."
    if ! python3 "$config_parser" --sync-from-repo; then
        return 1
    fi
    
    # Template processing is handled automatically during sync
    # Use process_env_templates manually if you need to process specific templates
}

# Backward compatibility alias
sync_dotfiles_from_git() {
    sync_dotfiles "$@"
}

# Sync dotfiles without template processing
sync_dotfiles_no_templates() {
    echo "Syncing dotfiles from repository to system (no template processing)..."
    python3 "$config_parser" --sync-from-repo --no-templates
}

# Backward compatibility alias
sync_dotfiles_from_git_no_templates() {
    sync_dotfiles_no_templates "$@"
}

# Collect dotfiles from system to repository
collect_dotfiles() {
    echo "Collecting dotfiles from system to repository..."
    python3 "$config_parser" --sync-to-repo
}

# Backward compatibility alias
collect_dotfiles_to_git() {
    collect_dotfiles "$@"
}

# Generic template processing with environment variable substitution
# Now a thin wrapper around the secure Python implementation
process_env_templates() {
    local template_path="${1:-$script_dir/llm/claude_desktop/claude_desktop_config_basic.json}"
    local output_path="${2:-${HOME}/Library/Application Support/Claude/claude_desktop_config.json}"
    
    echo "🔄 Processing template with environment variables..."
    echo "   Template: $(basename "$template_path")"
    echo "   Output: $output_path"
    echo ""
    
    # Use the new secure Python implementation
    if python3 "$config_parser" --process-template "$template_path" "$output_path"; then
        echo ""
        echo "⚠️  Security Note: The generated file may contain sensitive information"
        echo "   and should not be committed to version control."
        return 0
    else
        echo "Error: Template processing failed"
        return 1
    fi
}

# Environment variable analysis and reporting function
# Now a thin wrapper around the secure Python implementation
analyze_env_variables() {
    local template_path="$1"
    
    # Use the new secure Python implementation
    python3 "$config_parser" --analyze-template "$template_path"
    return $?
}

# Process all templates in managed files (useful after updating environment variables)
process_all_templates() {
    echo "Processing templates in all managed files..."
    echo "Note: This will scan all managed files for template variables and process them."
    echo ""
    
    # Get list of managed files and process any templates found
    python3 "$config_parser" --list | grep -E '\s*[^#].*->.*' | while IFS= read -r line; do
        # Extract destination path from the mapping (handle various formats)
        dest_path=$(echo "$line" | sed -E 's/.*->\s*([^[:space:]]+).*/\1/')
        dest_file="$HOME/$dest_path"
        
        if [ -f "$dest_file" ]; then
            # Use Python to check for template variables (more reliable than grep)
            if python3 -c "
from pathlib import Path
from config_parser import detect_template_variables
import sys
variables = detect_template_variables(Path('$dest_file'))
sys.exit(0 if variables else 1)
" 2>/dev/null; then
                echo "Found template: $dest_path"
                # Process this specific file using the secure Python implementation
                process_env_templates "$dest_file" "$dest_file"
            fi
        fi
    done
    
    echo ""
    echo "✅ Template processing completed for all managed files."
}


# Install shell integration (adds source command to user's shell config)
install_shell_integration() {
    local shell_config=""
    local source_line="source \"$script_dir/install.sh\""
    local marker="# mise-en-place integration"
    
    # Determine which shell config to use (priority order: .profile → .zshrc → .bashrc)
    if [[ -f ~/.profile ]]; then
        shell_config="$HOME/.profile"
    elif [[ "$SHELL" == *"zsh"* ]] && [[ -f ~/.zshrc ]]; then
        shell_config="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]] && [[ -f ~/.bashrc ]]; then
        shell_config="$HOME/.bashrc"
    elif [[ "$SHELL" == *"zsh"* ]]; then
        # Create .zshrc if user has zsh but no config files
        shell_config="$HOME/.zshrc"
        touch "$shell_config"
    elif [[ "$SHELL" == *"bash"* ]]; then
        # Create .bashrc if user has bash but no config files
        shell_config="$HOME/.bashrc"
        touch "$shell_config"
    else
        echo "Error: No suitable shell configuration file found and unable to determine shell type"
        return 1
    fi
    
    # Check if already installed
    if grep -q "$repo_name/install.sh" "$shell_config" 2>/dev/null; then
        echo "✅ Shell integration already installed in $shell_config"
        return 0
    fi
    
    # Backup the file
    cp "$shell_config" "$shell_config.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Append the source command
    cat >> "$shell_config" << EOF

$marker
# Automatically load dotfile management commands
if [[ -f "$script_dir/install.sh" ]]; then
    source "$script_dir/install.sh"
fi
EOF
    
    echo "✅ Shell integration installed in $shell_config"
    echo "   (Backup saved to $shell_config.backup.*)"
    echo ""
    echo "To activate now, run: source $shell_config"
    echo "Or start a new terminal session"
}

# Remove shell integration
remove_shell_integration() {
    local found=0
    
    for shell_config in ~/.zshrc ~/.bashrc ~/.profile; do
        if [[ -f "$shell_config" ]] && grep -q "$repo_name/install.sh" "$shell_config"; then
            # Create backup
            cp "$shell_config" "$shell_config.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Remove the integration block
            sed -i.tmp '/# mise-en-place integration/,/^fi$/d' "$shell_config"
            rm -f "$shell_config.tmp"
            
            echo "✅ Removed shell integration from $shell_config"
            echo "   (Backup saved to $shell_config.backup.*)"
            found=1
        fi
    done
    
    if [[ $found -eq 0 ]]; then
        echo "No shell integration found to remove"
    fi
}

# Process Claude Desktop basic config (expand ${HOME} variables)
process_claude_basic_config() {
    local config_path="${HOME}/Library/Application Support/Claude/claude_desktop_config.json"
    
    # Check if the basic config was synced
    if [[ ! -f "$config_path" ]]; then
        return 0  # Not an error, just nothing to do
    fi
    
    # Check if this is the basic config (has ${HOME} placeholders)
    if ! grep -q '\${HOME}' "$config_path" 2>/dev/null; then
        return 0  # Already processed or is a different config
    fi
    
    echo "Processing Claude Desktop configuration..."
    
    # Create backup
    cp "$config_path" "$config_path.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Read config and expand ${HOME} variables
    local config_content=$(cat "$config_path")
    config_content=$(echo "$config_content" | sed "s|\${HOME}|$HOME|g")
    
    # Write back the processed config
    echo "$config_content" > "$config_path"
    
    echo "✅ Claude Desktop config processed (${HOME} paths expanded)"
    return 0
}

# Quick install function for the happy path
quick_install() {
    echo "🚀 Starting mise-en-place Quick Install..."
    echo ""
    
    # Step 1: Validate configuration
    echo "Step 1/5: Validating configuration..."
    if ! validate_config; then
        echo "❌ Configuration validation failed. Please check errors above."
        return 1
    fi
    echo "✅ Configuration validated"
    echo ""
    
    # Step 2: Preview what will be synced
    echo "Step 2/5: Preview changes..."
    echo "The following files will be synced:"
    python3 "$config_parser" --list
    echo ""
    echo "Press Enter to continue or Ctrl+C to cancel..."
    read -r
    
    # Step 3: Sync dotfiles and process templates
    echo "Step 3/4: Syncing dotfiles and adding environment variables..."
    if ! sync_dotfiles; then
        echo "❌ Sync failed. Please check errors above."
        return 1
    fi
    echo ""
    
    # Step 4: Install shell integration
    echo "Step 4/4: Installing shell integration..."
    if ! install_shell_integration; then
        echo "❌ Shell integration failed. Please check errors above."
        return 1
    fi
    echo ""
    
    echo "🎉 Quick install completed successfully!"
    echo ""
    echo "What's ready:"
    echo "  ✅ Dotfiles synced to your system"
    echo "  ✅ Shell commands available after restart"
    if [[ -f "${HOME}/Library/Application Support/Claude/claude_desktop_config.json" ]]; then
        echo "  ✅ Claude Desktop basic config installed (MCP servers ready). Please quit & restart Claude Desktop. MCP servers will need 1-2 minutes to load & start."
    fi
    echo ""
    echo "Next steps:"
    echo "  1. Restart your terminal or run: source ~/.profile (or ~/.zshrc/~/.bashrc)"
    echo "  2. Create your .env file: cp ~/.config/dotfiles/.env.example ~/.config/dotfiles/.env"
    echo "  3. Edit ~/.config/dotfiles/.env and add your API keys"
    echo "  4. Re-run sync_dotfiles to process templates with your API keys"
    echo "  5. Customize dotfiles.conf to manage more files"
}

# Check if running with --quick-install flag
if [[ "$1" == "--quick-install" ]] || [[ "$1" == "-q" ]]; then
    quick_install
    exit $?
fi

# Only run startup logic when script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Check if user is in project directory and script hasn't been used yet
    if [[ "$PWD" == *"$repo_name"* ]]; then
        if [[ ! -d ~/.config/dotfiles && ! -d ~/.config/dotfiles.bak ]]; then
            # First time setup prompt
            echo "🎯 mise-en-place Manager"
            echo ""
            echo "This appears to be your first time running this script."
            echo "Would you like to run the quick install? This will:"
            echo "  • Validate your configuration"
            echo "  • Preview files to be synced"
            echo "  • Sync default set of dotfiles to your system"
            echo "  • Set up Claude Desktop basic configuration"
            echo "  • Install shell integration for easy commands"
            echo ""
            echo -n "Run quick install? [Y/n] "
            read -r response
            case "$response" in
                [nN][oO]|[nN])
                    echo ""
                    echo "Skipping quick install. Manual commands available below."
                    ;;
                *)
                    echo ""
                    quick_install
                    exit $?
                    ;;
            esac
        else
            # Initialize - show commands when dotfiles.bak exists (system already set up)
            echo "Dotfiles commands loaded. Key commands:"
            echo "  quick_install            - Complete setup (recommended)"
            echo "  sync_dotfiles            - Sync repo -> system"
            echo "  test_config              - List all managed files"
            echo "  validate_config          - Run detailed validation"
        fi
    fi
fi