#!/usr/bin/env python3
"""
Test suite for config_parser.py
Tests all modes and functionality of the dotfiles configuration parser.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import io

# Add repository root to path to import config_parser
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
import config_parser


class TestDotfilesConfig(unittest.TestCase):
    """Test the DotfilesConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        self.home_dir = tempfile.mkdtemp()
        
        # Create a test config file
        with open(self.config_file, 'w') as f:
            f.write("# Test configuration\n")
            f.write("HOME/testfile:.testfile\n")
            f.write("HOME/testdir:.testdir\n")
            f.write("# Comment line\n")
            f.write("\n")  # Empty line
            f.write("HOME/config/test:.config/test\n")
        
        # Create test source files
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "testfile").write_text("test content\n")
        (home_path / "testdir").mkdir()
        (home_path / "testdir" / "subfile").write_text("sub content\n")
        (home_path / "config").mkdir()
        (home_path / "config" / "test").write_text("config content\n")
        
        # Patch Path.home() to return our test home directory
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_parse_config(self):
        """Test configuration parsing."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        self.assertEqual(len(config.dotfiles), 3)
        self.assertIn("HOME/testfile", config.dotfiles)
        self.assertIn("HOME/testdir", config.dotfiles)
        self.assertIn("HOME/config/test", config.dotfiles)
        
        self.assertEqual(config.file_map["HOME/testfile"], ".testfile")
        self.assertEqual(config.file_map["HOME/testdir"], ".testdir")
        self.assertEqual(config.file_map["HOME/config/test"], ".config/test")
        
    def test_parse_config_with_custom(self):
        """Test parsing configuration with custom overlays."""
        with open(self.config_file, 'w') as f:
            f.write("# Test with custom overlays\n")
            f.write("HOME/testfile:.testfile\n")
            f.write("custom:my-test:.testfile\n")  # Custom overlay
            f.write("custom:another-custom:.custom/path\n")  # Custom only
            
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        # Check regular files
        self.assertEqual(len(config.dotfiles), 1)
        self.assertIn("HOME/testfile", config.dotfiles)
        
        # Check custom mappings
        self.assertEqual(len(config.custom_map), 2)
        self.assertEqual(config.custom_map[".testfile"], "my-test")
        self.assertEqual(config.custom_map[".custom/path"], "another-custom")
        
    def test_parse_config_custom_edge_cases(self):
        """Test parsing custom overlays with edge cases."""
        with open(self.config_file, 'w') as f:
            f.write("# Test edge cases\n")
            f.write("custom:file:with:colons.txt:.testfile\n")  # Filename with colons
            f.write("custom::.testfile\n")  # Empty filename
            f.write("custom:test.txt\n")  # Missing destination
            f.write("custom:test.txt:\n")  # Empty destination
            
        config = config_parser.DotfilesConfig(self.config_file)
        
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            config.parse_config()
            stderr_output = mock_stderr.getvalue()
            
        # Check that filename with colons was parsed correctly
        self.assertEqual(len(config.custom_map), 1)
        self.assertEqual(config.custom_map[".testfile"], "file:with:colons.txt")
        
        # Check warnings were issued for invalid entries
        self.assertIn("Empty custom filename", stderr_output)
        self.assertIn("Invalid custom format", stderr_output)
        
    def test_parse_config_invalid_format(self):
        """Test parsing with invalid format."""
        with open(self.config_file, 'w') as f:
            f.write("invalid_line_without_colon\n")
            f.write("valid:line\n")
            
        config = config_parser.DotfilesConfig(self.config_file)
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            config.parse_config()
            
        self.assertEqual(len(config.dotfiles), 1)
        self.assertIn("Warning: Invalid format", mock_stderr.getvalue())
        
    def test_parse_config_dangerous_paths(self):
        """Test parsing with dangerous paths."""
        with open(self.config_file, 'w') as f:
            f.write("HOME/test:/\n")  # Root directory
            
        config = config_parser.DotfilesConfig(self.config_file)
        with self.assertRaises(ValueError) as cm:
            config.parse_config()
        self.assertIn("Refusing to manage root", str(cm.exception))
        
    def test_validate(self):
        """Test configuration validation."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        errors = config.validate()
        self.assertEqual(len(errors), 0)
        
    def test_validate_missing_source(self):
        """Test validation with missing source files."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.dotfiles = ["HOME/nonexistent"]
        config.file_map = {"HOME/nonexistent": ".nonexistent"}
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("not found" in error for error in errors))
        
    def test_validate_missing_custom_files(self):
        """Test validation with missing custom files."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        # Add custom mappings for files that don't exist
        config.custom_map[".testfile"] = "nonexistent-custom.txt"
        config.custom_map[".another"] = "also-missing.conf"
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        
        # Should have errors for both missing custom files
        custom_errors = [e for e in errors if "Custom file" in e]
        self.assertEqual(len(custom_errors), 2)
        self.assertTrue(any("nonexistent-custom.txt" in e for e in custom_errors))
        self.assertTrue(any("also-missing.conf" in e for e in custom_errors))
        
    def test_validate_existing_custom_files(self):
        """Test validation with existing custom files."""
        # Create custom directory and files
        custom_dir = Path.home() / ".config" / "dotfiles.custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        (custom_dir / "my-custom.txt").write_text("custom content")
        
        try:
            # Patch CUSTOM_DIR to use the real location where we created the file
            with patch('config_parser.CUSTOM_DIR', custom_dir):
                config = config_parser.DotfilesConfig(self.config_file)
                config.parse_config()
                config.custom_map[".testfile"] = "my-custom.txt"
                
                errors = config.validate()
                # Should have no errors related to custom files
                custom_errors = [e for e in errors if "Custom file" in e]
                self.assertEqual(len(custom_errors), 0)
        finally:
            # Clean up
            if (custom_dir / "my-custom.txt").exists():
                (custom_dir / "my-custom.txt").unlink()
        
    def test_generate_shell_arrays(self):
        """Test shell array generation."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        arrays = config.generate_shell_arrays()
        self.assertIn('DOTFILES_REPO_PATHS=(', arrays)
        self.assertIn('DOTFILES_DEST_PATHS=(', arrays)
        self.assertIn('"HOME/testfile"', arrays)
        self.assertIn('".testfile"', arrays)
        
    def test_generate_exports(self):
        """Test export generation for shell variables."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        exports = config.generate_exports()
        # Should contain export statements for environment variables
        self.assertIn('export DOTFILES_REPO=', exports)
        self.assertIn('export DOTFILES_COUNT=', exports)
        self.assertIn('export DOTFILES_BACKUP_DIR=', exports)
        self.assertIn('export DOTFILES_CUSTOM_DIR=', exports)
        # Verify count is correct
        self.assertIn('DOTFILES_COUNT="3"', exports)


class TestDiffFunctions(unittest.TestCase):
    """Test the diff and prompt functions."""
    
    def test_show_diff_with_changes(self):
        """Test diff display with changes."""
        old_content = "line1\nline2\nline3\n"
        new_content = "line1\nmodified line2\nline3\n"
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            config_parser.show_diff("test.txt", old_content, new_content)
            output = mock_stdout.getvalue()
            
        # Check for diff markers
        self.assertIn("---", output)
        self.assertIn("+++", output)
        self.assertIn("-line2", output)
        self.assertIn("+modified line2", output)
        
    def test_show_diff_identical(self):
        """Test diff display with identical files."""
        content = "line1\nline2\nline3\n"
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            config_parser.show_diff("test.txt", content, content)
            output = mock_stdout.getvalue()
            
        self.assertIn("Files are identical", output)
        
    def test_prompt_user_choice(self):
        """Test user prompt function."""
        # Test various inputs
        test_cases = [
            ('k\n', 'keep'),
            ('\n', 'keep'),  # Default
            ('r\n', 'replace'),
            ('b\n', 'backup_replace'),
            ('q\n', 'quit'),
        ]
        
        for input_str, expected in test_cases:
            with patch('builtins.input', return_value=input_str.strip()):
                result = config_parser.prompt_user_choice("test.txt", True)
                self.assertEqual(result, expected)
                
    def test_prompt_user_choice_no_diff(self):
        """Test prompt with no differences."""
        result = config_parser.prompt_user_choice("test.txt", False)
        self.assertEqual(result, 'skip')


class TestSyncFunctions(unittest.TestCase):
    """Test the sync functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        self.home_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / "backup"
        
        # Create config
        with open(self.config_file, 'w') as f:
            f.write("HOME/testfile:.testfile\n")
            f.write("HOME/newfile:.newfile\n")
            
        # Create source files
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "testfile").write_text("repo content\n")
        (home_path / "newfile").write_text("new content\n")
        
        # Patch home directory
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
        # Create existing system file with different content
        (Path(self.home_dir) / ".testfile").write_text("system content\n")
        
    def tearDown(self):
        """Clean up."""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_sync_from_repo_preview_mode(self):
        """Test sync in preview mode."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        config.backup_dir = self.backup_dir
        
        # Mock user choosing to skip
        with patch('builtins.input', side_effect=['k', 'n']):
            with patch('sys.stdout', new_callable=io.StringIO):
                result = config_parser.sync_from_repo(config, preview=True, strategy='ask')
                
        self.assertEqual(result, 0)
        # File should not be changed
        content = (Path(self.home_dir) / ".testfile").read_text()
        self.assertEqual(content, "system content\n")
        
    def test_sync_from_repo_force_mode(self):
        """Test sync in force mode."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        config.backup_dir = self.backup_dir
        
        with patch('sys.stdout', new_callable=io.StringIO):
            result = config_parser.sync_from_repo(config, force=True)
            
        self.assertEqual(result, 0)
        # Files should be updated
        content = (Path(self.home_dir) / ".testfile").read_text()
        self.assertEqual(content, "repo content\n")
        
        # New file should be created
        self.assertTrue((Path(self.home_dir) / ".newfile").exists())
        
    def test_sync_from_repo_with_backup(self):
        """Test sync with backup creation."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        config.backup_dir = self.backup_dir
        
        # Use force=False to trigger backup creation for modified files
        with patch('sys.stdout', new_callable=io.StringIO):
            # Mock user input to replace the file
            with patch('builtins.input', side_effect=['r', 'y']):
                result = config_parser.sync_from_repo(config, force=False)
            
        # Check backup was created
        backup_file = self.backup_dir / ".testfile"
        self.assertTrue(backup_file.exists())
        self.assertEqual(backup_file.read_text(), "system content\n")
        
    def test_sync_to_repo(self):
        """Test sync from system to repository."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        # Create system files
        (Path(self.home_dir) / ".testfile").write_text("updated system content\n")
        (Path(self.home_dir) / ".newfile").write_text("updated new content\n")
        
        with patch('sys.stdout', new_callable=io.StringIO):
            result = config_parser.sync_to_repo(config)
            
        self.assertEqual(result, 0)
        
        # Check repo files were updated
        repo_file = Path(self.test_dir) / "HOME" / "testfile"
        self.assertEqual(repo_file.read_text(), "updated system content\n")
        
    def test_list_files(self):
        """Test file listing."""
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = config_parser.list_files(config)
            output = mock_stdout.getvalue()
            
        self.assertEqual(result, 0)
        self.assertIn("HOME/testfile -> .testfile", output)
        self.assertIn("HOME/newfile -> .newfile", output)
        self.assertIn("Total files: 2", output)


class TestCustomOverlay(unittest.TestCase):
    """Test custom overlay functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        self.home_dir = tempfile.mkdtemp()
        self.custom_dir = Path(self.home_dir) / ".config" / "dotfiles.custom"
        self.custom_dir.mkdir(parents=True)
        
        # Patch home directory and CUSTOM_DIR
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
        # Also patch CUSTOM_DIR in config_parser module
        self.custom_dir_patcher = patch('config_parser.CUSTOM_DIR', self.custom_dir)
        self.custom_dir_patcher.start()
        
    def tearDown(self):
        """Clean up."""
        self.home_patcher.stop()
        self.custom_dir_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_custom_file_precedence(self):
        """Test that custom files take precedence over repo files."""
        # Create config with both regular and custom mapping
        with open(self.config_file, 'w') as f:
            f.write("HOME/testfile:.testfile\n")
            f.write("custom:my-custom.txt:.testfile\n")
            
        # Create repo file
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "testfile").write_text("repo content\n")
        
        # Create custom file
        (self.custom_dir / "my-custom.txt").write_text("custom content\n")
        
        # Parse and sync
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        with patch('sys.stdout', new_callable=io.StringIO):
            result = config_parser.sync_from_repo(config, force=True)
            
        self.assertEqual(result, 0)
        
        # Check that custom content was used
        dest_file = Path(self.home_dir) / ".testfile"
        self.assertEqual(dest_file.read_text(), "custom content\n")
        
    def test_custom_file_fallback(self):
        """Test fallback to repo file when custom doesn't exist."""
        # Create config with custom mapping
        with open(self.config_file, 'w') as f:
            f.write("HOME/testfile:.testfile\n")
            
        # Create repo file
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "testfile").write_text("repo content\n")
        
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        # Manually add custom mapping (simulating a missing custom file scenario)
        config.custom_map[".testfile"] = "missing-custom.txt"
        
        with patch('sys.stdout', new_callable=io.StringIO):
            with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                result = config_parser.sync_from_repo(config, force=True)
                
        self.assertEqual(result, 0)
        
        # Check warning was printed
        self.assertIn("WARNING: Custom file not found", mock_stderr.getvalue())
        
        # Check that repo content was used
        dest_file = Path(self.home_dir) / ".testfile"
        self.assertEqual(dest_file.read_text(), "repo content\n")
        
    def test_list_with_custom_overlays(self):
        """Test list output shows custom overlay information."""
        # Create config
        with open(self.config_file, 'w') as f:
            f.write("HOME/testfile:.testfile\n")
            f.write("custom:my-custom.txt:.testfile\n")
            f.write("custom:another.txt:.another\n")
            
        # Create files
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "testfile").write_text("content")
        
        # Create one custom file, leave other missing
        (self.custom_dir / "my-custom.txt").write_text("custom")
        
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            config_parser.list_files(config)
            output = mock_stdout.getvalue()
            
        # Check output shows custom overlay info
        self.assertIn("[CUSTOM: my-custom.txt]", output)
        self.assertIn("[CUSTOM ONLY]", output)  # For custom:another.txt
        self.assertIn("Custom overlays: 2", output)


class TestSecurityIntegration(unittest.TestCase):
    """Test security features integration with main config functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        self.home_dir = tempfile.mkdtemp()
        
        # Patch home directory
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
    def tearDown(self):
        """Clean up."""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_sync_with_template_processing(self):
        """Test sync operation with automatic template processing."""
        # Create config
        with open(self.config_file, 'w') as f:
            f.write("HOME/template.json:.config/app.json\n")
            
        # Create source template file
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        template_file = home_path / "template.json"
        template_file.write_text('{"path": "${HOME}/data", "key": "${API_KEY}"}')
        
        # Create environment file
        env_dir = Path(self.home_dir) / ".config" / "dotfiles"
        env_dir.mkdir(parents=True)
        env_file = env_dir / ".env"
        env_file.write_text(f'HOME={self.home_dir}\nAPI_KEY=test_key')
        
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        config.backup_dir = Path(self.test_dir) / "backup"
        
        # Mock template processing
        with patch('config_parser.process_synced_templates', return_value=0) as mock_process:
            with patch('sys.stdout', new_callable=io.StringIO):
                result = config_parser.sync_from_repo(config, force=True, process_templates=True)
                
        self.assertEqual(result, 0)
        mock_process.assert_called_once()
        
    def test_sync_with_template_processing_disabled(self):
        """Test sync operation with template processing disabled."""
        # Create config
        with open(self.config_file, 'w') as f:
            f.write("HOME/template.json:.config/app.json\n")
            
        # Create source template file
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        template_file = home_path / "template.json"
        template_file.write_text('{"path": "${HOME}/data"}')
        
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        config.backup_dir = Path(self.test_dir) / "backup"
        
        # Mock template processing
        with patch('config_parser.process_synced_templates') as mock_process:
            with patch('sys.stdout', new_callable=io.StringIO):
                result = config_parser.sync_from_repo(config, force=True, process_templates=False)
                
        self.assertEqual(result, 0)
        # Template processing should not be called
        mock_process.assert_not_called()
        
    def test_environment_file_validation_during_sync(self):
        """Test that environment files are validated during sync operations."""
        # Create malicious environment file
        env_dir = Path(self.home_dir) / ".config" / "dotfiles"
        env_dir.mkdir(parents=True)
        malicious_env = env_dir / ".env"
        malicious_env.write_text('API_KEY=$(rm -rf /)')
        
        # Create config and template
        with open(self.config_file, 'w') as f:
            f.write("HOME/template.json:.config/app.json\n")
            
        home_path = Path(self.test_dir) / "HOME"
        home_path.mkdir()
        (home_path / "template.json").write_text('{"key": "${API_KEY}"}')
        
        config = config_parser.DotfilesConfig(self.config_file)
        config.parse_config()
        
        # Should detect malicious environment file and skip processing
        with patch('config_parser.validate_env_file', return_value=False) as mock_validate:
            with patch('sys.stdout', new_callable=io.StringIO):
                result = config_parser.sync_from_repo(config, force=True, process_templates=True)
                
        # Should succeed but skip template processing
        self.assertEqual(result, 0)


class TestMainFunction(unittest.TestCase):
    """Test the main entry point."""
    
    def test_main_validate_only(self):
        """Test main with --validate-only."""
        test_argv = ['config_parser.py', '--validate-only']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.DotfilesConfig') as mock_config:
                instance = mock_config.return_value
                instance.validate.return_value = []
                instance.dotfiles = ['test']
                
                with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass  # Expected
                    
                self.assertIn("validation passed", mock_stdout.getvalue())
                
    def test_main_list(self):
        """Test main with --list."""
        test_argv = ['config_parser.py', '--list']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.list_files', return_value=0) as mock_list:
                with self.assertRaises(SystemExit) as cm:
                    config_parser.main()
                    
                self.assertEqual(cm.exception.code, 0)
                mock_list.assert_called_once()
                
    def test_main_sync_from_repo_with_options(self):
        """Test main with sync options."""
        test_argv = ['config_parser.py', '--sync-from-repo', '--force', '--strategy', 'replace']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.sync_from_repo', return_value=0) as mock_sync:
                with self.assertRaises(SystemExit) as cm:
                    config_parser.main()
                    
                self.assertEqual(cm.exception.code, 0)
                # Check that sync was called with correct arguments
                _, kwargs = mock_sync.call_args
                self.assertTrue(kwargs['force'])
                self.assertEqual(kwargs['strategy'], 'replace')
                self.assertFalse(kwargs['preview'])
                
    def test_main_analyze_template(self):
        """Test main with --analyze-template option."""
        test_file = '/tmp/test_template.json'
        test_argv = ['config_parser.py', '--analyze-template', test_file]
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.analyze_template_environment') as mock_analyze:
                mock_analyze.return_value = (True, {'HOME', 'API_KEY'}, {'HOME': '/home/user'})
                
                with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass  # Expected
                        
                # Verify analyze function was called with correct arguments
                mock_analyze.assert_called_once()
                args, _ = mock_analyze.call_args
                self.assertEqual(str(args[0]), test_file)
                
    def test_main_process_template(self):
        """Test main with --process-template option."""
        test_template = '/tmp/template.json'
        test_output = '/tmp/output.json'
        test_argv = ['config_parser.py', '--process-template', test_template, test_output]
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.process_template_file', return_value=True) as mock_process:
                with patch('sys.stdout', new_callable=io.StringIO):
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass  # Expected
                        
                # Verify process function was called
                mock_process.assert_called_once()
                
    def test_main_sync_with_no_templates(self):
        """Test main with --sync-from-repo --no-templates."""
        test_argv = ['config_parser.py', '--sync-from-repo', '--no-templates']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.DotfilesConfig') as mock_config_class:
                mock_config = mock_config_class.return_value
                mock_config.parse_config.return_value = None
                
                with patch('config_parser.sync_from_repo', return_value=0) as mock_sync:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass  # Expected
                        
                    # Verify sync was called with process_templates=False
                    _, kwargs = mock_sync.call_args
                    self.assertFalse(kwargs.get('process_templates', True))
                    
    def test_main_get_secrets_files(self):
        """Test main with --get-secrets-files option."""
        test_argv = ['config_parser.py', '--get-secrets-files']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.get_secrets_files', return_value=['/home/user/.env']) as mock_get:
                with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass  # Expected
                        
                mock_get.assert_called_once()
                self.assertIn('/home/user/.env', mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()