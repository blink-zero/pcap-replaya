import logging
import threading
import queue
from datetime import datetime


class LogStreamer:
    """Service for streaming application logs to WebSocket clients."""
    
    def __init__(self):
        self.log_queue = queue.Queue(maxsize=1000)  # Buffer for log messages
        self.clients = set()  # Connected WebSocket clients
        self.is_streaming = False
        self.stream_thread = None
        self.socketio = None
        self.log_handler = None
        self.log_buffer = []  # Keep recent logs in memory
        self.max_buffer_size = 500
        
    def start_streaming(self, socketio):
        """Start the log streaming service."""
        if self.is_streaming:
            return
            
        self.socketio = socketio
        self.is_streaming = True
        
        # Set up custom log handler to capture logs
        self.setup_log_handler()
        
        # Start streaming thread
        self.stream_thread = threading.Thread(
            target=self._stream_logs, daemon=True)
        self.stream_thread.start()
        
        logging.info("Log streaming service started")
    
    def stop_streaming(self):
        """Stop the log streaming service."""
        self.is_streaming = False
        if self.log_handler:
            logging.getLogger().removeHandler(self.log_handler)
        logging.info("Log streaming service stopped")
    
    def setup_log_handler(self):
        """Set up a custom log handler to capture logs for streaming."""
        class WebSocketLogHandler(logging.Handler):
            def __init__(self, log_streamer):
                super().__init__()
                self.log_streamer = log_streamer
                
            def emit(self, record):
                try:
                    log_entry = self.format(record)
                    self.log_streamer.add_log_entry(record, log_entry)
                except Exception:
                    pass  # Don't let logging errors break the app
        
        # Create and configure the handler
        self.log_handler = WebSocketLogHandler(self)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )
        self.log_handler.setFormatter(formatter)
        self.log_handler.setLevel(logging.INFO)
        
        # Add to root logger
        logging.getLogger().addHandler(self.log_handler)
    
    def add_log_entry(self, record, formatted_message):
        """Add a log entry to the queue for streaming."""
        try:
            log_data = {
                'timestamp': datetime.fromtimestamp(
                    record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'filename': record.filename,
                'lineno': record.lineno,
                'formatted': formatted_message,
                'module': getattr(record, 'module', ''),
                'funcName': record.funcName
            }
            
            # Add to buffer
            self.log_buffer.append(log_data)
            if len(self.log_buffer) > self.max_buffer_size:
                self.log_buffer.pop(0)
            
            # Add to queue for real-time streaming
            if not self.log_queue.full():
                self.log_queue.put(log_data)
                
        except Exception:
            # Don't let logging errors break the app
            pass
    
    def _stream_logs(self):
        """Stream logs to connected WebSocket clients."""
        while self.is_streaming:
            try:
                # Get log entry from queue (blocking with timeout)
                log_data = self.log_queue.get(timeout=1.0)
                
                # Emit to all connected clients with error handling
                if self.socketio and self.clients:
                    try:
                        self.socketio.emit('log_entry', log_data,
                                           room='log_viewers')
                    except Exception:
                        # Don't log emit errors to prevent recursion
                        pass
                    
            except queue.Empty:
                continue
            except Exception:
                # Avoid logging errors that could cause recursion
                pass
    
    def add_client(self, client_id):
        """Add a client to receive log streams."""
        self.clients.add(client_id)
        logging.info(f"Client {client_id} subscribed to log stream")
        
        # Send recent logs to new client
        if self.socketio and self.log_buffer:
            recent_logs = self.log_buffer[-50:]  # Send last 50 logs
            self.socketio.emit('log_history', {
                'logs': recent_logs,
                'count': len(recent_logs)
            }, room=client_id)
    
    def remove_client(self, client_id):
        """Remove a client from log streams."""
        self.clients.discard(client_id)
        logging.info(f"Client {client_id} unsubscribed from log stream")
    
    def get_recent_logs(self, count=100):
        """Get recent log entries."""
        return self.log_buffer[-count:] if self.log_buffer else []
    
    def get_log_stats(self):
        """Get logging statistics."""
        return {
            'total_logs_buffered': len(self.log_buffer),
            'connected_clients': len(self.clients),
            'is_streaming': self.is_streaming,
            'queue_size': self.log_queue.qsize()
        }


# Global log streamer instance
log_streamer = LogStreamer()


def get_log_streamer():
    """Get the global log streamer instance."""
    return log_streamer
