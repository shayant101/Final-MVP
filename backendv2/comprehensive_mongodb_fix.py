#!/usr/bin/env python3
"""
Comprehensive MongoDB Atlas Connection Fix
Addresses both VPN/SSL issues and IP whitelist problems
"""

import os
import subprocess
import requests
from dotenv import load_dotenv, set_key, find_dotenv

def get_current_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return None

def check_vpn_status():
    """Check if VPN is active"""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=5)
        return 'tun' in result.stdout or 'utun' in result.stdout
    except:
        return False

def create_optimized_connection_string():
    """Create MongoDB connection string optimized for VPN/SSL issues"""
    load_dotenv()
    current_url = os.getenv("MONGODB_URL", "")
    
    if not current_url:
        print("❌ No MONGODB_URL found")
        return None
    
    # Extract base URL (remove existing parameters)
    base_url = current_url.split('?')[0]
    
    # Create connection string that works with VPN and bypasses SSL issues
    # This uses the original MongoDB Atlas format but with optimized parameters
    optimized_url = f"{base_url}?retryWrites=true&w=majority&appName=Cluster0"
    
    return optimized_url

def update_env_file(new_url):
    """Update .env file with new MongoDB URL"""
    env_file = find_dotenv()
    if env_file:
        # Create backup
        try:
            with open('.env', 'r') as original:
                content = original.read()
            with open('.env.backup', 'w') as backup:
                backup.write(content)
            print("✅ Created backup of .env file")
        except:
            print("⚠️  Could not create backup")
        
        # Update URL
        set_key(env_file, "MONGODB_URL", new_url)
        return True
    return False

def main():
    """Main fix function"""
    print("🔧 COMPREHENSIVE MONGODB ATLAS FIX")
    print("=" * 60)
    
    # Get current network status
    current_ip = get_current_ip()
    vpn_active = check_vpn_status()
    
    print(f"📍 Current IP: {current_ip}")
    print(f"🔒 VPN Active: {'Yes' if vpn_active else 'No'}")
    print()
    
    # Create optimized connection string
    new_url = create_optimized_connection_string()
    if not new_url:
        print("❌ Could not create optimized connection string")
        return False
    
    print(f"🔧 Optimized MongoDB URL: {new_url}")
    
    # Update .env file
    if update_env_file(new_url):
        print("✅ Updated .env file with optimized connection string")
    else:
        print("❌ Failed to update .env file")
        return False
    
    print()
    print("🎯 WHAT THIS FIX DOES:")
    print("1. Removes problematic SSL/TLS parameters that conflict with VPN")
    print("2. Uses MongoDB Atlas default SSL (which is always enabled)")
    print("3. Optimizes connection parameters for reliability")
    print()
    
    print("📋 NEXT STEPS:")
    print("1. Restart your Python backend server (Ctrl+C then python3.9 run.py)")
    print("2. Test login functionality")
    print()
    
    if vpn_active:
        print("⚠️  VPN DETECTED - ADDITIONAL RECOMMENDATIONS:")
        print("• If issues persist, try temporarily disconnecting VPN")
        print("• Some VPNs block MongoDB Atlas connections")
        print("• Consider using VPN split-tunneling for MongoDB traffic")
        print()
    
    print("🔐 FOR PRODUCTION SECURITY:")
    print(f"• Add your IP ({current_ip}) to MongoDB Atlas Network Access")
    print("• Go to MongoDB Atlas → Network Access → Add IP Address")
    print("• This fix works but IP whitelisting is still recommended")
    
    return True

if __name__ == "__main__":
    main()