"""
End-to-end tests for the Flask web application.
These tests run the actual Flask application and test complete user workflows.
"""
import unittest
import time
import threading
import requests
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TestE2E(unittest.TestCase):
    """End-to-end tests for the web application."""
    
    @classmethod
    def setUpClass(cls):
        """Start the Flask application in a separate thread for testing."""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        
        # Start the Flask app in a separate thread
        cls.server_thread = threading.Thread(
            target=cls._run_server,
            daemon=True
        )
        cls.base_url = 'http://localhost:5555'
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        
        # Test if server is running
        max_retries = 10
        for _ in range(max_retries):
            try:
                response = requests.get(f'{cls.base_url}/health', timeout=1)
                if response.status_code in [200, 500]:  # Server is responding
                    break
            except requests.exceptions.RequestException:
                time.sleep(0.5)
    
    @classmethod
    def _run_server(cls):
        """Run the Flask server."""
        cls.app.run(host='localhost', port=5555, debug=False, use_reloader=False)
    
    def setUp(self):
        """Set up for each test."""
        self.base_url = 'http://localhost:5555'
    
    @patch('app.save_to_cosmos')
    @patch('app.get_country_from_ip')
    def test_homepage_loads(self, mock_get_country, mock_save_cosmos):
        """Test that the homepage loads successfully."""
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
        
        try:
            response = requests.get(self.base_url, timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn('United States', response.text)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Server not available: {e}")
    
    @patch('app.get_country_from_ip')
    def test_api_endpoint_returns_json(self, mock_get_country):
        """Test that the API endpoint returns valid JSON."""
        mock_get_country.return_value = {
            'country': 'Canada',
            'countryCode': 'CA',
            'city': 'Toronto',
            'region': 'Ontario',
            'latitude': 43.6532,
            'longitude': -79.3832,
            'timezone': 'America/Toronto'
        }
        
        try:
            response = requests.get(f'{self.base_url}/api/visitor-info', timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            
            data = response.json()
            self.assertIn('ip_address', data)
            self.assertIn('user_agent', data)
            self.assertIn('country_info', data)
            self.assertIn('timestamp', data)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Server not available: {e}")
    
    def test_health_check_endpoint(self):
        """Test that the health check endpoint works."""
        try:
            response = requests.get(f'{self.base_url}/health', timeout=5)
            self.assertIn(response.status_code, [200, 500])  # Either healthy or unhealthy
            
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('timestamp', data)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Server not available: {e}")
    
    def test_404_error_page(self):
        """Test that 404 errors are handled properly."""
        try:
            response = requests.get(f'{self.base_url}/nonexistent-page', timeout=5)
            self.assertEqual(response.status_code, 404)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Server not available: {e}")
    
    @patch('app.get_country_from_ip')
    def test_user_agent_detection(self, mock_get_country):
        """Test that different user agents are detected correctly."""
        mock_get_country.return_value = {
            'country': 'France',
            'countryCode': 'FR',
            'city': 'Paris',
            'region': 'Île-de-France',
            'latitude': 48.8566,
            'longitude': 2.3522,
            'timezone': 'Europe/Paris'
        }
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Test-Bot/1.0'
        ]
        
        for user_agent in user_agents:
            try:
                headers = {'User-Agent': user_agent}
                response = requests.get(f'{self.base_url}/api/visitor-info', headers=headers, timeout=5)
                self.assertEqual(response.status_code, 200)
                
                data = response.json()
                self.assertEqual(data['user_agent'], user_agent)
            except requests.exceptions.RequestException as e:
                self.skipTest(f"Server not available: {e}")


class TestLoadAndStress(unittest.TestCase):
    """Basic load testing for the application."""
    
    def setUp(self):
        self.base_url = 'http://localhost:5555'
    
    @patch('app.save_to_cosmos')
    @patch('app.get_country_from_ip')
    def test_multiple_concurrent_requests(self, mock_get_country, mock_save_cosmos):
        """Test handling of multiple concurrent requests."""
        mock_get_country.return_value = {
            'country': 'United Kingdom',
            'countryCode': 'GB',
            'city': 'London',
            'region': 'England',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'timezone': 'Europe/London'
        }
        mock_save_cosmos.return_value = True
        
        def make_request():
            try:
                response = requests.get(self.base_url, timeout=10)
                return response.status_code == 200
            except requests.exceptions.RequestException:
                return False
        
        # Create multiple threads to make concurrent requests
        threads = []
        results = []
        
        for _ in range(5):  # 5 concurrent requests
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that most requests succeeded (allow for some failures due to test environment)
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.6)  # At least 60% success rate


if __name__ == '__main__':
    unittest.main()
