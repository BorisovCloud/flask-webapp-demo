@echo off
REM Local test runner script for Flask web application (Windows)

echo 🧪 Running Flask Web App Tests
echo ================================

REM Set PYTHONPATH to include the current directory
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Run linting
echo 🔍 Running code quality checks...
echo   - Checking with flake8...
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

REM Run tests
echo 🧪 Running tests...

echo   - Unit tests...
python -m pytest tests/test_utils.py -v

echo   - Integration tests...
python -m pytest tests/test_integration.py -v

echo   - Route tests...
python -m pytest tests/test_routes.py -v

echo   - All tests with coverage...
coverage run -m pytest tests/ -v
coverage report -m

echo ✅ Test run completed!
echo 📊 Coverage report generated above

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
