from functools import lru_cache
from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import os
import logging
from historian_processor import OptimizedHistorianProcessor, ConfigurationManager
from datetime import datetime, timedelta
import pandas as pd
import pyodbc
import threading
from typing import List
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Cache for filtered and paginated results
_tag_cache = {}
_cache_time = {}
CACHE_DURATION = 300  # 5 minutes

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logging():
    # Create formatters and handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/historian.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for info and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure Flask app logger
    app_logger = logging.getLogger('historian_app')
    app_logger.setLevel(logging.DEBUG)
    
    # Configure SQLAlchemy logger for SQL queries
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    
    return app_logger

# Initialize logger
logger = setup_logging()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Add this to see request details
@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

# Add this to log response details
@app.after_request
def log_response_info(response):
    logger.debug('Response: %s', response.get_data())
    return response

# Update your error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", str(e))
    return jsonify({"error": str(e)}), 500

# Constants
CONFIG_DIR = os.path.abspath(os.path.join(os.getcwd(), "configurations"))
OUTPUT_DIR = "/tmp/csv_processor_output"

# Global tag storage
_all_tags: List[str] = []
_tags_lock = threading.Lock()
_last_refresh = 0
    
def get_db_connection():
    conn_str = (
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=172.16.0.1,1433\\WIN911;'  # Using IP directly
        'DATABASE=master;'
        'UID=mpp;'
        'PWD=Melissa2014;'
        'TrustServerCertificate=yes;'
        'Encrypt=no;'
        'LoginTimeout=60'  # Increased timeout
    )
    return pyodbc.connect(conn_str)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/status', methods=['GET'])
def health_check():
    try:
        logger.info("Performing health check...")
        
        # Check database connectivity
        try:
            conn = get_db_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                cursor.execute("SELECT TOP 1 * FROM OPENQUERY(HISTORIAN_LINK, 'SELECT tagname FROM ihtags')")
                tag_result = cursor.fetchone()
                historian_status = "connected" if tag_result else "no tags found"
                
            db_status = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = f"error: {str(e)}"
            historian_status = "disconnected"
            raise

        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "historian": historian_status,
            "directories": {
                "config_dir": os.path.exists(CONFIG_DIR) and os.access(CONFIG_DIR, os.W_OK),
                "output_dir": os.path.exists(OUTPUT_DIR) and os.access(OUTPUT_DIR, os.W_OK)
            }
        }
        return jsonify(response), 200

    except Exception as e:
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        return jsonify(error_response), 500
    
@app.route('/api/export', methods=['POST'])
def export_data():
    try:
        data = request.json
        tags = data.get('tags', [])
        start_time = datetime.strptime(data.get('startTime'), "%Y-%m-%d %H:%M:%S") 
        end_time = datetime.strptime(data.get('endTime'), "%Y-%m-%d %H:%M:%S")
        
        logger.info(f"Starting export for {len(tags)} tags from {start_time} to {end_time}")
        
        all_data = []
        query_step = timedelta(hours=6)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for tag in tags:
                if not tag.startswith('MELSRV01.'):
                    tag = f"MELSRV01.{tag}"
                if not tag.endswith('.F_CV'):
                    tag = f"{tag}.F_CV"
                
                current_time = start_time
                while current_time <= end_time:
                    chunk_end = min(current_time + query_step, end_time)
                    
                    query = f"""
                        SELECT * FROM OPENQUERY(
                            HISTORIAN_LINK,
                            'SELECT tagname, timestamp, value, quality 
                             FROM ihrawdata 
                             WHERE tagname = ''{tag}''
                             AND timestamp >= ''{current_time.strftime("%Y-%m-%d %H:%M:%S")}'' 
                             AND timestamp <= ''{chunk_end.strftime("%Y-%m-%d %H:%M:%S")}''
                             AND samplingmode = ''Interpolated''
                             AND intervalmilliseconds = 5000'
                        )"""
                    
                    cursor.execute(query)
                    chunk_data = cursor.fetchall()
                    if chunk_data:
                        formatted_data = [(row.tagname, row.timestamp, row.value, row.quality) for row in chunk_data]
                        all_data.extend(formatted_data)
                    
                    current_time += query_step
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        
        if not all_data:
            return jsonify({"error": "No data found for the specified criteria"}), 404
          
        # Create DataFrame with all data
        df = pd.DataFrame(all_data, columns=['tagname', 'timestamp', 'value', 'quality'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Pivot the data to get timestamps as index and tags as columns
        pivoted_df = df.pivot(index='timestamp', columns='tagname', values='value')
        
        # Clean up column names (remove MELSRV01. and .F_CV)
        pivoted_df.columns = pivoted_df.columns.str.replace('MELSRV01.', '').str.replace('.F_CV', '')
        
        # Sort by timestamp
        pivoted_df.sort_index(inplace=True)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"historian_export_{timestamp}.csv"
        output_path = os.path.join(OUTPUT_DIR, filename)
        pivoted_df.to_csv(output_path)
        
        return jsonify({
            "message": "Data exported successfully",
            "filename": filename
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lru_cache(maxsize=128)
def get_filtered_tags(search_term: str) -> List[str]:
    """Cache filtered tag results"""
    if search_term:
        return [tag for tag in _all_tags if search_term in tag.lower()]
    return _all_tags

def get_cache_key(search: str, page: int, per_page: int) -> str:
    """Generate a cache key for the query"""
    return f"{search}:{page}:{per_page}"

@app.route('/api/tags', methods=['GET'])
def get_available_tags():
    try:
        with open('available_tags.txt', 'r') as f:
            tags = [line.strip() for line in f if line.strip()]
        return jsonify({'tags': tags})
    except Exception as e:
        return jsonify({'error': str(e)}), 404


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
        logger.error(f"Error creating configuration: {str(e)}")
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
        logger.error(f"Error saving configuration: {str(e)}")
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
        logger.error(f"Error deleting configuration: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        data = request.json
        config_name = data.get('configuration')
        start_date = datetime.strptime(data.get('startDate'), "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(data.get('endDate'), "%Y-%m-%d %H:%M:%S")
        frequency = data.get('frequency')

        logger.info(f"Processing request for config: {config_name}, period: {start_date} to {end_date}")

        processor = OptimizedHistorianProcessor(CONFIG_DIR, OUTPUT_DIR)
        if not processor.test_database_functionality():  # Using the correct method
            logger.warning("Database functionality tests failed - some features may not work correctly")

        tags = processor.read_configuration(config_name)
        valid_tags = processor.validate_tags(tags)  # This method uses get_db_connection internally

        if not valid_tags:
            return jsonify({"error": "No valid tags found"}), 400

        dataframes = {}
        for tag in valid_tags:
            logger.info(f"Processing tag: {tag}")
            df = processor.process_data(tag, start_date, end_date, frequency)
            if df is not None and not df.empty:
                dataframes[tag] = df

        if not dataframes:
            return jsonify({"error": "No data processed"}), 400

        # Merge dataframes
        logger.info("Merging dataframes")
        merged_df = processor.merge_dataframes(dataframes, frequency)

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{config_name.replace('.txt', '')}_{timestamp}.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        logger.info(f"Saving to file: {output_filename}")
        merged_df.to_csv(output_path, index=True)

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
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info(f"Starting server with CONFIG_DIR: {CONFIG_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=True)