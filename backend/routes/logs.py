from flask import Blueprint, jsonify, request
from flask_socketio import emit, join_room, leave_room
import logging
from services.log_service import get_log_streamer

logs_bp = Blueprint('logs', __name__)
logger = logging.getLogger(__name__)


@logs_bp.route('/logs/recent', methods=['GET'])
def get_recent_logs():
    """Get recent log entries."""
    try:
        count = request.args.get('count', 100, type=int)
        count = min(count, 500)  # Limit to 500 logs max
        
        log_streamer = get_log_streamer()
        logs = log_streamer.get_recent_logs(count)
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error getting recent logs: {str(e)}")
        return jsonify({'error': 'Failed to get recent logs'}), 500


@logs_bp.route('/logs/stats', methods=['GET'])
def get_log_stats():
    """Get logging statistics."""
    try:
        log_streamer = get_log_streamer()
        stats = log_streamer.get_log_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting log stats: {str(e)}")
        return jsonify({'error': 'Failed to get log stats'}), 500


def setup_log_websocket_handlers(socketio):
    """Set up WebSocket handlers for log streaming."""
    
    @socketio.on('subscribe_logs')
    def handle_subscribe_logs():
        """Handle client subscription to log stream."""
        try:
            client_id = request.sid
            join_room('log_viewers')
            
            log_streamer = get_log_streamer()
            log_streamer.add_client(client_id)
            
            emit('log_subscription_status', {
                'status': 'subscribed',
                'message': 'Successfully subscribed to log stream'
            })
            
        except Exception as e:
            logger.error(f"Error subscribing to logs: {str(e)}")
            emit('log_subscription_status', {
                'status': 'error',
                'message': 'Failed to subscribe to log stream'
            })
    
    @socketio.on('unsubscribe_logs')
    def handle_unsubscribe_logs():
        """Handle client unsubscription from log stream."""
        try:
            client_id = request.sid
            leave_room('log_viewers')
            
            log_streamer = get_log_streamer()
            log_streamer.remove_client(client_id)
            
            emit('log_subscription_status', {
                'status': 'unsubscribed',
                'message': 'Successfully unsubscribed from log stream'
            })
            
        except Exception as e:
            logger.error(f"Error unsubscribing from logs: {str(e)}")
            emit('log_subscription_status', {
                'status': 'error',
                'message': 'Failed to unsubscribe from log stream'
            })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnect."""
        try:
            client_id = request.sid
            log_streamer = get_log_streamer()
            log_streamer.remove_client(client_id)
            
        except Exception as e:
            logger.error(f"Error handling disconnect: {str(e)}")
    
    @socketio.on_error_default
    def default_error_handler(e):
        """Handle SocketIO errors."""
        logger.error(f"SocketIO error: {str(e)}")
