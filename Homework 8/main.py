from scapy.all import rdpcap, wrpcap, IP, TCP
import ipaddress
from collections import defaultdict
from datetime import datetime, timedelta

# Define IP ranges
SOURCE_IP_RANGES = [
    ('2.92.254.38', '94.102.51.17'),
    ('103.84.178.98', '156.96.156.136'),
    ('171.67.71.100', '213.217.1.225')
]
DEST_IP_RANGE = ('100.64.0.0', '100.64.255.255')
PACKET_RATE_THRESHOLD = 10  # Minimum packets per second

# Read the pcap file
input_pcap_file_path = "SYNflood.pcapng"
packets = rdpcap(input_pcap_file_path)

# Convert IP range to integer representation
def ip_to_int(ip):
    return int(ipaddress.IPv4Address(ip))

def is_ip_in_any_range(ip, ip_ranges):
    ip_int = ip_to_int(ip)
    for ip_range in ip_ranges:
        if ip_to_int(ip_range[0]) <= ip_int <= ip_to_int(ip_range[1]):
            return True
    return False

# Dictionary to store packet timestamps for each source IP
packet_timestamps = defaultdict(list)

# First pass: Collect packet timestamps
for pkt in packets:
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        timestamp = datetime.fromtimestamp(pkt.time)

        if is_ip_in_any_range(src_ip, SOURCE_IP_RANGES) and is_ip_in_any_range(dst_ip, [DEST_IP_RANGE]):
            packet_timestamps[src_ip].append(timestamp)

# Filter out sources that don't meet the packet rate threshold
high_rate_sources = set()
for src_ip, timestamps in packet_timestamps.items():
    timestamps.sort()
    for i in range(len(timestamps) - PACKET_RATE_THRESHOLD + 1):
        if timestamps[i + PACKET_RATE_THRESHOLD - 1] - timestamps[i] <= timedelta(seconds=1):
            high_rate_sources.add(src_ip)
            break

# Dictionary to track seen sequence numbers to identify retransmissions
seen_packets = set()
unique_src_ips = set()

# Second pass: Filter packets based on high rate sources, TCP flags, and retransmissions
filtered_packets = []
for pkt in packets:
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        tcp_flags = pkt[TCP].flags
        seq_num = pkt[TCP].seq

        if src_ip in high_rate_sources and is_ip_in_any_range(dst_ip, [DEST_IP_RANGE]):
            packet_id = (src_ip, dst_ip, seq_num)
            if packet_id not in seen_packets:
                if tcp_flags & 0x02 or tcp_flags & 0x10:  # SYN flag or ACK flag
                    filtered_packets.append(pkt)
                    unique_src_ips.add(src_ip)
                seen_packets.add(packet_id)

# Save the filtered packets to a new pcap file
output_pcap_file_path = "filtered_SYNflood.pcapng"
wrpcap(output_pcap_file_path, filtered_packets)

# Write unique source IPs to a text file
unique_src_ips_file_path = "unique_src_ips.txt"
with open(unique_src_ips_file_path, 'w') as file:
    for ip in unique_src_ips:
        file.write(ip + '\n')

print(f"Filtered packets have been saved to: {output_pcap_file_path}")
print(f"Unique source IPs have been saved to: {unique_src_ips_file_path}")
