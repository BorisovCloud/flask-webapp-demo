#!/bin/bash
# Local test runner script for Flask web application

echo "🧪 Running Flask Web App Tests"
echo "================================"

# Set PYTHONPATH to include the current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run linting
echo "🔍 Running code quality checks..."
echo "  - Checking with flake8..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run tests
echo "🧪 Running tests..."

echo "  - Unit tests..."
python -m pytest tests/test_utils.py -v

echo "  - Integration tests..."
python -m pytest tests/test_integration.py -v

echo "  - Route tests..."
python -m pytest tests/test_routes.py -v

echo "  - All tests with coverage..."
coverage run -m pytest tests/ -v
coverage report -m

echo "✅ Test run completed!"
echo "📊 Coverage report generated above"

# Deactivate virtual environment
deactivate 2>/dev/null || echo "Virtual environment deactivated"
