import logging
import os
from datetime import datetime


def setup_logger():
    """Configure application logging."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', '/var/log/pcap_replaya.log')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(message)s'
    )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")
    
    return logger


def log_replay_event(event_type, message, **kwargs):
    """Log replay-specific events with structured data."""
    logger = logging.getLogger('replay')
    
    log_data = {
        'event_type': event_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }
    
    logger.info(f"REPLAY_EVENT: {log_data}")


def log_upload_event(filename, file_size, status, **kwargs):
    """Log file upload events."""
    logger = logging.getLogger('upload')
    
    log_data = {
        'filename': filename,
        'file_size': file_size,
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }
    
    logger.info(f"UPLOAD_EVENT: {log_data}")
