# Historian Data Tool

A secure web application for processing and managing historical time-series data, featuring a React frontend and Flask backend. This application is designed to be accessed exclusively through a Tailscale VPN connection for enhanced security.

## Prerequisites

### Required
- Tailscale VPN installed on your device
- Tailscale network access (contact your administrator for credentials)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### For Development/Local Setup
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)
- SQL Server ODBC Driver 18

## VPN Setup

1. **Install Tailscale VPN**
   - Download Tailscale from [https://tailscale.com/download](https://tailscale.com/download)
   - Follow the installation instructions for your operating system
   - Contact your system administrator for:
     - Tailscale network credentials
     - Network access permissions
     - Application hostname

2. **Connect to VPN**
   - Open Tailscale VPN client
   - Log in using provided credentials
   - Verify connection status
   - Test connectivity to application hostname (provided by administrator)

## Accessing the Application

Once connected to the Tailscale VPN:
- Frontend Interface: `http://hostname:3002`
- Backend API: `http://hostname:5002`
- Replace 'hostname' with the actual hostname provided by your administrator

## Using the Application

### Data Processing

1. **Select Configuration**
   - Navigate to "Data Processor" tab
   - Choose an existing configuration from the dropdown menu
   - View included tags for the selected configuration

2. **Set Time Range**
   - Select start date and time
   - Select end date and time
   - Set data frequency (default: 00:10:00 format)
   - Common frequencies:
     - 00:01:00 (1 minute)
     - 00:10:00 (10 minutes)
     - 01:00:00 (1 hour)

3. **Process Data**
   - Click "Process Data" button
   - Wait for processing to complete
   - Download generated CSV files

### Managing Configurations

1. **Create New Configuration**
   - Navigate to "Configuration Manager" tab
   - Enter configuration name
   - Click "Create Configuration"

2. **Edit Configuration**
   - Select existing configuration
   - Search available tags
   - Add/remove tags as needed
   - Changes are saved automatically

3. **Delete Configuration**
   - Select configuration to delete
   - Click "Delete Configuration"
   - Confirm deletion

### Working with Tags

1. **Searching Tags**
   - Use search box in Configuration Manager
   - Tags are filtered as you type
   - View all available tags in the right panel

2. **Managing Tags in Configuration**
   - Click "Add to Config" to add tags
   - Click "Remove" to remove tags
   - View all selected tags in the left panel

## Troubleshooting

### Common Issues

1. **Cannot Access Application**
   - Verify Tailscale VPN is connected
   - Check if correct hostname is being used
   - Contact administrator for network access verification

2. **Processing Errors**
   - Verify selected time range is valid
   - Check if configuration contains valid tags
   - Ensure frequency format is correct (HH:MM:SS)

3. **Configuration Issues**
   - Ensure configuration name is unique
   - Verify tag selections are valid
   - Check for any error messages in red

### Error Messages

- "Configuration not found": Select a valid configuration
- "No data processed": Check time range and tag validity
- "API request failed": Verify VPN connection and try again

## Best Practices

1. **Data Processing**
   - Use appropriate time ranges (avoid extremely large ranges)
   - Select relevant frequency for your analysis
   - Download processed files promptly

2. **Configuration Management**
   - Use descriptive configuration names
   - Regularly review and update tag selections
   - Back up important configurations

3. **System Usage**
   - Log out of VPN when not in use
   - Clear downloaded files regularly
   - Report any issues to system administrator

## Support

For technical support or access issues:
1. Contact your system administrator
2. Provide specific error messages
3. Include details about:
   - VPN connection status
   - Browser being used
   - Actions that led to the issue

## Security Notes

- Never share VPN credentials
- Keep application URLs confidential
- Log out of VPN when done
- Report any security concerns immediately

## Updates and Maintenance

The application undergoes regular updates. Your administrator will notify you of:
- Scheduled maintenance windows
- New feature releases
- Required actions from users
- System upgrades

Remember to stay connected to Tailscale VPN throughout your session with the application.