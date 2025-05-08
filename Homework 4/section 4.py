import dns.resolver
import sys


def get_ipv4_addresses(server_name):
    # Create a DNS resolver instance
    resolver = dns.resolver.Resolver()
    try:
        # Resolve the server name to get IPv4 addresses (type 'A' record)
        answers = resolver.resolve(server_name, 'A')
        # Convert the answers to a list of string representations of the IP addresses
        ipv4_addresses = [str(answer) for answer in answers]
        if ipv4_addresses:
            # Print the server name and the list of IPv4 addresses
            print(f"Server Name: {server_name}")
            print("IPv4 Addresses:")
            for ip in ipv4_addresses:
                print(ip)
            print()
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers) as e:
        # Handle specific DNS resolution errors
        print(f"DNS query failed for {server_name}: {e}")
    except dns.name.LabelTooLong:
        # Handle error for domain name labels that are too long
        print(f"Skipping {server_name} because a DNS label is too long.")
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")


def dnsmap(domain, subdomains):
    # Iterate over each subdomain
    for subdomain in subdomains:
        # Clean up the subdomain string
        subdomain_cleaned = subdomain.strip().strip('"').strip(',')
        # Combine the cleaned subdomain with the main domain
        full_domain = f"{subdomain_cleaned}.{domain}"
        if len(full_domain) <= 253:  # Check the total length of the domain
            # If the domain length is valid, get its IPv4 addresses
            get_ipv4_addresses(full_domain)
        else:
            # Skip the domain if its length is too long
            print(f"Skipping {full_domain} because a DNS label is too long.")


if __name__ == "__main__":
    # Check if the script received exactly 2 command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python dnsmap.py <domain> <subdomains_file>")
        sys.exit(1)

    # Extract the domain and subdomains file from the command-line arguments
    domain = sys.argv[1]
    subdomains_file = "section 3.txt"

    print(f"Domain: {domain}")
    # print(f"Subdomains file: {subdomains_file}")

    try:
        # Open and read the subdomains file
        with open(subdomains_file, 'r') as file:
            # Clean and load the subdomains into a list
            subdomains = [line.strip().strip('"').strip(',') for line in file if line.strip()]
        # print(f"Subdomains loaded: {subdomains}")
    except Exception as e:
        # Handle errors while reading the subdomains file
        # print(f"Error reading subdomains file: {e}")
        sys.exit(1)

    # Perform DNS mapping for the domain and its subdomains
    dnsmap(domain, subdomains)
