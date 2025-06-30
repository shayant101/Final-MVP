#!/usr/bin/env python3
"""
MongoDB SSL Connection Diagnostic Script
Tests various connection configurations to identify SSL issues
"""

import os
import sys
import asyncio
import ssl
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from dotenv import load_dotenv
import certifi

# Load environment variables
load_dotenv()

# Original connection string
ORIGINAL_MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "momentum_growth")

print("🔍 MongoDB SSL Connection Diagnostic Tool")
print("=" * 50)
print(f"Database: {DATABASE_NAME}")
print(f"Original URL: {ORIGINAL_MONGODB_URL}")
print()

async def test_connection_config(url, description, timeout=10):
    """Test a specific MongoDB connection configuration"""
    print(f"🧪 Testing: {description}")
    print(f"   URL: {url}")
    
    try:
        # Test with AsyncIOMotorClient (used in the app)
        client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=timeout*1000)
        
        # Try to ping the database
        await client.admin.command('ping')
        
        # Try to access the database
        db = client[DATABASE_NAME]
        collections = await db.list_collection_names()
        
        print(f"   ✅ SUCCESS - Connected successfully")
        print(f"   📊 Collections found: {len(collections)}")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"   ❌ TIMEOUT ERROR: {str(e)}")
        return False
    except ConnectionFailure as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {str(e)}")
        return False
    finally:
        print()

def test_sync_connection(url, description, timeout=10):
    """Test synchronous MongoDB connection"""
    print(f"🧪 Testing (Sync): {description}")
    print(f"   URL: {url}")
    
    try:
        # Test with regular MongoClient
        client = MongoClient(url, serverSelectionTimeoutMS=timeout*1000)
        
        # Try to ping the database
        client.admin.command('ping')
        
        # Try to access the database
        db = client[DATABASE_NAME]
        collections = db.list_collection_names()
        
        print(f"   ✅ SUCCESS - Connected successfully")
        print(f"   📊 Collections found: {len(collections)}")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"   ❌ TIMEOUT ERROR: {str(e)}")
        return False
    except ConnectionFailure as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {str(e)}")
        return False
    finally:
        print()

async def main():
    """Run comprehensive MongoDB connection tests"""
    
    # Extract base connection info
    base_url = ORIGINAL_MONGODB_URL.split('?')[0]  # Remove existing parameters
    
    # Test configurations
    test_configs = [
        {
            "url": ORIGINAL_MONGODB_URL,
            "description": "Original Configuration"
        },
        {
            "url": f"{base_url}?ssl=true&ssl_cert_reqs=CERT_REQUIRED&ssl_ca_certs={certifi.where()}&retryWrites=true&w=majority",
            "description": "Explicit SSL with Certificate Validation"
        },
        {
            "url": f"{base_url}?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority",
            "description": "SSL without Certificate Validation"
        },
        {
            "url": f"{base_url}?tls=true&tlsCAFile={certifi.where()}&retryWrites=true&w=majority",
            "description": "TLS with CA File"
        },
        {
            "url": f"{base_url}?tls=true&tlsAllowInvalidCertificates=true&retryWrites=true&w=majority",
            "description": "TLS with Invalid Certificates Allowed"
        },
        {
            "url": f"{base_url}?ssl=true&authSource=admin&retryWrites=true&w=majority",
            "description": "SSL with Admin Auth Source"
        }
    ]
    
    print("🚀 Starting Async Connection Tests")
    print("-" * 40)
    
    successful_configs = []
    
    for config in test_configs:
        success = await test_connection_config(config["url"], config["description"])
        if success:
            successful_configs.append(config)
    
    print("🔄 Starting Sync Connection Tests")
    print("-" * 40)
    
    for config in test_configs:
        success = test_sync_connection(config["url"], config["description"])
        if success and config not in successful_configs:
            successful_configs.append(config)
    
    # Summary
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if successful_configs:
        print("✅ SUCCESSFUL CONFIGURATIONS:")
        for config in successful_configs:
            print(f"   • {config['description']}")
            print(f"     URL: {config['url']}")
            print()
        
        print("🔧 RECOMMENDED FIX:")
        best_config = successful_configs[0]
        print(f"Update your .env file with this connection string:")
        print(f"MONGODB_URL={best_config['url']}")
        
    else:
        print("❌ NO SUCCESSFUL CONFIGURATIONS FOUND")
        print()
        print("🔍 ADDITIONAL DIAGNOSTICS NEEDED:")
        print("1. Check MongoDB Atlas IP Whitelist")
        print("2. Verify database user permissions")
        print("3. Check network connectivity")
        print("4. Verify MongoDB Atlas cluster status")
    
    # System information
    print()
    print("🖥️  SYSTEM INFORMATION:")
    print(f"   Python Version: {sys.version}")
    print(f"   SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"   Certifi CA Bundle: {certifi.where()}")
    
    # PyMongo version
    try:
        import pymongo
        print(f"   PyMongo Version: {pymongo.version}")
    except:
        print("   PyMongo Version: Unable to determine")

if __name__ == "__main__":
    asyncio.run(main())