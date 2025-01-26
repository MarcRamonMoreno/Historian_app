import os
import pandas as pd
from datetime import datetime, timedelta
import pyodbc
from typing import Generator, List, Dict, Optional, Tuple
import logging
import shutil
import concurrent.futures
from functools import partial
import threading
from connection_pool import ConnectionPool

def setup_logging():
    """Set up logging configuration"""
    # This can be simplified since we're using Flask's logging
    return logging.getLogger('HistorianProcessor')

logger = setup_logging()

class ConfigurationManager:
    def __init__(self, config_dir: str):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_dir (str): Directory containing configuration files
        """
        self.config_dir = config_dir
        self.logger = logger
        
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            self.logger.info(f"Created configuration directory: {self.config_dir}")

    def list_configurations(self) -> List[str]:
        """List all configuration files."""
        if not os.path.exists(self.config_dir):
            return []
        return sorted([f for f in os.listdir(self.config_dir) if f.endswith('.txt')])

    def create_configuration(self, name: str, tags: List[str]) -> bool:
        """
        Create a new configuration file.
        
        Args:
            name (str): Name of the configuration file
            tags (List[str]): List of tags to include
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not name.endswith('.txt'):
                name = f"{name}.txt"
            
            file_path = os.path.join(self.config_dir, name)
            
            if os.path.exists(file_path):
                self.logger.error(f"Configuration file {name} already exists")
                return False
            
            with open(file_path, 'w') as f:
                for tag in tags:
                    f.write(f"{tag}\n")
            
            self.logger.info(f"Created configuration file: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating configuration file {name}: {str(e)}")
            return False

    def read_configuration(self, config_file: str) -> List[str]:
        """Read configuration file and return list of tags."""
        config_path = os.path.join(self.config_dir, config_file)
        try:
            with open(config_path, 'r') as f:
                tags = []
                for line in f:
                    tag = line.strip()
                    if tag:
                        # Add MELSRV01 prefix and F_CV suffix if not present
                        if not tag.startswith('MELSRV01.'):
                            tag = f"MELSRV01.{tag}"
                        if not tag.endswith('.F_CV'):
                            tag = f"{tag}.F_CV"
                        tags.append(tag)
            return tags
        except Exception as e:
            self.logger.error(f"Error reading configuration file {config_file}: {str(e)}")
            return []

    def update_configuration(self, name: str, tags: List[str]) -> bool:
        """
        Update an existing configuration file.
        
        Args:
            name (str): Name of the configuration file
            tags (List[str]): New list of tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.config_dir, name)
            if not os.path.exists(file_path):
                self.logger.error(f"Configuration file {name} not found")
                return False
            
            # Create backup
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w') as f:
                for tag in tags:
                    f.write(f"{tag}\n")
            
            self.logger.info(f"Updated configuration file: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating configuration file {name}: {str(e)}")
            # Restore from backup if exists
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            return False

    def delete_configuration(self, name: str) -> bool:
        """
        Delete a configuration file.
        
        Args:
            name (str): Name of the configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.config_dir, name)
            if not os.path.exists(file_path):
                self.logger.error(f"Configuration file {name} not found")
                return False
            
            # Create backup before deletion
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            
            os.remove(file_path)
            self.logger.info(f"Deleted configuration file: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting configuration file {name}: {str(e)}")
            return False

class OptimizedHistorianProcessor:
    def __init__(self, config_dir: str, output_dir: str):  
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.logger = setup_logging()
        self.conn_str = (
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=172.16.0.1,1433\\WIN911;'  # Using IP directly
            'DATABASE=master;'
            'UID=mpp;'
            'PWD=Melissa2014;'
            'TrustServerCertificate=yes;'
            'Encrypt=no;'
            'LoginTimeout=60'  # Increased timeout
        )
        self.conn_pool = ConnectionPool(self.conn_str, pool_size=5)        

    def get_db_connection(self):
        return pyodbc.connect(self.conn_str)

    def test_database_connection(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            self.logger.error("Full stack trace:", exc_info=True)
            return False

    def test_database_functionality(self):
        self.logger.info("Starting database functionality test")
        return self.test_database_connection()

    def read_configuration(self, config_file: str) -> List[str]:
        config_path = os.path.join(self.config_dir, config_file)
        try:
            with open(config_path, 'r') as f:
                tags = []
                for line in f:
                    tag = line.strip()
                    if tag:
                        if not tag.startswith('MELSRV01.'):
                            tag = f"MELSRV01.{tag}"
                        if not tag.endswith('.F_CV'):
                            tag = f"{tag}.F_CV"
                        tags.append(tag)
                return tags
        except Exception as e:
            self.logger.error(f"Error reading configuration: {str(e)}")
            return []

    def validate_tags(self, tags: List[str]) -> List[str]:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                valid_tags = []
                for tag in tags:
                    try:
                        query = f"""
                            SELECT * FROM OPENQUERY(
                                HISTORIAN_LINK, 
                                'SELECT tagname FROM ihtags WHERE tagname = ''{tag}'''
                            )
                        """
                        cursor.execute(query)
                        if cursor.fetchone():
                            valid_tags.append(tag)
                    except Exception as tag_error:
                        self.logger.warning(f"Error validating tag {tag}: {str(tag_error)}")
                        continue
                return valid_tags
        except Exception as e:
            self.logger.error(f"Error validating tags: {str(e)}")
            return []
        
    def process_data(self, tag: str, start_date: datetime, end_date: datetime, frequency_ms: int) -> Optional[pd.DataFrame]:
        try:
            query = f"""
                SELECT * FROM OPENQUERY(
                    HISTORIAN_LINK, 
                    'SELECT tagname, timestamp, value, quality 
                     FROM ihrawdata WITH (NOLOCK)
                     WHERE tagname = ''{tag}''
                     AND timestamp >= ''{start_date.strftime("%Y-%m-%d %H:%M:%S")}'' 
                     AND timestamp < ''{end_date.strftime("%Y-%m-%d %H:%M:%S")}''
                     AND samplingmode = ''Interpolated''
                     AND intervalmilliseconds = {frequency_ms}'
                )"""
    
            with self.get_db_connection() as conn:
                conn.timeout = 300  # 5 minutes timeout
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
    
                if rows:
                    data = {
                        'tagname': [row[0] for row in rows],
                        'datetime': [row[1] for row in rows],
                        'value': [row[2] for row in rows],
                        'quality': [row[3] for row in rows]
                    }
                    df = pd.DataFrame(data)
                    df.set_index('datetime', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    df = df[~df.index.duplicated(keep='first')]
                    df = df[['value']]
                    df.columns = [tag.replace('MELSRV01.', '').replace('.F_CV', '')]
                    return df
    
            return None
    
        except Exception as e:
            self.logger.error(f"Error processing data for tag {tag}: {str(e)}", exc_info=True)
            return None

    def merge_dataframes(self, dfs: Dict[str, pd.DataFrame], frequency_ms: int) -> pd.DataFrame:
        if not dfs:
            return pd.DataFrame()

        try:
            # Create fixed time range
            dates = list(dfs.values())[0].index
            start_time = dates.min()
            end_time = dates.max()

            # Create time range using the frequency
            freq_sec = frequency_ms / 1000
            time_range = pd.date_range(
                start=start_time,
                end=end_time,
                freq=f'{int(freq_sec)}S',
                inclusive='both'
            )

            # Process each dataframe
            processed_dfs = {}
            for tag, df in dfs.items():
                df = df.apply(pd.to_numeric, errors='coerce')
                df = df.reindex(time_range, method='ffill')
                processed_dfs[tag] = df

            # Merge dataframes
            merged_df = pd.concat(processed_dfs.values(), axis=1, join='outer')
            merged_df.index = merged_df.index.strftime('%Y-%m-%d %H:%M:%S')

            return merged_df

        except Exception as e:
            self.logger.error(f"Error merging dataframes: {str(e)}")
            return pd.DataFrame()