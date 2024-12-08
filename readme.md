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

3. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3002
- Backend API: http://localhost:5002

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

## Configuration

The application uses several environment variables that can be configured:
- `FLASK_ENV`: Flask environment (development/production)
- `REACT_APP_API_URL`: Backend API URL
- Database connection parameters in `historian_processor.py`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
