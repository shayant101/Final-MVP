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

# Direct collection exports for easier imports
users_collection = None
restaurants_collection = None
campaigns_collection = None
checklist_collection = None
checklist_categories_collection = None
checklist_items_collection = None
restaurant_checklist_status_collection = None
sessions_collection = None

async def initialize_collections():
    """Initialize collection references after database connection"""
    global users_collection, restaurants_collection, campaigns_collection
    global checklist_collection, checklist_categories_collection, checklist_items_collection
    global restaurant_checklist_status_collection, sessions_collection
    
    users_collection = db.database.users
    restaurants_collection = db.database.restaurants
    campaigns_collection = db.database.campaigns
    checklist_collection = db.database.checklist_status  # Using checklist_status for compatibility
    checklist_categories_collection = db.database.checklist_categories
    checklist_items_collection = db.database.checklist_items
    restaurant_checklist_status_collection = db.database.restaurant_checklist_status
    sessions_collection = db.database.sessions