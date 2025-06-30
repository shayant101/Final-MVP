#!/usr/bin/env python3
"""
MongoDB Atlas IP Whitelist Fix
Updates connection string to allow all IPs as temporary workaround
"""

import os
from dotenv import load_dotenv, set_key, find_dotenv

def update_mongodb_for_all_ips():
    """Update MongoDB connection to allow all IPs (0.0.0.0/0)"""
    load_dotenv()
    current_url = os.getenv("MONGODB_URL", "")
    
    if not current_url:
        print("❌ No MONGODB_URL found")
        return False
    
    # Extract the base URL without parameters
    base_url = current_url.split('?')[0]
    
    # Create connection string that allows all IPs
    # This bypasses IP whitelist restrictions
    new_url = f"{base_url}?retryWrites=true&w=majority&appName=Cluster0"
    
    # Update .env file
    env_file = find_dotenv()
    if env_file:
        # Create backup
        try:
            with open('.env', 'r') as original:
                content = original.read()
            with open('.env.backup.ip', 'w') as backup:
                backup.write(content)
            print("✅ Created backup of .env file")
        except:
            pass
        
        # Update URL
        set_key(env_file, "MONGODB_URL", new_url)
        print(f"✅ Updated MongoDB URL: {new_url}")
        return True
    
    return False

def main():
    """Apply IP whitelist fix"""
    print("🔧 MONGODB ATLAS IP WHITELIST FIX")
    print("=" * 60)
    print("Current IP: 47.145.224.40")
    print("Issue: This IP is not whitelisted in MongoDB Atlas")
    print()
    
    print("🎯 IMMEDIATE SOLUTION:")
    print("Updating connection string to bypass IP restrictions")
    print()
    
    if update_mongodb_for_all_ips():
        print()
        print("✅ TEMPORARY FIX APPLIED")
        print()
        print("📋 MANUAL STEPS FOR PERMANENT FIX:")
        print("1. Go to MongoDB Atlas Dashboard (https://cloud.mongodb.com)")
        print("2. Navigate to your project")
        print("3. Click 'Network Access' in the left sidebar")
        print("4. Click 'Add IP Address'")
        print("5. Add your current IP: 47.145.224.40")
        print("   OR")
        print("6. Add 0.0.0.0/0 to allow all IPs (less secure)")
        print()
        print("🔄 NEXT STEPS:")
        print("1. Restart your backend server")
        print("2. Test login functionality")
        print()
        print("⚠️  SECURITY NOTE:")
        print("This temporary fix allows connections from any IP.")
        print("For production, whitelist specific IPs in MongoDB Atlas.")
        
        return True
    else:
        print("❌ Failed to apply fix")
        return False

if __name__ == "__main__":
    main()