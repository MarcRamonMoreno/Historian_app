
import os
import pandas as pd
from datetime import datetime, timedelta
import pyodbc
from typing import List, Dict, Generator, Optional
import logging
from logging.handlers import RotatingFileHandler
import shutil


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

    def read_configuration(self, name: str) -> List[str]:
        """
        Read tags from a configuration file.
        
        Args:
            name (str): Name of the configuration file
            
        Returns:
            List[str]: List of tags in the configuration
        """
        try:
            file_path = os.path.join(self.config_dir, name)
            if not os.path.exists(file_path):
                self.logger.error(f"Configuration file {name} not found")
                return []
            
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
                
        except Exception as e:
            self.logger.error(f"Error reading configuration file {name}: {str(e)}")
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
        """Initialize the Historian processor."""
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.logger = logger
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def get_db_connection(self) -> pyodbc.Connection:
        """Create and return an optimized database connection"""
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=100.97.52.112;"
            "DATABASE=HistorianData;"
            "UID=mpp;"
            "PWD=MPP_DataBase_2024##;"
            "TrustServerCertificate=yes;"
            "MARS_Connection=yes;"
            "Packet Size=32768"
        )
        return pyodbc.connect(conn_str)

    @staticmethod
    def convert_time_to_minutes(time_str: str) -> int:
        """Convert time string in HH:MM:SS format to total minutes."""
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_minutes = hours * 60 + minutes + (seconds / 60)
            return round(total_minutes)
        except Exception as e:
            raise ValueError(f"Invalid time format. Expected HH:MM:SS, got {time_str}. Error: {str(e)}")

    def read_configuration(self, config_file: str) -> List[str]:
        """Read configuration file and return list of tags."""
        config_path = os.path.join(self.config_dir, config_file)
        try:
            with open(config_path, 'r') as f:
                tags = []
                for line in f:
                    tag = line.strip()
                    if tag:
                        if tag.endswith('.F_CV.csv'):
                            tag = tag[:-9]
                        if not tag.startswith('MELSRV01.'):
                            tag = f"MELSRV01.{tag}"
                        tags.append(tag)
            return tags
        except Exception as e:
            self.logger.error(f"Error reading configuration file {config_file}: {str(e)}")
            return []

    def validate_tags(self, tags: List[str]) -> List[str]:
        """Validate tags exist in database."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                valid_tags = []
                
                for tag in tags:
                    cursor.execute("""
                        SELECT TOP 1 1 
                        FROM TagData WITH (NOLOCK) 
                        WHERE TagName = ?
                    """, (tag,))
                    
                    if cursor.fetchone():
                        valid_tags.append(tag)
                    else:
                        self.logger.warning(f"Tag not found in database: {tag}")
                
                return valid_tags
                
        except Exception as e:
            self.logger.error(f"Error validating tags: {str(e)}")
            return []

    def process_data(self, tag: str, start_date: datetime, end_date: datetime, frequency: str) -> Optional[pd.DataFrame]:
        """Process data for a given tag"""
        try:
            self.logger.info(f"Processing data for tag {tag}")
            dataframes = []
            
            # Collect chunks from the generator
            for chunk in self.process_data_in_chunks(tag, start_date, end_date, frequency):
                if chunk is not None and not chunk.empty:
                    dataframes.append(chunk)
                    self.logger.debug(f"Collected chunk with {len(chunk)} rows")
            
            # If no data was collected, return None
            if not dataframes:
                self.logger.warning(f"No data collected for tag {tag}")
                return None
            
            # Concatenate all chunks and sort by timestamp
            result = pd.concat(dataframes)
            result.sort_index(inplace=True)
            
            # Log summary statistics
            self.logger.info(f"Processed data for {tag}:")
            self.logger.info(f"Total data points: {len(result):,}")
            self.logger.info(f"Date range: {result.index.min()} to {result.index.max()}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing data for tag {tag}: {str(e)}")
            return None

    def process_data_in_chunks(self, tag: str, start_date: datetime, end_date: datetime, frequency: str) -> Generator[pd.DataFrame, None, None]:
        """Generate dataframes in chunks to optimize memory usage"""
        try:
            interval_minutes = self.convert_time_to_minutes(frequency)
            chunk_size = timedelta(days=1)  # Process one day at a time

            current_chunk_start = start_date
            while current_chunk_start < end_date:
                current_chunk_end = min(current_chunk_start + chunk_size, end_date)

                try:
                    with self.get_db_connection() as conn:
                        query = """
                        WITH TimeBuckets AS (
                            SELECT 
                                DATEADD(MINUTE, 
                                    (DATEDIFF(MINUTE, '2000-01-01', Timestamp) / ?) * ?,
                                    '2000-01-01'
                                ) as bucket_timestamp,
                                Value
                            FROM TagData WITH (NOLOCK)
                            WHERE TagName = ?
                            AND Timestamp >= ?
                            AND Timestamp < ?
                        )
                        SELECT 
                            bucket_timestamp as timestamp,
                            AVG(Value) as value
                        FROM TimeBuckets
                        GROUP BY bucket_timestamp
                        ORDER BY bucket_timestamp
                        """

                        # Convert to list of tuples first to avoid pandas warning
                        cursor = conn.cursor()
                        cursor.execute(query, (
                            interval_minutes,
                            interval_minutes,
                            tag,
                            current_chunk_start,
                            current_chunk_end
                        ))
                        rows = cursor.fetchall()

                        if rows:
                            # Create DataFrame from the list of tuples
                            df_chunk = pd.DataFrame.from_records(
                                rows,
                                columns=['timestamp', 'value']
                            )
                            df_chunk.set_index('timestamp', inplace=True)
                            df_chunk.columns = [tag]
                            self.logger.debug(f"Yielding chunk with {len(df_chunk)} rows for {tag}")
                            yield df_chunk

                except Exception as chunk_error:
                        self.logger.error(f"Error processing chunk for {tag} from {current_chunk_start} to {current_chunk_end}: {str(chunk_error)}")
                        # Continue to next chunk even if this one fails

                current_chunk_start = current_chunk_end

        except Exception as e:
            self.logger.error(f"Error in process_data_in_chunks for {tag}: {str(e)}")
            yield None

    def merge_dataframes(self, dfs: Dict[str, pd.DataFrame], frequency: str) -> pd.DataFrame:
        """Efficiently merge multiple dataframes"""
        if not dfs:
            return pd.DataFrame()

        # Start with the first dataframe
        merged_df = next(iter(dfs.values()))

        # Merge remaining dataframes
        for tag, df in dfs.items():
            if df is not merged_df:
                merged_df = pd.merge(
                    merged_df,
                    df,
                    left_index=True,
                    right_index=True,
                    how='outer'
                )

        # Sort and handle missing values using new preferred methods
        merged_df.sort_index(inplace=True)
        merged_df = merged_df.ffill().bfill()  # Chain the operations instead of using method parameter

        return merged_df