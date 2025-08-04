# PCAP Replaya

A comprehensive web application for replaying network packet capture (PCAP) files using tcpreplay. Built with React frontend, Flask backend, and fully containerized with Docker.

## Features

### Core Functionality
- **File Upload**: Drag-and-drop PCAP file upload with validation (supports .pcap, .pcapng, .cap up to 1GB)
- **PCAP Analysis**: Automatic analysis of uploaded files showing packet count, duration, protocols, and file format using Scapy
- **Advanced Packet Manipulation**: Comprehensive packet modification capabilities before replay
  - **IP Address Mapping**: Replace source and destination IP addresses (IPv4 and IPv6)
  - **MAC Address Mapping**: Modify source and destination MAC addresses
  - **Port Mapping**: Change TCP/UDP port numbers for traffic redirection
  - **VLAN Operations**: Add, remove, or modify VLAN tags on packets
  - **Timestamp Shifting**: Adjust packet timestamps for time-based testing
  - **Payload Replacement**: Search and replace patterns in packet payloads
- **Manipulation Preview**: Preview packet modifications before applying them with before/after comparison
- **Manipulation Templates**: Pre-configured scenarios for common manipulation tasks
- **Interface Selection**: Dynamic detection and selection of available network interfaces using psutil
- **Speed Control**: Flexible replay speed configuration with two modes:
  - **Multiplier**: Real-time speed multiplier (e.g., 1.0x = real-time, 2.0x = double speed)
  - **PPS**: Packets per second (up to 1,000,000 pps)
- **Real-time Monitoring**: Live progress tracking with WebSocket updates via Flask-SocketIO
- **Process Management**: Start, stop, and monitor replay operations with tcpreplay integration
- **Replay History**: Persistent history of all replay operations with status tracking and pagination

### Technical Features
- **Dockerized Deployment**: Complete containerization with multi-stage Docker builds
- **tcpreplay Integration**: Built-in tcpreplay installation and management with process monitoring
- **Security**: Input validation, file type verification using magic bytes, and secure file handling
- **Responsive UI**: Modern Material-UI interface with drag-and-drop file upload
- **Error Handling**: Comprehensive error handling and user feedback with timeout protection
- **Structured Logging**: Detailed logging for debugging and monitoring with log streaming
- **Performance Optimization**: Large file handling with analysis limits and memory-efficient processing

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Flask Backend  │    │   tcpreplay     │
│                 │    │                 │    │                 │
│ • File Upload   │◄──►│ • API Endpoints │◄──►│ • Packet Replay │
│ • Config UI     │    │ • File Handling │    │ • Progress Mon. │
│ • Progress Mon. │    │ • WebSocket     │    │ • Speed Control │
│ • Real-time UI  │    │ • Process Mgmt  │    │ • Interface Mgmt│
│ • History View  │    │ • History Svc   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Docker      │
                    │   Environment   │
                    │                 │
                    │ • Nginx Proxy   │
                    │ • Host Network  │
                    │ • Privileged    │
                    │ • Volume Mounts │
                    └─────────────────┘
```

## Technology Stack

### Backend
- **Flask 2.3.3** - Web framework
- **Flask-SocketIO 5.3.6** - Real-time WebSocket communication
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **Scapy 2.5.0** - PCAP file analysis and packet manipulation
- **psutil 5.9.5** - System and network interface monitoring
- **python-magic 0.4.27** - File type detection using magic bytes
- **tcpreplay** - Network packet replay utility

### Frontend
- **React 18.2.0** - Frontend framework
- **Material-UI 5.14.1** - UI component library
- **axios 1.4.0** - HTTP client for API communication
- **socket.io-client 4.7.2** - WebSocket client
- **react-dropzone 14.2.3** - Drag-and-drop file upload

### Infrastructure
- **Docker & Docker Compose** - Containerization and orchestration
- **Nginx** - Reverse proxy and static file serving
- **Python 3.11** - Backend runtime
- **Node.js 18** - Frontend build environment

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Linux environment (for network interface access)
- Root/sudo privileges (required for tcpreplay network access)

### Option 1: Quick Deploy (Recommended)
**One-command deployment using pre-built Docker images:**

```bash
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/quick-deploy.sh | sudo bash
```

This will:
- Download the production configuration
- Pull pre-built images from Docker Hub
- Generate secure environment variables
- Start the application automatically

### Option 2: Production Deployment
**Using pre-built Docker images:**

```bash
# Download production docker-compose file
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/docker-compose.prod.yml -o docker-compose.yml

# Start with pre-built images
sudo docker-compose up -d
```

### Option 3: Development Build
**Build from source:**

```bash
# Clone the repository
git clone https://github.com/blink-zero/pcap-replaya.git
cd pcap-replaya

# Build and start
sudo docker-compose up --build
```

### Access the Application
- Frontend: http://localhost
- Backend API: http://localhost:5000/api
- Works with any IP address (localhost, 10.150.0.140, domain names)

## Updating Your Deployment

### Manual Update Process
To update to the latest version:

```bash
# Navigate to your deployment directory
cd pcap-replaya-deploy

# Pull latest images
sudo docker-compose pull

# Stop current containers
sudo docker-compose down

# Start with new images
sudo docker-compose up -d

# Check status
sudo docker-compose ps
```

### Update Features
The manual update process will:
- ✅ Pull the latest Docker images
- ✅ Preserve your existing configuration and data
- ✅ Maintain your `.env` file and settings
- ✅ Keep your replay history and uploaded files
- ✅ Restart services with zero configuration changes needed

### Troubleshooting Updates
If you encounter issues during update:

```bash
# Check logs
sudo docker-compose logs

# Restart services
sudo docker-compose restart

# Full reset (preserves data)
sudo docker-compose down
sudo docker-compose up -d
```

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Usage

### 1. Upload PCAP File
- Drag and drop a PCAP file onto the upload area or click to select
- Supported formats: .pcap, .pcapng, .cap
- Maximum file size: 1GB
- The system will automatically analyze the file and display:
  - File format and size
  - Packet count and duration (limited to 100,000 packets for performance)
  - Detected protocols (IP, IPv6, TCP, UDP, ICMP)
  - Analysis warnings for large files

### 2. Configure Replay Settings
- **Network Interface**: Select from dynamically detected network interfaces
- **Speed Control**: Choose between:
  - **Multiplier**: Speed multiplier (e.g., 1.0x = real-time, 2.0x = double speed, max 100x)
  - **PPS**: Packets per second (max 1,000,000 pps)

### 3. Start Replay
- Click "Start Replay" to begin packet replay using tcpreplay
- Monitor real-time progress including:
  - Progress percentage
  - Packets sent
  - Data transmitted
  - Elapsed time
  - Packets per second rate
- Use "Stop" button to halt replay at any time
- View replay history with status and statistics

### 4. Monitor and Logs
- Real-time log streaming via WebSocket
- Live system status monitoring (CPU, memory, disk usage)
- Replay history with detailed statistics
- Error handling and user feedback

## API Documentation

### Endpoints

#### Health Check
- `GET /api/health` - Application health status

#### File Management
- `POST /api/upload` - Upload PCAP file (multipart/form-data)
- `GET /api/upload/status/{file_id}` - Get upload status
- `DELETE /api/upload/cleanup/{file_id}` - Clean up uploaded file

#### System Information
- `GET /api/interfaces` - List network interfaces with status and IP addresses
- `GET /api/system/status` - Get system resource status (CPU, memory, disk, tcpreplay availability)
- `GET /api/system/capabilities` - Get system capabilities and tcpreplay features

#### Replay Control
- `POST /api/replay/start` - Start PCAP replay with configuration
- `POST /api/replay/stop` - Stop current replay
- `GET /api/replay/status` - Get current replay status and progress
- `GET /api/replay/history` - Get replay history (last 50 entries)
- `POST /api/replay/validate` - Validate replay configuration

#### Packet Manipulation
- `POST /api/manipulation/analyze` - Analyze PCAP for manipulation opportunities
- `POST /api/manipulation/preview` - Preview packet modifications before applying
- `POST /api/manipulation/apply` - Apply manipulation rules and create modified PCAP
- `POST /api/manipulation/replay` - Apply manipulation and start replay in one operation
- `GET /api/manipulation/templates` - Get predefined manipulation templates
- `POST /api/manipulation/validate` - Validate manipulation rules
- `DELETE /api/manipulation/cleanup` - Clean up temporary manipulation files

#### Logging
- `GET /api/logs/recent` - Get recent log entries
- `GET /api/logs/stats` - Get logging statistics

### WebSocket Events
- `replay_status` - Replay status updates (starting, running, completed, failed, stopped)
- `replay_progress` - Real-time progress updates (every 2 seconds during replay)
- `log_stream` - Live log streaming

### Request/Response Examples

#### Start Replay
```json
POST /api/replay/start
{
  "file_id": "uuid-of-uploaded-file",
  "interface": "eth0",
  "speed": 2.0,
  "speed_unit": "multiplier"
}
```

#### Replay Status Response
```json
{
  "replay_id": "uuid",
  "status": "running",
  "progress_percent": 45,
  "packets_sent": 1250,
  "bytes_sent": 892400,
  "elapsed_time": 12.5,
  "packets_per_second": 100.0
}
```

## Configuration

### Environment Variables

#### Backend Configuration
- `FLASK_ENV` - Flask environment (development/production)
- `UPLOAD_FOLDER` - Directory for uploaded files (default: /tmp/pcap_uploads)
- `LOG_FILE` - Log file path (default: /var/log/pcap_replaya.log)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR, default: INFO)
- `SECRET_KEY` - Flask secret key for sessions
- `MAX_ANALYSIS_PACKETS` - Maximum packets to analyze (default: 1,000,000)

#### Frontend Configuration
- `REACT_APP_API_URL` - Backend API URL (default: /api)

### Docker Configuration

The application uses Docker Compose with the following services:

#### Backend Service
- **Base Image**: python:3.11-slim
- **Network Mode**: host (required for network interface access)
- **Privileged**: true (required for tcpreplay)
- **Dependencies**: tcpreplay, tcpdump, libpcap-dev, python3-dev
- **Volumes**: pcap_uploads, logs
- **Health Check**: HTTP health endpoint

#### Frontend Service
- **Build Stage**: node:18-alpine (for building React app)
- **Runtime Stage**: nginx:alpine (for serving static files)
- **Network Mode**: host (for backend communication)
- **Configuration**: Custom nginx.conf with API proxying

#### Key Docker Features
- Multi-stage builds for optimized image sizes
- Host networking for direct interface access
- Privileged containers for network operations
- Volume persistence for uploads and logs
- Health checks for service monitoring

## Security Considerations

### File Upload Security
- **File Type Validation**: Magic byte verification for PCAP files
- **File Size Limits**: 1GB maximum upload size
- **Filename Sanitization**: Secure filename handling with werkzeug
- **Temporary Storage**: Secure temporary file storage with cleanup
- **Upload Timeouts**: 5-minute timeout for large file uploads and analysis

### Network Security
- **Input Validation**: Comprehensive validation for all API endpoints
- **CORS Configuration**: Controlled cross-origin access
- **Security Headers**: X-Frame-Options, X-XSS-Protection, Content-Security-Policy
- **Interface Validation**: Alphanumeric interface name validation
- **Speed Limits**: Maximum speed limits to prevent system overload

### Container Security
- **Privileged Access**: Required only for network interface access
- **Host Network**: Necessary for direct interface manipulation
- **Volume Isolation**: Isolated storage for uploads and logs
- **Health Monitoring**: Container health checks and restart policies

### Deployment Security
- **Environment Variables**: Sensitive configuration via environment variables
- **Log Security**: Structured logging without sensitive data exposure
- **Process Isolation**: Containerized process isolation
- **Access Control**: Root privileges only where necessary

## Troubleshooting

### Common Issues

#### 1. Permission Denied for Network Interfaces
```bash
# Ensure Docker has necessary privileges
sudo docker-compose down
sudo docker-compose up --build
```

#### 2. tcpreplay Not Found or Not Working
```bash
# Check tcpreplay installation in container
docker-compose exec backend tcpreplay --version

# Rebuild backend container
docker-compose build backend --no-cache
```

#### 3. File Upload Fails
- **Check file size**: Maximum 1GB supported
- **Verify file format**: Only .pcap, .pcapng, .cap files accepted
- **Check disk space**: Ensure sufficient storage available
- **Review timeout**: Large files may take several minutes to analyze

#### 4. Network Interface Not Listed
- **Check container privileges**: Ensure privileged mode is enabled
- **Verify host network**: Container must use host networking
- **Check interface status**: `ip link show` to verify interface exists
- **Interface permissions**: Ensure interface is accessible

#### 5. Replay Fails to Start
- **Interface access**: Verify tcpreplay can access the interface
- **File corruption**: Re-upload the PCAP file
- **Speed settings**: Check speed configuration is within limits
- **System resources**: Ensure sufficient CPU and memory

#### 6. WebSocket Connection Issues
- **Proxy configuration**: Check nginx WebSocket proxy settings
- **Firewall**: Ensure ports 80 and 5000 are accessible
- **Browser compatibility**: Modern browsers required for WebSocket support

### Debugging Commands

#### View Application Logs
```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# System logs
docker-compose exec backend tail -f /var/log/pcap_replaya.log
```

#### Check System Status
```bash
# Container status
docker-compose ps

# System resources
docker-compose exec backend python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"

# Network interfaces
docker-compose exec backend python -c "
import psutil
for name, addrs in psutil.net_if_addrs().items():
    print(f'{name}: {[addr.address for addr in addrs]}')"
```

#### Test tcpreplay
```bash
# Check tcpreplay version
docker-compose exec backend tcpreplay --version

# Test interface access (replace eth0 with your interface)
docker-compose exec backend tcpreplay --intf1 eth0 --dualfile
```

### Performance Optimization

#### Large File Handling
- Files with >100,000 packets have limited analysis for performance
- Full replay capability maintained regardless of analysis limits
- Memory-efficient processing using Scapy's PcapReader
- Progress monitoring optimized to update every 2 seconds

#### System Requirements
- **Minimum**: 2GB RAM, 2 CPU cores, 10GB disk space
- **Recommended**: 4GB RAM, 4 CPU cores, 50GB disk space
- **Network**: Gigabit Ethernet for high-speed replay

## Development

### Project Structure
```
PCAP_Replaya/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask application with SocketIO
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── routes/                # API route handlers
│   │   ├── upload.py         # File upload endpoints
│   │   ├── replay.py         # Replay control endpoints
│   │   ├── system.py         # System information endpoints
│   │   └── logs.py           # Logging endpoints
│   ├── services/              # Business logic services
│   │   ├── pcap_service.py   # PCAP analysis using Scapy
│   │   ├── replay_service.py # tcpreplay management
│   │   ├── history_service.py# Replay history management
│   │   └── log_service.py    # Log streaming service
│   └── utils/                 # Utility functions
│       ├── validators.py     # Input validation
│       └── logger.py         # Logging configuration
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── App.js            # Main application component
│   │   ├── components/       # React components
│   │   │   ├── FileUpload.js # Drag-and-drop file upload
│   │   │   ├── ReplayConfig.js# Replay configuration
│   │   │   ├── ProgressMonitor.js# Real-time progress
│   │   │   ├── ReplayHistory.js# History display
│   │   │   ├── LiveLog.js    # Log streaming
│   │   │   └── UserGuide.js  # Help documentation
│   │   └── services/
│   │       └── api.js        # API client with axios
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
├── Dockerfile.backend        # Backend container definition
├── Dockerfile.frontend       # Frontend container definition
├── docker-compose.yml        # Container orchestration
├── nginx.conf               # Nginx reverse proxy configuration
├── start.sh                 # Application startup script
├── clean-rebuild.sh         # Development rebuild script
└── README.md               # This documentation
```

### Development Workflow

#### Adding New Features

1. **Backend Development**
   - Add new routes in `backend/routes/`
   - Implement business logic in `backend/services/`
   - Add utilities in `backend/utils/`
   - Update configuration in `config.py`
   - Add tests and update documentation

2. **Frontend Development**
   - Create new components in `frontend/src/components/`
   - Add API calls in `frontend/src/services/api.js`
   - Update main app in `frontend/src/App.js`
   - Add Material-UI styling and responsive design

3. **Integration**
   - Update Docker configurations if needed
   - Test with full Docker Compose stack
   - Update API documentation
   - Add error handling and validation

#### Code Quality Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ES6+ features and React best practices
- **Error Handling**: Comprehensive error handling with user feedback
- **Logging**: Structured logging for debugging and monitoring
- **Security**: Input validation and secure coding practices
- **Performance**: Optimize for large file handling and real-time updates

### Testing

#### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

#### Frontend Testing
```bash
cd frontend
npm test
```

#### Integration Testing
```bash
# Start application
sudo docker-compose up --build -d

# Run integration tests
curl http://localhost:5000/api/health
curl http://localhost/

# Test file upload
curl -X POST -F "file=@test.pcap" http://localhost:5000/api/upload
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the development guidelines
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

### Development Guidelines
- Follow existing code style and patterns
- Add comprehensive error handling
- Include logging for debugging
- Update API documentation for new endpoints
- Test with various PCAP file sizes and formats
- Ensure responsive UI design

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs using the debugging commands
3. Check system requirements and dependencies
4. Create an issue on the repository with:
   - System information (OS, Docker version)
   - Error logs and screenshots
   - Steps to reproduce the issue
   - PCAP file characteristics (if applicable)

## Acknowledgments

- **tcpreplay** - Network packet replay utility for Linux
- **Scapy** - Powerful Python library for packet manipulation and analysis
- **React** - Frontend framework for building user interfaces
- **Flask** - Lightweight Python web framework
- **Material-UI** - React UI component library
- **Docker** - Containerization platform for deployment
- **Nginx** - High-performance web server and reverse proxy
- **psutil** - Cross-platform library for system and process monitoring

## Version History

- **v1.3.0** - Advanced packet manipulation capabilities
  - Added comprehensive packet manipulation system with IP/MAC/Port mapping
  - Implemented VLAN operations and timestamp shifting capabilities
  - Added packet analysis engine with protocol detection
  - Created manipulation preview system with before/after comparison
  - Added manipulation templates for common scenarios
  - Integrated manipulation workflow into main UI
  - Enhanced API with manipulation endpoints
  - Added Scapy-based packet processing with streaming support

- **v1.2.1** - Docker version display and search fixes
  - Fixed VERSION file not being found in Docker containers
  - Fixed search input focus issue in replay history
  - Enhanced error logging and fallback version handling
  - Added debouncing to search input for better performance

- **v1.2.0** - Version information and search functionality
  - Added version information display throughout UI
  - Restored broken search functionality in replay history
  - Enhanced history service with search and status filtering
  - Improved performance with server-side filtering

- **v1.1.0** - Enhanced replay history with pagination
  - Added pagination support for replay history (20 items per page)
  - Improved performance for large history datasets
  - Enhanced filtering and search functionality
  - Better user experience with navigation controls
  - Backend API optimization with limit/offset parameters

- **v1.0.0** - Initial release with core PCAP replay functionality
  - File upload and analysis
  - tcpreplay integration
  - Real-time monitoring
  - Docker containerization
  - Material-UI interface
  - WebSocket communication
  - Replay history tracking
