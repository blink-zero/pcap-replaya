#!/usr/bin/env python3
"""
Debug script to test PCAP file upload and analysis
"""
import sys
import os
import logging
from services.pcap_service import analyze_pcap_file, get_pcap_summary
from utils.validators import validate_pcap_file
from config import Config

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_pcap_file(file_path):
    """Debug a PCAP file upload process"""
    print(f"=== Debugging PCAP file: {file_path} ===")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File does not exist: {file_path}")
        return False
    
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
    
    # Check against config limits
    print(f"Max allowed size: {Config.MAX_CONTENT_LENGTH} bytes ({Config.MAX_CONTENT_LENGTH / (1024*1024*1024):.2f} GB)")
    if file_size > Config.MAX_CONTENT_LENGTH:
        print(f"ERROR: File exceeds maximum size limit")
        return False
    
    # Test file validation (simulating Flask FileStorage)
    class MockFile:
        def __init__(self, path):
            self.filename = os.path.basename(path)
            self._file = open(path, 'rb')
            self._size = os.path.getsize(path)
            
        def read(self, size=-1):
            return self._file.read(size)
            
        def seek(self, pos, whence=0):
            return self._file.seek(pos, whence)
            
        def tell(self):
            return self._file.tell()
            
        def close(self):
            self._file.close()
    
    try:
        mock_file = MockFile(file_path)
        is_valid, error_msg = validate_pcap_file(mock_file)
        mock_file.close()
        
        if not is_valid:
            print(f"ERROR: File validation failed: {error_msg}")
            return False
        else:
            print("✓ File validation passed")
    except Exception as e:
        print(f"ERROR: Exception during file validation: {str(e)}")
        return False
    
    # Test PCAP summary
    try:
        summary = get_pcap_summary(file_path)
        print(f"✓ PCAP summary: {summary}")
    except Exception as e:
        print(f"ERROR: Exception during PCAP summary: {str(e)}")
        return False
    
    # Test PCAP analysis
    try:
        print("Starting PCAP analysis...")
        analysis = analyze_pcap_file(file_path)
        print(f"✓ PCAP analysis completed:")
        print(f"  - Packet count: {analysis.get('packet_count', 'unknown')}")
        print(f"  - Duration: {analysis.get('duration', 'unknown')}")
        print(f"  - File format: {analysis.get('file_format', 'unknown')}")
        print(f"  - Protocols: {analysis.get('protocols', [])}")
        if analysis.get('analysis_limited'):
            print(f"  - Analysis limited: {analysis.get('analysis_limit_reason')}")
        return True
    except Exception as e:
        print(f"ERROR: Exception during PCAP analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_upload.py <pcap_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = debug_pcap_file(file_path)
    
    if success:
        print("\n✓ All tests passed - file should upload successfully")
    else:
        print("\n✗ Tests failed - this explains the upload failure")
