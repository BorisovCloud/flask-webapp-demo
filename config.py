import os

from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()


class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

    # Azure Cosmos DB settings
    COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")
    COSMOS_DATABASE_NAME = os.environ.get("COSMOS_DATABASE_NAME", "webapp-db")
    COSMOS_CONTAINER_NAME = os.environ.get("COSMOS_CONTAINER_NAME", "visitor-logs")

    # Application settings
    PORT = int(os.environ.get("PORT", 8000))

    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        required_vars = ["COSMOS_ENDPOINT"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return True


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
