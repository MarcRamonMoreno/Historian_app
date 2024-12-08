from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from historian_processor import HistorianProcessor, ConfigurationManager
from datetime import datetime
import pandas as pd
import pyodbc
import time
import threading
from typing import List, Optional

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

# Constants from environment variables
CONFIG_DIR = os.getenv('CONFIG_DIR', os.path.abspath(os.path.join(os.getcwd(), "configurations")))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', "/tmp/csv_processor_output")
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Global tag storage
_all_tags: List[str] = []
_tags_lock = threading.Lock()
_last_refresh = 0

# Database connection string from environment variables
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    "TrustServerCertificate=yes"
)

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def initialize_tags():
    """Initialize tags from database"""
    global _all_tags, _last_refresh
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT TagName FROM TagData WITH (NOLOCK) ORDER BY TagName")
            with _tags_lock:
                _all_tags = [row[0] for row in cursor.fetchall()]
                _last_refresh = time.time()
                logger.info(f"Initialized {len(_all_tags)} tags")
    except Exception as e:
        logger.error(f"Error initializing tags: {str(e)}")
        _all_tags = []

# Create Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": cors_origins.split(',')}})

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize tags at startup
initialize_tags()

@app.route('/status', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global _all_tags
    return jsonify({
        "status": "healthy",
        "environment": FLASK_ENV,
        "tags_loaded": len(_all_tags),
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/tags/available', methods=['GET'])
def get_available_tags():
    """Get available tags with pagination and search"""
    try:
        global _all_tags
        
        # Refresh tags if empty
        if not _all_tags:
            with _tags_lock:
                if not _all_tags:
                    initialize_tags()
        
        # Get query parameters
        search = request.args.get('search', '').strip().lower()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 250))
        
        # Filter tags if search term provided
        filtered_tags = [tag for tag in _all_tags if search in tag.lower()] if search else _all_tags
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_tags = filtered_tags[start_idx:min(end_idx, len(filtered_tags))]
        
        return jsonify({
            "tags": paginated_tags,
            "total": len(filtered_tags),
            "page": page,
            "per_page": per_page,
            "has_more": end_idx < len(filtered_tags)
        })
    except Exception as e:
        logger.error(f"Error in get_available_tags: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/configurations', methods=['GET'])
def list_configurations():
    """List all configurations"""
    try:
        configs = [f for f in os.listdir(CONFIG_DIR) if f.endswith('.txt')]
        configs.sort()
        return jsonify({"configurations": configs})
    except Exception as e:
        logger.error(f"Error listing configurations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/configurations/<config_name>/tags', methods=['GET'])
def get_configuration_tags(config_name):
    """Get tags for a specific configuration"""
    try:
        config_path = os.path.join(CONFIG_DIR, config_name)
        if not os.path.exists(config_path):
            return jsonify({"error": "Configuration not found"}), 404
            
        with open(config_path, 'r') as f:
            tags = [line.strip() for line in f if line.strip()]
        return jsonify({"tags": tags})
    except Exception as e:
        logger.error(f"Error reading configuration {config_name}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/configurations/create', methods=['POST'])
def create_configuration():
    """Create a new configuration"""
    try:
        data = request.json
        name = data.get('name')
        tags = data.get('tags', [])
        
        if not name:
            return jsonify({"error": "Configuration name is required"}), 400
            
        config_manager = ConfigurationManager(CONFIG_DIR)
        if config_manager.create_configuration(name, tags):
            return jsonify({"message": "Configuration created successfully"})
        else:
            return jsonify({"error": "Failed to create configuration"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/configurations/save', methods=['POST'])
def save_configuration():
    """Save/update an existing configuration"""
    try:
        data = request.json
        name = data.get('name')
        tags = data.get('tags', [])
        
        if not name:
            return jsonify({"error": "Configuration name is required"}), 400
            
        config_manager = ConfigurationManager(CONFIG_DIR)
        if config_manager.update_configuration(name, tags):
            return jsonify({"message": "Configuration saved successfully"})
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/configurations/delete', methods=['POST'])
def delete_configuration():
    """Delete a configuration"""
    try:
        data = request.json
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Configuration name is required"}), 400
            
        config_manager = ConfigurationManager(CONFIG_DIR)
        if config_manager.delete_configuration(name):
            return jsonify({"message": "Configuration deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete configuration"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_data():
    """Process data for given configuration and time range"""
    try:
        data = request.json
        config_name = data.get('configuration')
        start_date = datetime.strptime(data.get('startDate'), "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(data.get('endDate'), "%Y-%m-%d %H:%M:%S")
        frequency = data.get('frequency')

        processor = HistorianProcessor(CONFIG_DIR, OUTPUT_DIR)
        tags = processor.read_configuration(config_name)
        valid_tags = processor.validate_tags(tags)

        if not valid_tags:
            return jsonify({"error": "No valid tags found"}), 400

        dataframes = {}
        for tag in valid_tags:
            df = processor.process_data(tag, start_date, end_date, frequency)
            if df is not None and not df.empty:
                dataframes[tag] = df

        if not dataframes:
            return jsonify({"error": "No data processed"}), 400

        # Merge dataframes
        merged_df = None
        for tag, df in dataframes.items():
            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.merge(merged_df, df, on='timestamp', how='outer')

        merged_df = merged_df.sort_values('timestamp')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{config_name.replace('.txt', '')}_{timestamp}.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        merged_df.to_csv(output_path, index=False)

        return jsonify({
            "message": "Data processed successfully",
            "processed_files": [output_filename]
        })

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download processed file"""
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info(f"Starting server in {FLASK_ENV} mode")
    logger.info(f"CONFIG_DIR: {CONFIG_DIR}")
    logger.info(f"OUTPUT_DIR: {OUTPUT_DIR}")
    app.run(host=HOST, port=PORT, debug=FLASK_DEBUG)