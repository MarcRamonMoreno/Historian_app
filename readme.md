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

## Configuration

### Environment Variables and Credentials

Before deploying the application, you need to configure several important parameters:

1. **Database Configuration**
   Edit `historian_processor.py` and `app.py` to update the database connection string:
   ```python
   conn_str = (
       "DRIVER={ODBC Driver 18 for SQL Server};"
       "SERVER=your_server_hostname;"  # Replace with your SQL Server hostname
       "DATABASE=your_database_name;"   # Replace with your database name
       "UID=your_username;"            # Replace with your database username
       "PWD=your_password;"            # Replace with your database password
       "TrustServerCertificate=yes;"
       "MARS_Connection=yes;"
       "Packet Size=32768"
   )
   ```

2. **Hostname Configuration**
   - In `docker-compose.yml`:
     ```yaml
     ports:
       - "your_hostname:5002:5000"  # Replace your_hostname with actual hostname
       - "your_hostname:3002:3000"  # Replace your_hostname with actual hostname
     ```
   - In `frontend/.env`:
     ```
     REACT_APP_API_URL=http://your_hostname:5002/api
     ```

3. **Create Environment Files**
   
   Create a `.env` file in the project root:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   DATABASE_SERVER=your_server_hostname
   DATABASE_NAME=your_database_name
   DATABASE_USER=your_username
   DATABASE_PASSWORD=your_password
   ```

4. **Security Considerations**
   - Never commit `.env` files or files containing credentials to version control
   - Use environment-specific configurations for development and production
   - Consider using a secrets management service for production deployments

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
   - Update database credentials as described in the Configuration section
   - Set the appropriate hostname in docker-compose.yml
   - Create and configure .env files

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

3. Set up environment variables:
```bash
cp .env.example .env  # Create from template
# Edit .env with your configurations
```

4. Run the Flask application:
```bash
python app.py
```

### Frontend
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env  # Create from template
# Edit .env with your configurations
```

3. Start the development server:
```bash
npm start
```

## Project Structure

```
historian_app/
├── backend/
│   ├── app.py                 # Flask application
│   ├── historian_processor.py # Data processing logic
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container configuration
├── configurations/           # Tag configurations directory
├── docker-compose.yml       # Docker services configuration
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── App.js          # Main application component
    │   ├── ConfigManager.js # Configuration management
    │   └── DataProcessor.js # Data processing interface
    ├── package.json        # Frontend dependencies
    └── Dockerfile         # Frontend container configuration
```

## Environment Variables Reference

### Backend Variables
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode
- `DATABASE_SERVER`: SQL Server hostname
- `DATABASE_NAME`: Database name
- `DATABASE_USER`: Database username
- `DATABASE_PASSWORD`: Database password
- `PYTHONUNBUFFERED`: Python output buffering

### Frontend Variables
- `REACT_APP_API_URL`: Backend API URL
- `NODE_ENV`: Node environment (development/production)
- `PORT`: Frontend port (default: 3000)
- `HOST`: Frontend host (default: 0.0.0.0)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in .env file
   - Ensure SQL Server is accessible from the application
   - Check if ODBC Driver 18 is properly installed

2. **Port Conflicts**
   - Ensure ports 3002 and 5002 are available
   - Check for other services using these ports
   - Modify docker-compose.yml if needed

3. **Configuration Issues**
   - Verify all environment variables are properly set
   - Check hostname configuration in all relevant files
   - Ensure configuration files have correct permissions

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