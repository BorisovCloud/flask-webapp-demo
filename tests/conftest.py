# Test configuration and fixtures
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_cosmos_client, get_client_ip, get_country_from_ip, save_to_cosmos


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client."""
    with patch('app.get_cosmos_client') as mock:
        mock_client = Mock()
        mock_database = Mock()
        mock_container = Mock()
        
        mock_client.get_database_client.return_value = mock_database
        mock_database.get_container_client.return_value = mock_container
        mock.return_value = mock_client
        
        yield mock_client, mock_database, mock_container


@pytest.fixture
def mock_requests():
    """Mock requests for external API calls."""
    with patch('app.requests') as mock:
        yield mock


@pytest.fixture
def sample_visitor_data():
    """Sample visitor data for testing."""
    return {
        'ip_address': '203.0.113.1',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'country': 'United States',
        'country_code': 'US',
        'city': 'New York',
        'region': 'New York',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'timezone': 'America/New_York',
        'referer': 'Direct',
        'accept_language': 'en-US,en;q=0.9'
    }


@pytest.fixture
def mock_ip_api_response():
    """Mock response from ip-api.com."""
    return {
        'status': 'success',
        'country': 'United States',
        'countryCode': 'US',
        'region': 'NY',
        'city': 'New York',
        'lat': 40.7128,
        'lon': -74.0060,
        'timezone': 'America/New_York'
    }
