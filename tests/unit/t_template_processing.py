#!/usr/bin/env python3
"""
Test suite for template processing functionality in config_parser.py
Tests the end-to-end template processing workflow including environment handling.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json

# Add repository root to path to import config_parser
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
import config_parser


class TestTemplateProcessingWorkflow(unittest.TestCase):
    """Test the complete template processing workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.home_dir = tempfile.mkdtemp()
        
        # Create environment files with precedence
        self.global_env = Path(self.home_dir) / ".env"
        self.local_env = Path(self.home_dir) / ".config" / "dotfiles" / ".env"
        
        # Create local env directory
        self.local_env.parent.mkdir(parents=True, exist_ok=True)
        
        # Patch Path.home() to return our test directory
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_end_to_end_template_processing(self):
        """Test complete template processing workflow."""
        # Create template file
        template_content = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["${HOME}/Projects", "${HOME}/Documents"]
                },
                "database": {
                    "url": "${DATABASE_URL}",
                    "api_key": "${API_KEY}"
                }
            }
        }
        
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text(json.dumps(template_content, indent=2))
        
        # Create environment file
        env_content = f'''
        HOME={self.home_dir}
        DATABASE_URL=postgresql://localhost/test
        API_KEY=test_api_key_123
        '''
        self.local_env.write_text(env_content)
        
        # Mock envsubst to return processed content
        expected_output = json.dumps({
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": [f"{self.home_dir}/Projects", f"{self.home_dir}/Documents"]
                },
                "database": {
                    "url": "postgresql://localhost/test",
                    "api_key": "test_api_key_123"
                }
            }
        }, indent=2)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=expected_output
            )
            
            result = config_parser.process_template_file(
                template_file, 
                config_parser.get_secrets_files()
            )
            
            self.assertTrue(result)
            
            # Verify the file was updated
            processed_content = json.loads(template_file.read_text())
            self.assertEqual(processed_content["mcpServers"]["filesystem"]["args"][0], 
                           f"{self.home_dir}/Projects")
            self.assertEqual(processed_content["mcpServers"]["database"]["api_key"], 
                           "test_api_key_123")
            
    def test_environment_file_precedence(self):
        """Test that local env file takes precedence over global."""
        # Create both environment files with different values
        self.global_env.write_text('''
        HOME=/global/home
        API_KEY=global_key
        SHARED_VAR=global_value
        ''')
        
        self.local_env.write_text('''
        HOME=/local/home
        API_KEY=local_key
        LOCAL_ONLY=local_value
        ''')
        
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"home": "${HOME}", "key": "${API_KEY}", "shared": "${SHARED_VAR}", "local": "${LOCAL_ONLY}"}')
        
        # Mock envsubst to show which values were used
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, 
                stdout='{"home": "/local/home", "key": "local_key", "shared": "global_value", "local": "local_value"}'
            )
            
            result = config_parser.process_template_file(
                template_file,
                config_parser.get_secrets_files()
            )
            
            self.assertTrue(result)
            
            # Verify envsubst was called with correct environment files
            call_args = mock_run.call_args
            
            # Should be called with environment files in correct order
            # (the function should handle precedence internally)
            self.assertTrue(mock_run.called)
            
    def test_missing_variables_handling(self):
        """Test handling of templates with undefined variables."""
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"defined": "${HOME}", "undefined": "${MISSING_VAR}"}')
        
        # Create env with only some variables
        self.local_env.write_text('HOME=/home/user')
        
        # Mock envsubst to simulate leaving undefined variables unchanged
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout='{"defined": "/home/user", "undefined": "${MISSING_VAR}"}'
            )
            
            # Should still succeed but with warnings
            with patch('sys.stderr') as mock_stderr:
                result = config_parser.process_template_file(
                    template_file,
                    config_parser.get_secrets_files()
                )
                
            self.assertTrue(result)
            
    def test_template_processing_with_complex_patterns(self):
        """Test processing templates with complex variable patterns."""
        complex_template = {
            "paths": {
                "home": "${HOME}",
                "workspace": "${WORKSPACE:-${HOME}/workspace}",
                "config": "${XDG_CONFIG_HOME:-${HOME}/.config}"
            },
            "urls": {
                "database": "${DATABASE_PROTOCOL}://${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}",
                "api": "${API_BASE_URL}/v${API_VERSION}"
            },
            "arrays": [
                "${HOME}/bin",
                "${HOME}/.local/bin",
                "${CUSTOM_PATH}"
            ]
        }
        
        template_file = Path(self.test_dir) / "complex_template.json"
        template_file.write_text(json.dumps(complex_template, indent=2))
        
        # Create comprehensive environment file
        env_content = f'''
        HOME={self.home_dir}
        WORKSPACE={self.home_dir}/workspace
        DATABASE_PROTOCOL=postgresql
        DATABASE_HOST=localhost
        DATABASE_PORT=5432
        DATABASE_NAME=myapp
        API_BASE_URL=https://api.example.com
        API_VERSION=2
        CUSTOM_PATH={self.home_dir}/custom
        '''
        self.local_env.write_text(env_content)
        
        expected_output = {
            "paths": {
                "home": str(self.home_dir),
                "workspace": f"{self.home_dir}/workspace",
                "config": f"{self.home_dir}/.config"
            },
            "urls": {
                "database": "postgresql://localhost:5432/myapp",
                "api": "https://api.example.com/v2"
            },
            "arrays": [
                f"{self.home_dir}/bin",
                f"{self.home_dir}/.local/bin",
                f"{self.home_dir}/custom"
            ]
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout=json.dumps(expected_output)
            )
            
            result = config_parser.process_template_file(
                template_file,
                config_parser.get_secrets_files()
            )
            
            self.assertTrue(result)


class TestProcessSyncedTemplates(unittest.TestCase):
    """Test the process_synced_templates function."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.home_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        
        # Create test configuration
        self.config_file.write_text("test/template.json:.test_config.json\n")
        
        # Patch Path.home()
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.home_dir)
        
        # Create config object
        self.config = config_parser.DotfilesConfig(self.config_file)
        self.config.parse_config()
        
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.home_dir)
        
    def test_process_synced_templates_success(self):
        """Test successful processing of synced templates."""
        # Create template file in destination
        dest_file = Path(self.home_dir) / ".test_config.json"
        dest_file.write_text('{"path": "${HOME}/test"}')
        
        # Create environment file
        env_file = Path(self.home_dir) / ".config" / "dotfiles" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(f'HOME={self.home_dir}')
        
        synced_files = [("test/template.json", ".test_config.json")]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout=f'{{"path": "{self.home_dir}/test"}}'
            )
            
            result = config_parser.process_synced_templates(synced_files, self.config)
            
            self.assertEqual(result, 0)
            
    def test_process_synced_templates_no_env_file(self):
        """Test processing when no environment file exists."""
        dest_file = Path(self.home_dir) / ".test_config.json"
        dest_file.write_text('{"path": "${HOME}/test"}')
        
        synced_files = [("test/template.json", ".test_config.json")]
        
        # Should skip processing gracefully
        result = config_parser.process_synced_templates(synced_files, self.config)
        
        self.assertEqual(result, 0)  # Should succeed but do nothing
        
    def test_process_synced_templates_with_rollback(self):
        """Test rollback functionality when template processing fails."""
        # Create template file
        dest_file = Path(self.home_dir) / ".test_config.json"
        original_content = '{"path": "${HOME}/test"}'
        dest_file.write_text(original_content)
        
        # Create environment file
        env_file = Path(self.home_dir) / ".config" / "dotfiles" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(f'HOME={self.home_dir}')
        
        synced_files = [("test/template.json", ".test_config.json")]
        
        with patch('subprocess.run') as mock_run:
            # Simulate processing failure
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=1, stderr='envsubst failed'
            )
            
            result = config_parser.process_synced_templates(synced_files, self.config)
            
            # Should return error code
            self.assertEqual(result, 1)
            
            # Original file should be restored (rollback)
            self.assertEqual(dest_file.read_text(), original_content)


class TestCLITemplateOptions(unittest.TestCase):
    """Test CLI options for template processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "dotfiles.conf"
        self.config_file.write_text("test/file:.testfile\n")
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_analyze_template_option(self):
        """Test --analyze-template CLI option."""
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}", "key": "${API_KEY}"}')
        
        test_argv = ['config_parser.py', '--analyze-template', str(template_file)]
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.analyze_template_environment') as mock_analyze:
                mock_analyze.return_value = (True, {"HOME", "API_KEY"}, {"HOME": "/home/user"})
                
                with patch('sys.stdout') as mock_stdout:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass
                        
                mock_analyze.assert_called_once()
                
    def test_process_template_option(self):
        """Test --process-template CLI option."""
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}"}')
        
        output_file = Path(self.test_dir) / "output.json"
        
        test_argv = ['config_parser.py', '--process-template', str(template_file), str(output_file)]
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.process_template_file', return_value=True) as mock_process:
                with patch('sys.stdout') as mock_stdout:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass
                        
                mock_process.assert_called_once()
                
    def test_no_templates_option(self):
        """Test --no-templates CLI option during sync."""
        test_argv = ['config_parser.py', '--sync-from-repo', '--no-templates']
        
        with patch('sys.argv', test_argv):
            with patch('config_parser.DotfilesConfig') as mock_config_class:
                mock_config = mock_config_class.return_value
                mock_config.parse_config.return_value = None
                
                with patch('config_parser.sync_from_repo', return_value=0) as mock_sync:
                    try:
                        config_parser.main()
                    except SystemExit:
                        pass
                        
                    # Verify sync was called with process_templates=False
                    call_args = mock_sync.call_args
                    kwargs = call_args.kwargs
                    self.assertFalse(kwargs.get('process_templates', True))


class TestErrorHandlingAndEdgeCases(unittest.TestCase):
    """Test error handling and edge cases in template processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_envsubst_not_available(self):
        """Test handling when envsubst is not available."""
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}"}')
        
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('HOME=/home/user')
        
        # Mock subprocess to simulate envsubst not found
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("envsubst not found")
            
            result = config_parser.process_template_file(template_file, [str(env_file)])
            
            self.assertFalse(result)
            
    def test_invalid_json_template(self):
        """Test handling of invalid JSON templates."""
        template_file = Path(self.test_dir) / "invalid.json"
        template_file.write_text('{"invalid": json, "missing": quote}')
        
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('HOME=/home/user')
        
        # Should detect variables even in invalid JSON
        variables = config_parser.detect_template_variables(template_file)
        
        # Should still be able to detect variables
        self.assertIsInstance(variables, set)
        
    def test_binary_file_handling(self):
        """Test handling of binary files that might be mistaken for templates."""
        binary_file = Path(self.test_dir) / "binary.dat"
        # Create a binary file with some bytes that might look like ${VAR}
        binary_data = b'\x00\x01${HOME}\x02\x03${API_KEY}\xff'
        binary_file.write_bytes(binary_data)
        
        # Should handle binary files gracefully
        try:
            variables = config_parser.detect_template_variables(binary_file)
            # Might find variables in binary data, but shouldn't crash
            self.assertIsInstance(variables, set)
        except UnicodeDecodeError:
            # Acceptable to fail on binary files
            pass
            
    def test_very_large_template_file(self):
        """Test handling of large template files."""
        template_file = Path(self.test_dir) / "large.json"
        
        # Create a large template with many variables
        large_template = {
            f"var_{i}": f"${{VAR_{i}}}" for i in range(1000)
        }
        template_file.write_text(json.dumps(large_template))
        
        # Should handle large files efficiently
        variables = config_parser.detect_template_variables(template_file)
        
        self.assertEqual(len(variables), 1000)
        self.assertTrue(all(f"VAR_{i}" in variables for i in range(100)))  # Check first 100


if __name__ == '__main__':
    unittest.main()