import subprocess
import threading
import time
import uuid
import logging
import os
import signal
from datetime import datetime
from flask_socketio import emit


class ReplayManager:
    """Manages PCAP replay operations using tcpreplay."""
    
    def __init__(self):
        self.current_process = None
        self.current_replay_id = None
        self.replay_thread = None
        self.is_replay_running = False
        self.replay_stats = {}
        self.socketio = None
        self.lock = threading.Lock()
    
    def start_replay(self, file_path, interface, speed, speed_unit='multiplier', continuous=False, socketio=None):
        """
        Start PCAP replay with specified parameters.
        
        Args:
            file_path: Path to PCAP file
            interface: Network interface name
            speed: Replay speed value
            speed_unit: Speed unit ('multiplier', 'mbps', 'gbps')
            continuous: Whether to replay continuously until stopped
            socketio: SocketIO instance for real-time updates
            
        Returns:
            str: Replay ID
        """
        with self.lock:
            if self.is_replay_running:
                raise RuntimeError("Replay already in progress")
            
            replay_id = str(uuid.uuid4())
            self.current_replay_id = replay_id
            self.socketio = socketio
            
            # Build tcpreplay command
            cmd = self._build_tcpreplay_command(file_path, interface, speed, speed_unit)
            
            # Initialize replay stats
            self.replay_stats = {
                'replay_id': replay_id,
                'file_path': file_path,
                'interface': interface,
                'speed': speed,
                'speed_unit': speed_unit,
                'continuous': continuous,
                'start_time': datetime.utcnow().isoformat(),
                'status': 'starting',
                'packets_sent': 0,
                'bytes_sent': 0,
                'progress_percent': 0,
                'elapsed_time': 0,
                'estimated_remaining': 0,
                'error': None,
                'loop_count': 0
            }
            
            # Start replay in separate thread
            self.replay_thread = threading.Thread(
                target=self._run_replay,
                args=(cmd, replay_id),
                daemon=True
            )
            self.is_replay_running = True
            self.replay_thread.start()
            
            # Log the command prominently for user visibility
            cmd_str = ' '.join(cmd)
            logging.info(f"REPLAY_COMMAND: {cmd_str}")
            logging.info(f"Started replay {replay_id} for file: {os.path.basename(file_path)}")
            logging.info(f"Interface: {interface}, Speed: {speed} {speed_unit}")
            
            # Log expected vs actual timing for debugging
            if speed_unit == 'multiplier' and hasattr(self, '_log_timing_expectation'):
                self._log_timing_expectation(file_path, speed)
            
            return replay_id
    
    def stop_replay(self):
        """Stop the current replay."""
        with self.lock:
            if not self.is_replay_running:
                return False
            
            logging.info(f"STOP_COMMAND: Terminating replay process {self.current_replay_id}")
            
            if self.current_process:
                try:
                    # Send SIGTERM first
                    logging.info("Sending SIGTERM to tcpreplay process")
                    self.current_process.terminate()
                    
                    # Wait a bit for graceful shutdown
                    try:
                        self.current_process.wait(timeout=5)
                        logging.info("tcpreplay process terminated gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't stop gracefully
                        logging.info("Forcing kill of tcpreplay process")
                        self.current_process.kill()
                        self.current_process.wait()
                        
                except Exception as e:
                    logging.error(f"Error stopping replay process: {str(e)}")
            
            self.is_replay_running = False
            self.replay_stats['status'] = 'stopped'
            self.replay_stats['end_time'] = datetime.utcnow().isoformat()
            
            # Update history service
            self._update_history_status()
            
            # Notify clients
            if self.socketio:
                self.socketio.emit('replay_status', self.replay_stats)
            
            logging.info(f"Replay {self.current_replay_id} stopped successfully")
            return True
    
    def is_running(self):
        """Check if replay is currently running."""
        return self.is_replay_running
    
    def get_current_replay_id(self):
        """Get current replay ID."""
        return self.current_replay_id
    
    def get_status(self):
        """Get current replay status."""
        with self.lock:
            return self.replay_stats.copy()
    
    def test_interface_access(self, interface):
        """Test if tcpreplay can access the specified interface."""
        try:
            # Test with tcpreplay --version to see if it's available
            version_cmd = ['tcpreplay', '--version']
            logging.info(f"TEST_COMMAND: {' '.join(version_cmd)}")
            result = subprocess.run(version_cmd, 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logging.error(f"tcpreplay not available: {result.stderr}")
                return False, "tcpreplay not available"
            
            # Test interface access with a dry run
            test_cmd = ['tcpreplay', '--intf1', interface, '--dualfile']
            logging.info(f"TEST_COMMAND: {' '.join(test_cmd)}")
            result = subprocess.run(test_cmd, 
                                  capture_output=True, text=True, timeout=5)
            
            # tcpreplay will fail without a file, but we can check the error message
            if "permission denied" in result.stderr.lower():
                logging.warning(f"Permission denied accessing interface {interface}")
                return False, "Permission denied accessing interface"
            elif "no such device" in result.stderr.lower():
                logging.warning(f"Interface {interface} not found")
                return False, f"Interface {interface} not found"
            
            logging.info(f"Interface {interface} is accessible")
            return True, "Interface accessible"
            
        except subprocess.TimeoutExpired:
            logging.error(f"tcpreplay test timed out for interface {interface}")
            return False, "tcpreplay test timed out"
        except Exception as e:
            logging.error(f"Interface test failed: {str(e)}")
            return False, f"Test failed: {str(e)}"

    def _build_tcpreplay_command(self, file_path, interface, speed, speed_unit):
        """Build tcpreplay command based on parameters."""
        cmd = ['tcpreplay']
        
        # Add interface
        cmd.extend(['-i', interface])
        
        # Add speed control based on unit
        if speed_unit == 'pps':
            # Use --pps for packets per second
            cmd.extend(['--pps', f'{int(speed)}'])
        else:
            # Use --multiplier for speed multiplier (default)
            cmd.extend(['--multiplier', f'{speed:.2f}'])
        
        # Add timing options for better accuracy
        cmd.extend([
            '--timer', 'select',  # Use select() timer for better precision
            '--quiet'             # Quiet mode for better performance
        ])
        
        # Add the PCAP file
        cmd.append(file_path)
        
        return cmd
    
    def _run_replay(self, cmd, replay_id):
        """Run the tcpreplay command and monitor progress."""
        try:
            self.replay_stats['status'] = 'running'
            continuous = self.replay_stats.get('continuous', False)
            
            # Notify clients that replay started
            if self.socketio:
                self.socketio.emit('replay_status', self.replay_stats)
            
            # Log continuous mode
            if continuous:
                logging.info(f"Starting continuous replay mode for {replay_id}")
            
            # Main replay loop - runs once for normal mode, loops for continuous
            while self.is_replay_running:
                # Increment loop count
                self.replay_stats['loop_count'] += 1
                
                if continuous and self.replay_stats['loop_count'] > 1:
                    logging.info(f"Starting loop #{self.replay_stats['loop_count']} for continuous replay {replay_id}")
                
                # Start tcpreplay process
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                start_time = time.time()
                last_progress_emit = 0
                
                # Monitor output for progress
                for line in iter(self.current_process.stdout.readline, ''):
                    if not self.is_replay_running:
                        break
                    
                    line = line.strip()
                    if line:
                        # Only log important lines, not every output line
                        if 'Actual:' in line or 'Error' in line or 'Failed' in line:
                            logging.info(f"tcpreplay output: {line}")
                        
                        # Parse tcpreplay output for progress information
                        self._parse_tcpreplay_output(line, start_time)
                        
                        # Emit progress update only every 2 seconds to reduce overhead
                        current_time = time.time()
                        if self.socketio and (current_time - last_progress_emit) >= 2:
                            progress_data = {
                                'replay_id': replay_id,
                                'progress': self.replay_stats['progress_percent'],
                                'packets_sent': self.replay_stats['packets_sent'],
                                'bytes_sent': self.replay_stats['bytes_sent'],
                                'elapsed_time': self.replay_stats['elapsed_time'],
                                'loop_count': self.replay_stats['loop_count']
                            }
                            if continuous:
                                progress_data['continuous'] = True
                            self.socketio.emit('replay_progress', progress_data)
                            last_progress_emit = current_time
                
                # Wait for process to complete and capture any error output
                stdout, stderr = self.current_process.communicate()
                return_code = self.current_process.returncode
                
                # Process any remaining output
                if stdout:
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            logging.info(f"tcpreplay final output: {line.strip()}")
                            self._parse_tcpreplay_output(line.strip(), start_time)
                
                # Check if replay failed
                if return_code != 0:
                    error_msg = f"tcpreplay exited with code {return_code}"
                    if stderr:
                        error_msg += f": {stderr.strip()}"
                    self.replay_stats['error'] = error_msg
                    logging.error(f"tcpreplay error: {error_msg}")
                    break
                
                # If not continuous mode, break after one iteration
                if not continuous:
                    break
                
                # For continuous mode, reset progress for next loop
                if continuous and self.is_replay_running:
                    self.replay_stats['progress_percent'] = 0
                    # Small delay between loops to prevent overwhelming the system
                    time.sleep(0.1)
            
            # Update final status
            with self.lock:
                if self.replay_stats.get('error'):
                    self.replay_stats['status'] = 'failed'
                elif not self.is_replay_running:
                    self.replay_stats['status'] = 'stopped'
                else:
                    self.replay_stats['status'] = 'completed'
                    self.replay_stats['progress_percent'] = 100
                
                self.replay_stats['end_time'] = datetime.utcnow().isoformat()
                self.is_replay_running = False
                
                # Update history service
                self._update_history_status()
                
                # Final status update
                if self.socketio:
                    self.socketio.emit('replay_status', self.replay_stats)
            
            if continuous:
                logging.info(f"Continuous replay {replay_id} completed {self.replay_stats['loop_count']} loops")
            else:
                logging.info(f"Replay {replay_id} completed")
            
        except Exception as e:
            logging.error(f"Error during replay {replay_id}: {str(e)}")
            
            with self.lock:
                self.replay_stats['status'] = 'error'
                self.replay_stats['error'] = str(e)
                self.replay_stats['end_time'] = datetime.utcnow().isoformat()
                self.is_replay_running = False
                
                if self.socketio:
                    self.socketio.emit('replay_status', self.replay_stats)
        
        finally:
            self.current_process = None
    
    def _parse_tcpreplay_output(self, line, start_time):
        """Parse tcpreplay output to extract progress information."""
        try:
            current_time = time.time()
            elapsed = current_time - start_time
            self.replay_stats['elapsed_time'] = elapsed
            
            # Log the line for debugging
            logging.debug(f"tcpreplay output: {line}")
            
            # tcpreplay verbose output patterns:
            # "Actual: 2809 packets (1588752 bytes) sent in 20.47 seconds"
            # "Rated: 77648.8 Bps, 0.62 Mbps, 137.25 pps"
            # "Statistics for network device: ens224"
            
            # Look for final statistics line
            if 'Actual:' in line and 'packets' in line and 'bytes' in line and 'sent in' in line:
                # Parse: "Actual: 78 packets (49693 bytes) sent in 3.71 seconds"
                try:
                    logging.info(f"Parsing final statistics: {line}")
                    
                    # Extract packets - look for number before "packets"
                    import re
                    packets_match = re.search(r'(\d+)\s+packets', line)
                    if packets_match:
                        packets = int(packets_match.group(1))
                        self.replay_stats['packets_sent'] = packets
                        logging.info(f"Extracted packets: {packets}")
                    
                    # Extract bytes - look for number in parentheses before "bytes"
                    bytes_match = re.search(r'\((\d+)\s+bytes\)', line)
                    if bytes_match:
                        bytes_sent = int(bytes_match.group(1))
                        self.replay_stats['bytes_sent'] = bytes_sent
                        logging.info(f"Extracted bytes: {bytes_sent}")
                    
                    # Extract time - look for number before "seconds"
                    time_match = re.search(r'sent in\s+([\d.]+)\s+seconds', line)
                    if time_match:
                        actual_time = float(time_match.group(1))
                        self.replay_stats['actual_replay_time'] = actual_time
                        self.replay_stats['elapsed_time'] = actual_time
                        logging.info(f"Extracted time: {actual_time}")
                    
                    # Set progress to 100% when we get final stats
                    self.replay_stats['progress_percent'] = 100
                    logging.info(f"Updated stats: {self.replay_stats}")
                    
                except (ValueError, IndexError) as e:
                    logging.error(f"Error parsing statistics line: {e}")
            
            # Look for rate information
            elif 'Rated:' in line and 'Bps' in line:
                # Parse: "Rated: 77648.8 Bps, 0.62 Mbps, 137.25 pps"
                try:
                    if 'pps' in line:
                        parts = line.split(',')
                        for part in parts:
                            if 'pps' in part:
                                pps_str = part.strip().split()[0]
                                pps = float(pps_str)
                                self.replay_stats['packets_per_second'] = pps
                                break
                except (ValueError, IndexError) as e:
                    logging.debug(f"Error parsing rate line: {e}")
            
            # For progress estimation during replay, use elapsed time
            # This is approximate since tcpreplay doesn't give real-time progress
            if elapsed > 0 and self.replay_stats['packets_sent'] == 0:
                # Estimate progress based on time (very rough)
                estimated_duration = 10  # Assume 10 seconds max for small files
                progress = min(90, (elapsed / estimated_duration) * 100)
                self.replay_stats['progress_percent'] = progress
            
        except Exception as e:
            logging.debug(f"Error parsing tcpreplay output: {str(e)}")
    
    def _update_history_status(self):
        """Update the history service with replay completion status."""
        try:
            from services.history_service import get_history_service
            
            history_service = get_history_service()
            replay_id = self.replay_stats.get('replay_id')
            status = self.replay_stats.get('status')
            
            if replay_id and status:
                # Prepare update data
                update_data = {}
                
                if self.replay_stats.get('packets_sent'):
                    update_data['packets_sent'] = self.replay_stats['packets_sent']
                
                if self.replay_stats.get('error'):
                    update_data['error_message'] = self.replay_stats['error']
                
                # Update history
                history_service.update_replay_status(replay_id, status, **update_data)
                logging.info(f"Updated history for replay {replay_id}: {status}")
            
        except Exception as e:
            logging.error(f"Error updating history status: {e}")
    
    def _log_timing_expectation(self, file_path, speed):
        """Log expected timing for debugging speed issues."""
        try:
            from services.pcap_service import get_pcap_service
            
            pcap_service = get_pcap_service()
            pcap_info = pcap_service.get_pcap_info(file_path)
            
            if pcap_info and 'duration' in pcap_info:
                original_duration = pcap_info['duration']
                expected_duration = original_duration / speed
                
                logging.info(f"TIMING DEBUG - Original duration: {original_duration:.2f}s, "
                           f"Speed: {speed}x, Expected duration: {expected_duration:.2f}s")
                
                self.replay_stats['expected_duration'] = expected_duration
                self.replay_stats['original_duration'] = original_duration
            
        except Exception as e:
            logging.debug(f"Could not log timing expectation: {e}")


# Global replay manager instance
replay_manager = ReplayManager()


def get_replay_manager():
    """Get the global replay manager instance."""
    return replay_manager
