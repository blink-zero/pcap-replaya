from flask import Blueprint, request, jsonify, current_app
import subprocess
import threading
import time
import os
import signal
import logging
from datetime import datetime
from flask_socketio import emit

from utils.validators import validate_replay_config
from utils.logger import log_replay_event
from services.replay_service import ReplayManager
from services.history_service import get_history_service

replay_bp = Blueprint('replay', __name__)

# Global replay manager instance
replay_manager = ReplayManager()


@replay_bp.route('/replay/start', methods=['POST'])
def start_replay():
    """Start PCAP replay with specified configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400
        
        # Validate configuration
        is_valid, error_msg, config = validate_replay_config(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Get file information
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({'error': 'File ID is required'}), 400
        
        # Find the uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = None
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if replay is already running
        if replay_manager.is_running():
            return jsonify({'error': 'Replay already in progress'}), 409
        
        # Start the replay
        replay_id = replay_manager.start_replay(
            file_path=file_path,
            interface=config['interface'],
            speed=config['speed'],
            speed_unit=config['speed_unit'],
            socketio=current_app.config.get('SOCKETIO')
        )
        
        # Add to history
        history_service = get_history_service()
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        history_service.add_replay({
            'filename': filename,
            'file_id': file_id,
            'file_size': file_size,
            'interface': config['interface'],
            'speed': config['speed'],
            'speed_unit': config['speed_unit'],
            'loop': config.get('loop', False),
            'preload_pcap': config.get('preload_pcap', False),
            'replay_id': replay_id
        })
        
        log_replay_event(
            'replay_started',
            f'Started replay of {file_path}',
            replay_id=replay_id,
            interface=config['interface'],
            speed=config['speed'],
            speed_unit=config['speed_unit']
        )
        
        return jsonify({
            'success': True,
            'message': 'Replay started successfully',
            'replay_id': replay_id,
            'file_path': file_path,
            'config': config,
            'start_time': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error starting replay: {str(e)}")
        return jsonify({'error': f'Failed to start replay: {str(e)}'}), 500


@replay_bp.route('/replay/stop', methods=['POST'])
def stop_replay():
    """Stop the current replay."""
    try:
        if not replay_manager.is_running():
            return jsonify({'error': 'No replay in progress'}), 400
        
        replay_id = replay_manager.get_current_replay_id()
        replay_manager.stop_replay()
        
        log_replay_event(
            'replay_stopped',
            'Replay stopped by user request',
            replay_id=replay_id
        )
        
        return jsonify({
            'message': 'Replay stopped successfully',
            'replay_id': replay_id,
            'stop_time': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error stopping replay: {str(e)}")
        return jsonify({'error': f'Failed to stop replay: {str(e)}'}), 500


@replay_bp.route('/replay/status', methods=['GET'])
def get_replay_status():
    """Get current replay status and progress."""
    try:
        status = replay_manager.get_status()
        return jsonify(status), 200
        
    except Exception as e:
        logging.error(f"Error getting replay status: {str(e)}")
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500


@replay_bp.route('/replay/history', methods=['GET'])
def get_replay_history():
    """Get history of recent replays."""
    try:
        history_service = get_history_service()
        limit = request.args.get('limit', 50, type=int)
        history = history_service.get_history(limit)
        
        return jsonify({
            'history': history,
            'count': len(history),
            'message': f'Retrieved {len(history)} replay history entries'
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting replay history: {str(e)}")
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500


@replay_bp.route('/replay/validate', methods=['POST'])
def validate_replay_configuration():
    """Validate replay configuration without starting replay."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration provided'}), 400
        
        is_valid, error_msg, config = validate_replay_config(data)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'config': config,
                'message': 'Configuration is valid'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': error_msg
            }), 400
            
    except Exception as e:
        logging.error(f"Error validating configuration: {str(e)}")
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500
