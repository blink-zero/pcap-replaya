# PCAP Replaya

A modern web application for replaying network packet capture (PCAP) files using tcpreplay. Built with React frontend, Flask backend, and fully containerized with Docker.

![Version](https://img.shields.io/badge/version-1.3.9-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## ✨ Features

- **📁 File Upload**: Drag-and-drop PCAP upload with validation (.pcap, .pcapng, .cap up to 1GB)
- **📊 PCAP Analysis**: Automatic analysis showing packet count, duration, and protocols
- **🔄 Flexible Replay**: Speed control with multiplier or PPS modes
- **🔁 Continuous Replay**: Loop PCAP files continuously until manually stopped
- **📈 Real-time Monitoring**: Live progress tracking with WebSocket updates
- **📋 Replay History**: Persistent history with pagination, search, and filtering
- **⬇️ Download Feature**: Download previously replayed PCAP files
- **🖥️ Interface Selection**: Dynamic network interface detection
- **📱 Responsive UI**: Modern Material-UI interface

## 🚀 Quick Start

### One-Command Deployment (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/quick-deploy.sh | sudo bash
```

### Manual Deployment

```bash
# Download production configuration
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/docker-compose.prod.yml -o docker-compose.yml

# Start the application
sudo docker-compose up -d
```

### Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000/api

## 📋 Prerequisites

- Docker and Docker Compose
- Linux environment (for network interface access)
- Root/sudo privileges (required for tcpreplay network access)

## 🔄 Updating

### Quick Update
```bash
cd pcap-replaya-deploy
curl -sSL https://raw.githubusercontent.com/blink-zero/pcap-replaya/main/update.sh | sudo bash
```

### Manual Update
```bash
sudo docker-compose pull
sudo docker-compose down
sudo docker-compose up -d
```

## 📖 Usage

### 1. Upload PCAP File
- Drag and drop or click to select a PCAP file
- Supported formats: `.pcap`, `.pcapng`, `.cap`
- Maximum size: 1GB

### 2. Configure Replay
- **Interface**: Select network interface
- **Speed**: Choose multiplier (0.1x-100x) or PPS (1-1,000,000)
- **Continuous**: Enable for continuous looping
- **Advanced**: Loop count and preload options

### 3. Monitor Progress
- Real-time progress updates
- Live packet and data transmission stats
- Stop replay at any time

### 4. View History
- Browse all previous replays
- Search and filter by status
- Download original PCAP files
- Replay with same configuration

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
No authentication required for local deployment.

### Endpoints

#### Health & System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health status |
| `GET` | `/version` | Application version information |
| `GET` | `/interfaces` | List available network interfaces |
| `GET` | `/system/status` | System resource status (CPU, memory, disk) |
| `GET` | `/system/capabilities` | System capabilities and tcpreplay features |

#### File Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload PCAP file (multipart/form-data) |
| `GET` | `/upload/status/{file_id}` | Get upload status |
| `GET` | `/upload/download/{file_id}` | Download PCAP file |
| `DELETE` | `/upload/cleanup/{file_id}` | Clean up uploaded file |

#### Replay Control
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/replay/start` | Start PCAP replay |
| `POST` | `/replay/stop` | Stop current replay |
| `GET` | `/replay/status` | Get current replay status |
| `GET` | `/replay/history` | Get replay history (paginated) |
| `POST` | `/replay/validate` | Validate replay configuration |

#### Packet Manipulation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/manipulation/modify` | Modify packets in PCAP |
| `GET` | `/manipulation/templates` | Get modification templates |

#### Logging
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/logs/recent` | Get recent log entries |
| `GET` | `/logs/stats` | Get logging statistics |

### Request Examples

#### Start Replay
```bash
curl -X POST http://localhost:5000/api/replay/start \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uuid-of-uploaded-file",
    "interface": "eth0",
    "speed": 2.0,
    "speed_unit": "multiplier",
    "continuous": false,
    "loop": 1,
    "preload_pcap": false
  }'
```

#### Upload File
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@example.pcap"
```

#### Get Replay History
```bash
curl "http://localhost:5000/api/replay/history?limit=20&offset=0&search=test&status=completed"
```

### Response Examples

#### Replay Status
```json
{
  "replay_id": "uuid",
  "status": "running",
  "progress_percent": 45.2,
  "packets_sent": 1250,
  "bytes_sent": 892400,
  "elapsed_time": 12.5,
  "packets_per_second": 100.0,
  "continuous": false,
  "loop_count": 1
}
```

#### Upload Response
```json
{
  "message": "File uploaded successfully",
  "file_id": "uuid",
  "filename": "example.pcap",
  "file_size": 1048576,
  "pcap_info": {
    "packet_count": 1000,
    "duration": 30.5,
    "file_format": "pcap",
    "protocols": ["IP", "TCP", "UDP"]
  }
}
```

#### History Response
```json
{
  "history": [
    {
      "id": "uuid",
      "filename": "example.pcap",
      "file_id": "file-uuid",
      "status": "completed",
      "started_at": "2025-08-08T15:30:00Z",
      "duration": 25.3,
      "packets_sent": 1000,
      "config": {
        "interface": "eth0",
        "speed": 2.0,
        "speed_unit": "multiplier",
        "continuous": false
      }
    }
  ],
  "total_count": 50,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

### WebSocket Events

Connect to: `ws://localhost:5000`

| Event | Description | Data |
|-------|-------------|------|
| `replay_status` | Replay status updates | `{status, replay_id, message}` |
| `replay_progress` | Real-time progress | `{progress_percent, packets_sent, ...}` |
| `log_stream` | Live log streaming | `{level, message, timestamp}` |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `UPLOAD_FOLDER` | Upload directory | `/tmp/pcap_uploads` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `MAX_ANALYSIS_PACKETS` | Max packets to analyze | `1000000` |

### Docker Configuration

The application uses host networking and privileged containers for network interface access.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│◄──►│  Flask Backend  │◄──►│   tcpreplay     │
│                 │    │                 │    │                 │
│ • File Upload   │    │ • API Endpoints │    │ • Packet Replay │
│ • Config UI     │    │ • File Handling │    │ • Speed Control │
│ • Progress Mon. │    │ • WebSocket     │    │ • Interface Mgmt│
│ • History View  │    │ • Process Mgmt  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Development

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Build from Source
```bash
git clone https://github.com/blink-zero/pcap-replaya.git
cd pcap-replaya
sudo docker-compose up --build
```

## 🔧 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Ensure Docker has necessary privileges
sudo docker-compose down
sudo docker-compose up --build
```

#### tcpreplay Not Working
```bash
# Check tcpreplay in container
docker-compose exec backend tcpreplay --version
```

#### File Upload Fails
- Check file size (max 1GB)
- Verify file format (.pcap, .pcapng, .cap)
- Ensure sufficient disk space

### Debug Commands

```bash
# View logs
docker-compose logs -f

# Check system status
docker-compose exec backend python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"

# Test tcpreplay
docker-compose exec backend tcpreplay --version
```

## 📊 Technology Stack

### Backend
- **Flask 2.3.3** - Web framework
- **Flask-SocketIO 5.3.6** - WebSocket communication
- **Scapy 2.5.0** - PCAP analysis
- **psutil 5.9.5** - System monitoring
- **tcpreplay** - Packet replay

### Frontend
- **React 18.2.0** - Frontend framework
- **Material-UI 5.14.1** - UI components
- **axios 1.4.0** - HTTP client
- **socket.io-client 4.7.2** - WebSocket client

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **Python 3.11** - Backend runtime
- **Node.js 18** - Frontend build

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/blink-zero/pcap-replaya/issues)
- **Documentation**: Check troubleshooting section above
- **Logs**: Use `docker-compose logs -f` for debugging

## 🏷️ Version History

- **v1.3.9** - Complete README overhaul and comprehensive API documentation
- **v1.3.8** - Added PCAP download feature to replay history
- **v1.3.7** - Fixed continuous mode display in history details
- **v1.3.6** - Fixed speed unit display (PPS showing correctly)
- **v1.3.5** - Fixed critical status override bug (stopped vs failed)
- **v1.3.4** - Improved status handling for manually stopped replays
- **v1.3.3** - Fixed critical validator bug for continuous parameter
- **v1.3.2** - Fixed continuous replay frontend logic
- **v1.3.1** - Fixed continuous replay process communication
- **v1.3.0** - Added continuous replay feature
- **v1.2.1** - Fixed Docker version display and search input focus
- **v1.2.0** - Enhanced replay history with pagination and search
- **v1.1.0** - Added pagination for replay history
- **v1.0.0** - Initial release

## 🙏 Acknowledgments

- [tcpreplay](https://tcpreplay.appneta.com/) - Network packet replay utility
- [Scapy](https://scapy.net/) - Packet manipulation library
- [React](https://reactjs.org/) - Frontend framework
- [Flask](https://flask.palletsprojects.com/) - Backend framework
- [Material-UI](https://mui.com/) - UI component library
