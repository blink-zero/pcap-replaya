from flask import Blueprint, jsonify
import psutil
import subprocess
import logging
from datetime import datetime

from utils.logger import log_replay_event

system_bp = Blueprint('system', __name__)


@system_bp.route('/interfaces', methods=['GET'])
def get_network_interfaces():
    """Get list of available network interfaces."""
    try:
        interfaces = []
        
        # Get network interfaces using psutil
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            # Skip loopback interfaces
            if interface_name.startswith('lo'):
                continue
                
            interface_info = {
                'name': interface_name,
                'addresses': [],
                'is_up': False,
                'speed': None,
                'mtu': None
            }
            
            # Get interface statistics
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info['is_up'] = stats.isup
                interface_info['speed'] = stats.speed
                interface_info['mtu'] = stats.mtu
            
            # Get IP addresses
            for addr in addresses:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    interface_info['addresses'].append({
                        'family': addr.family.name,
                        'address': addr.address,
                        'netmask': addr.netmask
                    })
            
            interfaces.append(interface_info)
        
        # Sort interfaces by name
        interfaces.sort(key=lambda x: x['name'])
        
        return jsonify({
            'interfaces': interfaces,
            'count': len(interfaces),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting network interfaces: {str(e)}")
        return jsonify({'error': f'Failed to get interfaces: {str(e)}'}), 500


@system_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get system resource status."""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage for upload directory
        disk_usage = psutil.disk_usage('/')
        
        # Check if tcpreplay is available
        tcpreplay_available = False
        tcpreplay_version = None
        try:
            result = subprocess.run(
                ['tcpreplay', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                tcpreplay_available = True
                # Extract version from output
                version_line = result.stdout.split('\n')[0]
                tcpreplay_version = version_line.split()[-1] if version_line else 'unknown'
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        return jsonify({
            'cpu_percent': cpu_percent,
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk_usage.total,
                'free': disk_usage.free,
                'used': disk_usage.used,
                'percent': (disk_usage.used / disk_usage.total) * 100
            },
            'tcpreplay': {
                'available': tcpreplay_available,
                'version': tcpreplay_version
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting system status: {str(e)}")
        return jsonify({'error': f'Failed to get system status: {str(e)}'}), 500


@system_bp.route('/system/capabilities', methods=['GET'])
def get_system_capabilities():
    """Get system capabilities for PCAP replay."""
    try:
        capabilities = {
            'tcpreplay_available': False,
            'tcpreplay_version': None,
            'supported_formats': ['pcap', 'pcapng'],
            'max_file_size': '1GB',
            'features': {
                'speed_control': True,
                'interface_selection': True,
                'real_time_monitoring': True,
                'progress_tracking': True
            }
        }
        
        # Check tcpreplay availability and capabilities
        try:
            # Check version
            result = subprocess.run(
                ['tcpreplay', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                capabilities['tcpreplay_available'] = True
                version_line = result.stdout.split('\n')[0]
                capabilities['tcpreplay_version'] = version_line.split()[-1] if version_line else 'unknown'
            
            # Check help for available options
            help_result = subprocess.run(
                ['tcpreplay', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if help_result.returncode == 0:
                help_text = help_result.stdout.lower()
                capabilities['features'].update({
                    'mbps_control': '--mbps' in help_text,
                    'pps_control': '--pps' in help_text,
                    'multiplier_control': '--multiplier' in help_text,
                    'loop_support': '--loop' in help_text
                })
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logging.warning(f"Could not check tcpreplay capabilities: {str(e)}")
        
        return jsonify(capabilities), 200
        
    except Exception as e:
        logging.error(f"Error getting system capabilities: {str(e)}")
        return jsonify({'error': f'Failed to get capabilities: {str(e)}'}), 500
