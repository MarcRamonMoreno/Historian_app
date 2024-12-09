# Historian Data Tool

A secure internal web application for processing and managing historical data with a React frontend and Flask backend. The application is accessible only through Tailscale VPN connection.

## Access Requirements

1. **Tailscale VPN**
   - Must have Tailscale VPN installed on your device
   - Need to be granted access to the network by the administrator
   - Join the Tailscale network using provided credentials

2. **Application Access**
   - Frontend: http://hostname:3002
   - Backend API: http://hostname:5002
   - Contact the administrator for actual hostname and access permissions

## Features

- Data processing with configurable time ranges and frequencies
- Configuration management for tag selections
- Real-time tag search and filtering
- CSV file generation and download
- Docker containerization for easy deployment

## Tech Stack

### Backend
- Python 3.x
- Flask
- pandas
- pyodbc
- SQL Server connection

### Frontend
- React
- Tailwind CSS
- Modern React Hooks
- Responsive UI components

## Prerequisites

- Docker and Docker Compose
- Node.js (for local development)
- Python 3.x (for local development)
- SQL Server ODBC Driver 18

## Project Structure and Configuration

```
historian_app/
├── backend/
│   ├── app.py                 # Flask application
│   ├── available_tags.txt     # List of available tags
│   ├── Dockerfile            # Backend container configuration
│   ├── gunicorn.conf.py      # Gunicorn WSGI configuration
│   ├── historian_processor.py # Data processing logic
│   └── requirements.txt      # Python dependencies
├── configurations/           # Tag configurations directory
├── docker-compose.yml       # Docker services configuration
├── frontend/
│   ├── Dockerfile          # Frontend container configuration
│   ├── package.json        # Frontend dependencies
│   ├── postcss.config.js   # PostCSS configuration
│   ├── public/
│   │   └── index.html     # Main HTML file
│   ├── src/
│   │   ├── App.js         # Main application component
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── alert.jsx   # Alert component
│   │   │       ├── button.jsx  # Button component
│   │   │       └── input.jsx   # Input component
│   │   ├── ConfigManager.js    # Configuration management
│   │   ├── DataProcessor.js    # Data processing interface
│   │   ├── hooks/
│   │   │   └── useAPI.js      # API hook
│   │   ├── index.css          # Global styles
│   │   ├── index.js           # Entry point
│   │   └── lib/
│   │       └── utils.js       # Utility functions
│   └── tailwind.config.js     # Tailwind configuration
├── readme.md
└── technical-docs.md          # Technical documentation
```

### Required Configuration Changes

Before deploying the application, you need to update several configuration files:

1. **Database Connection Configuration**
   
   In both `backend/app.py` and `backend/historian_processor.py`, update the database connection string:
   ```python
   conn_str = (
       "DRIVER={ODBC Driver 18 for SQL Server};"
       "SERVER=hostname;"            # Replace with your SQL Server hostname
       "DATABASE=database_name;"     # Replace with your database name
       "UID=database_username;"      # Replace with your database username
       "PWD=database_password;"      # Replace with your database password
       "TrustServerCertificate=yes;"
       "MARS_Connection=yes;"
       "Packet Size=32768"
   )
   ```

2. **Docker Compose Configuration**
   
   In `docker-compose.yml`, update the hostname for both services:
   ```yaml
   services:
     backend:
       ports:
         - "hostname:5002:5000"    # Replace hostname with your actual hostname
     
     frontend:
       ports:
         - "hostname:3002:3000"    # Replace hostname with your actual hostname
       environment:
         - REACT_APP_API_URL=http://hostname:5002/api    # Replace hostname
   ```

3. **Frontend API Configuration**
   
   In `frontend/src/hooks/useAPI.js`, update the default API URL:
   ```javascript
   const API_URL = process.env.REACT_APP_API_URL || 'http://hostname:5002/api';  // Replace hostname
   ```

4. **Available Tags Configuration**
   
   Update `backend/available_tags.txt` with your list of available tags:
   ```text
   TT_4112_AVG
   AT_1011_02
   CL1001_FEED_VOLUME_SP
   ...
   ```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/historian-data-tool.git
cd historian-data-tool
```

2. Create necessary directories:
```bash
mkdir -p configurations
```

3. Configure the application:
   - Update database credentials in backend files
   - Set the appropriate hostname in docker-compose.yml
   - Update available_tags.txt

4. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://your_hostname:3002
- Backend API: http://your_hostname:5002

## Development Setup

### Backend
1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask application:
```bash
python app.py
```

### Frontend
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in app.py and historian_processor.py
   - Ensure SQL Server is accessible from the application
   - Check if ODBC Driver 18 is properly installed

2. **Port Conflicts**
   - Ensure ports 3002 and 5002 are available
   - Check for other services using these ports
   - Modify docker-compose.yml if needed

3. **Configuration Issues**
   - Verify hostname configuration in all relevant files
   - Ensure configuration files have correct permissions
   - Check if available_tags.txt exists and contains valid tags

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security Notes

- Always use secure passwords and keep them confidential
- Regularly update dependencies for security patches
- Use HTTPS in production environments
- Implement proper access controls and authentication
- Regular security audits and updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact your system administrator or open an issue in the repository.