# Flask Visitor Info Web App

A Flask web application that displays visitor information including IP address, geolocation data, and user agent details. The application saves visitor data to Azure Cosmos DB.

## Features

- **Real-time Visitor Information**: Shows IP address, country, city, timezone, and user agent
- **Geolocation**: Automatically determines location from IP address using ip-api.com
- **Data Persistence**: Saves visitor data to Azure Cosmos DB
- **Responsive UI**: Bootstrap 5 responsive design
- **Health Monitoring**: Health check endpoint for monitoring
- **JSON API**: RESTful API endpoint for programmatic access
- **Azure Integration**: Uses Azure Managed Identity for secure database access

## Technology Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: Bootstrap 5, Font Awesome
- **Database**: Azure Cosmos DB (NoSQL)
- **Authentication**: Azure Managed Identity

## Local Development

### Prerequisites

- Python 3.11+
- Azure Cosmos DB account (or emulator for local development)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd flask-visitor-app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open http://localhost:8000 in your browser

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `COSMOS_ENDPOINT` | Cosmos DB endpoint URL | Yes | - |
| `COSMOS_DATABASE_NAME` | Database name | No | `webapp-db` |
| `COSMOS_CONTAINER_NAME` | Container name | No | `visitor-logs` |
| `DEBUG` | Enable debug mode | No | `False` |
| `SECRET_KEY` | Flask secret key | No | Generated |
| `PORT` | Application port | No | `8000` |

## API Endpoints

- `GET /` - Main application interface
- `GET /api/visitor-info` - JSON API for visitor information
- `GET /health` - Health check endpoint

### Example API Response

```json
{
  "ip_address": "203.0.113.195",
  "user_agent": "Mozilla/5.0...",
  "country_info": {
    "country": "United States",
    "countryCode": "US",
    "city": "New York",
    "region": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "timestamp": "2025-08-04T12:00:00.000Z"
}
```

## Azure Deployment

This application is designed to be deployed on Azure App Service. For infrastructure deployment using Terraform, see the companion infrastructure repository.

### Required Azure Resources

- Azure App Service (Linux, Python 3.11)
- Azure Cosmos DB account with:
  - Database: `webapp-db`
  - Container: `visitor-logs`
  - Partition key: `/ip_address`
- Azure Managed Identity with Cosmos DB Data Contributor role

### Application Settings (Environment Variables)

When deploying to Azure App Service, configure these application settings:

```
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_DATABASE_NAME=webapp-db
COSMOS_CONTAINER_NAME=visitor-logs
AZURE_CLIENT_ID=<managed-identity-client-id>
FLASK_ENV=production
PORT=8000
```

## Testing

This project includes comprehensive test coverage with unit tests, integration tests, and end-to-end tests.

### Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_utils.py         # Unit tests for utility functions
├── test_routes.py        # Tests for Flask routes
├── test_integration.py   # Integration tests for Cosmos DB
├── test_e2e.py          # End-to-end tests
└── run_tests.py         # Test runner script
```

### Running Tests

#### Local Testing

**Quick Setup (Windows):**
```cmd
run_tests.bat
```

**Quick Setup (Linux/macOS):**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Manual Setup:**
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run specific test suites
python -m pytest tests/test_utils.py -v          # Unit tests
python -m pytest tests/test_routes.py -v         # Route tests
python -m pytest tests/test_integration.py -v    # Integration tests

# Run all tests with coverage
coverage run -m pytest tests/ -v
coverage report -m
coverage html  # Generate HTML coverage report
```

#### Test Categories

- **Unit Tests** (`test_utils.py`): Test individual functions like IP detection, geolocation, and Cosmos DB operations
- **Route Tests** (`test_routes.py`): Test Flask routes and API endpoints
- **Integration Tests** (`test_integration.py`): Test Cosmos DB integration and environment configuration
- **End-to-End Tests** (`test_e2e.py`): Test complete user workflows

### GitHub Actions CI/CD

The project includes automated testing via GitHub Actions that runs on every push and pull request:

#### Workflow Features

- **Multi-Python Testing**: Tests against Python 3.8, 3.9, 3.10, and 3.11
- **Code Quality Checks**: Linting with flake8, formatting with Black, import sorting with isort
- **Security Scanning**: Safety check for vulnerabilities, Bandit for security issues
- **Test Coverage**: Comprehensive test coverage reporting
- **Docker Building**: Automated Docker image creation and testing
- **Deployment**: Automated deployment to staging environment

#### Workflow Triggers

- Push to `main` or `develop` branches
- Pull requests to `main` branch

#### Jobs

1. **Test**: Runs all test suites across multiple Python versions
2. **Security Scan**: Runs security and vulnerability checks
3. **Code Quality**: Checks code formatting and style
4. **Docker Build**: Builds and tests Docker image (on main branch)
5. **Deploy Staging**: Deploys to staging environment (on main branch)

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

#### Coverage Configuration
Coverage reporting includes:
- Line coverage for all Python files
- Branch coverage
- HTML reports for detailed analysis
- XML reports for CI integration

### Mocking Strategy

Tests use comprehensive mocking to isolate functionality:
- **Cosmos DB**: Mocked client, database, and container operations
- **External APIs**: Mocked requests to ip-api.com
- **Flask Context**: Proper request context for route testing
- **Environment Variables**: Isolated environment configuration

### Continuous Integration

The GitHub Actions workflow ensures:
- All tests pass before merging
- Code quality standards are maintained
- Security vulnerabilities are detected
- Docker images are properly built and tested
- Coverage reports are generated and tracked

Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
