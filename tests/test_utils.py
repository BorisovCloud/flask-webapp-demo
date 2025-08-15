import json
import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_client_ip, get_country_from_ip, save_to_cosmos


class TestGetClientIp(unittest.TestCase):
    """Test the get_client_ip function."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_get_client_ip_azure_header(self):
        """Test IP extraction from X-Azure-ClientIP header."""
        with self.app.test_request_context(
            "/", headers={"X-Azure-ClientIP": "203.0.113.1"}
        ):
            ip = get_client_ip()
            self.assertEqual(ip, "203.0.113.1")

    def test_get_client_ip_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header."""
        with self.app.test_request_context(
            "/", headers={"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        ):
            ip = get_client_ip()
            self.assertEqual(ip, "203.0.113.1")

    def test_get_client_ip_real_ip(self):
        """Test IP extraction from X-Real-IP header."""
        with self.app.test_request_context("/", headers={"X-Real-IP": "203.0.113.1"}):
            ip = get_client_ip()
            self.assertEqual(ip, "203.0.113.1")

    def test_get_client_ip_remote_addr(self):
        """Test IP extraction from remote_addr."""
        with self.app.test_request_context(
            "/", environ_base={"REMOTE_ADDR": "203.0.113.1"}
        ):
            ip = get_client_ip()
            self.assertEqual(ip, "203.0.113.1")

    def test_get_client_ip_with_port(self):
        """Test IP extraction when port is included."""
        with self.app.test_request_context(
            "/", headers={"X-Azure-ClientIP": "203.0.113.1:8080"}
        ):
            ip = get_client_ip()
            self.assertEqual(ip, "203.0.113.1")


class TestGetCountryFromIp(unittest.TestCase):
    """Test the get_country_from_ip function."""

    def test_local_ip_detection(self):
        """Test detection of local/private IPs."""
        local_ips = ["127.0.0.1", "localhost", "192.168.1.1", "10.0.0.1", "172.16.0.1"]

        for ip in local_ips:
            result = get_country_from_ip(ip)
            self.assertEqual(result["country"], "Local/Private")
            self.assertEqual(result["countryCode"], "LOCAL")

    def test_empty_ip(self):
        """Test handling of empty IP address."""
        result = get_country_from_ip("")
        self.assertEqual(result["country"], "Invalid IP")
        self.assertEqual(result["countryCode"], "XX")

    @patch("app.requests.get")
    def test_successful_api_call(self, mock_get):
        """Test successful API call to ip-api.com."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "United States",
            "countryCode": "US",
            "region": "NY",
            "city": "New York",
            "lat": 40.7128,
            "lon": -74.0060,
            "timezone": "America/New_York",
        }
        mock_get.return_value = mock_response

        result = get_country_from_ip("203.0.113.1")

        self.assertEqual(result["country"], "United States")
        self.assertEqual(result["countryCode"], "US")
        self.assertEqual(result["city"], "New York")
        self.assertEqual(result["latitude"], 40.7128)
        self.assertEqual(result["longitude"], -74.0060)

    @patch("app.requests.get")
    def test_api_error_response(self, mock_get):
        """Test API error response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "fail", "message": "private range"}
        mock_get.return_value = mock_response

        result = get_country_from_ip("203.0.113.1")

        self.assertIn("API Error", result["country"])
        self.assertEqual(result["countryCode"], "XX")

    @patch("app.requests.get")
    def test_http_error(self, mock_get):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = get_country_from_ip("203.0.113.1")

        self.assertIn("HTTP Error: 429", result["country"])
        self.assertEqual(result["countryCode"], "XX")

    @patch("app.requests.get")
    def test_timeout_error(self, mock_get):
        """Test timeout error handling."""
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout()

        result = get_country_from_ip("203.0.113.1")

        self.assertEqual(result["country"], "Timeout Error")
        self.assertEqual(result["countryCode"], "XX")

    @patch("app.requests.get")
    def test_general_exception(self, mock_get):
        """Test general exception handling."""
        mock_get.side_effect = Exception("Network error")

        result = get_country_from_ip("203.0.113.1")

        self.assertIn("Error: Network error", result["country"])
        self.assertEqual(result["countryCode"], "XX")


class TestSaveToCosmos(unittest.TestCase):
    """Test the save_to_cosmos function."""

    @patch("app.get_cosmos_client")
    def test_save_to_cosmos_success(self, mock_get_client):
        """Test successful save to Cosmos DB."""
        # Setup mocks
        mock_client = Mock()
        mock_database = Mock()
        mock_container = Mock()

        mock_client.get_database_client.return_value = mock_database
        mock_database.get_container_client.return_value = mock_container
        mock_container.create_item.return_value = None
        mock_get_client.return_value = mock_client

        visitor_data = {"ip_address": "203.0.113.1", "country": "United States"}

        result = save_to_cosmos(visitor_data)

        self.assertTrue(result)
        mock_container.create_item.assert_called_once()

        # Check that timestamp and id were added
        self.assertIn("timestamp", visitor_data)
        self.assertIn("id", visitor_data)

    @patch("app.get_cosmos_client")
    def test_save_to_cosmos_no_client(self, mock_get_client):
        """Test save when Cosmos client is not available."""
        mock_get_client.return_value = None

        visitor_data = {"ip_address": "203.0.113.1"}
        result = save_to_cosmos(visitor_data)

        self.assertFalse(result)

    @patch("app.get_cosmos_client")
    def test_save_to_cosmos_exception(self, mock_get_client):
        """Test save with Cosmos DB exception."""
        mock_client = Mock()
        mock_database = Mock()
        mock_container = Mock()

        mock_client.get_database_client.return_value = mock_database
        mock_database.get_container_client.return_value = mock_container
        mock_container.create_item.side_effect = Exception("Database error")
        mock_get_client.return_value = mock_client

        visitor_data = {"ip_address": "203.0.113.1"}
        result = save_to_cosmos(visitor_data)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
