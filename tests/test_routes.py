import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask application routes."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('app.save_to_cosmos')
    @patch('app.get_country_from_ip')
    @patch('app.get_client_ip')
    def test_index_route_success(self, mock_get_ip, mock_get_country, mock_save_cosmos):
        """Test successful index route."""
        # Setup mocks
        mock_get_ip.return_value = '203.0.113.1'
        mock_get_country.return_value = {
            'country': 'United States',
            'countryCode': 'US',
            'city': 'New York',
            'region': 'NY',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'timezone': 'America/New_York'
        }
        mock_save_cosmos.return_value = True
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'United States', response.data)
        mock_get_ip.assert_called_once()
        mock_get_country.assert_called_once_with('203.0.113.1')
        mock_save_cosmos.assert_called_once()
    
    @patch('app.save_to_cosmos')
    @patch('app.get_country_from_ip')
    @patch('app.get_client_ip')
    def test_index_route_with_headers(self, mock_get_ip, mock_get_country, mock_save_cosmos):
        """Test index route with various headers."""
        mock_get_ip.return_value = '203.0.113.1'
        mock_get_country.return_value = {
            'country': 'Canada',
            'countryCode': 'CA',
            'city': 'Toronto',
            'region': 'Ontario',
            'latitude': 43.6532,
            'longitude': -79.3832,
            'timezone': 'America/Toronto'
        }
        mock_save_cosmos.return_value = True
        
        headers = {
            'User-Agent': 'Mozilla/5.0 Test Browser',
            'Referer': 'https://google.com',
            'Accept-Language': 'en-CA,en;q=0.9'
        }
        
        response = self.client.get('/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        mock_save_cosmos.assert_called_once()
        
        # Verify the visitor data passed to save_to_cosmos includes headers
        call_args = mock_save_cosmos.call_args[0][0]
        self.assertEqual(call_args['user_agent'], 'Mozilla/5.0 Test Browser')
        self.assertEqual(call_args['referer'], 'https://google.com')
        self.assertEqual(call_args['accept_language'], 'en-CA,en;q=0.9')
    
    @patch('app.get_client_ip')
    def test_index_route_exception(self, mock_get_ip):
        """Test index route with exception."""
        mock_get_ip.side_effect = Exception('Test error')
        
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Test error', response.data)
    
    @patch('app.get_country_from_ip')
    @patch('app.get_client_ip')
    def test_api_visitor_info_success(self, mock_get_ip, mock_get_country):
        """Test successful API visitor info endpoint."""
        mock_get_ip.return_value = '203.0.113.1'
        mock_get_country.return_value = {
            'country': 'Germany',
            'countryCode': 'DE',
            'city': 'Berlin',
            'region': 'Berlin',
            'latitude': 52.5200,
            'longitude': 13.4050,
            'timezone': 'Europe/Berlin'
        }
        
        headers = {
            'User-Agent': 'Test API Client'
        }
        
        response = self.client.get('/api/visitor-info', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(data['ip_address'], '203.0.113.1')
        self.assertEqual(data['user_agent'], 'Test API Client')
        self.assertEqual(data['country_info']['country'], 'Germany')
        self.assertIn('timestamp', data)
    
    @patch('app.get_client_ip')
    def test_api_visitor_info_exception(self, mock_get_ip):
        """Test API visitor info endpoint with exception."""
        mock_get_ip.side_effect = Exception('API test error')
        
        response = self.client.get('/api/visitor-info')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'API test error')
    
    @patch('app.get_cosmos_client')
    def test_health_check_healthy(self, mock_get_client):
        """Test health check endpoint when healthy."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['cosmos_db'], 'connected')
        self.assertIn('timestamp', data)
    
    @patch('app.get_cosmos_client')
    def test_health_check_unhealthy(self, mock_get_client):
        """Test health check endpoint when unhealthy."""
        mock_get_client.return_value = None
        
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['cosmos_db'], 'disconnected')
    
    @patch('app.get_cosmos_client')
    def test_health_check_exception(self, mock_get_client):
        """Test health check endpoint with exception."""
        mock_get_client.side_effect = Exception('Health check error')
        
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['error'], 'Health check error')


class TestFlaskApp(unittest.TestCase):
    """Test Flask application configuration."""
    
    def test_app_exists(self):
        """Test that the Flask app exists."""
        self.assertIsNotNone(app)
    
    def test_app_is_testing(self):
        """Test that app can be configured for testing."""
        app.config['TESTING'] = True
        self.assertTrue(app.config['TESTING'])
    
    def test_404_error(self):
        """Test 404 error handling."""
        client = app.test_client()
        response = client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
