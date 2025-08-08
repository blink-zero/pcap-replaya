# Changelog

All notable changes to PCAP Replaya will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.10] - 2025-08-08

### Fixed
- **History Details Display**: Improved replay mode display in history details
  - Changed "Loop: Yes/No" to more descriptive "Mode: Continuous (loops until stopped)" or "Mode: Single run"
  - Removed confusing "Preload PCAP" parameter from history details view
  - Better differentiation between continuous replay mode and single run mode
  - Cleaner, more intuitive display of replay configuration in history details

### Enhanced
- **User Experience**: More intuitive replay configuration display
  - Clear indication when a replay was run in continuous mode
  - Simplified history details with only relevant configuration parameters
  - Better visual distinction between different replay modes

## [1.3.9] - 2025-08-08

### Improved
- **Documentation Overhaul**: Complete README restructure and cleanup
  - Streamlined and organized content with clear sections
  - Added comprehensive API documentation with all endpoints
  - Included request/response examples for all major operations
  - Added proper endpoint tables with methods and descriptions
  - Enhanced troubleshooting and development sections
  - Updated version badges and modern formatting
  - Improved navigation with emoji icons and clear structure
  - Added WebSocket events documentation
  - Better organized technology stack and architecture information

### Enhanced
- **API Documentation**: Complete endpoint reference
  - Health & System endpoints
  - File Management operations (including new download endpoint)
  - Replay Control with all parameters
  - Packet Manipulation endpoints
  - Logging endpoints
  - Request/response examples with proper JSON formatting
  - WebSocket events documentation

### Technical Improvements
- Better documentation structure for developers and users
- Clear API reference for integration purposes
- Improved onboarding experience with streamlined quick start
- Enhanced troubleshooting guidance

## [1.3.8] - 2025-08-08

### Added
- **PCAP Download Feature**: Added ability to download previously replayed PCAP files from history
  - New download button in replay history actions column
  - Backend endpoint `/upload/download/<file_id>` for secure file downloads
  - Downloads preserve original filename and use proper MIME type
  - Download events are logged for audit purposes
  - Error handling for missing or unavailable files
  - Seamless integration with existing history interface

### Enhanced
- **Replay History Interface**: Improved user experience with download functionality
  - Added download icon button next to view details and replay actions
  - Tooltip guidance for download feature
  - Error messages when files are no longer available
  - Maintains existing pagination and filtering capabilities

### Technical Improvements
- Enhanced upload route with file download endpoint
- Improved API service with download functionality
- Better file management and availability checking
- Comprehensive error handling for download operations
- Logging integration for download tracking

## [1.3.7] - 2025-08-08

### Fixed
- **Continuous Mode History Display**: Fixed history details not showing continuous mode correctly
  - Added missing `continuous` parameter to history service configuration storage
  - History details now properly display "Continuous: Yes" for continuous replays
  - Fixed issue where continuous replays were always showing "Continuous: No" in view details
  - Ensures accurate replay configuration tracking in history

### Technical Improvements
- Enhanced history service to store complete replay configuration
- Better configuration persistence for all replay modes
- Improved accuracy of historical replay information

## [1.3.6] - 2025-08-08

### Fixed
- **Speed Unit Display**: Fixed history details not showing PPS (Packets Per Second) unit correctly
  - Added missing `pps` case to `formatSpeed()` function in frontend
  - History details now properly display "100 PPS" instead of "100x" for PPS-based replays
  - Speed formatting now correctly handles all units: multiplier (x), PPS, Mbps, Gbps
  - Improves clarity in replay history when reviewing different speed configurations

### Technical Improvements
- Enhanced speed unit formatting for better user experience
- Consistent speed display across all UI components
- Better differentiation between speed modes in history view

## [1.3.5] - 2025-08-08

### Fixed
- **Critical Status Override Bug**: Fixed replay thread overriding manual stop status
  - Identified and fixed race condition where replay thread was overriding "stopped" status with "failed"
  - Added status protection to prevent thread completion from changing manually set "stopped" status
  - When user manually stops a replay, the status now permanently remains "stopped" in history
  - Enhanced logging to show when thread completion is skipped due to manual stop
  - This was the root cause of manually stopped replays appearing as "failed" in history

### Technical Improvements
- Added status checking before thread completion updates
- Prevented duplicate status updates from different execution paths
- Better separation of manual stop vs thread completion logic
- Enhanced debugging information for status determination

## [1.3.4] - 2025-08-08

### Fixed
- **Replay Status Display**: Improved status handling for manually stopped replays
  - Enhanced logic to distinguish between failed replays and manually stopped replays
  - When a user manually stops a replay, it now correctly shows "stopped" instead of "failed" in history
  - Added better logging to differentiate between expected termination (manual stop) vs actual errors
  - Improved race condition handling between manual stop and process termination

### Technical Improvements
- Better process termination handling with clearer status determination
- Enhanced logging for debugging replay termination scenarios
- More robust status logic that properly handles manual stop vs error conditions

## [1.3.3] - 2025-08-08

### Fixed
- **Critical Validator Bug**: Fixed `validate_replay_config` function that was stripping out the `continuous` parameter
  - Backend validator was only validating `speed`, `interface`, and `speed_unit` but ignoring `continuous`
  - Added proper validation and sanitization for the `continuous` parameter in backend
  - Continuous replay parameter now properly passes through the entire request pipeline
  - This was the root cause preventing continuous replay from working

### Added
- **Beta UI Indicator**: Added "BETA" tag to Continuous Replay checkbox in UI
  - Orange warning-colored chip indicates the feature is in beta testing
  - Helps users understand the experimental nature of continuous replay

### Technical Improvements
- Enhanced parameter validation with proper boolean conversion for continuous flag
- Better error handling for malformed continuous parameter values
- Improved frontend visual indicators for experimental features

## [1.3.2] - 2025-08-08

### Fixed
- **Continuous Replay Frontend Logic**: Fixed critical frontend issue preventing continuous replay from working
  - Fixed App.js `handleReplayComplete` function that was resetting config after each loop completion
  - Frontend now only resets config when replay is actually stopped/failed, not on loop completion
  - Continuous replay now properly maintains state between loops
  - Backend status handling improved to distinguish between loop completion and replay termination

### Technical Improvements
- Enhanced status management for continuous vs normal replay modes
- Better separation of loop completion vs replay termination logic
- Improved frontend state persistence for continuous replay sessions

## [1.3.1] - 2025-08-08

### Fixed
- **Continuous Replay Process Communication**: Fixed critical issue preventing continuous replay from working
  - Fixed blocking process communication logic that prevented proper looping
  - Improved process monitoring with proper select() usage on Unix systems
  - Added proper process cleanup between loops to prevent resource leaks
  - Increased delay between loops from 0.1s to 2s for better system stability
  - Enhanced error handling and logging for continuous replay debugging
  - Fixed bare except clause and other code quality issues

### Technical Improvements
- Non-blocking process output reading with timeout handling
- Platform-specific handling for Windows vs Unix systems
- Responsive stopping mechanism with smaller sleep intervals
- Better process termination with timeout and fallback to kill
- Enhanced logging for debugging continuous replay behavior

## [1.3.0] - 2025-08-08

### Added
- **Continuous Replay Feature**: Added ability to replay PCAP files continuously until manually stopped
  - New "Continuous Replay" checkbox in replay configuration interface
  - Backend support for looping PCAP replay automatically
  - Loop count tracking and display in progress monitor
  - Continuous mode indicator in replay status and history
  - Enhanced replay service with automatic restart logic between loops
  - Warning alerts to inform users about continuous mode behavior

### Changed
- **Replay Configuration**: Extended replay config to include continuous option
- **Progress Monitor**: Enhanced to display loop count for continuous replays
- **Replay History**: Updated to store and display continuous mode setting
- **Backend API**: Modified replay endpoints to accept continuous parameter

### Technical Improvements
- Enhanced replay service with loop management and status tracking
- Improved WebSocket communication for continuous replay progress updates
- Better error handling and graceful termination for continuous replays
- Small delay between loops to prevent system overload
- Comprehensive logging for continuous replay operations

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
