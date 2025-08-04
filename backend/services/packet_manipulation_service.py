import os
import logging
import ipaddress
import re
from datetime import datetime
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, Dot1Q
from scapy.utils import PcapReader, PcapWriter, wrpcap


class PacketManipulator:
    """Service for manipulating packets before replay."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_manipulations = [
            'ip_mapping',
            'mac_mapping', 
            'port_mapping',
            'vlan_operations',
            'timestamp_shift',
            'payload_replacement'
        ]
    
    def manipulate_pcap(self, input_file, output_file, rules):
        """
        Apply manipulation rules to PCAP file.
        
        Args:
            input_file: Original PCAP file path
            output_file: Modified PCAP file path  
            rules: Dictionary of manipulation rules
            
        Returns:
            dict: Manipulation results and statistics
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Validate rules
        self._validate_rules(rules)
        
        self.logger.info(f"Starting packet manipulation: {input_file} -> {output_file}")
        self.logger.info(f"Rules: {rules}")
        
        stats = {
            'input_file': input_file,
            'output_file': output_file,
            'rules_applied': rules,
            'packets_processed': 0,
            'packets_modified': 0,
            'start_time': datetime.utcnow().isoformat(),
            'errors': []
        }
        
        try:
            # Use streaming approach for memory efficiency
            self._manipulate_streaming(input_file, output_file, rules, stats)
            
            stats['end_time'] = datetime.utcnow().isoformat()
            stats['success'] = True
            
            self.logger.info(f"Manipulation completed: {stats['packets_processed']} packets processed, "
                           f"{stats['packets_modified']} packets modified")
            
            return stats
            
        except Exception as e:
            stats['success'] = False
            stats['error'] = str(e)
            stats['end_time'] = datetime.utcnow().isoformat()
            self.logger.error(f"Manipulation failed: {str(e)}")
            raise
    
    def preview_manipulation(self, input_file, rules, sample_size=10):
        """
        Preview packet manipulation without creating output file.
        
        Args:
            input_file: PCAP file path
            rules: Manipulation rules
            sample_size: Number of packets to preview
            
        Returns:
            dict: Preview results with before/after packet summaries
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        self._validate_rules(rules)
        
        preview_results = {
            'input_file': input_file,
            'rules': rules,
            'samples': [],
            'total_packets_analyzed': 0
        }
        
        try:
            with PcapReader(input_file) as pcap_reader:
                for i, packet in enumerate(pcap_reader):
                    if i >= sample_size:
                        break
                    
                    original_summary = self._get_packet_summary(packet)
                    modified_packet = self._apply_rules(packet, rules)
                    modified_summary = self._get_packet_summary(modified_packet)
                    
                    # Check if packet was actually modified
                    was_modified = original_summary != modified_summary
                    
                    preview_results['samples'].append({
                        'packet_number': i + 1,
                        'original_summary': original_summary,
                        'modified_summary': modified_summary,
                        'was_modified': was_modified,
                        'original_hex': self._get_packet_hex(packet)[:100] + '...',
                        'modified_hex': self._get_packet_hex(modified_packet)[:100] + '...'
                    })
                    
                    preview_results['total_packets_analyzed'] = i + 1
            
            return preview_results
            
        except Exception as e:
            self.logger.error(f"Preview failed: {str(e)}")
            raise
    
    def get_packet_analysis(self, input_file, analysis_limit=1000):
        """
        Analyze PCAP file to identify manipulation opportunities.
        
        Args:
            input_file: PCAP file path
            analysis_limit: Maximum packets to analyze
            
        Returns:
            dict: Analysis results with unique IPs, MACs, ports, etc.
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        analysis = {
            'unique_ips': set(),
            'unique_macs': set(),
            'unique_ports': set(),
            'protocols': set(),
            'vlan_tags': set(),
            'packet_count': 0,
            'has_timestamps': False
        }
        
        try:
            with PcapReader(input_file) as pcap_reader:
                for i, packet in enumerate(pcap_reader):
                    if i >= analysis_limit:
                        break
                    
                    analysis['packet_count'] = i + 1
                    
                    # Check for timestamps
                    if hasattr(packet, 'time'):
                        analysis['has_timestamps'] = True
                    
                    # Analyze Ethernet layer
                    if packet.haslayer(Ether):
                        eth = packet[Ether]
                        analysis['unique_macs'].add(eth.src)
                        analysis['unique_macs'].add(eth.dst)
                    
                    # Analyze VLAN tags
                    if packet.haslayer(Dot1Q):
                        vlan = packet[Dot1Q]
                        analysis['vlan_tags'].add(vlan.vlan)
                    
                    # Analyze IP layer
                    if packet.haslayer(IP):
                        ip = packet[IP]
                        analysis['unique_ips'].add(ip.src)
                        analysis['unique_ips'].add(ip.dst)
                        analysis['protocols'].add('IPv4')
                        
                        # Analyze transport layer
                        if packet.haslayer(TCP):
                            tcp = packet[TCP]
                            analysis['unique_ports'].add(tcp.sport)
                            analysis['unique_ports'].add(tcp.dport)
                            analysis['protocols'].add('TCP')
                        elif packet.haslayer(UDP):
                            udp = packet[UDP]
                            analysis['unique_ports'].add(udp.sport)
                            analysis['unique_ports'].add(udp.dport)
                            analysis['protocols'].add('UDP')
                        elif packet.haslayer(ICMP):
                            analysis['protocols'].add('ICMP')
                    
                    # Analyze IPv6
                    elif packet.haslayer(IPv6):
                        ipv6 = packet[IPv6]
                        analysis['unique_ips'].add(ipv6.src)
                        analysis['unique_ips'].add(ipv6.dst)
                        analysis['protocols'].add('IPv6')
            
            # Convert sets to sorted lists for JSON serialization
            analysis['unique_ips'] = sorted(list(analysis['unique_ips']))
            analysis['unique_macs'] = sorted(list(analysis['unique_macs']))
            analysis['unique_ports'] = sorted(list(analysis['unique_ports']))
            analysis['protocols'] = sorted(list(analysis['protocols']))
            analysis['vlan_tags'] = sorted(list(analysis['vlan_tags']))
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def _manipulate_streaming(self, input_file, output_file, rules, stats):
        """Perform streaming manipulation for memory efficiency."""
        writer = PcapWriter(output_file)
        
        try:
            with PcapReader(input_file) as pcap_reader:
                for packet in pcap_reader:
                    try:
                        original_packet = packet.copy()
                        modified_packet = self._apply_rules(packet, rules)
                        
                        writer.write(modified_packet)
                        stats['packets_processed'] += 1
                        
                        # Check if packet was actually modified
                        if self._packets_differ(original_packet, modified_packet):
                            stats['packets_modified'] += 1
                        
                        # Progress logging for large files
                        if stats['packets_processed'] % 10000 == 0:
                            self.logger.info(f"Processed {stats['packets_processed']} packets")
                            
                    except Exception as e:
                        error_msg = f"Error processing packet {stats['packets_processed']}: {str(e)}"
                        self.logger.warning(error_msg)
                        stats['errors'].append(error_msg)
                        
                        # Write original packet if modification fails
                        writer.write(packet)
                        stats['packets_processed'] += 1
        
        finally:
            writer.close()
    
    def _apply_rules(self, packet, rules):
        """Apply manipulation rules to a single packet."""
        modified_packet = packet.copy()
        
        try:
            # IP Address Manipulation
            if 'ip_mapping' in rules and rules['ip_mapping']:
                modified_packet = self._apply_ip_mapping(modified_packet, rules['ip_mapping'])
            
            # MAC Address Manipulation
            if 'mac_mapping' in rules and rules['mac_mapping']:
                modified_packet = self._apply_mac_mapping(modified_packet, rules['mac_mapping'])
            
            # Port Manipulation
            if 'port_mapping' in rules and rules['port_mapping']:
                modified_packet = self._apply_port_mapping(modified_packet, rules['port_mapping'])
            
            # VLAN Operations
            if 'vlan_operations' in rules and rules['vlan_operations']:
                modified_packet = self._apply_vlan_operations(modified_packet, rules['vlan_operations'])
            
            # Timestamp Shift
            if 'timestamp_shift' in rules and rules['timestamp_shift']:
                modified_packet = self._apply_timestamp_shift(modified_packet, rules['timestamp_shift'])
            
            # Payload Replacement
            if 'payload_replacement' in rules and rules['payload_replacement']:
                modified_packet = self._apply_payload_replacement(modified_packet, rules['payload_replacement'])
            
            return modified_packet
            
        except Exception as e:
            self.logger.warning(f"Error applying rules to packet: {str(e)}")
            return packet  # Return original packet if modification fails
    
    def _apply_ip_mapping(self, packet, ip_mapping):
        """Apply IP address mapping to packet."""
        if packet.haslayer(IP):
            ip_layer = packet[IP]
            
            # Source IP replacement
            if ip_layer.src in ip_mapping:
                ip_layer.src = ip_mapping[ip_layer.src]
            
            # Destination IP replacement  
            if ip_layer.dst in ip_mapping:
                ip_layer.dst = ip_mapping[ip_layer.dst]
            
            # Recalculate checksums
            del ip_layer.chksum
            if packet.haslayer(TCP):
                del packet[TCP].chksum
            elif packet.haslayer(UDP):
                del packet[UDP].chksum
        
        elif packet.haslayer(IPv6):
            ipv6_layer = packet[IPv6]
            
            # Source IPv6 replacement
            if ipv6_layer.src in ip_mapping:
                ipv6_layer.src = ip_mapping[ipv6_layer.src]
            
            # Destination IPv6 replacement
            if ipv6_layer.dst in ip_mapping:
                ipv6_layer.dst = ip_mapping[ipv6_layer.dst]
        
        return packet
    
    def _apply_mac_mapping(self, packet, mac_mapping):
        """Apply MAC address mapping to packet."""
        if packet.haslayer(Ether):
            eth_layer = packet[Ether]
            
            if eth_layer.src in mac_mapping:
                eth_layer.src = mac_mapping[eth_layer.src]
            
            if eth_layer.dst in mac_mapping:
                eth_layer.dst = mac_mapping[eth_layer.dst]
        
        return packet
    
    def _apply_port_mapping(self, packet, port_mapping):
        """Apply port mapping to packet."""
        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            if tcp_layer.sport in port_mapping:
                tcp_layer.sport = port_mapping[tcp_layer.sport]
            if tcp_layer.dport in port_mapping:
                tcp_layer.dport = port_mapping[tcp_layer.dport]
            del tcp_layer.chksum
        
        elif packet.haslayer(UDP):
            udp_layer = packet[UDP]
            if udp_layer.sport in port_mapping:
                udp_layer.sport = port_mapping[udp_layer.sport]
            if udp_layer.dport in port_mapping:
                udp_layer.dport = port_mapping[udp_layer.dport]
            del udp_layer.chksum
        
        return packet
    
    def _apply_vlan_operations(self, packet, vlan_ops):
        """Apply VLAN operations to packet."""
        if vlan_ops.get('add_vlan'):
            # Add VLAN tag
            if packet.haslayer(Ether) and not packet.haslayer(Dot1Q):
                vlan_id = vlan_ops['add_vlan']
                eth = packet[Ether]
                new_packet = Ether(src=eth.src, dst=eth.dst) / Dot1Q(vlan=vlan_id) / eth.payload
                return new_packet
        
        elif vlan_ops.get('remove_vlan'):
            # Remove VLAN tag
            if packet.haslayer(Dot1Q):
                eth = packet[Ether]
                new_packet = Ether(src=eth.src, dst=eth.dst) / packet[Dot1Q].payload
                return new_packet
        
        elif vlan_ops.get('modify_vlan'):
            # Modify existing VLAN tag
            if packet.haslayer(Dot1Q):
                packet[Dot1Q].vlan = vlan_ops['modify_vlan']
        
        return packet
    
    def _apply_timestamp_shift(self, packet, time_shift):
        """Apply timestamp shift to packet."""
        if hasattr(packet, 'time'):
            packet.time += time_shift
        return packet
    
    def _apply_payload_replacement(self, packet, payload_rules):
        """Apply payload replacement rules."""
        if packet.haslayer(Raw):
            payload = packet[Raw].load
            
            for rule in payload_rules:
                if 'search' in rule and 'replace' in rule:
                    search_bytes = rule['search'].encode('utf-8') if isinstance(rule['search'], str) else rule['search']
                    replace_bytes = rule['replace'].encode('utf-8') if isinstance(rule['replace'], str) else rule['replace']
                    payload = payload.replace(search_bytes, replace_bytes)
            
            packet[Raw].load = payload
        
        return packet
    
    def _validate_rules(self, rules):
        """Validate manipulation rules."""
        if not isinstance(rules, dict):
            raise ValueError("Rules must be a dictionary")
        
        # Validate IP mappings
        if 'ip_mapping' in rules:
            for src_ip, dst_ip in rules['ip_mapping'].items():
                if not self._is_valid_ip(src_ip) or not self._is_valid_ip(dst_ip):
                    raise ValueError(f"Invalid IP address mapping: {src_ip} -> {dst_ip}")
        
        # Validate MAC mappings
        if 'mac_mapping' in rules:
            for src_mac, dst_mac in rules['mac_mapping'].items():
                if not self._is_valid_mac(src_mac) or not self._is_valid_mac(dst_mac):
                    raise ValueError(f"Invalid MAC address mapping: {src_mac} -> {dst_mac}")
        
        # Validate port mappings
        if 'port_mapping' in rules:
            for src_port, dst_port in rules['port_mapping'].items():
                if not (1 <= int(src_port) <= 65535) or not (1 <= int(dst_port) <= 65535):
                    raise ValueError(f"Invalid port mapping: {src_port} -> {dst_port}")
    
    def _is_valid_ip(self, ip_str):
        """Validate IP address (IPv4 or IPv6)."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    def _is_valid_mac(self, mac_str):
        """Validate MAC address."""
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac_str))
    
    def _get_packet_summary(self, packet):
        """Get a human-readable summary of the packet."""
        try:
            return packet.summary()
        except:
            return "Unknown packet format"
    
    def _get_packet_hex(self, packet):
        """Get hexadecimal representation of packet."""
        try:
            return packet.hexdump(dump=True)
        except:
            return "Unable to generate hex dump"
    
    def _packets_differ(self, packet1, packet2):
        """Check if two packets are different."""
        try:
            return bytes(packet1) != bytes(packet2)
        except:
            return True  # Assume different if comparison fails


# Global packet manipulator instance
packet_manipulator = PacketManipulator()


def get_packet_manipulator():
    """Get the global packet manipulator instance."""
    return packet_manipulator
