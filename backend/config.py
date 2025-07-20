import os


class Config:
    """Application configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp/pcap_uploads'
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB max file size
    ALLOWED_EXTENSIONS = {'pcap', 'pcapng', 'cap'}
    
    # Replay settings
    DEFAULT_REPLAY_SPEED = 1.0  # Real-time
    MAX_REPLAY_SPEED = 100.0    # 100x speed limit
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/var/log/pcap_replaya.log'
    
    # Network interface settings
    INTERFACE_REFRESH_INTERVAL = 30  # seconds
    
    # PCAP analysis settings
    MAX_ANALYSIS_PACKETS = int(os.environ.get('MAX_ANALYSIS_PACKETS') or 1000000)  # 1M packets default
    ANALYSIS_PERFORMANCE_LIMIT = 100000  # Stop analysis at this many packets for performance
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed."""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS)
