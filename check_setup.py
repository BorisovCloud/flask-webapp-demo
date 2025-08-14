#!/usr/bin/env python3
"""
Project status check script.
Verifies that all test files exist and basic project structure is correct.
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and print status."""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (MISSING)")
        return False

def check_project_structure():
    """Check the basic project structure."""
    print("🔍 Checking Flask Web App Project Structure")
    print("=" * 50)
    
    all_good = True
    
    # Core application files
    core_files = [
        ("app.py", "Main Flask application"),
        ("requirements.txt", "Python dependencies"),
        ("requirements-dev.txt", "Development dependencies"),
        ("Dockerfile", "Docker configuration"),
        ("pytest.ini", "Pytest configuration"),
        (".gitignore", "Git ignore file"),
        ("README.md", "Project documentation"),
    ]
    
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n📁 Test Structure")
    print("-" * 20)
    
    # Test files
    test_files = [
        ("tests/conftest.py", "Test configuration"),
        ("tests/test_utils.py", "Utility function tests"),
        ("tests/test_routes.py", "Flask route tests"),
        ("tests/test_integration.py", "Integration tests"),
        ("tests/test_e2e.py", "End-to-end tests"),
        ("tests/run_tests.py", "Test runner script"),
    ]
    
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n🔧 GitHub Actions")
    print("-" * 20)
    
    # GitHub Actions files
    gh_files = [
        (".github/workflows/ci-cd.yml", "CI/CD Pipeline"),
        (".github/workflows/tests.yml", "Test Pipeline"),
    ]
    
    for file_path, description in gh_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n🎯 Test Runners")
    print("-" * 15)
    
    # Test runner scripts
    runner_files = [
        ("run_tests.sh", "Linux/macOS test runner"),
        ("run_tests.bat", "Windows test runner"),
    ]
    
    for file_path, description in runner_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 All project files are present!")
        print("\n📋 Next steps:")
        print("1. Run tests locally: ./run_tests.sh (Linux/macOS) or run_tests.bat (Windows)")
        print("2. Commit and push to trigger GitHub Actions")
        print("3. Check GitHub Actions workflow results")
        return True
    else:
        print("⚠️  Some files are missing. Please check the setup.")
        return False

if __name__ == "__main__":
    success = check_project_structure()
    sys.exit(0 if success else 1)
