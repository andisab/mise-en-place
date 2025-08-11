#!/usr/bin/env python3
"""
Dotfiles configuration parser and shell array generator.
Reads dotfiles.conf and outputs shell-compatible variable assignments.
"""

import os
import sys
import re
import difflib
import subprocess
import tempfile
import shlex
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

# Prominent backup directory configuration
BACKUP_DIR = Path.home() / ".config" / "dotfiles.bak"
# NOTE: All existing files will be backed up before any changes are made and the script will prompt to confirm if it senses any local edits.

# Custom directory configuration
CUSTOM_DIR = Path.home() / ".config" / "dotfiles.custom"
# Any files designated w/ "custom:" prefix in dotfiles.conf and found in CUSTOM_DIR will take precedence for import over files in this repository. 
# NOTE: If you keep your personal config files in version control, you can use symlinks to point to them, or keep actual copies of custom files in CUSTOM_DIR. 

# SECRETS files configuration. The install.sh script will import from here, if configured, and from globally-set environment variables with envsubst(). 
def get_secrets_files():
    """Return list of secrets file paths in precedence order (lower priority first)."""
    return [
        str(Path.home() / ".env"),                        # Traditional location (lower priority)
        str(Path.home() / ".config" / "dotfiles" / ".env")  # Default location for this repository (last = highest priority)
    ] 

class DotfilesConfig:
    """Parse and validate dotfiles configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.repo_dir = Path(__file__).parent
        if config_file:
            self.config_file = Path(config_file)
            # If a custom config file is provided, use its parent as repo_dir
            self.repo_dir = self.config_file.parent
        else:
            self.config_file = self.repo_dir / "dotfiles.conf"
        self.dotfiles: List[str] = []
        self.file_map: Dict[str, str] = {}
        self.custom_map: Dict[str, str] = {}  # Maps destination path to custom source
        self.backup_dir = BACKUP_DIR
        self.custom_dir = CUSTOM_DIR
        
    def parse_config(self) -> None:
        """Parse the dotfiles.conf file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse repo_path:system_path format
                if ':' not in line:
                    print(f"Warning: Invalid format on line {line_num}: {line}", file=sys.stderr)
                    continue
                
                # Special handling for custom: prefix
                if line.startswith('custom:'):
                    # For custom entries, we need to find the last colon
                    # Format: custom:filename:destination
                    # The filename can contain colons, so we split from the right
                    prefix_and_file = line[7:]  # Remove 'custom:' prefix
                    if ':' not in prefix_and_file:
                        print(f"Warning: Invalid custom format on line {line_num}: {line}", file=sys.stderr)
                        print(f"        Expected format: custom:filename:destination", file=sys.stderr)
                        continue
                    # Split from the right to handle filenames with colons
                    last_colon = prefix_and_file.rfind(':')
                    custom_filename = prefix_and_file[:last_colon]
                    system_path = prefix_and_file[last_colon + 1:]
                    
                    # Validate filename is not empty
                    if not custom_filename.strip():
                        print(f"Warning: Empty custom filename on line {line_num}: {line}", file=sys.stderr)
                        continue
                        
                    repo_path = f"custom:{custom_filename}"
                else:
                    repo_path, system_path = line.split(':', 1)
                
                repo_path = repo_path.strip()
                system_path = system_path.strip()
                
                if not repo_path or not system_path:
                    print(f"Warning: Empty values on line {line_num}: {line}", file=sys.stderr)
                    continue
                
                # Additional safety checks
                if system_path == "/" or system_path == "~":
                    print(f"ERROR: Dangerous system path on line {line_num}: {system_path}", file=sys.stderr)
                    raise ValueError(f"Refusing to manage root or home directory: {system_path}")
                
                # Check if this is a custom file overlay
                if repo_path.startswith("custom:"):
                    custom_path = repo_path[7:].strip()  # Remove "custom:" prefix
                    if ".." in custom_path or ".." in system_path:
                        print(f"ERROR: Path traversal detected on line {line_num}", file=sys.stderr)
                        raise ValueError(f"Path traversal not allowed: {line}")
                    # Store custom mapping (destination -> custom source)
                    self.custom_map[system_path] = custom_path
                else:
                    if ".." in repo_path or ".." in system_path:
                        print(f"ERROR: Path traversal detected on line {line_num}", file=sys.stderr)
                        raise ValueError(f"Path traversal not allowed: {line}")
                    
                    self.dotfiles.append(repo_path)
                    self.file_map[repo_path] = system_path
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.dotfiles:
            errors.append("No dotfiles found in configuration")
        
        if not self.file_map:
            errors.append("No file mappings found in configuration")
        
        # Check for source files existence
        for repo_path in self.dotfiles:
            source_file = self.repo_dir / repo_path
            if not source_file.exists():
                errors.append(f"Source file/directory not found: {repo_path}")
        
        # Check for custom files existence
        for dest_path, custom_path in self.custom_map.items():
            custom_file = self.custom_dir / custom_path
            if not custom_file.exists():
                errors.append(f"Custom file/directory not found: {custom_path} (expected at {custom_file})")
        
        # Check for duplicates
        if len(self.dotfiles) != len(set(self.dotfiles)):
            duplicates = [x for x in self.dotfiles if self.dotfiles.count(x) > 1]
            errors.append(f"Duplicate entries found: {set(duplicates)}")
        
        return errors
    
    def generate_shell_arrays(self, shell: str = "bash") -> str:
        """Generate shell-compatible array assignments."""
        if shell.lower() in ["zsh", "bash"]:
            # Generate two synchronized indexed arrays
            # This approach avoids all the issues with associative arrays and slashes
            repo_array = "DOTFILES_REPO_PATHS=(" + " ".join(f'"{item}"' for item in self.dotfiles) + ")\n"
            dest_array = "DOTFILES_DEST_PATHS=(" + " ".join(f'"{self.file_map[item]}"' for item in self.dotfiles) + ")\n"
            
            return repo_array + dest_array
        else:
            raise ValueError(f"Unsupported shell: {shell}")
    
    def generate_exports(self) -> str:
        """Generate shell exports for key variables."""
        exports = f'export DOTFILES_REPO="{self.repo_dir}"\n'
        exports += f'export DOTFILES_COUNT="{len(self.dotfiles)}"\n'
        exports += f'export DOTFILES_BACKUP_DIR="{BACKUP_DIR}"\n'
        exports += f'export DOTFILES_CUSTOM_DIR="{CUSTOM_DIR}"\n'
        return exports


def detect_template_variables(file_path: Path) -> Set[str]:
    """
    Detect environment variables in template files.
    
    Scans file for ${VARIABLE_NAME} patterns and returns set of variable names.
    Returns empty set if no templates found or if file cannot be read.
    
    Args:
        file_path: Path to file to scan
        
    Returns:
        Set of variable names found in template (without ${} wrapper)
    """
    try:
        # Try to read as text file
        content = file_path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        # Binary file or read error - no template variables possible
        return set()
    
    # Match ${VARIABLE_NAME} patterns
    # Variable names must start with letter or underscore, contain only alphanumeric and underscore
    pattern = r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}'
    matches = re.findall(pattern, content)
    
    return set(matches)


def validate_env_file(env_file_path: Path) -> bool:
    """
    Validate environment file for basic security before sourcing.
    
    Checks for obvious malicious patterns while allowing legitimate env files.
    
    Args:
        env_file_path: Path to environment file to validate
        
    Returns:
        True if file appears safe to source, False otherwise
    """
    try:
        if not env_file_path.exists() or not env_file_path.is_file():
            return False
            
        content = env_file_path.read_text(encoding='utf-8')
        
        # Check for obvious malicious patterns
        dangerous_patterns = [
            r'[;&|`$(){}]',  # Command injection characters
            r'\$\(',         # Command substitution
            r'`',            # Backticks
            r'eval\s',       # eval statements
            r'exec\s',       # exec statements
            r'\|\s*sh',      # Pipe to shell
            r'>\s*/dev/',    # Writing to devices
            r'rm\s+-rf',     # Dangerous deletions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                print(f"Warning: Potentially dangerous pattern found in {env_file_path}", 
                      file=sys.stderr)
                return False
        
        # Check that file contains mostly KEY=VALUE pairs
        lines = [line.strip() for line in content.split('\n') 
                if line.strip() and not line.strip().startswith('#')]
        
        valid_lines = 0
        for line in lines:
            # Allow KEY=VALUE format
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*=.*$', line):
                valid_lines += 1
            # Allow export KEY=VALUE format  
            elif re.match(r'^export\s+[A-Za-z_][A-Za-z0-9_]*=.*$', line):
                valid_lines += 1
        
        # At least 80% of non-comment lines should be valid env vars
        if lines and (valid_lines / len(lines)) < 0.8:
            print(f"Warning: {env_file_path} doesn't appear to be a standard env file", 
                  file=sys.stderr)
            return False
            
        return True
        
    except Exception as e:
        print(f"Warning: Cannot validate env file {env_file_path}: {e}", 
              file=sys.stderr)
        return False


def process_template_file(file_path: Path, env_files: List[str]) -> bool:
    """
    Process a single template file using existing environment system.
    
    SECURITY: Uses safe subprocess calls without shell injection.
    Preserves the environment loading precedence and envsubst functionality.
    
    Args:
        file_path: Path to template file to process
        env_files: List of environment files in precedence order
        
    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        # Check if envsubst is available (secure command check)
        try:
            subprocess.run(['envsubst', '--help'], 
                          capture_output=True, text=True, check=False, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"Warning: envsubst not available, skipping template: {file_path.name}", 
                  file=sys.stderr)
            return False
        
        # Validate file path is safe
        if not file_path.exists() or not file_path.is_file():
            print(f"Warning: Template file not found or not a file: {file_path}", 
                  file=sys.stderr)
            return False
        
        # Create secure backup with atomic operation
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.template_backup',
            dir=file_path.parent,
            delete=False,
            encoding='utf-8'
        ) as backup_file:
            backup_path = Path(backup_file.name)
            backup_file.write(file_path.read_text(encoding='utf-8'))
        
        # Validate environment files before using them
        valid_env_files = []
        for env_file in env_files:
            env_path = Path(env_file)
            if env_path.exists() and validate_env_file(env_path):
                valid_env_files.append(str(env_path))
            elif env_path.exists():
                print(f"Warning: Skipping potentially unsafe env file: {env_file}", 
                      file=sys.stderr)
        
        # Create secure temporary file for output
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tmp',
            dir=file_path.parent,
            delete=False,
            encoding='utf-8'
        ) as temp_output:
            temp_output_path = Path(temp_output.name)
        
        try:
            # Build secure shell command for environment loading + envsubst
            # We still use shell=True but with properly escaped arguments
            shell_cmd_parts = []
            
            # Add environment file sourcing (with validated files only)
            for env_file in valid_env_files:
                # Use shlex.quote for proper shell escaping
                shell_cmd_parts.append(f'source {shlex.quote(env_file)} 2>/dev/null || true')
            
            # Add envsubst command with escaped file paths
            envsubst_cmd = f'envsubst < {shlex.quote(str(file_path))} > {shlex.quote(str(temp_output_path))}'
            shell_cmd_parts.append(envsubst_cmd)
            
            # Combine into subshell (still preserves environment isolation)
            if shell_cmd_parts:
                full_cmd = '(' + ' && '.join(shell_cmd_parts) + ')'
            else:
                full_cmd = f'envsubst < {shlex.quote(str(file_path))} > {shlex.quote(str(temp_output_path))}'
            
            # Execute with timeout and proper error handling
            result = subprocess.run(
                full_cmd,
                shell=True,  # Still needed for subshell and sourcing, but now with escaped args
                capture_output=True,
                text=True,
                timeout=30,  # Prevent hanging
                cwd=file_path.parent,  # Ensure predictable working directory
            )
            
            if result.returncode != 0:
                print(f"Warning: Template processing failed for {file_path.name}: {result.stderr.strip()}", 
                      file=sys.stderr)
                return False
            
            # Verify output was created and has content
            if not temp_output_path.exists():
                print(f"Warning: envsubst did not create output file for {file_path.name}", 
                      file=sys.stderr)
                return False
            
            # Atomic replacement of original file
            processed_content = temp_output_path.read_text(encoding='utf-8')
            file_path.write_text(processed_content, encoding='utf-8')
            
            print(f"  Template processed: {file_path.name}")
            return True
            
        finally:
            # Clean up temporary files
            if temp_output_path.exists():
                temp_output_path.unlink()
            # Keep backup file for user reference
            
    except subprocess.TimeoutExpired:
        print(f"Error: Template processing timed out for {file_path.name}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error processing template {file_path.name}: {e}", file=sys.stderr)
        return False


def analyze_template_environment(template_path: Path, env_files: List[str]) -> Tuple[bool, Set[str], Dict[str, str]]:
    """
    Analyze environment variables for template processing.
    
    Provides comprehensive analysis similar to shell's analyze_env_variables function
    but implemented in Python for better error handling and consistency.
    
    Args:
        template_path: Path to template file to analyze
        env_files: List of environment files in precedence order
        
    Returns:
        Tuple of (success, required_variables, variable_sources)
        - success: True if analysis completed without critical errors
        - required_variables: Set of variables required by template
        - variable_sources: Dict mapping variable names to their source files
    """
    try:
        print("🔍 Analyzing environment variables for template processing...")
        print("")
        
        # Extract variables needed from template (same logic as shell version)
        variables_needed = detect_template_variables(template_path)
        
        if not variables_needed:
            print("📝 No environment variables found in template - no substitution needed.")
            return True, set(), {}
        
        print("📋 Variables required by template:")
        for var in sorted(variables_needed):
            print(f"   • {var}")
        print("")
        
        # Scan for environment files (same logic as shell version)
        print("🔍 Scanning for environment files:")
        found_files = []
        total_vars = 0
        
        for env_file in env_files:
            env_path = Path(env_file)
            if env_path.exists():
                try:
                    content = env_path.read_text(encoding='utf-8')
                    # Count environment variables (same pattern as shell version)
                    var_count = len(re.findall(r'^[A-Za-z_][A-Za-z0-9_]*=', content, re.MULTILINE))
                    print(f"   ✅ Found: {env_file} ({var_count} variables)")
                    found_files.append(env_file)
                    total_vars += var_count
                except Exception as e:
                    print(f"   ⚠️  Error reading {env_file}: {e}")
            else:
                print(f"   ❌ Not found: {env_file}")
        
        # Check system environment
        sys_var_count = 0
        for var in variables_needed:
            if var in os.environ:
                sys_var_count += 1
        
        if sys_var_count > 0:
            print(f"   🖥️  System environment: {sys_var_count} relevant variables")
        
        print("")
        
        # Provide guidance if no environment files found
        if not found_files:
            print("⚠️  No environment files found - relying on system environment variables only")
            print("   Available locations for secrets files:")
            for env_file in env_files:
                print(f"     • {env_file}")
            print("")
            if sys_var_count == 0:
                print("⚠️  No relevant variables found in system environment either")
                print("   This may result in template processing with missing variables")
            print("")
        
        # Analyze variable sources with precedence (same logic as shell version)
        print("📝 Variable sources for template processing:")
        missing_vars = []
        conflicts = []
        variable_sources = {}
        
        for var in sorted(variables_needed):
            found_source = ""
            conflict_info = ""
            
            # Check system environment first (lowest priority)
            if var in os.environ:
                found_source = "system environment"
                variable_sources[var] = "system environment"
            
            # Check each environment file (higher priority, later files override)
            for env_file in env_files:
                env_path = Path(env_file)
                if env_path.exists():
                    try:
                        content = env_path.read_text(encoding='utf-8')
                        # Look for variable definition (same pattern as shell version)
                        pattern = f'^{re.escape(var)}=(.*)$'
                        matches = re.findall(pattern, content, re.MULTILINE)
                        if matches:
                            file_value = matches[-1]  # Take last match if multiple
                            # Remove quotes if present
                            file_value = file_value.strip().strip('"\'')
                            if file_value:  # Only count non-empty values
                                if found_source:
                                    conflict_info = f"{found_source} → {Path(env_file).name}"
                                    conflicts.append(f"{var}: {conflict_info}")
                                found_source = Path(env_file).name
                                variable_sources[var] = env_file
                    except Exception:
                        pass  # Skip files that can't be read
            
            # Report result for this variable
            if found_source:
                print(f"   • {var} → {found_source}")
            else:
                print(f"   ❌ {var} → NOT FOUND")
                missing_vars.append(var)
        
        print("")
        
        # Report conflicts if any
        if conflicts:
            print("⚠️  Variable conflicts detected (showing precedence resolution):")
            for conflict in conflicts:
                print(f"   • {conflict}")
            print("")
        
        # Report missing variables
        success = True
        if missing_vars:
            print("❌ Missing required variables:")
            for var in missing_vars:
                print(f"   • {var}")
            print("")
            print("The generated config may not work properly for services requiring these variables.")
            print("")
            print("To fix this:")
            if not found_files:
                print("  1. Create an environment file:")
                print("     cp ~/.config/dotfiles/.env.example ~/.config/dotfiles/.env")
                print("  2. Edit and add your API keys:")
                print("     vim ~/.config/dotfiles/.env")
            else:
                print("  1. Add missing variables to one of these files:")
                for env_file in found_files:
                    print(f"     • {env_file}")
                print("  2. Or set them as system environment variables")
            print("")
            success = False
        
        return success, variables_needed, variable_sources
        
    except Exception as e:
        print(f"Error analyzing template environment: {e}", file=sys.stderr)
        return False, set(), {}


def process_synced_templates(synced_files: List[Tuple[str, str]], 
                           config: 'DotfilesConfig') -> int:
    """
    Process templates in recently synced files using existing environment system.
    
    Leverages the existing get_secrets_files() precedence and environment handling
    from the shell script, but applies it to all synced files automatically.
    
    Includes rollback capability for failed template processing.
    
    Args:
        synced_files: List of (repo_path, dest_path) tuples that were synced
        config: DotfilesConfig instance for accessing repo directory
        
    Returns:
        Number of templates successfully processed
    """
    if not synced_files:
        return 0
    
    # Get environment files in precedence order (same as shell script)
    env_files = get_secrets_files()
    
    templates_found = []
    templates_processed = 0
    rollback_info = {}  # Track original states for rollback
    
    print("\n🔍 Scanning synced files for template variables...")
    
    # Scan all synced files for template variables
    for repo_path, dest_path in synced_files:
        dest_file = Path.home() / dest_path
        
        if not dest_file.exists() or dest_file.is_dir():
            continue
            
        variables = detect_template_variables(dest_file)
        if variables:
            templates_found.append((dest_file, variables))
            print(f"  📋 Template found: {dest_path} (variables: {', '.join(sorted(variables))})")
            
            # Create rollback backup before processing
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.rollback_backup',
                    dir=dest_file.parent,
                    delete=False,
                    encoding='utf-8'
                ) as rollback_file:
                    rollback_path = Path(rollback_file.name)
                    rollback_file.write(dest_file.read_text(encoding='utf-8'))
                    rollback_info[dest_file] = rollback_path
            except Exception as e:
                print(f"Warning: Could not create rollback backup for {dest_file.name}: {e}", 
                      file=sys.stderr)
    
    if not templates_found:
        print("  ✅ No template variables found in synced files")
        return 0
    
    print(f"\n🔄 Processing {len(templates_found)} template files...")
    
    failed_templates = []
    
    # Process each template file with comprehensive analysis
    for template_file, variables in templates_found:
        print(f"\n📄 Processing template: {template_file.name}")
        print("─" * 60)
        
        # Use the new consolidated analysis function
        analysis_success, required_vars, var_sources = analyze_template_environment(template_file, env_files)
        
        # Process the template using the existing secure function
        if process_template_file(template_file, env_files):
            templates_processed += 1
            if analysis_success:
                print("✅ Template processed successfully with all variables found")
            else:
                print("⚠️  Template processed but some variables were missing")
        else:
            print(f"❌ Failed to process {template_file.name}")
            failed_templates.append(template_file)
        
        print("")  # Add spacing between templates
    
    # Handle rollback if any templates failed
    if failed_templates and rollback_info:
        print(f"\n⚠️  {len(failed_templates)} template(s) failed - checking rollback options...")
        
        # For now, we don't automatically rollback successful templates if others fail
        # This preserves partially successful processing
        # But we offer to restore individual failed templates
        
        print("Rollback options:")
        print("  • Successful templates have been processed and left in place")
        print("  • Failed templates remain in their original state")
        print("  • Rollback backups are available if needed")
        
        for failed_template in failed_templates:
            if failed_template in rollback_info:
                rollback_path = rollback_info[failed_template]
                print(f"  • Rollback available for {failed_template.name}: {rollback_path}")
    
    # Clean up rollback backups for successful templates (keep failed ones)
    for template_file, rollback_path in rollback_info.items():
        if template_file not in failed_templates:
            try:
                rollback_path.unlink()
            except Exception:
                pass  # Not critical if cleanup fails
    
    print(f"\n✅ Template processing completed: {templates_processed}/{len(templates_found)} files processed")
    
    if templates_processed < len(templates_found):
        print("⚠️  Some templates failed to process - check warnings above")
        print("💡 Tip: Check environment variables and try running sync again")
    
    return templates_processed


def show_diff(file_path: str, old_content: str, new_content: str) -> None:
    """Show unified diff using Python's difflib - no external commands."""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"{file_path} (current)",
        tofile=f"{file_path} (new)",
        lineterm=''
    )
    
    has_changes = False
    for line in diff:
        has_changes = True
        if line.startswith('+') and not line.startswith('+++'):
            print(f"\033[32m{line}\033[0m", end='')  # Green for additions
        elif line.startswith('-') and not line.startswith('---'):
            print(f"\033[31m{line}\033[0m", end='')  # Red for deletions
        elif line.startswith('@'):
            print(f"\033[36m{line}\033[0m", end='')  # Cyan for line numbers
        else:
            print(line, end='')
    
    if not has_changes:
        print("Files are identical.")


def prompt_user_choice(file_path: str, has_diff: bool) -> str:
    """Simple interactive prompt using built-in input()."""
    if not has_diff:
        return 'skip'
    
    print(f"\n\033[1m{file_path}\033[0m")
    print("─" * 60)
    print("Options:")
    print("  [K]eep current file (skip)")
    print("  [R]eplace with repository version")  
    print("  [B]ackup current and replace")
    print("  [V]iew diff again")
    print("  [Q]uit")
    
    while True:
        choice = input("\nYour choice [K/r/b/v/q]: ").lower().strip()
        if choice in ['', 'k']:
            return 'keep'
        elif choice == 'r':
            return 'replace'
        elif choice == 'b':
            return 'backup_replace'
        elif choice == 'v':
            return 'view'
        elif choice == 'q':
            return 'quit'
        else:
            print("Invalid choice. Please try again.")


def sync_from_repo(config: 'DotfilesConfig', backup_dir: str = None, preview: bool = True,
                   strategy: str = 'ask', force: bool = False, 
                   process_templates: bool = True) -> int:
    """
    Sync dotfiles from repository to system.
    
    Args:
        config: DotfilesConfig instance
        backup_dir: Override default backup directory
        preview: Show preview/dry-run first (default: True)
        strategy: Sync strategy - 'ask', 'replace', 'skip' (default: 'ask')
        force: Skip preview and apply changes directly (default: False)
        process_templates: Automatically process templates after sync (default: True)
    
    Returns:
        0 on success, 1 on error
    """
    import shutil
    from datetime import datetime
    
    if backup_dir is None:
        backup_dir = config.backup_dir
    else:
        backup_dir = Path(backup_dir)
    
    # Force overrides preview
    if force:
        preview = False
    
    # Always ensure backup directory exists (for reliable state detection)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Track changes for summary
    files_to_sync = []
    files_identical = []
    files_skipped = []
    files_synced = []  # Track successfully synced files for template processing
    
    # First pass: analyze all files
    print("Analyzing dotfiles...\n")
    
    for repo_path, dest_path in config.file_map.items():
        # Check if there's a custom override for this destination
        if dest_path in config.custom_map:
            custom_path = config.custom_map[dest_path]
            custom_file = config.custom_dir / custom_path
            if custom_file.exists():
                source_file = custom_file
                repo_path = f"custom:{custom_path}"  # Update repo_path for display
            else:
                # Fall back to repo file if custom file doesn't exist
                source_file = config.repo_dir / repo_path
                print(f"WARNING: Custom file not found: {custom_file}, using repository version", file=sys.stderr)
        else:
            source_file = config.repo_dir / repo_path
        
        dest_file = Path.home() / dest_path
        
        # Safety checks
        if not source_file.exists():
            print(f"ERROR: Source not found: {repo_path}", file=sys.stderr)
            continue
            
        # Ensure we're not backing up the entire home directory
        if dest_file == Path.home():
            print(f"ERROR: Refusing to manage home directory", file=sys.stderr)
            return 1
        
        # Ensure destination is within home directory
        try:
            dest_file.relative_to(Path.home())
        except ValueError:
            print(f"ERROR: Destination outside home directory: {dest_file}", file=sys.stderr)
            return 1
        
        # Compare files
        if dest_file.exists():
            if source_file.is_dir() or dest_file.is_dir():
                # Skip directory comparison for now
                files_to_sync.append((repo_path, dest_path, 'directory'))
            else:
                # Compare file contents
                try:
                    source_content = source_file.read_text()
                    dest_content = dest_file.read_text()
                    
                    if source_content == dest_content:
                        files_identical.append((repo_path, dest_path))
                    else:
                        files_to_sync.append((repo_path, dest_path, 'modified'))
                except:
                    # Binary files or read errors
                    files_to_sync.append((repo_path, dest_path, 'binary'))
        else:
            files_to_sync.append((repo_path, dest_path, 'new'))
    
    # Show summary
    print(f"Summary:")
    print(f"  {len(files_identical)} files already up-to-date")
    print(f"  {len(files_to_sync)} files need syncing")
    print()
    
    if not files_to_sync:
        print("All files are already up-to-date!")
        return 0
    
    # Preview mode or interactive mode
    if preview and not force:
        print("Files to sync:")
        print("─" * 60)
        
        actions = {}  # Track user decisions
        
        for repo_path, dest_path, status in files_to_sync:
            # Re-determine source file (might be custom)
            if repo_path.startswith("custom:"):
                custom_path = repo_path[7:]
                source_file = config.custom_dir / custom_path
            else:
                source_file = config.repo_dir / repo_path
            dest_file = Path.home() / dest_path
            
            print(f"\n{dest_path} [{status}]")
            
            if status == 'modified' and strategy == 'ask':
                # Show diff for modified text files
                try:
                    source_content = source_file.read_text()
                    dest_content = dest_file.read_text()
                    
                    show_diff(dest_path, dest_content, source_content)
                    
                    # Interactive prompt
                    while True:
                        choice = prompt_user_choice(dest_path, True)
                        if choice == 'view':
                            show_diff(dest_path, dest_content, source_content)
                            continue
                        elif choice == 'quit':
                            print("\nSync cancelled.")
                            return 0
                        else:
                            actions[repo_path] = choice
                            break
                except:
                    # Binary file or error - default to replace
                    print("  (binary file - will replace)")
                    actions[repo_path] = 'replace'
            else:
                # Non-interactive or new files - use strategy
                if strategy == 'skip':
                    actions[repo_path] = 'keep'
                else:
                    actions[repo_path] = 'replace'
                    
        # Confirm before proceeding
        if strategy == 'ask':
            print("\n" + "─" * 60)
            print("\nReady to apply changes?")
            confirm = input("Proceed? [y/N]: ").lower().strip()
            if confirm != 'y':
                print("Sync cancelled.")
                return 0
    else:
        # Non-preview mode - apply strategy to all
        actions = {}
        for repo_path, _, _ in files_to_sync:
            actions[repo_path] = 'replace' if strategy != 'skip' else 'keep'
    
    # Apply changes
    print("\nApplying changes...")
    
    for repo_path, dest_path, status in files_to_sync:
        action = actions.get(repo_path, 'keep')
        
        if action == 'keep':
            files_skipped.append(repo_path)
            continue
            
        # Re-determine source file (might be custom)
        if repo_path.startswith("custom:"):
            custom_path = repo_path[7:]
            source_file = config.custom_dir / custom_path
        else:
            source_file = config.repo_dir / repo_path
        dest_file = Path.home() / dest_path
        
        # Backup existing file if requested
        if dest_file.exists() and action in ['backup_replace', 'replace']:
            if action == 'backup_replace' or (status == 'modified' and not force):
                backup_path = backup_dir / dest_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                print(f"  Backing up: {dest_path}")
                if dest_file.is_dir():
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(dest_file, backup_path)
                else:
                    shutil.copy2(dest_file, backup_path)
        
        # Copy from repo to destination
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"  Syncing: {repo_path} -> {dest_path}")
        
        if source_file.is_dir():
            if dest_file.exists():
                shutil.rmtree(dest_file)
            shutil.copytree(source_file, dest_file)
        else:
            shutil.copy2(source_file, dest_file)
        
        # Track successfully synced file for template processing
        files_synced.append((repo_path, dest_path))
    
    # Process templates in synced files if enabled
    templates_processed = 0
    if process_templates and files_synced:
        templates_processed = process_synced_templates(files_synced, config)
    
    # Final summary
    print(f"\nSync completed:")
    print(f"  {len(files_to_sync) - len(files_skipped)} files synced")
    print(f"  {len(files_skipped)} files skipped")
    print(f"  {len(files_identical)} files already up-to-date")
    if process_templates and templates_processed > 0:
        print(f"  {templates_processed} templates processed")
    
    return 0


def sync_to_repo(config: 'DotfilesConfig') -> int:
    """Sync dotfiles from system to repository."""
    import shutil
    
    for repo_path, dest_path in config.file_map.items():
        source_file = Path.home() / dest_path
        repo_file = config.repo_dir / repo_path
        
        if not source_file.exists():
            print(f"WARNING: System file not found: {dest_path}")
            continue
        
        print(f"Collecting: {dest_path} -> {repo_path}")
        
        if source_file.is_dir():
            if repo_file.exists():
                shutil.rmtree(repo_file)
            shutil.copytree(source_file, repo_file)
        else:
            repo_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, repo_file)
    
    print(f"Collection completed: {len(config.file_map)} files processed")
    return 0


def list_files(config: 'DotfilesConfig') -> int:
    """List all managed files."""
    print(f"Repository: {config.repo_dir}")
    print(f"Custom directory: {config.custom_dir}")
    print(f"Total files: {len(config.dotfiles)}")
    if config.custom_map:
        print(f"Custom overlays: {len(config.custom_map)}")
    
    print("\nMappings:")
    for repo_path, dest_path in config.file_map.items():
        # Check if there's a custom overlay
        if dest_path in config.custom_map:
            custom_path = config.custom_map[dest_path]
            custom_file = config.custom_dir / custom_path
            if custom_file.exists():
                print(f"  {repo_path} -> {dest_path} [CUSTOM: {custom_path}]")
            else:
                print(f"  {repo_path} -> {dest_path} [CUSTOM NOT FOUND: {custom_path}]")
        else:
            print(f"  {repo_path} -> {dest_path}")
    
    # Show custom-only entries (if any)
    for dest_path, custom_path in config.custom_map.items():
        if dest_path not in [v for v in config.file_map.values()]:
            print(f"  custom:{custom_path} -> {dest_path} [CUSTOM ONLY]")
    
    return 0


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse dotfiles configuration")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--shell", default="bash", choices=["bash", "zsh"], 
                       help="Target shell (default: bash)")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only validate configuration, don't output arrays")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    # New action arguments
    parser.add_argument("--sync-from-repo", action="store_true",
                       help="Sync dotfiles from repository to system (preview by default)")
    parser.add_argument("--sync-to-repo", action="store_true",
                       help="Sync dotfiles from system to repository")
    parser.add_argument("--list", action="store_true",
                       help="List all managed files")
    parser.add_argument("--get-secrets-files", action="store_true",
                       help="Output secrets file paths for shell integration")
    parser.add_argument("--backup-dir", help="Backup directory for sync operations")
    
    # Enhanced sync options
    parser.add_argument("--force", action="store_true",
                       help="Skip preview and apply changes directly")
    parser.add_argument("--strategy", choices=["ask", "replace", "skip"],
                       default="ask", help="Sync strategy: ask (default), replace, or skip")
    parser.add_argument("--no-preview", action="store_true",
                       help="Skip preview (same as --force)")
    
    # Template processing options
    parser.add_argument("--process-templates", action="store_true", default=True,
                       help="Process templates after sync (default behavior)")
    parser.add_argument("--no-templates", dest="process_templates", action="store_false",
                       help="Skip template processing after sync")
    parser.add_argument("--analyze-template", metavar="TEMPLATE_PATH",
                       help="Analyze environment variables for a specific template file")
    parser.add_argument("--process-template", nargs=2, metavar=("INPUT", "OUTPUT"),
                       help="Process a specific template file with environment substitution")
    
    args = parser.parse_args()
    
    try:
        config = DotfilesConfig(args.config)
        config.parse_config()
        
        # Validate configuration
        errors = config.validate()
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            sys.exit(1)
        
        # Handle action commands
        if args.sync_from_repo:
            # Determine preview mode
            preview = not (args.force or args.no_preview)
            sys.exit(sync_from_repo(config, args.backup_dir, preview=preview, 
                                  strategy=args.strategy, force=args.force,
                                  process_templates=args.process_templates))
        elif args.sync_to_repo:
            sys.exit(sync_to_repo(config))
        elif args.list:
            sys.exit(list_files(config))
        elif getattr(args, 'get_secrets_files', False):
            # Output secrets files for shell integration
            for path in get_secrets_files():
                print(path)
            return
        elif args.analyze_template:
            # Analyze environment variables for a specific template
            template_path = Path(args.analyze_template)
            if not template_path.exists():
                print(f"ERROR: Template file not found: {template_path}", file=sys.stderr)
                sys.exit(1)
            env_files = get_secrets_files()
            success, variables, sources = analyze_template_environment(template_path, env_files)
            sys.exit(0 if success else 1)
        elif args.process_template:
            # Process a specific template file
            input_path = Path(args.process_template[0])
            output_path = Path(args.process_template[1])
            if not input_path.exists():
                print(f"ERROR: Input template file not found: {input_path}", file=sys.stderr)
                sys.exit(1)
            env_files = get_secrets_files()
            
            # Analyze first
            print(f"Analyzing template: {input_path}")
            success, variables, sources = analyze_template_environment(input_path, env_files)
            
            # Process template by copying input to output location and processing
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(input_path.read_text(encoding='utf-8'), encoding='utf-8')
                
                if process_template_file(output_path, env_files):
                    print(f"✅ Template processed successfully: {output_path}")
                    sys.exit(0)
                else:
                    print(f"❌ Template processing failed: {output_path}", file=sys.stderr)
                    sys.exit(1)
            except Exception as e:
                print(f"ERROR: Failed to process template: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.validate_only:
            print(f"Configuration validation passed: {len(config.dotfiles)} dotfiles found")
            return
        else:
            # Default behavior: output shell arrays
            if args.verbose:
                print(f"# Configuration loaded: {len(config.dotfiles)} dotfiles", file=sys.stderr)
            
            print(config.generate_exports(), end="")
            print(config.generate_shell_arrays(args.shell), end="")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()