# historian_processor.py
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import pyodbc
from typing import List, Dict
import logging
from logging.handlers import RotatingFileHandler
import shutil


load_dotenv()

def setup_logging():
    """Set up logging configuration"""
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger('HistorianProcessor')
    
    # Only add handlers if the logger doesn't have any
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = RotatingFileHandler('logs/historian_processor.log', maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

class ConfigurationManager:
    def __init__(self, config_dir: str):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_dir (str): Directory containing configuration files
        """
        self.config_dir = config_dir
        self.logger = setup_logging()
        
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

    def add_tags(self, name: str, new_tags: List[str]) -> bool:
        """
        Add tags to an existing configuration file.
        
        Args:
            name (str): Name of the configuration file
            new_tags (List[str]): Tags to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_tags = set(self.read_configuration(name))
            updated_tags = sorted(list(current_tags.union(new_tags)))
            return self.update_configuration(name, updated_tags)
            
        except Exception as e:
            self.logger.error(f"Error adding tags to {name}: {str(e)}")
            return False

    def remove_tags(self, name: str, tags_to_remove: List[str]) -> bool:
        """
        Remove tags from an existing configuration file.
        
        Args:
            name (str): Name of the configuration file
            tags_to_remove (List[str]): Tags to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_tags = set(self.read_configuration(name))
            updated_tags = sorted(list(current_tags - set(tags_to_remove)))
            return self.update_configuration(name, updated_tags)
            
        except Exception as e:
            self.logger.error(f"Error removing tags from {name}: {str(e)}")
            return False
        
def convert_time_to_minutes(time_str: str) -> int:
    """Convert time string in HH:MM:SS format to total minutes."""
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        total_minutes = hours * 60 + minutes + (seconds / 60)
        return round(total_minutes)  # Round to nearest minute
    except Exception as e:
        raise ValueError(f"Invalid time format. Expected HH:MM:SS, got {time_str}. Error: {str(e)}")

class HistorianProcessor:
    def __init__(self, config_dir: str, output_dir: str):
        """Initialize the Historian processor."""
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.logger = setup_logging()
        
        # Database connection string using environment variables
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            "TrustServerCertificate=yes"
        )
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def list_configuration_files(self) -> List[str]:
        """List all txt configuration files."""
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
        return [f for f in os.listdir(self.config_dir) if f.endswith('.txt')]

    def read_configuration(self, config_file: str) -> List[str]:
        """
        Read tag names from a configuration file.
        
        Args:
            config_file (str): Name of the configuration file
            
        Returns:
            List[str]: List of tag names with prefix
        """
        config_path = os.path.join(self.config_dir, config_file)
        try:
            with open(config_path, 'r') as f:
                # Read lines, remove whitespace, empty lines, add prefix
                tags = []
                for line in f:
                    tag = line.strip()
                    if tag:
                        if tag.endswith('.F_CV.csv'):
                            tag = tag[:-9]  # Remove .F_CV.csv
                        if not tag.startswith('MELSRV01.'):
                            tag = f"MELSRV01.{tag}"
                        tags.append(tag)
            return tags
        except Exception as e:
            self.logger.error(f"Error reading configuration file {config_file}: {str(e)}")
            return []

    def validate_tags(self, tags: List[str]) -> List[str]:
        """
        Validate that specified tags exist in the database using a single query.
        
        Args:
            tags (List[str]): List of tag names to validate
            
        Returns:
            List[str]: List of existing tags
        """
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                # Create a temporary table for the tags
                cursor.execute("""
                    IF OBJECT_ID('tempdb..#TagList') IS NOT NULL DROP TABLE #TagList;
                    CREATE TABLE #TagList (TagName NVARCHAR(255));
                """)
                
                # Insert all tags in a single batch
                tags_values = ', '.join(f"('{tag}')" for tag in tags)
                cursor.execute(f"INSERT INTO #TagList (TagName) VALUES {tags_values}")
                
                # Single query to get existing tags
                cursor.execute("""
                    SELECT DISTINCT t.TagName 
                    FROM #TagList t
                    INNER JOIN (
                        SELECT DISTINCT TagName 
                        FROM TagData
                    ) td ON t.TagName = td.TagName
                """)
                
                existing_tags = [row[0] for row in cursor.fetchall()]
                
                # Log missing tags
                missing_tags = set(tags) - set(existing_tags)
                for tag in missing_tags:
                    self.logger.warning(f"Warning: Tag not found in database: {tag}")
                
                return existing_tags
                
        except Exception as e:
            self.logger.error(f"Error validating tags: {str(e)}")
            return []

    def process_data(self, tag: str, start_date: datetime, end_date: datetime, frequency: str) -> pd.DataFrame:
        """
        Query and process data according to date range and frequency.
        
        Args:
            tag (str): Tag name
            start_date (datetime): Start date for filtering
            end_date (datetime): End date for filtering
            frequency (str): Data frequency in HH:MM:SS format
        """
        try:
            # Convert frequency from HH:MM:SS to minutes
            interval_minutes = convert_time_to_minutes(frequency)
            self.logger.debug(f"Converted frequency {frequency} to {interval_minutes} minutes")

            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                
                # Get tag statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as TotalReadings,
                        MIN(Timestamp) as FirstReading,
                        MAX(Timestamp) as LastReading,
                        MIN(Value) as MinValue,
                        MAX(Value) as MaxValue,
                        AVG(Value) as AvgValue
                    FROM TagData 
                    WHERE TagName = ?
                    AND Timestamp BETWEEN ? AND ?
                """, (tag, start_date, end_date))
                
                stats = cursor.fetchone()
                
                if not stats or stats.TotalReadings == 0:
                    self.logger.warning(f"No data found for tag {tag} in specified date range")
                    return None
                
                self.logger.info(f"\nStatistics for {tag}:")
                self.logger.info(f"Total readings: {stats.TotalReadings:,}")
                self.logger.info(f"Date range: {stats.FirstReading} to {stats.LastReading}")
                self.logger.info(f"Value range: {stats.MinValue:.2f} to {stats.MaxValue:.2f}")
                self.logger.info(f"Average value: {stats.AvgValue:.2f}")
                
                # Get the data with proper interval
                cursor.execute("""
                    SELECT 
                        interval_time as timestamp,
                        AVG(Value) as value
                    FROM (
                        SELECT 
                            Value,
                            DATEADD(MINUTE, 
                                (DATEDIFF(MINUTE, '2000-01-01', Timestamp) / ?) * ?,
                                '2000-01-01'
                            ) as interval_time
                        FROM TagData 
                        WHERE TagName = ?
                        AND Timestamp BETWEEN ? AND ?
                    ) as SubQuery
                    GROUP BY interval_time
                    ORDER BY interval_time
                """, (interval_minutes, interval_minutes, tag, start_date, end_date))
                
                # Convert to DataFrame
                rows = cursor.fetchall()
                if not rows:
                    self.logger.warning(f"No data returned for {tag} after resampling")
                    return None
                
                df = pd.DataFrame.from_records(
                    rows,
                    columns=['timestamp', tag]
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                self.logger.info(f"\nProcessed data points: {len(df):,}")
                self.logger.info(f"Data from: {df['timestamp'].min()}")
                self.logger.info(f"Data until: {df['timestamp'].max()}")
                
                return df
                
        except Exception as e:
            self.logger.error(f"Error processing tag {tag}: {str(e)}")
            return None


def manage_configurations():
    """Function to manage configuration files"""
    CONFIG_DIR = "/home/mpp/Historian_csv_processor/configurations"
    config_manager = ConfigurationManager(CONFIG_DIR)
    
    while True:
        print("\nConfiguration Management Menu:")
        print("1. List all configurations")
        print("2. Create new configuration")
        print("3. View configuration content")
        print("4. Add tags to configuration")
        print("5. Remove tags from configuration")
        print("6. Delete configuration")
        print("7. Return to main menu")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            configs = config_manager.list_configurations()
            if configs:
                print("\nAvailable configurations:")
                for i, config in enumerate(configs, 1):
                    print(f"{i}. {config}")
            else:
                print("\nNo configuration files found.")
                
        elif choice == '2':
            name = input("\nEnter configuration name (without .txt): ").strip()
            print("Enter tags (one per line, empty line to finish):")
            tags = []
            while True:
                tag = input().strip()
                if not tag:
                    break
                tags.append(tag)
            
            if config_manager.create_configuration(name, tags):
                print(f"\nConfiguration {name}.txt created successfully.")
            
        elif choice == '3':
            configs = config_manager.list_configurations()
            if not configs:
                print("\nNo configuration files found.")
                continue
                
            print("\nAvailable configurations:")
            for i, config in enumerate(configs, 1):
                print(f"{i}. {config}")
                
            try:
                idx = int(input("\nEnter configuration number: ").strip()) - 1
                if 0 <= idx < len(configs):
                    tags = config_manager.read_configuration(configs[idx])
                    print("\nTags in configuration:")
                    for tag in tags:
                        print(tag)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '4':
            configs = config_manager.list_configurations()
            if not configs:
                print("\nNo configuration files found.")
                continue
                
            print("\nAvailable configurations:")
            for i, config in enumerate(configs, 1):
                print(f"{i}. {config}")
                
            try:
                idx = int(input("\nEnter configuration number: ").strip()) - 1
                if 0 <= idx < len(configs):
                    print("Enter tags to add (one per line, empty line to finish):")
                    new_tags = []
                    while True:
                        tag = input().strip()
                        if not tag:
                            break
                        new_tags.append(tag)
                    
                    if config_manager.add_tags(configs[idx], new_tags):
                        print(f"\nTags added to {configs[idx]} successfully.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '5':
            configs = config_manager.list_configurations()
            if not configs:
                print("\nNo configuration files found.")
                continue
                
            print("\nAvailable configurations:")
            for i, config in enumerate(configs, 1):
                print(f"{i}. {config}")
                
            try:
                idx = int(input("\nEnter configuration number: ").strip()) - 1
                if 0 <= idx < len(configs):
                    tags = config_manager.read_configuration(configs[idx])
                    print("\nCurrent tags:")
                    for i, tag in enumerate(tags, 1):
                        print(f"{i}. {tag}")
                    
                    print("\nEnter tag numbers to remove (comma-separated):")
                    selections = input().strip()
                    try:
                        indices = [int(x.strip()) - 1 for x in selections.split(',')]
                        tags_to_remove = [tags[i] for i in indices if 0 <= i < len(tags)]
                        
                        if config_manager.remove_tags(configs[idx], tags_to_remove):
                            print(f"\nTags removed from {configs[idx]} successfully.")
                    except ValueError:
                        print("Please enter valid numbers.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '6':
            configs = config_manager.list_configurations()
            if not configs:
                print("\nNo configuration files found.")
                continue
                
            print("\nAvailable configurations:")
            for i, config in enumerate(configs, 1):
                print(f"{i}. {config}")
                
            try:
                idx = int(input("\nEnter configuration number to delete: ").strip()) - 1
                if 0 <= idx < len(configs):
                    confirm = input(f"Are you sure you want to delete {configs[idx]}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if config_manager.delete_configuration(configs[idx]):
                            print(f"\nConfiguration {configs[idx]} deleted successfully.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '7':
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    while True:
        print("\nMain Menu:")
        print("1. Process Data")
        print("2. Manage Configurations")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            process_data()
        elif choice == '2':
            manage_configurations()
        elif choice == '3':
            print("\nExiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()