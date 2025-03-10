import os
import requests
import argparse


# Cloudflare API credentials
API_KEY = os.getenv("CLOUDFLARE_API_KEY")  # Set this in your environment variables
EMAIL = os.getenv("CLOUDFLARE_EMAIL")  # Set this in your environment variables
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")

# Base URL for Cloudflare API
BASE_URL = "https://api.cloudflare.com/client/v4"

# Headers for authentication
HEADERS = {
    "X-Auth-Email": EMAIL,
    "X-Auth-Key": API_KEY,
    "Content-Type": "application/json"
}

def list_dns_records():
    """Fetches and displays all DNS records for the given zone."""
    url = f"{BASE_URL}/zones/{ZONE_ID}/dns_records"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        records = response.json()["result"]
        for record in records:
            print(f"{record['type']} {record['name']} -> {record['content']}")
    else:
        print("Failed to fetch DNS records:", response.json())

def add_dns_record(record_type, name, content, ttl=1, proxied=False):
    """Adds a new DNS record."""
    url = f"{BASE_URL}/zones/{ZONE_ID}/dns_records"
    data = {
        "type": record_type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200 or response.status_code == 201:
        print("Successfully added DNS record:", response.json()["result"])
    else:
        print("Failed to add DNS record:", response.json())

def delete_dns_record(record_id):
    """Deletes a DNS record by ID."""
    url = f"{BASE_URL}/zones/{ZONE_ID}/dns_records/{record_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 200:
        print("Successfully deleted DNS record")
    else:
        print("Failed to delete DNS record:", response.json())

def block_ip(ip):
    """Blocks a specific IP address using Cloudflare firewall rules."""
    
    url = f"{BASE_URL}/zones/{ZONE_ID}/firewall/rules"
    
    data = [{
        "action": "block",
        "priority": 1,
        "paused": False,
        "description": f"Blocked IP {ip}",
        "filter": {
            "expression": f"(ip.src eq \"{ip}\")"
        }
    }]
    
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code in [200, 201]:
        print(f"Successfully blocked IP: {ip}")
    else:
        print("Failed to block IP:", response.json())
        
def unblock_ip(rule_id):
    """Removes a firewall rule to unblock an IP address."""
    url = f"{BASE_URL}/zones/{ZONE_ID}/firewall/rules/{rule_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 200:
        print("Successfully unblocked IP")
    else:
        print("Failed to unblock IP:", response.json())

def list_firewall_rules():
    """Lists all firewall rules for the given zone."""
    url = f"{BASE_URL}/zones/{ZONE_ID}/firewall/rules"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        rules = response.json()["result"]
        for rule in rules:
            print(f"Rule ID: {rule['id']} | Target: {rule['configuration']['target']} | Value: {rule['configuration']['value']} | Mode: {rule['mode']}")
    else:
        print("Failed to fetch firewall rules:", response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare DNS and Firewall Management Tool")
    parser.add_argument("--list-dns", action="store_true", help="List all DNS records")
    parser.add_argument("--add-dns", nargs=3, metavar=("TYPE", "NAME", "CONTENT"), help="Add a new DNS record")
    parser.add_argument("--delete-dns", metavar="RECORD_ID", help="Delete a DNS record by ID")
    parser.add_argument("--block-ip", metavar="IP", help="Block an IP address")
    parser.add_argument("--unblock-ip", metavar="RULE_ID", help="Unblock an IP address by rule ID")
    parser.add_argument("--list-firewall", action="store_true", help="List all firewall rules")
    
    args = parser.parse_args()
    
    if args.list_dns:
        list_dns_records()
    elif args.add_dns:
        add_dns_record(*args.add_dns)
    elif args.delete_dns:
        delete_dns_record(args.delete_dns)
    elif args.block_ip:
        block_ip(args.block_ip)
    elif args.unblock_ip:
        unblock_ip(args.unblock_ip)
    elif args.list_firewall:
        list_firewall_rules()
    else:
        parser.print_help()