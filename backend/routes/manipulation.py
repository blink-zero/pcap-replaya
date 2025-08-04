from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import logging
from datetime import datetime

from services.packet_manipulation_service import get_packet_manipulator
from services.replay_service import get_replay_manager
from utils.validators import validate_file_id

manipulation_bp = Blueprint('manipulation', __name__)
logger = logging.getLogger(__name__)


@manipulation_bp.route('/manipulation/analyze', methods=['POST'])
def analyze_pcap_for_manipulation():
    """Analyze PCAP file to identify manipulation opportunities."""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        analysis_limit = data.get('analysis_limit', 1000)
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        # Find the uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = None
        
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Perform analysis
        manipulator = get_packet_manipulator()
        analysis = manipulator.get_packet_analysis(file_path, analysis_limit)
        
        return jsonify({
            'file_id': file_id,
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@manipulation_bp.route('/manipulation/preview', methods=['POST'])
def preview_manipulation():
    """Preview packet manipulation without creating output file."""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        manipulation_rules = data.get('manipulation_rules', {})
        sample_size = data.get('sample_size', 10)
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        if not manipulation_rules:
            return jsonify({'error': 'manipulation_rules are required'}), 400
        
        # Find the uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = None
        
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                file_path = os.path.join(upload_folder, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Preview manipulation
        manipulator = get_packet_manipulator()
        preview = manipulator.preview_manipulation(
            file_path, 
            manipulation_rules, 
            sample_size
        )
        
        return jsonify({
            'file_id': file_id,
            'preview': preview,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Preview failed: {str(e)}")
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500


@manipulation_bp.route('/manipulation/apply', methods=['POST'])
def apply_manipulation():
    """Apply packet manipulation and create modified PCAP file."""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        manipulation_rules = data.get('manipulation_rules', {})
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        if not manipulation_rules:
            return jsonify({'error': 'manipulation_rules are required'}), 400
        
        # Find the uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        input_file = None
        original_filename = None
        
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                input_file = os.path.join(upload_folder, filename)
                original_filename = filename
                break
        
        if not input_file or not os.path.exists(input_file):
            return jsonify({'error': 'File not found'}), 404
        
        # Generate output filename
        manipulation_id = str(uuid.uuid4())
        base_name = original_filename.replace(f"{file_id}_", "")
        output_filename = f"{manipulation_id}_manipulated_{base_name}"
        output_file = os.path.join(upload_folder, output_filename)
        
        # Apply manipulation
        manipulator = get_packet_manipulator()
        result = manipulator.manipulate_pcap(
            input_file, 
            output_file, 
            manipulation_rules
        )
        
        # Add manipulation metadata
        result.update({
            'manipulation_id': manipulation_id,
            'original_file_id': file_id,
            'manipulated_filename': output_filename,
            'file_size': os.path.getsize(output_file)
        })
        
        logger.info(f"Manipulation completed: {manipulation_id}")
        
        return jsonify({
            'message': 'Manipulation completed successfully',
            'result': result
        })
        
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Manipulation failed: {str(e)}")
        return jsonify({'error': f'Manipulation failed: {str(e)}'}), 500


@manipulation_bp.route('/manipulation/replay', methods=['POST'])
def manipulate_and_replay():
    """Apply manipulation and start replay in one operation."""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        manipulation_rules = data.get('manipulation_rules', {})
        replay_config = data.get('replay_config', {})
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        if not manipulation_rules:
            return jsonify({'error': 'manipulation_rules are required'}), 400
        
        if not replay_config.get('interface'):
            return jsonify({'error': 'replay interface is required'}), 400
        
        if not replay_config.get('speed'):
            return jsonify({'error': 'replay speed is required'}), 400
        
        # Find the uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        input_file = None
        original_filename = None
        
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{file_id}_"):
                input_file = os.path.join(upload_folder, filename)
                original_filename = filename
                break
        
        if not input_file or not os.path.exists(input_file):
            return jsonify({'error': 'File not found'}), 404
        
        # Generate output filename
        manipulation_id = str(uuid.uuid4())
        base_name = original_filename.replace(f"{file_id}_", "")
        output_filename = f"{manipulation_id}_manipulated_{base_name}"
        output_file = os.path.join(upload_folder, output_filename)
        
        # Apply manipulation
        manipulator = get_packet_manipulator()
        manipulation_result = manipulator.manipulate_pcap(
            input_file, 
            output_file, 
            manipulation_rules
        )
        
        # Start replay with manipulated file
        replay_manager = get_replay_manager()
        replay_id = replay_manager.start_replay(
            output_file,
            replay_config['interface'],
            replay_config['speed'],
            replay_config.get('speed_unit', 'multiplier'),
            current_app.config.get('SOCKETIO')
        )
        
        logger.info(f"Manipulation and replay started: {manipulation_id}, {replay_id}")
        
        return jsonify({
            'message': 'Manipulation and replay started successfully',
            'manipulation_id': manipulation_id,
            'replay_id': replay_id,
            'manipulation_result': manipulation_result
        })
        
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Manipulation and replay failed: {str(e)}")
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500


@manipulation_bp.route('/manipulation/templates', methods=['GET'])
def get_manipulation_templates():
    """Get predefined manipulation templates."""
    templates = {
        'ip_anonymization': {
            'name': 'IP Address Anonymization',
            'description': 'Replace real IP addresses with anonymized ones',
            'example_rules': {
                'ip_mapping': {
                    '192.168.1.100': '10.0.0.100',
                    '192.168.1.1': '10.0.0.1'
                }
            }
        },
        'network_translation': {
            'name': 'Network Translation',
            'description': 'Translate between different network segments',
            'example_rules': {
                'ip_mapping': {
                    '172.16.0.0/16': '10.0.0.0/16'
                }
            }
        },
        'port_standardization': {
            'name': 'Port Standardization',
            'description': 'Standardize non-standard ports to standard ones',
            'example_rules': {
                'port_mapping': {
                    8080: 80,
                    8443: 443
                }
            }
        },
        'vlan_addition': {
            'name': 'VLAN Tag Addition',
            'description': 'Add VLAN tags to untagged traffic',
            'example_rules': {
                'vlan_operations': {
                    'add_vlan': 100
                }
            }
        },
        'mac_vendor_change': {
            'name': 'MAC Vendor Change',
            'description': 'Change MAC addresses to different vendors',
            'example_rules': {
                'mac_mapping': {
                    '00:0c:29:xx:xx:xx': '00:50:56:xx:xx:xx'
                }
            }
        }
    }
    
    return jsonify({
        'templates': templates,
        'timestamp': datetime.utcnow().isoformat()
    })


@manipulation_bp.route('/manipulation/validate', methods=['POST'])
def validate_manipulation_rules():
    """Validate manipulation rules without applying them."""
    try:
        data = request.get_json()
        manipulation_rules = data.get('manipulation_rules', {})
        
        if not manipulation_rules:
            return jsonify({'error': 'manipulation_rules are required'}), 400
        
        # Validate rules using the manipulator
        manipulator = get_packet_manipulator()
        manipulator._validate_rules(manipulation_rules)
        
        return jsonify({
            'valid': True,
            'message': 'Manipulation rules are valid',
            'rules': manipulation_rules
        })
        
    except ValueError as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'rules': manipulation_rules
        }), 400
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return jsonify({
            'valid': False,
            'error': f'Validation failed: {str(e)}'
        }), 500


@manipulation_bp.route('/manipulation/cleanup/<manipulation_id>', methods=['DELETE'])
def cleanup_manipulated_file(manipulation_id):
    """Clean up manipulated PCAP file."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Find and delete file with this manipulation ID
        deleted_files = []
        for filename in os.listdir(upload_folder):
            if filename.startswith(f"{manipulation_id}_"):
                file_path = os.path.join(upload_folder, filename)
                os.remove(file_path)
                deleted_files.append(filename)
                logger.info(f"Deleted manipulated file: {filename}")
        
        if not deleted_files:
            return jsonify({'error': 'Manipulated file not found'}), 404
        
        return jsonify({
            'message': 'Manipulated files cleaned up successfully',
            'deleted_files': deleted_files,
            'manipulation_id': manipulation_id
        })
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500
