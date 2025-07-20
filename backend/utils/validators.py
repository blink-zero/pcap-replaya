import os
from werkzeug.utils import secure_filename
from config import Config


def validate_pcap_file(file):
    """
    Validate uploaded file to ensure it's a valid PCAP file.
    
    Args:
        file: FileStorage object from Flask request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    if not Config.allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    # Check file size (Flask handles this automatically, but we can add custom logic)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size == 0:
        return False, "File is empty"
    
    if file_size > Config.MAX_CONTENT_LENGTH:
        return False, f"File too large. Maximum size: {Config.MAX_CONTENT_LENGTH // (1024*1024*1024)}GB"
    
    # Check file magic bytes to verify it's actually a PCAP file
    try:
        file_header = file.read(16)  # Read first 16 bytes
        file.seek(0)  # Reset file pointer
        
        # PCAP magic numbers
        pcap_magic = [
            b'\xd4\xc3\xb2\xa1',  # Standard PCAP
            b'\xa1\xb2\xc3\xd4',  # Standard PCAP (swapped)
            b'\x0a\x0d\x0d\x0a',  # PCAPNG
        ]
        
        is_pcap = any(file_header.startswith(magic_bytes) for magic_bytes in pcap_magic)
        
        if not is_pcap:
            return False, "File does not appear to be a valid PCAP file"
            
    except Exception as e:
        return False, f"Error validating file: {str(e)}"
    
    return True, None


def validate_replay_config(config):
    """
    Validate replay configuration parameters.
    
    Args:
        config: Dictionary containing replay configuration
        
    Returns:
        tuple: (is_valid, error_message, sanitized_config)
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary", None
    
    sanitized = {}
    
    # Validate speed
    speed = config.get('speed', Config.DEFAULT_REPLAY_SPEED)
    speed_unit = config.get('speed_unit', 'multiplier')
    
    try:
        speed = float(speed)
        if speed <= 0:
            return False, "Speed must be greater than 0", None
        
        # Apply different limits based on speed unit
        if speed_unit == 'pps':
            # For PPS, allow up to 1 million packets per second
            if speed > 1000000:
                return False, "PPS cannot exceed 1,000,000", None
        else:
            # For multiplier, use existing limit
            if speed > Config.MAX_REPLAY_SPEED:
                return False, f"Speed multiplier cannot exceed {Config.MAX_REPLAY_SPEED}x", None
        
        sanitized['speed'] = speed
    except (ValueError, TypeError):
        return False, "Speed must be a valid number", None
    
    # Validate interface
    interface = config.get('interface', '').strip()
    if not interface:
        return False, "Network interface is required", None
    
    # Basic interface name validation (alphanumeric, hyphens, underscores)
    if not interface.replace('-', '').replace('_', '').replace('.', '').isalnum():
        return False, "Invalid interface name", None
    
    sanitized['interface'] = interface
    
    # Validate speed unit (if provided)
    speed_unit = config.get('speed_unit', 'multiplier')
    if speed_unit not in ['multiplier', 'pps']:
        return False, "Invalid speed unit. Must be 'multiplier' or 'pps'", None
    
    sanitized['speed_unit'] = speed_unit
    
    return True, None, sanitized


def sanitize_filename(filename):
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "unknown_file.pcap"
    
    # Use werkzeug's secure_filename and ensure extension
    safe_name = secure_filename(filename)
    
    # Ensure it has a valid extension
    if not Config.allowed_file(safe_name):
        name_part = safe_name.rsplit('.', 1)[0] if '.' in safe_name else safe_name
        safe_name = f"{name_part}.pcap"
    
    return safe_name
