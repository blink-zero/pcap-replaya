# Changelog

All notable changes to PCAP Replaya will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-29

### Added
- **Pagination for Replay History**: Added pagination support to the replay history view
  - Backend API now supports `limit` and `offset` parameters for paginated history retrieval
  - Frontend displays 20 replays per page with Material-UI Pagination component
  - Shows total count and current page range information
  - Automatic page reset when filters are applied
  - Improved performance for large history datasets

### Changed
- **History Service**: Updated `get_history()` method to return pagination metadata
- **API Response**: History endpoint now returns `total_count`, `has_more`, `limit`, and `offset` fields
- **Frontend State Management**: Enhanced state management for pagination and filtering

### Technical Improvements
- Optimized database queries with pagination support
- Reduced memory usage for large history datasets
- Improved user experience with better navigation controls
- Enhanced filtering and search functionality with pagination

## [1.0.0] - 2025-07-20

### Added
- Initial release of PCAP Replaya
- Web-based PCAP file upload with drag-and-drop support
- Real-time PCAP analysis using Scapy (packet count, duration, protocols)
- Network interface detection and selection
- Flexible replay speed control (multiplier and PPS modes)
- tcpreplay integration for packet replay
- Real-time progress monitoring with WebSocket updates
- Live application log streaming
- Replay history tracking and management
- Docker containerization with multi-stage builds
- Nginx reverse proxy with WebSocket support
- Material-UI responsive interface
- Comprehensive error handling and validation
- Security features (file type validation, size limits, CORS)
- Linux-only deployment (requires privileged containers for network access)

### Features
- **File Support**: .pcap, .pcapng, .cap files up to 1GB
- **Speed Control**: Real-time multiplier (0.1x-100x) or PPS (1-1,000,000)
- **Real-time Monitoring**: Live progress updates every 2 seconds
- **Network Interfaces**: Dynamic detection of available interfaces
- **Analysis Optimization**: Performance limits for large files (100K+ packets)
- **WebSocket Communication**: Automatic host detection for portability
- **Security**: Input validation, magic byte verification, secure file handling
- **Logging**: Structured logging with real-time streaming
- **History**: Persistent replay history with detailed statistics

### Technical Stack
- **Backend**: Flask 2.3.3, Flask-SocketIO 5.3.6, Scapy 2.5.0, psutil 5.9.5
- **Frontend**: React 18.2.0, Material-UI 5.14.1, socket.io-client 4.7.2
- **Infrastructure**: Docker, Nginx, tcpreplay, Python 3.11, Node.js 18
- **Deployment**: Host networking, privileged containers, volume persistence

### Security
- Environment variable configuration for sensitive data
- No hardcoded secrets or credentials
- Comprehensive .gitignore for security
- File type validation using magic bytes
- CORS configuration and security headers
- Input sanitization and validation
