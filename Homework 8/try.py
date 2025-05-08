from scapy.all import rdpcap

# i found the correct ranges to filter

# List of IP addresses to check
ip_list = [
    '185.39.11.29', '185.39.10.95', '185.39.10.58', '193.27.228.146', '185.39.10.29',
    '185.39.11.111', '185.39.10.52', '185.153.197.104', '195.54.166.101', '31.10.5.89',
    '195.54.167.140', '185.39.10.27', '185.39.11.88', '195.54.167.144', '185.39.10.19',
    '79.124.62.18', '185.153.197.11', '92.63.196.3', '118.184.168.26', '194.26.29.31',
    '185.153.197.101', '45.134.179.57', '193.27.228.147', '2.92.254.38', '185.153.197.103',
    '193.27.228.145', '195.54.161.26', '185.156.73.38', '194.26.29.52', '156.96.156.136',
    '185.39.11.47', '194.26.29.53', '45.148.10.184', '185.176.27.14', '51.91.212.81',
    '213.217.1.225', '193.27.228.148', '171.67.71.100', '103.84.178.98', '195.54.167.141',
    '195.54.166.143', '188.129.232.167', '36.89.128.251', '193.27.228.135', '194.26.29.25',
    '185.53.88.240', '45.141.84.44', '94.102.51.17', '185.23.214.140', '45.92.126.74',
    '195.54.160.60'
]

# Read the pcap file
pcap_file_path = "SYNflood.pcapng"
packets = rdpcap(pcap_file_path)

# Convert the list of IP addresses to a set for faster lookup
ip_set = set(ip_list)

# Set to store unique destination IP addresses
unique_dst_ips = set()

# Iterate through the packets and collect unique destination addresses
for pkt in packets:
    if pkt.haslayer('IP'):
        src_ip = pkt['IP'].src
        dst_ip = pkt['IP'].dst

        # Check if the source IP is in the list of IP addresses
        if src_ip in ip_set:
            unique_dst_ips.add(dst_ip)

# Print the unique destination IP addresses
for ip in unique_dst_ips:
    print(ip)
