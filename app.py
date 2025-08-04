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
COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
COSMOS_DATABASE_NAME = os.environ.get('COSMOS_DATABASE_NAME', 'webapp-db')
COSMOS_CONTAINER_NAME = os.environ.get('COSMOS_CONTAINER_NAME', 'visitor-logs')

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
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_country_from_ip(ip_address):
    """Get country information from IP address using ip-api.com (free tier)"""
    try:
        # Skip for local IPs
        if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return {
                'country': 'Local/Private',
                'countryCode': 'LOCAL',
                'city': 'Local',
                'region': 'Local'
            }
        
        response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,city,lat,lon,timezone', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'countryCode': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone', 'Unknown')
                }
        
        return {
            'country': 'Unknown',
            'countryCode': 'XX',
            'city': 'Unknown',
            'region': 'Unknown'
        }
    except Exception as e:
        logger.error(f"Error getting country from IP {ip_address}: {e}")
        return {
            'country': 'Error',
            'countryCode': 'XX',
            'city': 'Error',
            'region': 'Error'
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
        visitor_data['id'] = f"{visitor_data['ip_address']}_{int(datetime.now().timestamp())}"
        visitor_data['timestamp'] = datetime.now().isoformat()
        
        container.create_item(body=visitor_data)
        logger.info(f"Saved visitor data to Cosmos DB: {visitor_data['id']}")
        return True
        
    except exceptions.CosmosResourceExistsError:
        logger.warning("Document already exists")
        return True
    except Exception as e:
        logger.error(f"Error saving to Cosmos DB: {e}")
        return False

@app.route('/')
def index():
    """Main page showing visitor information"""
    try:
        # Get client information
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        country_info = get_country_from_ip(client_ip)
        
        # Prepare visitor data
        visitor_data = {
            'ip_address': client_ip,
            'user_agent': user_agent,
            'country': country_info['country'],
            'country_code': country_info['countryCode'],
            'city': country_info['city'],
            'region': country_info['region'],
            'latitude': country_info.get('latitude'),
            'longitude': country_info.get('longitude'),
            'timezone': country_info.get('timezone'),
            'referer': request.headers.get('Referer', 'Direct'),
            'accept_language': request.headers.get('Accept-Language', 'Unknown')
        }
        
        # Save to Cosmos DB
        # cosmos_saved = save_to_cosmos(visitor_data.copy())
        
        # return render_template('index.html', 
        #                      visitor_data=visitor_data,
        #                      cosmos_saved=cosmos_saved)
        return render_template('index.html', 
                             visitor_data=visitor_data,
                             cosmos_saved=True)  # Assuming save is always successful for demo

                             
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/visitor-info')
def api_visitor_info():
    """API endpoint to get visitor information as JSON"""
    try:
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown')
        country_info = get_country_from_ip(client_ip)
        
        return jsonify({
            'ip_address': client_ip,
            'user_agent': user_agent,
            'country_info': country_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test Cosmos DB connection
        client = get_cosmos_client()
        cosmos_status = "connected" if client else "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'cosmos_db': cosmos_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
