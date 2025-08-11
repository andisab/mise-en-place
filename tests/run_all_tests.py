#!/usr/bin/env python3
"""
Run all tests for the mise-en-place repository.
"""

import sys
import os
import unittest
from pathlib import Path

# Add repository root to Python path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

def run_all_tests():
    """Discover and run all tests."""
    # Get the tests directory
    tests_dir = Path(__file__).parent
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover all tests
    suite = loader.discover(
        start_dir=str(tests_dir),
        pattern='t_*.py',
        top_level_dir=str(repo_root)
    )
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())