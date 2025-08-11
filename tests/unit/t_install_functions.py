#!/usr/bin/env python3
"""
Test suite for install.sh shell functions
Tests the shell functions, particularly quick_install and process_claude_basic_config
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import json

class TestInstallFunctions(unittest.TestCase):
    """Test the shell functions in install.sh"""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        
        # Set test HOME
        os.environ['HOME'] = self.test_home
        
        # Path to the actual install.sh
        self.install_sh = Path(__file__).parent.parent.parent / "install.sh"
        
    def tearDown(self):
        """Clean up test environment."""
        # Restore original HOME
        if self.original_home:
            os.environ['HOME'] = self.original_home
        
        # Clean up temp directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_home)
        
    def run_shell_function(self, function_name, setup_commands=""):
        """Helper to run a shell function from install.sh"""
        script = f"""
        #!/bin/bash
        export HOME="{self.test_home}"
        cd "{Path(__file__).parent.parent.parent}"
        {setup_commands}
        source ./install.sh > /dev/null 2>&1
        {function_name}
        """
        
        result = subprocess.run(
            ['bash', '-c', script],
            capture_output=True,
            text=True
        )
        return result
        
    def test_process_claude_basic_config(self):
        """Test process_claude_basic_config function"""
        # Create Claude config directory
        claude_dir = Path(self.test_home) / "Library" / "Application Support" / "Claude"
        claude_dir.mkdir(parents=True)
        
        # Create config with ${HOME} placeholders
        config_path = claude_dir / "claude_desktop_config.json"
        config_content = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["${HOME}/Projects", "${HOME}/Documents"]
                }
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_content, f)
        
        # Run the function
        result = self.run_shell_function("process_claude_basic_config")
        
        # Check if successful
        self.assertEqual(result.returncode, 0, f"Function failed: {result.stderr}")
        
        # Read the processed config
        with open(config_path, 'r') as f:
            processed_config = json.load(f)
        
        # Check if ${HOME} was replaced
        args = processed_config["mcpServers"]["filesystem"]["args"]
        self.assertEqual(args[0], f"{self.test_home}/Projects")
        self.assertEqual(args[1], f"{self.test_home}/Documents")
        self.assertNotIn("${HOME}", str(processed_config))
        
    def test_process_claude_basic_config_no_file(self):
        """Test process_claude_basic_config when config doesn't exist"""
        # Ensure no config exists
        claude_dir = Path(self.test_home) / "Library" / "Application Support" / "Claude"
        if claude_dir.exists():
            shutil.rmtree(claude_dir)
        
        # Run the function - should succeed even without file
        result = self.run_shell_function("process_claude_basic_config")
        self.assertEqual(result.returncode, 0)
        
    def test_process_claude_basic_config_already_processed(self):
        """Test process_claude_basic_config with already processed config"""
        # Create Claude config directory
        claude_dir = Path(self.test_home) / "Library" / "Application Support" / "Claude"
        claude_dir.mkdir(parents=True)
        
        # Create config WITHOUT ${HOME} placeholders
        config_path = claude_dir / "claude_desktop_config.json"
        config_content = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": [f"{self.test_home}/Projects", f"{self.test_home}/Documents"]
                }
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_content, f)
        
        # Save original content
        original_content = config_path.read_text()
        
        # Run the function
        result = self.run_shell_function("process_claude_basic_config")
        self.assertEqual(result.returncode, 0)
        
        # Content should be unchanged
        new_content = config_path.read_text()
        self.assertEqual(original_content, new_content)
        
    def test_shell_integration_install(self):
        """Test install_shell_integration function"""
        # Create a .profile file
        profile_path = Path(self.test_home) / ".profile"
        profile_path.write_text("# Existing profile content\n")
        
        # Run install_shell_integration
        result = self.run_shell_function("install_shell_integration")
        self.assertEqual(result.returncode, 0)
        
        # Check if integration was added
        profile_content = profile_path.read_text()
        self.assertIn("mise-en-place/install.sh", profile_content)
        self.assertIn("mise-en-place integration", profile_content)
        
    def test_shell_integration_already_installed(self):
        """Test install_shell_integration when already installed"""
        # Create a .profile file with integration already present
        profile_path = Path(self.test_home) / ".profile"
        profile_path.write_text("""# Existing content
# mise-en-place integration
if [[ -f "/some/path/mise-en-place/install.sh" ]]; then
    source "/some/path/mise-en-place/install.sh"
fi
""")
        
        # Run install_shell_integration
        result = self.run_shell_function("install_shell_integration")
        self.assertEqual(result.returncode, 0)
        
        # Should detect it's already installed
        self.assertIn("already installed", result.stdout)
        
    def test_shell_integration_remove(self):
        """Test remove_shell_integration function"""
        # Create a .profile file with integration
        profile_path = Path(self.test_home) / ".profile"
        profile_path.write_text("""# Existing content

# mise-en-place integration
if [[ -f "/some/path/mise-en-place/install.sh" ]]; then
    source "/some/path/mise-en-place/install.sh"
fi

# More content after
""")
        
        # Run remove_shell_integration
        result = self.run_shell_function("remove_shell_integration")
        self.assertEqual(result.returncode, 0)
        
        # Check if integration was removed
        profile_content = profile_path.read_text()
        self.assertNotIn("mise-en-place/install.sh", profile_content)
        self.assertNotIn("mise-en-place integration", profile_content)
        # But other content should remain
        self.assertIn("# Existing content", profile_content)
        self.assertIn("# More content after", profile_content)
        
    def test_commands_available(self):
        """Test that all expected commands are available after sourcing"""
        # Get list of functions
        script = """
        source ./install.sh > /dev/null 2>&1
        # List all functions that don't start with underscore
        declare -F | grep -v " _" | cut -d' ' -f3
        """
        
        result = subprocess.run(
            ['bash', '-c', f'cd "{Path(__file__).parent.parent.parent}" && {script}'],
            capture_output=True,
            text=True,
            env={**os.environ, 'HOME': self.test_home}
        )
        
        functions = result.stdout.strip().split('\n')
        
        # Check expected functions are present
        expected_functions = [
            'test_config',
            'validate_config',
            'sync_dotfiles_from_git',
            'collect_dotfiles_to_git',
            'process_claude_basic_config',
            'process_env_templates',
            'install_shell_integration',
            'remove_shell_integration',
            'quick_install'
        ]
        
        for func in expected_functions:
            self.assertIn(func, functions, f"Function {func} not found")
            
    def test_validate_config_success(self):
        """Test validate_config with valid configuration"""
        # This test assumes config_parser.py validates successfully
        # In real usage, we'd need a valid dotfiles.conf
        result = self.run_shell_function("validate_config")
        
        # The function should at least run without bash errors
        # (actual validation depends on config_parser.py)
        self.assertNotIn("syntax error", result.stderr)
        self.assertNotIn("command not found", result.stderr)
        
    def test_quick_install_components(self):
        """Test that quick_install calls the right functions"""
        # Create a mock environment with necessary files
        # Create .profile for shell integration
        profile_path = Path(self.test_home) / ".profile"
        profile_path.write_text("# Test profile\n")
        
        # Create Claude config directory
        claude_dir = Path(self.test_home) / "Library" / "Application Support" / "Claude"
        claude_dir.mkdir(parents=True)
        
        # We can't easily test the full quick_install interactively,
        # but we can verify its components work
        components_script = """
        source ./install.sh > /dev/null 2>&1
        
        # Test each component that quick_install uses
        echo "Testing validate_config..."
        if validate_config > /dev/null 2>&1; then
            echo "validate_config: OK"
        else
            echo "validate_config: FAILED"
        fi
        
        echo "Testing process_claude_basic_config..."
        if process_claude_basic_config > /dev/null 2>&1; then
            echo "process_claude_basic_config: OK"
        else
            echo "process_claude_basic_config: FAILED"
        fi
        
        echo "Testing install_shell_integration..."
        if install_shell_integration > /dev/null 2>&1; then
            echo "install_shell_integration: OK"
        else
            echo "install_shell_integration: FAILED"
        fi
        """
        
        result = subprocess.run(
            ['bash', '-c', f'cd "{Path(__file__).parent.parent.parent}" && {components_script}'],
            capture_output=True,
            text=True,
            env={**os.environ, 'HOME': self.test_home}
        )
        
        # All components should work
        self.assertIn("validate_config: OK", result.stdout)
        self.assertIn("process_claude_basic_config: OK", result.stdout)
        self.assertIn("install_shell_integration: OK", result.stdout)


class TestClaudeConfigProcessing(unittest.TestCase):
    """Specific tests for Claude Desktop config processing"""
    
    def test_home_variable_expansion_complex(self):
        """Test expansion of ${HOME} in various contexts"""
        test_cases = [
            # Simple case
            ('{"path": "${HOME}/test"}', f'{{"path": "{os.environ["HOME"]}/test"}}'),
            
            # Multiple occurrences
            ('{"a": "${HOME}/a", "b": "${HOME}/b"}', 
             f'{{"a": "{os.environ["HOME"]}/a", "b": "{os.environ["HOME"]}/b"}}'),
            
            # Nested in arrays
            ('{"args": ["${HOME}/Projects", "${HOME}/Documents"]}',
             f'{{"args": ["{os.environ["HOME"]}/Projects", "{os.environ["HOME"]}/Documents"]}}'),
        ]
        
        for input_str, expected in test_cases:
            # Use sed to process like the shell function does
            result = subprocess.run(
                ['sed', f's|${{HOME}}|{os.environ["HOME"]}|g'],
                input=input_str,
                capture_output=True,
                text=True
            )
            self.assertEqual(result.stdout, expected)


if __name__ == '__main__':
    unittest.main()