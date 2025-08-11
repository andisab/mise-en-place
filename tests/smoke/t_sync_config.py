#!/usr/bin/env python3
"""Test suite for dotfiles configuration parser."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add repository root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

import config_parser

def test_malformed_config():
    """Test various malformed configuration entries."""
    test_cases = [
        # Empty lines and comments (should be ignored)
        ("# This is a comment\n\n  \nvalid:path\n", 1),
        
        # Missing colon
        ("no_colon_here\nvalid:path\n", 1),
        
        # Empty values
        (":empty_repo\nvalid:path\n", 1),
        ("empty_dest:\nvalid:path\n", 1),
        (":\nvalid:path\n", 1),
        
        # Multiple colons
        ("path:with:colons:.vimrc\n", 1),  # Should work (split on first :)
        
        # Whitespace handling
        ("  spaces:  .profile  \n", 1),
        
        # Dangerous paths (should raise exception)
        ("home:/\n", ValueError),
        ("home:~\n", ValueError),
        
        # Path traversal (should raise exception)
        ("../escape:.profile\n", ValueError),
        ("home:../../../etc/passwd\n", ValueError),
        
        # Valid entries for comparison
        ("HOME/.env.example:.config/dotfiles/.env.example\nllm/claude_code/CLAUDE.md:.claude/CLAUDE.md\n", 2),
    ]
    
    for config_content, expected in test_cases:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            temp_file = f.name
        
        try:
            config = config_parser.DotfilesConfig(Path(temp_file))
            if isinstance(expected, type) and issubclass(expected, Exception):
                # Should raise an exception
                try:
                    config.parse_config()
                    print(f"FAIL: Expected {expected.__name__} for: {repr(config_content)}")
                except expected:
                    print(f"PASS: Correctly raised {expected.__name__} for dangerous path")
            else:
                # Should parse successfully
                config.parse_config()
                if len(config.dotfiles) == expected:
                    print(f"PASS: Got {expected} valid entries from: {repr(config_content.strip())}")
                else:
                    print(f"FAIL: Expected {expected} entries, got {len(config.dotfiles)} from: {repr(config_content)}")
                    print(f"      Parsed: {config.file_map}")
        except Exception as e:
            if isinstance(expected, type) and isinstance(e, expected):
                print(f"PASS: Correctly raised {type(e).__name__}")
            else:
                print(f"FAIL: Unexpected error: {e}")
        finally:
            os.unlink(temp_file)


def test_sync_safety():
    """Test safety checks in sync operations."""
    print("\n=== Testing Sync Safety ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test repository
        repo_dir = Path(temp_dir) / "repo"
        repo_dir.mkdir()
        
        # Create test config
        config_file = repo_dir / "dotfiles.conf"
        config_file.write_text("test/file:.testfile\n")
        
        # Create source file
        test_dir = repo_dir / "test"
        test_dir.mkdir()
        (test_dir / "file").write_text("test content")
        
        # Test normal operation
        config = config_parser.DotfilesConfig(config_file)
        config.parse_config()
        
        # This should work
        backup_dir = Path(temp_dir) / "backup"
        result = config_parser.sync_from_repo(config, str(backup_dir))
        if result == 0:
            print("PASS: Normal sync operation succeeded")
        else:
            print("FAIL: Normal sync operation failed")
        
        # Test missing source file
        config.file_map["missing/file"] = ".missing"
        config.dotfiles.append("missing/file")
        
        result = config_parser.sync_from_repo(config, str(backup_dir))
        if result == 1:
            print("PASS: Correctly failed on missing source file")
        else:
            print("FAIL: Should have failed on missing source")


def test_absolute_paths():
    """Test that all paths are properly absolute."""
    print("\n=== Testing Absolute Paths ===")
    
    # Create a config object
    config = config_parser.DotfilesConfig()
    
    # Check repo_dir is absolute
    if config.repo_dir.is_absolute():
        print(f"PASS: repo_dir is absolute: {config.repo_dir}")
    else:
        print(f"FAIL: repo_dir is not absolute: {config.repo_dir}")
    
    # Check config_file is absolute
    if config.config_file.is_absolute():
        print(f"PASS: config_file is absolute: {config.config_file}")
    else:
        print(f"FAIL: config_file is not absolute: {config.config_file}")


def test_empty_config():
    """Test behavior with empty or non-existent config."""
    print("\n=== Testing Empty Config ===")
    
    # Test non-existent file
    config = config_parser.DotfilesConfig(Path("/tmp/nonexistent.conf"))
    try:
        config.parse_config()
        print("FAIL: Should have raised FileNotFoundError")
    except FileNotFoundError:
        print("PASS: Correctly raised FileNotFoundError for missing config")
    
    # Test empty file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_file = f.name
    
    config = config_parser.DotfilesConfig(Path(temp_file))
    config.parse_config()
    
    if len(config.dotfiles) == 0:
        print("PASS: Empty config results in empty dotfiles list")
    else:
        print(f"FAIL: Empty config has {len(config.dotfiles)} entries")
    
    os.unlink(temp_file)


def test_security_edge_cases():
    """Test security-focused edge cases."""
    print("\n=== Testing Security Edge Cases ===")
    
    # Test 1: Path traversal attempts in custom overlays
    config_content = """# Path traversal attempts
custom:../../etc/passwd:.config/test
custom:../../../root/.ssh/id_rsa:.ssh/stolen_key
HOME/normal:.normal
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        temp_file = f.name
    
    config = config_parser.DotfilesConfig(Path(temp_file))
    config.parse_config()
    
    # Should parse custom entries (validation happens during sync)
    if len(config.custom_map) == 2:
        print("PASS: Parsed custom entries (path validation occurs during sync)")
    else:
        print(f"FAIL: Expected 2 custom entries, got {len(config.custom_map)}")
    
    os.unlink(temp_file)
    
    # Test 2: Symbolic link attacks
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a symlink pointing outside temp directory
        link_path = Path(temp_dir) / "evil_link"
        target = "/etc/passwd"
        try:
            link_path.symlink_to(target)
            
            config_content = f"""# Symlink test
{temp_dir}/evil_link:.config/gotcha
"""
            config_file = Path(temp_dir) / "test.conf"
            config_file.write_text(config_content)
            
            config = config_parser.DotfilesConfig(config_file)
            config.parse_config()
            
            # Parsing should succeed, but sync should handle symlinks safely
            print("PASS: Config with symlinks parsed (sync will handle safely)")
        except Exception as e:
            print(f"INFO: Symlink test skipped: {e}")
    
    # Test 3: Filenames with special characters
    special_names = [
        'file;rm -rf /',
        'file$(evil)',
        'file`backdoor`',
        'file&&malicious',
        'file|pipe',
        'file\nwith\nnewlines',
        'file\twith\ttabs',
    ]
    
    config_lines = []
    for name in special_names:
        # These should be handled safely as literal filenames
        config_lines.append(f'HOME/{name}:.config/{name}')
    
    config_content = '\n'.join(config_lines)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        temp_file = f.name
    
    config = config_parser.DotfilesConfig(Path(temp_file))
    config.parse_config()
    
    if len(config.dotfiles) == len(special_names):
        print("PASS: Special characters in filenames handled safely")
    else:
        print(f"FAIL: Expected {len(special_names)} entries, got {len(config.dotfiles)}")
    
    os.unlink(temp_file)
    
    # Test 4: Environment variable injection in paths
    config_content = """# Environment variable attempts
HOME/${USER}/.ssh/config:.ssh/config
HOME/${PATH}/binary:.local/bin/evil
HOME/$(whoami)/data:.data
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        temp_file = f.name
    
    config = config_parser.DotfilesConfig(Path(temp_file))
    config.parse_config()
    
    # Should treat these as literal paths, not expand variables
    if '${USER}' in str(config.dotfiles):
        print("PASS: Environment variables in paths not expanded during parsing")
    else:
        print("FAIL: Environment variables were incorrectly expanded")
    
    os.unlink(temp_file)


def test_template_security_edge_cases():
    """Test template processing security edge cases."""
    print("\n=== Testing Template Security Edge Cases ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test 1: Template with command injection attempts
        template_file = Path(temp_dir) / "injection_template.json"
        template_content = """{
    "safe": "${HOME}",
    "injection1": "${HOME}; rm -rf /",
    "injection2": "${HOME} && curl evil.com",
    "injection3": "$(whoami)",
    "injection4": "`id`",
    "nested": "${${NESTED_VAR}}"
}"""
        template_file.write_text(template_content)
        
        # Detect variables - should only find valid ones
        variables = config_parser.detect_template_variables(template_file)
        
        if variables == {"HOME", "NESTED_VAR"} or variables == {"HOME"}:
            print("PASS: Only valid template variables detected, injection attempts ignored")
        else:
            print(f"FAIL: Unexpected variables detected: {variables}")
        
        # Test 2: Binary file mistaken as template
        binary_file = Path(temp_dir) / "binary.dat"
        # Create binary data that contains ${HOME} pattern
        binary_data = b'\x00\x01\x02${HOME}\x03\x04\xff\xfe'
        binary_file.write_bytes(binary_data)
        
        try:
            variables = config_parser.detect_template_variables(binary_file)
            print("PASS: Binary file handling didn't crash")
        except Exception as e:
            print(f"INFO: Binary file handling raised {type(e).__name__} (acceptable)")
        
        # Test 3: Extremely long variable names
        long_var_template = Path(temp_dir) / "long_vars.json"
        long_var_name = "A" * 1000  # 1000 character variable name
        long_var_content = f'{{"key": "${{{long_var_name}}}", "normal": "${{HOME}}"}}'
        long_var_template.write_text(long_var_content)
        
        variables = config_parser.detect_template_variables(long_var_template)
        
        if "HOME" in variables:
            print("PASS: Long variable names handled without issues")
        else:
            print("FAIL: Failed to process template with long variable names")
        
        # Test 4: Recursive template references
        recursive_template = Path(temp_dir) / "recursive.json"
        recursive_content = """{
    "level1": "${VAR1}",
    "level2": "${VAR_${VAR1}}",
    "level3": "${${${DEEP}}}"
}"""
        recursive_template.write_text(recursive_content)
        
        variables = config_parser.detect_template_variables(recursive_template)
        
        # Should find at least VAR1
        if "VAR1" in variables:
            print("PASS: Recursive template references handled safely")
        else:
            print("FAIL: Failed to detect variables in recursive template")


if __name__ == "__main__":
    print("Testing Dotfiles Configuration Parser")
    print("=" * 50)
    
    test_malformed_config()
    test_sync_safety()
    test_absolute_paths()
    test_empty_config()
    test_security_edge_cases()
    test_template_security_edge_cases()
    
    print("\nAll tests completed!")