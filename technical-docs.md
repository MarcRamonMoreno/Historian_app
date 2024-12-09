# Historian Data Tool - Technical Documentation

## System Overview

The Historian Data Tool is a full-stack web application designed for processing and managing historical time-series data. The system consists of a Python Flask backend and a React frontend, both containerized using Docker.

## Architecture

### Backend Components

#### Core Services
- **Flask Web Server**: Handles HTTP requests and API endpoints
- **Historian Processor**: Manages data retrieval and processing from the SQL Server database
- **Configuration Manager**: Handles tag configuration file management

#### Technology Stack
- Python 3.10
- Flask 2.3.3
- SQLServer with ODBC Driver 18
- Gunicorn WSGI server

### Frontend Components

#### Core Features
- **Data Processor Interface**: Manages data extraction requests
- **Configuration Manager Interface**: Handles tag configuration
- **Tag Browser**: Allows searching and viewing available tags

#### Technology Stack
- React 18.2.0
- Tailwind CSS
- Custom UI components

### Database Schema

```sql
CREATE TABLE TagData (
    ID BIGINT IDENTITY(1,1) NOT NULL,
    TagName NVARCHAR(255) NOT NULL,
    Timestamp DATETIME2 NOT NULL,
    Value FLOAT NOT NULL,
    ImportDate DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT PK_TagData PRIMARY KEY (ID),
    CONSTRAINT UQ_TagData_TagName_Timestamp UNIQUE (TagName, Timestamp)
);
```

## Backend Implementation Details

### Data Processing Pipeline

1. **Tag Validation**
   - Validates requested tags against database
   - Filters out invalid or non-existent tags

2. **Data Retrieval**
   - Uses optimized SQL queries with chunked processing
   - Implements memory-efficient data handling
   ```python
   def process_data_in_chunks(self, tag: str, start_date: datetime, end_date: datetime, frequency: str)
   ```

3. **Data Processing**
   - Aggregates data based on specified frequency
   - Handles missing values through forward/backward filling
   - Merges multiple tag datasets

### Configuration Management

1. **File Operations**
   - Creates and manages tag configuration files
   - Implements backup functionality for configuration changes
   ```python
   def create_configuration(self, name: str, tags: List[str]) -> bool
   def update_configuration(self, name: str, tags: List[str]) -> bool
   ```

2. **Error Handling**
   - Implements comprehensive error logging
   - Provides detailed error messages for client feedback

### API Endpoints

| Endpoint | Method | Description |
|----------|---------|------------|
| `/status` | GET | Health check endpoint |
| `/api/tags/all` | GET | Retrieve all available tags |
| `/api/configurations` | GET | List all configurations |
| `/api/configurations/create` | POST | Create new configuration |
| `/api/configurations/save` | POST | Update existing configuration |
| `/api/configurations/delete` | POST | Delete configuration |
| `/api/process` | POST | Process data for given configuration |
| `/api/download/<filename>` | GET | Download processed file |

## Frontend Implementation Details

### Component Structure

1. **App Component**
   - Main navigation
   - View management between Data Processor and Configuration Manager

2. **DataProcessor Component**
   - Date range selection
   - Configuration selection
   - Processing requests management
   - File download handling

3. **ConfigManager Component**
   - Configuration creation/deletion
   - Tag management interface
   - Tag search functionality

### State Management

- Uses React's useState for local state management
- Implements useEffect for data fetching and side effects
- Manages form state and validation

### UI Components

Custom UI components built with Tailwind CSS:
- Alert
- Button
- Input
- Select

## Deployment

### Docker Configuration

#### Backend Container
```dockerfile
FROM python:3.10-slim
# Configuration for Python backend
# Includes ODBC driver setup and Python dependencies
```

#### Frontend Container
```dockerfile
FROM node:18-alpine
# Configuration for React frontend
# Includes npm installation and build process
```

### Environment Configuration

Backend Environment Variables:
- `FLASK_ENV`
- `FLASK_DEBUG`
- `PYTHONUNBUFFERED`

Frontend Environment Variables:
- `NODE_ENV`
- `REACT_APP_API_URL`
- `PORT`
- `HOST`

## Performance Considerations

### Backend Optimizations

1. **Database Access**
   - Implements connection pooling
   - Uses optimized SQL queries with proper indexing
   - Implements chunked data processing

2. **Memory Management**
   - Streams large datasets
   - Implements generator patterns for data processing
   - Uses efficient data structures

### Frontend Optimizations

1. **Data Loading**
   - Implements pagination for large datasets
   - Uses efficient data caching
   - Optimizes component rendering

2. **UI Responsiveness**
   - Implements loading states
   - Provides immediate user feedback
   - Handles errors gracefully

## Security Considerations

1. **Database Security**
   - Uses parameterized queries
   - Implements proper connection string management
   - Uses least privilege principle

2. **API Security**
   - Implements CORS protection
   - Validates all input data
   - Implements rate limiting through Gunicorn

## Maintenance and Monitoring

1. **Logging**
   - Implements rotating file logs
   - Captures application errors
   - Monitors system health

2. **Error Handling**
   - Implements global error handling
   - Provides detailed error messages
   - Implements backup and recovery procedures

## Future Considerations

1. **Scalability Improvements**
   - Implement caching layer
   - Add load balancing
   - Optimize database queries further

2. **Feature Additions**
   - Add user authentication
   - Implement real-time data viewing
   - Add advanced data visualization options

## Appendix

### Dependencies

Backend Dependencies:
```
flask==2.3.3
flask-cors==4.0.0
numpy==1.24.3
pandas==2.1.0
pyodbc==4.0.39
python-dateutil==2.8.2
python-dotenv==1.0.0
```

Frontend Dependencies:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "tailwindcss": "^3.3.5"
  }
}
```
