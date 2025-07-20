import os
import logging
from scapy.all import PcapReader
from datetime import datetime
from config import Config


def analyze_pcap_file(file_path):
    """
    Analyze PCAP file to extract basic information.
    
    Args:
        file_path: Path to the PCAP file
        
    Returns:
        dict: Analysis results containing packet count, duration, etc.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PCAP file not found: {file_path}")
    
    logging.info(f"Starting PCAP analysis for: {file_path}")
    
    try:
        analysis = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'packet_count': 0,
            'duration': 0,
            'start_time': None,
            'end_time': None,
            'file_format': 'unknown',
            'protocols': set(),
            'data_rate': 0,
            'analysis_time': datetime.utcnow().isoformat()
        }
        
        # Determine file format by reading magic bytes
        with open(file_path, 'rb') as f:
            magic_bytes = f.read(4)
            if magic_bytes == b'\xd4\xc3\xb2\xa1' or magic_bytes == b'\xa1\xb2\xc3\xd4':
                analysis['file_format'] = 'pcap'
            elif magic_bytes == b'\x0a\x0d\x0d\x0a':
                analysis['file_format'] = 'pcapng'
        
        # Use PcapReader for memory-efficient reading of large files
        packet_count = 0
        first_timestamp = None
        last_timestamp = None
        total_bytes = 0
        
        try:
            with PcapReader(file_path) as pcap_reader:
                for packet in pcap_reader:
                    packet_count += 1
                    
                    # Get timestamp
                    if hasattr(packet, 'time'):
                        timestamp = packet.time
                        if first_timestamp is None:
                            first_timestamp = timestamp
                        last_timestamp = timestamp
                    
                    # Count bytes
                    total_bytes += len(packet)
                    
                    # Analyze protocols (basic)
                    if packet.haslayer('IP'):
                        analysis['protocols'].add('IP')
                    if packet.haslayer('IPv6'):
                        analysis['protocols'].add('IPv6')
                    if packet.haslayer('TCP'):
                        analysis['protocols'].add('TCP')
                    if packet.haslayer('UDP'):
                        analysis['protocols'].add('UDP')
                    if packet.haslayer('ICMP'):
                        analysis['protocols'].add('ICMP')
                    
                    # Limit analysis for very large files to prevent memory issues
                    if packet_count >= Config.ANALYSIS_PERFORMANCE_LIMIT:
                        logging.warning(f"Large file detected, stopping analysis at {packet_count} packets")
                        analysis['analysis_limited'] = True
                        analysis['analysis_limit_reason'] = f"Analysis stopped at {packet_count} packets for performance reasons. Full file can still be replayed."
                        break
                        
        except Exception as e:
            logging.warning(f"Error during detailed packet analysis: {str(e)}")
            # Fall back to basic file info
            pass
        
        # Update analysis results
        analysis['packet_count'] = packet_count
        
        if first_timestamp and last_timestamp:
            duration = float(last_timestamp - first_timestamp)
            analysis['duration'] = duration
            analysis['start_time'] = datetime.fromtimestamp(float(first_timestamp)).isoformat()
            analysis['end_time'] = datetime.fromtimestamp(float(last_timestamp)).isoformat()
            
            # Calculate data rate (bytes per second)
            if duration > 0:
                analysis['data_rate'] = total_bytes / duration
        
        # Convert protocols set to list for JSON serialization
        analysis['protocols'] = list(analysis['protocols'])
        
        logging.info(f"PCAP analysis complete: {packet_count} packets, {analysis['duration']} seconds")
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing PCAP file {file_path}: {str(e)}")
        raise


def get_pcap_summary(file_path):
    """
    Get a quick summary of PCAP file without full analysis.
    
    Args:
        file_path: Path to the PCAP file
        
    Returns:
        dict: Basic file information
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PCAP file not found: {file_path}")
    
    try:
        summary = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_format': 'unknown',
            'readable': False
        }
        
        # Check file format
        with open(file_path, 'rb') as f:
            magic_bytes = f.read(4)
            if magic_bytes == b'\xd4\xc3\xb2\xa1' or magic_bytes == b'\xa1\xb2\xc3\xd4':
                summary['file_format'] = 'pcap'
                summary['readable'] = True
            elif magic_bytes == b'\x0a\x0d\x0d\x0a':
                summary['file_format'] = 'pcapng'
                summary['readable'] = True
        
        return summary
        
    except Exception as e:
        logging.error(f"Error getting PCAP summary for {file_path}: {str(e)}")
        raise


def validate_pcap_for_replay(file_path):
    """
    Validate that PCAP file is suitable for replay.
    
    Args:
        file_path: Path to the PCAP file
        
    Returns:
        tuple: (is_valid, error_message, warnings)
    """
    warnings = []
    
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist", []
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty", []
        
        if file_size > 1024 * 1024 * 1024:  # 1GB
            warnings.append("Large file size may impact performance")
        
        # Check file format
        summary = get_pcap_summary(file_path)
        if not summary['readable']:
            return False, "File format not supported for replay", warnings
        
        # Try to read first few packets
        try:
            with PcapReader(file_path) as pcap_reader:
                packet_count = 0
                for packet in pcap_reader:
                    packet_count += 1
                    if packet_count >= 10:  # Just check first 10 packets
                        break
                
                if packet_count == 0:
                    return False, "No readable packets found", warnings
                    
        except Exception as e:
            return False, f"Error reading packets: {str(e)}", warnings
        
        return True, None, warnings
        
    except Exception as e:
        return False, f"Validation error: {str(e)}", warnings
