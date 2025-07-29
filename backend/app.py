from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging
from datetime import datetime

from routes.upload import upload_bp
from routes.replay import replay_bp
from routes.system import system_bp
from routes.logs import logs_bp, setup_log_websocket_handlers
from utils.logger import setup_logger
from services.log_service import get_log_streamer
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set longer timeout for large file uploads
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Enable CORS for all routes
    CORS(app, origins=["*"])
    
    # Initialize SocketIO with better error handling
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        logger=False,  # Disable SocketIO's own logging to prevent conflicts
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    
    # Setup logging
    setup_logger()
    
    # Register blueprints
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(replay_bp, url_prefix='/api')
    app.register_blueprint(system_bp, url_prefix='/api')
    app.register_blueprint(logs_bp, url_prefix='/api')
    
    # Store socketio instance in app config for access in other modules
    app.config['SOCKETIO'] = socketio
    
    # Setup log streaming WebSocket handlers
    setup_log_websocket_handlers(socketio)
    
    # Start log streaming service
    log_streamer = get_log_streamer()
    log_streamer.start_streaming(socketio)
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/version')
    def get_version():
        """Get application version information."""
        try:
            # Try multiple possible locations for VERSION file
            possible_paths = [
                # From backend directory, go up one level to project root
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 'VERSION'
                ),
                # From current working directory
                os.path.join(os.getcwd(), 'VERSION'),
                # From project root (assuming we're in backend subdirectory)
                os.path.join(os.path.dirname(os.getcwd()), 'VERSION'),
                # Absolute path if running from project root
                'VERSION'
            ]
            
            version = '1.2.0'  # default to current version
            
            for version_file in possible_paths:
                if os.path.exists(version_file):
                    with open(version_file, 'r') as f:
                        version = f.read().strip()
                    logging.info(f"Found VERSION file at: {version_file}")
                    break
            else:
                logging.warning("VERSION file not found in any expected location")
            
            return jsonify({
                'version': version,
                'name': 'PCAP Replaya',
                'description': 'Network Packet Replay Tool',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logging.error(f"Error reading version: {e}")
            return jsonify({
                'version': '1.2.0',
                'name': 'PCAP Replaya',
                'description': 'Network Packet Replay Tool',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large. Maximum size is 1GB.'}), 413
    
    @app.errorhandler(500)
    def internal_error(e):
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the application
    # Use allow_unsafe_werkzeug=True for production or disable debug
    is_production = os.environ.get('FLASK_ENV') == 'production'
    if is_production:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False,
                     allow_unsafe_werkzeug=True)
    else:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False,
                     allow_unsafe_werkzeug=True)
