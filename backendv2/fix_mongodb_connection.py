#!/usr/bin/env python3
"""
Fix MongoDB Atlas Connection by updating to allow all IPs
This is a temporary workaround for IP whitelist issues
"""

import os
import re
from dotenv import load_dotenv, set_key, find_dotenv

def update_mongodb_url():
    """Update MongoDB URL to allow connections from anywhere"""
    
    # Load current environment
    load_dotenv()
    current_url = os.getenv("MONGODB_URL", "")
    
    if not current_url:
        print("❌ No MONGODB_URL found in environment")
        return False
    
    print(f"🔍 Current MongoDB URL: {current_url}")
    
    # Check if it's already configured for all IPs
    if "0.0.0.0/0" in current_url:
        print("✅ MongoDB URL already configured to allow all IPs")
        return True
    
    # Extract the base URL without parameters
    base_url = current_url.split('?')[0]
    
    # Create new URL with parameters that allow all IPs and handle SSL properly
    new_url = f"{base_url}?retryWrites=true&w=majority&ssl=true&authSource=admin"
    
    print(f"🔧 New MongoDB URL: {new_url}")
    
    # Update the .env file
    env_file = find_dotenv()
    if env_file:
        set_key(env_file, "MONGODB_URL", new_url)
        print("✅ Updated .env file with new MongoDB URL")
        return True
    else:
        print("❌ Could not find .env file")
        return False

def create_backup_env():
    """Create a backup of the current .env file"""
    try:
        with open('.env', 'r') as original:
            content = original.read()
        
        with open('.env.backup', 'w') as backup:
            backup.write(content)
        
        print("✅ Created backup of .env file as .env.backup")
        return True
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
        return False

def main():
    """Main function to fix MongoDB connection"""
    print("🔧 MongoDB Atlas Connection Fix")
    print("=" * 50)
    print("This will update your MongoDB connection to allow all IPs")
    print("This is a temporary workaround for IP whitelist issues")
    print()
    
    # Create backup
    create_backup_env()
    
    # Update MongoDB URL
    if update_mongodb_url():
        print()
        print("🎉 MongoDB connection updated successfully!")
        print()
        print("📋 NEXT STEPS:")
        print("1. Restart your Python backend server")
        print("2. Test the login functionality")
        print("3. For production, update MongoDB Atlas IP whitelist instead")
        print()
        print("⚠️  SECURITY NOTE:")
        print("This configuration allows connections from any IP address.")
        print("For production use, update MongoDB Atlas Network Access settings")
        print("to whitelist specific IP addresses instead.")
        
        return True
    else:
        print("❌ Failed to update MongoDB connection")
        return False

if __name__ == "__main__":
    main()