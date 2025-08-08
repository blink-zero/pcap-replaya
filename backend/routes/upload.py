from flask import Blueprint, request, jsonify, current_app, send_file
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from utils.validators import validate_pcap_file, sanitize_filename
from utils.logger import log_upload_event
from services.pcap_service import analyze_pcap_file

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle PCAP file upload."""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate the file
        is_valid, error_message = validate_pcap_file(file)
        if not is_valid:
            log_upload_event(
                filename=file.filename or 'unknown',
                file_size=0,
                status='validation_failed',
                error=error_message
            )
            return jsonify({'error': error_message}), 400
        
        # Generate unique filename
        original_filename = file.filename
        safe_filename = sanitize_filename(original_filename)
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{safe_filename}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Analyze PCAP file with timeout protection
        try:
            import logging
            logging.info(f"Starting PCAP analysis for file: {original_filename} ({file_size} bytes)")
            pcap_info = analyze_pcap_file(file_path)
            logging.info(f"PCAP analysis completed for file: {original_filename}")
        except Exception as e:
            # If analysis fails, still allow upload but with limited info
            logging.error(f"PCAP analysis failed for {file_path}: {str(e)}")
            pcap_info = {
                'error': f'Analysis failed: {str(e)}',
                'packet_count': 'unknown',
                'duration': 'unknown',
                'file_format': 'unknown'
            }
        
        # Log successful upload
        log_upload_event(
            filename=original_filename,
            file_size=file_size,
            status='success',
            unique_id=unique_id,
            stored_filename=filename
        )
        
        response_data = {
            'message': 'File uploaded successfully',
            'file_id': unique_id,
            'filename': original_filename,
            'stored_filename': filename,
            'file_size': file_size,
            'upload_time': datetime.utcnow().isoformat(),
            'pcap_info': pcap_info
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        log_upload_event(
            filename=request.files.get('file', {}).filename or 'unknown',
            file_size=0,
            status='error',
            error=str(e)
        )
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@upload_bp.route('/upload/status/<file_id>', methods=['GET'])
def get_upload_status(file_id):
    """Get status of uploaded file."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Find file with this ID
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                file_size = os.path.getsize(file_path)
                
                return jsonify({
                    'file_id': file_id,
                    'filename': filename,
                    'file_size': file_size,
                    'status': 'ready',
                    'upload_time': datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    ).isoformat()
                }), 200
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500


@upload_bp.route('/upload/cleanup/<file_id>', methods=['DELETE'])
def cleanup_file(file_id):
    """Clean up uploaded file."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Find and delete file with this ID
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                os.remove(file_path)
                
                log_upload_event(
                    filename=filename,
                    file_size=0,
                    status='deleted',
                    file_id=file_id
                )
                
                return jsonify({
                    'message': 'File deleted successfully',
                    'file_id': file_id
                }), 200
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500


@upload_bp.route('/upload/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download PCAP file by file ID."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Find file with this ID
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                
                # Extract original filename (remove UUID prefix)
                original_filename = filename[37:]  # Remove UUID + underscore
                
                # Log download event
                log_upload_event(
                    filename=original_filename,
                    file_size=os.path.getsize(file_path),
                    status='downloaded',
                    file_id=file_id
                )
                
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=original_filename,
                    mimetype='application/octet-stream'
                )
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
