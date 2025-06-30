#!/usr/bin/env python3
"""
Check IP Address and MongoDB Atlas Connectivity
Diagnoses IP whitelist issues with MongoDB Atlas
"""

import requests
import socket
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_public_ip():
    """Get current public IP address"""
    try:
        # Try multiple services in case one is down
        services = [
            'https://api.ipify.org',
            'https://ipinfo.io/ip',
            'https://icanhazip.com',
            'https://ident.me'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"✅ Current public IP: {ip}")
                    return ip
            except:
                continue
        
        print("❌ Could not determine public IP address")
        return None
    except Exception as e:
        print(f"❌ Error getting public IP: {e}")
        return None

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"📍 Local IP address: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"❌ Error getting local IP: {e}")
        return None

def test_mongodb_connectivity():
    """Test basic connectivity to MongoDB Atlas"""
    mongodb_url = os.getenv("MONGODB_URL", "")
    
    if "mongodb+srv://" in mongodb_url:
        try:
            # Extract hostname
            hostname = mongodb_url.split("@")[1].split("/")[0].split("?")[0]
            print(f"\n🌐 Testing connectivity to MongoDB Atlas: {hostname}")
            
            # Test DNS resolution
            try:
                ip_addresses = socket.gethostbyname_ex(hostname)
                print(f"✅ DNS resolution successful:")
                for ip in ip_addresses[2]:
                    print(f"   - {ip}")
            except socket.gaierror as e:
                print(f"❌ DNS resolution failed: {e}")
                return False
            
            # Test port connectivity
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((hostname, 27017))
                sock.close()
                
                if result == 0:
                    print("✅ Port 27017 is reachable")
                    return True
                else:
                    print("❌ Port 27017 is not reachable (likely IP whitelist issue)")
                    return False
            except Exception as e:
                print(f"❌ Port connectivity test failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Could not parse MongoDB URL: {e}")
            return False
    else:
        print("❌ Invalid MongoDB URL format")
        return False

def check_network_info():
    """Check network configuration"""
    print("\n🔍 NETWORK CONFIGURATION")
    print("=" * 50)
    
    # Check if using VPN
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=5)
        if 'tun' in result.stdout or 'utun' in result.stdout:
            print("🔒 VPN detected - this may affect IP whitelisting")
        else:
            print("📡 No VPN detected")
    except:
        print("⚠️  Could not check VPN status")
    
    # Check network interface
    try:
        result = subprocess.run(['route', 'get', 'default'], capture_output=True, text=True, timeout=5)
        if 'interface:' in result.stdout:
            interface = [line for line in result.stdout.split('\n') if 'interface:' in line][0]
            print(f"🌐 Network interface: {interface.strip()}")
    except:
        print("⚠️  Could not determine network interface")

def main():
    """Run IP and connectivity diagnostics"""
    print("🔍 MONGODB ATLAS IP WHITELIST DIAGNOSTIC")
    print("=" * 60)
    print("Checking if the new internet connection is causing MongoDB SSL issues...")
    print()
    
    # Get IP addresses
    print("📍 IP ADDRESS INFORMATION")
    print("=" * 40)
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    # Check network configuration
    check_network_info()
    
    # Test MongoDB connectivity
    print("\n🌐 MONGODB ATLAS CONNECTIVITY TEST")
    print("=" * 50)
    connectivity_ok = test_mongodb_connectivity()
    
    # Analysis and recommendations
    print("\n🎯 DIAGNOSIS AND RECOMMENDATIONS")
    print("=" * 60)
    
    if not connectivity_ok:
        print("❌ LIKELY CAUSE: IP WHITELIST ISSUE")
        print()
        print("🔧 IMMEDIATE SOLUTIONS:")
        print("1. Add your current IP to MongoDB Atlas whitelist:")
        if public_ip:
            print(f"   - Add IP: {public_ip}")
        print("   - Or use 0.0.0.0/0 for temporary access (less secure)")
        print()
        print("2. Check MongoDB Atlas Network Access settings:")
        print("   - Go to MongoDB Atlas Dashboard")
        print("   - Navigate to Network Access")
        print("   - Add current IP address")
        print()
        print("3. Alternative: Use MongoDB Atlas from anywhere:")
        print("   - Add 0.0.0.0/0 to whitelist (allows all IPs)")
        print("   - This is less secure but works from any connection")
    else:
        print("✅ Network connectivity is OK")
        print("The issue may be related to SSL configuration rather than IP whitelisting")
    
    print("\n💡 ADDITIONAL NOTES:")
    print("- MongoDB Atlas requires IP whitelisting for security")
    print("- Changing internet connections changes your public IP")
    print("- VPNs can also affect your apparent IP address")
    print("- Corporate networks may have additional restrictions")

if __name__ == "__main__":
    main()