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
        
        # Set up logging
        self.logger = logging.getLogger('HistorianProcessor')
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Add file handler
        fh = RotatingFileHandler(
            'logs/historian.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")
        
        # Test database connection on initialization
        self.test_database_connection()

    def test_database_functionality(self):
        """Test all database-related functionality."""
        self.logger.info("Starting database functionality test")

        try:
            # 1. Test basic connection
            self.logger.info("Testing database connection...")
            if not self.test_database_connection():
                self.logger.error("Failed basic connection test")
                return False

            # 2. Test sample tag query
            tag = "MELSRV01.CL3011_O2_VOLUME"
            self.logger.info(f"Testing tag query for: {tag}")

            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TOP 1 1 FROM TagData WHERE TagName = ?", (tag,))
                if cursor.fetchone():
                    self.logger.info(f"Tag {tag} exists in database")
                else:
                    self.logger.warning(f"Tag {tag} not found in database")

            # 3. Test data retrieval
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()

            self.logger.info(f"Testing data retrieval for period: {start_date} to {end_date}")
            if self.verify_data_exists(tag, start_date, end_date):
                self.logger.info("Data verification test passed")
            else:
                self.logger.warning("Data verification test failed")

            return True

        except Exception as e:
            self.logger.error(f"Database functionality test failed: {str(e)}")
            self.logger.exception("Full stack trace:")
            return False
        
    def get_db_connection(self) -> pyodbc.Connection:
        """Create and return an optimized database connection"""
        try:
            conn_str = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                "SERVER=100.97.52.112,1433;"  # Add port number
                "DATABASE=HistorianData;"
                "UID=mpp;"
                "PWD=MPP_DataBase_2024##;"
                "TrustServerCertificate=yes;"
                "MARS_Connection=yes;"
                "Connection Timeout=30;"  # Increase connection timeout
                "Packet Size=32768;"
                "APP=HistorianProcessor"
            )

            self.logger.debug("Attempting database connection...")
            conn = pyodbc.connect(conn_str, timeout=30)

            # Configure connection settings
            conn.timeout = 30
            conn.autocommit = True

            # Test connection with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            self.logger.debug(f"Connected to database: {version}")

            return conn

        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            self.logger.exception("Full connection error details:")
            raise

    def test_database_connection(self) -> bool:
        """Test database connection and verify table structure."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Test basic connection
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                self.logger.info(f"Connected to SQL Server version: {version}")
                
                # Verify TagData table exists
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'TagData'
                """)
                if cursor.fetchone()[0] == 0:
                    self.logger.error("TagData table not found in database")
                    return False
                    
                # Sample query to verify permissions
                cursor.execute("SELECT TOP 1 * FROM TagData WITH (NOLOCK)")
                row = cursor.fetchone()
                if row:
                    self.logger.info("Successfully queried TagData table")
                    return True
                else:
                    self.logger.warning("TagData table exists but is empty")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            self.logger.exception("Full stack trace:")
            return False

    def verify_data_exists(self, tag: str, start_date: datetime, end_date: datetime) -> bool:
        """Verify data exists for the given tag and time range."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # First check if tag exists
                check_tag_sql = "SELECT TOP 1 1 FROM TagData WITH (NOLOCK) WHERE TagName = ?"
                self.logger.debug(f"Executing tag check query: {check_tag_sql} with tag: {tag}")
                cursor.execute(check_tag_sql, (tag,))
                
                if not cursor.fetchone():
                    self.logger.warning(f"Tag {tag} not found in database")
                    return False
                
                # Then check for data in the time range
                check_data_sql = """
                SELECT TOP 1 1 
                FROM TagData WITH (NOLOCK) 
                WHERE TagName = ? 
                AND Timestamp >= ? 
                AND Timestamp < ?
                """
                
                self.logger.debug(
                    f"Executing data check query: {check_data_sql} "
                    f"with params: {tag}, {start_date}, {end_date}"
                )
                
                cursor.execute(check_data_sql, (tag, start_date, end_date))
                has_data = cursor.fetchone() is not None
                
                if has_data:
                    self.logger.info(f"Found data for tag {tag} in specified time range")
                else:
                    self.logger.warning(f"No data found for tag {tag} in specified time range")
                
                return has_data
                
        except Exception as e:
            self.logger.error(f"Error in verify_data_exists: {str(e)}")
            self.logger.exception("Full stack trace:")
            return False

    @staticmethod
    def convert_time_to_seconds(time_str: str) -> int:
        """Convert time string in HH:MM:SS format to total seconds."""
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            if total_seconds <= 0:
                raise ValueError("Time interval must be greater than zero")
            return total_seconds
        except Exception as e:
            raise ValueError(f"Invalid time format. Expected HH:MM:SS, got {time_str}. Error: {str(e)}")

    @staticmethod
    def convert_time_to_minutes(time_str: str) -> int:
        """Convert time string in HH:MM:SS format to total minutes (deprecated)."""
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

    def validate_frequency(self, frequency: str) -> bool:
        """Validate the frequency string format and value."""
        try:
            # Check format
            if not isinstance(frequency, str) or not frequency.count(':') == 2:
                return False

            # Parse and validate values
            hours, minutes, seconds = map(int, frequency.split(':'))

            # Basic range checks
            if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                return False

            # Check if total duration is greater than zero
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds > 0

        except ValueError:
            return False


    def process_data(self, tag: str, start_date: datetime, end_date: datetime, frequency: str) -> Optional[pd.DataFrame]:
        """Process data for a given tag."""
        try:
            self.logger.info(f"Starting data processing for tag {tag}")
            self.logger.info(f"Time range: {start_date} to {end_date}")
            self.logger.info(f"Frequency: {frequency}")

            # First verify data exists
            if not self.verify_data_exists(tag, start_date, end_date):
                self.logger.warning(f"No data available for tag {tag} in specified time range")
                return None

            # Continue with processing if data exists
            dataframes = []
            for chunk in self.process_data_in_chunks(tag, start_date, end_date, frequency):
                if chunk is not None and not chunk.empty:
                    dataframes.append(chunk)
                    self.logger.debug(f"Added chunk with {len(chunk)} rows")

            if not dataframes:
                self.logger.warning(f"No data processed for tag {tag}")
                return None

            # Combine all chunks
            result = pd.concat(dataframes)
            result.sort_index(inplace=True)
            
            self.logger.info(f"Successfully processed {len(result)} total rows for tag {tag}")
            return result

        except Exception as e:
            self.logger.error(f"Error processing data for tag {tag}: {str(e)}")
            self.logger.exception("Full exception details:")
            return None
        
    def debug_sql_query(self, query: str, params: dict) -> None:
        """Debug a SQL query by logging the actual query that would be executed."""
        try:
            # Create a copy of the query for debugging
            debug_query = query

            # Replace parameters with their actual values
            for key, value in params.items():
                if isinstance(value, str):
                    # Escape single quotes in strings
                    escaped_value = value.replace("'", "''")
                    debug_query = debug_query.replace(f'@{key}', f"'{escaped_value}'")
                elif isinstance(value, datetime):
                    # Format datetime objects
                    debug_query = debug_query.replace(f'@{key}', f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                else:
                    # Handle other types
                    debug_query = debug_query.replace(f'@{key}', str(value))

            # Log the complete query
            self.logger.debug("Executing SQL Query:")
            self.logger.debug(debug_query)

            # Log the parameters separately
            self.logger.debug("Parameters:")
            for key, value in params.items():
                self.logger.debug(f"{key}: {value} (type: {type(value)})")

        except Exception as e:
            self.logger.error(f"Error in debug_sql_query: {str(e)}")

    def process_data_in_chunks(self, tag: str, start_date: datetime, end_date: datetime, frequency: str) -> Generator[pd.DataFrame, None, None]:
        """Generate dataframes in chunks to optimize memory usage"""
        try:
            # Parse and validate frequency
            hours, minutes, seconds = map(int, frequency.split(':'))
            interval_seconds = hours * 3600 + minutes * 60 + seconds
            
            self.logger.info(f"Starting process_data_in_chunks with parameters:")
            self.logger.info(f"Tag: {tag}")
            self.logger.info(f"Start date: {start_date}")
            self.logger.info(f"End date: {end_date}")
            self.logger.info(f"Frequency: {frequency} (converted to {interval_seconds} seconds)")
    
            if interval_seconds == 0:
                self.logger.error("Invalid interval: frequency cannot be zero")
                yield None
                return
    
            chunk_size = timedelta(days=1)
            current_chunk_start = start_date
    
            while current_chunk_start < end_date:
                current_chunk_end = min(current_chunk_start + chunk_size, end_date)
                
                try:
                    with self.get_db_connection() as conn:
                        # Modified query to properly handle timestamp grouping
                        query = """
                        WITH TimeBuckets AS (
                            SELECT 
                                DATEADD(
                                    SECOND,
                                    CAST((DATEDIFF(SECOND, ?, Timestamp) / ?) * ? AS BIGINT),
                                    ?
                                ) as bucket_timestamp,
                                Value
                            FROM TagData WITH (NOLOCK)
                            WHERE 
                                TagName = ?
                                AND Timestamp >= ?
                                AND Timestamp < ?
                                AND Value IS NOT NULL
                        )
                        SELECT 
                            bucket_timestamp,
                            AVG(CAST(Value AS FLOAT)) as value,
                            COUNT(*) as data_points
                        FROM TimeBuckets
                        GROUP BY bucket_timestamp
                        HAVING COUNT(*) > 0
                        ORDER BY bucket_timestamp
                        """
    
                        # Parameters for both the DATEADD and WHERE clauses
                        params = (
                            current_chunk_start,  # DATEADD reference point
                            interval_seconds,      # Division interval
                            interval_seconds,      # Multiplication interval
                            current_chunk_start,   # DATEADD base
                            tag,                   # WHERE TagName
                            current_chunk_start,   # WHERE start time
                            current_chunk_end      # WHERE end time
                        )
    
                        self.logger.debug(f"Executing query for chunk {current_chunk_start} to {current_chunk_end}")
                        self.logger.debug(f"Query parameters: {params}")
                        
                        cursor = conn.cursor()
                        cursor.execute(query, params)
                        rows = cursor.fetchall()
    
                        if rows:
                            self.logger.info(f"Retrieved {len(rows)} rows for chunk")
                            df_chunk = pd.DataFrame.from_records(
                                rows,
                                columns=['timestamp', 'value', 'data_points']
                            )
                            df_chunk.set_index('timestamp', inplace=True)
                            df_chunk = df_chunk.drop('data_points', axis=1)
                            df_chunk.columns = [tag]
                            yield df_chunk
                        else:
                            self.logger.warning(f"No data found for period {current_chunk_start} to {current_chunk_end}")
    
                except Exception as chunk_error:
                    self.logger.error(f"Error processing chunk for {tag} from {current_chunk_start} to {current_chunk_end}")
                    self.logger.error(f"Error details: {str(chunk_error)}")
                    self.logger.exception("Full stack trace:")
                    continue
                    
                current_chunk_start = current_chunk_end
    
        except Exception as e:
            self.logger.error(f"Error in process_data_in_chunks: {str(e)}")
            self.logger.exception("Full stack trace:")
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