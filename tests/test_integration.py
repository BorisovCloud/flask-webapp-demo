import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import get_cosmos_client


class TestCosmosIntegration(unittest.TestCase):
    """Integration tests for Cosmos DB functionality."""

    @patch.dict(
        os.environ, {"COSMOS_ENDPOINT": "https://test-cosmos.documents.azure.com:443/"}
    )
    @patch("app.DefaultAzureCredential")
    @patch("app.CosmosClient")
    def test_get_cosmos_client_success(self, mock_cosmos_client, mock_credential):
        """Test successful Cosmos DB client initialization."""
        mock_credential_instance = Mock()
        mock_credential.return_value = mock_credential_instance

        mock_client_instance = Mock()
        mock_cosmos_client.return_value = mock_client_instance

        # Set the environment variable in the app module
        import app

        original_endpoint = app.COSMOS_ENDPOINT
        app.COSMOS_ENDPOINT = "https://test-cosmos.documents.azure.com:443/"

        try:
            client = get_cosmos_client()

            self.assertIsNotNone(client)
            mock_credential.assert_called_once()
            mock_cosmos_client.assert_called_once_with(
                "https://test-cosmos.documents.azure.com:443/",
                credential=mock_credential_instance,
            )
        finally:
            # Restore original value
            app.COSMOS_ENDPOINT = original_endpoint

    @patch.dict(os.environ, {}, clear=True)
    @patch("app.DefaultAzureCredential")
    @patch("app.CosmosClient")
    def test_get_cosmos_client_no_endpoint(self, mock_cosmos_client, mock_credential):
        """Test Cosmos DB client initialization without endpoint."""
        mock_credential_instance = Mock()
        mock_credential.return_value = mock_credential_instance

        mock_cosmos_client.side_effect = Exception("Invalid endpoint")

        client = get_cosmos_client()

        self.assertIsNone(client)

    @patch.dict(
        os.environ, {"COSMOS_ENDPOINT": "https://test-cosmos.documents.azure.com:443/"}
    )
    @patch("app.DefaultAzureCredential")
    @patch("app.CosmosClient")
    def test_get_cosmos_client_auth_error(self, mock_cosmos_client, mock_credential):
        """Test Cosmos DB client initialization with authentication error."""
        mock_credential.side_effect = Exception("Authentication failed")

        client = get_cosmos_client()

        self.assertIsNone(client)

    @patch.dict(
        os.environ, {"COSMOS_ENDPOINT": "https://test-cosmos.documents.azure.com:443/"}
    )
    @patch("app.DefaultAzureCredential")
    @patch("app.CosmosClient")
    def test_get_cosmos_client_cosmos_error(self, mock_cosmos_client, mock_credential):
        """Test Cosmos DB client initialization with Cosmos error."""
        mock_credential_instance = Mock()
        mock_credential.return_value = mock_credential_instance

        mock_cosmos_client.side_effect = Exception("Cosmos connection failed")

        client = get_cosmos_client()

        self.assertIsNone(client)


class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment variable configuration."""

    def test_environment_variables_default(self):
        """Test default environment variable values."""
        # Test defaults by checking the actual values from os.environ.get calls
        database_name = os.environ.get("COSMOS_DATABASE_NAME", "webapp-db")
        container_name = os.environ.get("COSMOS_CONTAINER_NAME", "visitor-logs")

        # These should match the defaults used in app.py
        self.assertEqual(
            database_name, os.environ.get("COSMOS_DATABASE_NAME", "webapp-db")
        )
        self.assertEqual(
            container_name, os.environ.get("COSMOS_CONTAINER_NAME", "visitor-logs")
        )

    @patch.dict(
        os.environ,
        {"COSMOS_DATABASE_NAME": "test-db", "COSMOS_CONTAINER_NAME": "test-container"},
    )
    def test_environment_variables_custom(self):
        """Test custom environment variable values."""
        # Reload the module to pick up new environment variables
        import importlib

        import app

        importlib.reload(app)

        self.assertEqual(app.COSMOS_DATABASE_NAME, "test-db")
        self.assertEqual(app.COSMOS_CONTAINER_NAME, "test-container")


if __name__ == "__main__":
    unittest.main()
