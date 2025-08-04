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
- **Containerization**: Docker

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
