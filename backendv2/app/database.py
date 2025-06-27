import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "momentum_growth")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

# Database instance
db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.database = db.client[DATABASE_NAME]
    print(f"✅ Connected to MongoDB: {DATABASE_NAME}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("✅ Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database

# Collections
def get_users_collection():
    return db.database.users

def get_restaurants_collection():
    return db.database.restaurants

def get_campaigns_collection():
    return db.database.campaigns

def get_checklist_status_collection():
    return db.database.checklist_status

def get_checklist_categories_collection():
    return db.database.checklist_categories

def get_checklist_items_collection():
    return db.database.checklist_items

def get_restaurant_checklist_status_collection():
    return db.database.restaurant_checklist_status

def get_sessions_collection():
    return db.database.sessions