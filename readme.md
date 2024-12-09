# Historian Data Tool

A secure internal web application for processing and managing historical data with a React frontend and Flask backend. The application is accessible only through Tailscale VPN connection.

## Important Security Notice

**VPN Required**: This application is only accessible through Tailscale VPN. You must have:
- Tailscale VPN installed on your device
- Network access granted by administrator
- Valid connection credentials

## Access Requirements

1. **Tailscale VPN Setup**
   - Install Tailscale VPN from [https://tailscale.com/download](https://tailscale.com/download)
   - Request network access from administrator
   - Connect using provided credentials
   - Verify VPN connection status

2. **Application Access**
   - Frontend: `http://hostname:3002`
   - Backend API: `http://hostname:5002`
   - Contact administrator for actual hostname

## Features

- Secure VPN-based access
- Data processing with configurable time ranges
- Tag configuration management
- Real-time tag search and filtering
- CSV file generation and download
- Docker containerization for deployment

## Tech Stack

### Backend
- Python 3.10
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
- Python 3.10+ (for local development)
- SQL Server ODBC Driver 18
- Tailscale VPN client

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
- Frontend: `http://localhost:3002`
- Backend API: `http://localhost:5002`

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
│   ├── available_tags.txt     # List of available tags
│   ├── Dockerfile            # Backend container configuration
│   ├── gunicorn.conf.py      # Gunicorn server configuration 
│   ├── historian_processor.py # Data processing logic
│   └── requirements.txt       # Python dependencies
├── configurations/            # Tag configurations directory
├── docker-compose.yml        # Docker services configuration
├── frontend/
│   ├── Dockerfile           # Frontend container configuration
│   ├── package.json         # Frontend dependencies
│   ├── postcss.config.js    # PostCSS configuration
│   ├── public/
│   │   └── index.html      # HTML entry point
│   ├── src/
│   │   ├── App.js          # Main application component
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── alert.jsx   # Alert component
│   │   │       ├── button.jsx  # Button component
│   │   │       └── input.jsx   # Input component
│   │   ├── ConfigManager.js # Configuration management
│   │   ├── DataProcessor.js # Data processing interface
│   │   ├── hooks/
│   │   │   └── useAPI.js    # API hook utilities
│   │   ├── index.css       # Global styles
│   │   ├── index.js        # React entry point
│   │   └── lib/
│   │       └── utils.js     # Utility functions
│   └── tailwind.config.js   # Tailwind CSS configuration
├── .gitignore              # Git ignore rules
├── readme.md               # Project documentation
└── technical-docs.md       # Technical documentation
```

## Configuration

The application uses several environment variables that can be configured:
- `FLASK_ENV`: Flask environment (development/production)
- `REACT_APP_API_URL`: Backend API URL
- Database connection parameters in `historian_processor.py`

## Documentation

- See `technical-docs.md` for technical documentation
- See `user-guide.md` for detailed usage instructions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

- Access restricted to Tailscale VPN network
- Secure database connections
- Data validation and sanitization
- Error logging and monitoring

## License

This project is licensed under the MIT License - see the LICENSE file for details.