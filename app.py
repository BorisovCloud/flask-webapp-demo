import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")
COSMOS_DATABASE_NAME = os.environ.get("COSMOS_DATABASE_NAME", "webapp-db")
COSMOS_CONTAINER_NAME = os.environ.get("COSMOS_CONTAINER_NAME", "visitor-logs")


# Initialize Cosmos DB client
def get_cosmos_client():
    try:
        # Use managed identity for authentication
        credential = DefaultAzureCredential()
        client = CosmosClient(COSMOS_ENDPOINT, credential=credential)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Cosmos client: {e}")
        return None


def get_client_ip():
    """Get the real client IP address, considering proxy headers"""
    # Azure App Service specific headers
    if request.headers.get("X-Azure-ClientIP"):
        ip = request.headers.get("X-Azure-ClientIP")
    elif request.headers.get("X-Forwarded-For"):
        # X-Forwarded-For can contain multiple IPs, get the first one
        ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        ip = request.headers.get("X-Real-IP")
    else:
        ip = request.remote_addr

    # Remove port number if present (format: IP:PORT)
    if ":" in ip and not ip.startswith("["):  # Handle IPv4 with port, but not IPv6
        ip = ip.split(":")[0]

    return ip


def get_country_from_ip(ip_address):
    """Get country information from IP address using ip-api.com (free tier)"""
    try:
        logger.info(f"Getting geolocation for IP: {ip_address}")

        # Skip for local IPs
        if (
            ip_address in ["127.0.0.1", "localhost"]
            or ip_address.startswith("192.168.")
            or ip_address.startswith("10.")
            or ip_address.startswith("172.")
        ):
            logger.info(f"Local/Private IP detected: {ip_address}")
            return {
                "country": "Local/Private",
                "countryCode": "LOCAL",
                "city": "Local",
                "region": "Local",
            }

        # Validate IP format
        if not ip_address or ip_address == "":
            logger.warning("Empty IP address provided")
            return {
                "country": "Invalid IP",
                "countryCode": "XX",
                "city": "Unknown",
                "region": "Unknown",
            }

        url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,city,lat,lon,timezone"
        logger.info(f"Making request to: {url}")

        response = requests.get(url, timeout=10)
        logger.info(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"API response: {data}")

            if data.get("status") == "success":
                result = {
                    "country": data.get("country", "Unknown"),
                    "countryCode": data.get("countryCode", "XX"),
                    "city": data.get("city", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon"),
                    "timezone": data.get("timezone", "Unknown"),
                }
                logger.info(f"Successfully retrieved geolocation: {result}")
                return result
            else:
                logger.error(
                    f"API returned error: {data.get('message', 'Unknown error')}"
                )
                return {
                    "country": f"API Error: {data.get('message', 'Unknown')}",
                    "countryCode": "XX",
                    "city": "Unknown",
                    "region": "Unknown",
                }

        logger.error(f"HTTP error: {response.status_code}")
        return {
            "country": f"HTTP Error: {response.status_code}",
            "countryCode": "XX",
            "city": "Unknown",
            "region": "Unknown",
        }

    except requests.exceptions.Timeout:
        logger.error(f"Timeout getting country from IP {ip_address}")
        return {
            "country": "Timeout Error",
            "countryCode": "XX",
            "city": "Unknown",
            "region": "Unknown",
        }
    except Exception as e:
        logger.error(f"Error getting country from IP {ip_address}: {e}")
        return {
            "country": f"Error: {str(e)}",
            "countryCode": "XX",
            "city": "Error",
            "region": "Error",
        }


def save_to_cosmos(visitor_data):
    """Save visitor data to Cosmos DB"""
    try:
        client = get_cosmos_client()
        if not client:
            logger.error("Cosmos client not available")
            return False

        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)

        # Add timestamp and unique ID
        visitor_data["id"] = (
            f"{visitor_data['ip_address']}_{int(datetime.now().timestamp())}"
        )
        visitor_data["timestamp"] = datetime.now().isoformat()

        container.create_item(body=visitor_data)
        logger.info(f"Saved visitor data to Cosmos DB: {visitor_data['id']}")
        return True

    except exceptions.CosmosResourceExistsError:
        logger.warning("Document already exists")
        return True
    except Exception as e:
        logger.error(f"Error saving to Cosmos DB: {e}")
        return False


@app.route("/")
def index():
    """Main page showing visitor information"""
    try:
        # Get client information
        client_ip = get_client_ip()
        user_agent = request.headers.get("User-Agent", "Unknown")

        # Log headers for debugging
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Extracted IP: {client_ip}")

        country_info = get_country_from_ip(client_ip)

        # Prepare visitor data
        visitor_data = {
            "ip_address": client_ip,
            "user_agent": user_agent,
            "country": country_info["country"],
            "country_code": country_info["countryCode"],
            "city": country_info["city"],
            "region": country_info["region"],
            "latitude": country_info.get("latitude"),
            "longitude": country_info.get("longitude"),
            "timezone": country_info.get("timezone"),
            "referer": request.headers.get("Referer", "Direct"),
            "accept_language": request.headers.get("Accept-Language", "Unknown"),
        }

        logger.info(f"Visitor data: {visitor_data}")

        # Save to Cosmos DB
        cosmos_saved = save_to_cosmos(visitor_data.copy())

        return render_template(
            "index.html", visitor_data=visitor_data, cosmos_saved=cosmos_saved
        )

    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template("error.html", error=str(e)), 500


@app.route("/api/visitor-info")
def api_visitor_info():
    """API endpoint to get visitor information as JSON"""
    try:
        client_ip = get_client_ip()
        user_agent = request.headers.get("User-Agent", "Unknown")
        country_info = get_country_from_ip(client_ip)

        return jsonify(
            {
                "ip_address": client_ip,
                "user_agent": user_agent,
                "country_info": country_info,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error in API route: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test Cosmos DB connection
        client = get_cosmos_client()
        cosmos_status = "connected" if client else "disconnected"

        return jsonify(
            {
                "status": "healthy",
                "cosmos_db": cosmos_status,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


if __name__ == "__main__":
    # For local development
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
