#!/usr/bin/env python3.9
"""
Create Admin User Script
Creates a default admin user for the Python backend
"""
import asyncio
from datetime import datetime
from app.database import connect_to_mongo, get_users_collection
from app.auth import get_password_hash
from app.models import UserRole

async def create_admin_user():
    """Create default admin user"""
    print("🔧 Creating admin user...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Get users collection
    users_collection = get_users_collection()
    
    # Check if admin already exists
    existing_admin = await users_collection.find_one({"email": "admin@momentum.com"})
    if existing_admin:
        print("✅ Admin user already exists")
        print(f"📧 Email: admin@momentum.com")
        print(f"🔑 Password: admin123")
        return
    
    # Create admin user
    admin_data = {
        "email": "admin@momentum.com",
        "password_hash": get_password_hash("admin123"),
        "role": UserRole.admin,
        "created_at": datetime.utcnow()
    }
    
    # Insert admin user
    result = await users_collection.insert_one(admin_data)
    admin_id = str(result.inserted_id)
    
    print("✅ Admin user created successfully!")
    print(f"📧 Email: admin@momentum.com")
    print(f"🔑 Password: admin123")
    print(f"🆔 User ID: {admin_id}")
    print("\n🎉 You can now login with these credentials!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())