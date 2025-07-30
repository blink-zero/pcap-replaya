# Changelog

All notable changes to PCAP Replaya will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-07-30

### Fixed
- **Docker Version Display**: Fixed VERSION file not being found in Docker containers
  - Added VERSION file copy to Dockerfile.backend to ensure it's available in container
  - Updated version endpoint to prioritize Docker container path (working directory)
  - Enhanced error logging to show all attempted paths for better debugging
  - Improved fallback version handling for container environments

- **Search Input Focus Issue**: Fixed clunky search behavior in replay history
  - Added debouncing to search input to prevent excessive API calls
  - Fixed search box losing focus after each character typed
  - Improved user experience with smooth, continuous typing in search field
  - Search now waits 300ms after user stops typing before triggering API call

### Technical Improvements
- VERSION file now properly copied into Docker container at `/app/VERSION`
- Version endpoint tries Docker-specific paths first for better container compatibility
- Enhanced logging provides better visibility into version file resolution process
- Robust fallback ensures version display even if file reading fails
- Debounced search reduces server load and improves frontend responsiveness
- Better state management prevents unnecessary component re-renders during search

## [1.2.0] - 2025-07-29

### Added
- **Version Information in UI**: Added version display throughout the user interface
  - New `/api/version` endpoint that reads from VERSION file
  - Version displayed in app bar header next to application name
  - Complete version information shown in footer with app name and description
  - Fallback version handling for error cases
  - Version information fetched automatically on app startup

### Fixed
- **Search Functionality**: Restored broken search functionality in replay history
  - Fixed search that was only working on current page after pagination implementation
  - Moved search and filtering logic from frontend to backend for proper functionality
  - Search now works across all history entries, not just current page
  - Added server-side search on filename and interface fields
  - Added status filtering (ALL, completed, running, failed, stopped)
  - Case-insensitive search with real-time updates
  - Proper pagination integration with search and filters

### Changed
- **History Service**: Enhanced with search and status filtering parameters
- **API Endpoint**: Updated `/replay/history` to accept search and status query parameters
- **Frontend Components**: Removed client-side filtering that was causing pagination issues
- **Performance**: Server-side filtering provides better performance with large datasets

### Technical Improvements
- Server-side search and filtering before pagination for accurate results
- Reduced data transfer with filtered results
- Better scalability for large history datasets
- Improved response times with efficient backend filtering
- Enhanced user experience with comprehensive search capabilities

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
