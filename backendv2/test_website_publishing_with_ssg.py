#!/usr/bin/env python3
"""
Test Script for Website Publishing with Static Site Generation Integration
Tests the complete publishing workflow including SSG integration
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.website_publishing_service import WebsitePublishingService
from app.models_website_builder import WebsitePublishRequest
from motor.motor_asyncio import AsyncIOMotorClient

async def create_test_database():
    """Create a test database connection"""
    # Use a test database
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_momentum_ssg
    return db

async def create_test_website_in_db(db):
    """Create a test website in the database"""
    website_data = {
        "website_id": "test_ssg_website_001",
        "restaurant_id": "test_restaurant_001",
        "website_name": "Test SSG Restaurant",
        "status": "ready",
        "design_system": {
            "color_palette": {
                "primary": "#2c3e50",
                "secondary": "#3498db",
                "accent": "#e74c3c",
                "neutral": "#ecf0f1",
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d"
            },
            "typography": {
                "headings_font": "Georgia, serif",
                "body_font": "Arial, sans-serif"
            },
            "border_radius": "8px"
        },
        "seo_settings": {
            "site_title": "Test SSG Restaurant - Great Food",
            "site_description": "A test restaurant for SSG functionality testing",
            "keywords": ["test", "restaurant", "food"],
            "robots_txt": "User-agent: *\nAllow: /"
        },
        "hero_image": "https://example.com/hero.jpg",
        "menu_items": [
            {
                "name": "Test Burger",
                "description": "A delicious test burger",
                "price": "12.99",
                "image": "https://example.com/burger.jpg"
            },
            {
                "name": "Test Pizza",
                "description": "A tasty test pizza",
                "price": "15.99",
                "image": "https://example.com/pizza.jpg"
            }
        ],
        "pages": [
            {
                "page_id": "homepage",
                "page_name": "Home",
                "page_slug": "/",
                "page_title": "Test SSG Restaurant - Great Food",
                "meta_description": "A test restaurant for SSG functionality testing",
                "is_homepage": True,
                "published": True,
                "components": [],
                "sections": {}
            }
        ],
        "integration_settings": {
            "social_media_links": {
                "facebook": "https://facebook.com/testrestaurant"
            }
        },
        "performance_settings": {
            "image_optimization": True,
            "lazy_loading": True,
            "minify_css": True,
            "minify_js": True
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert the test website
    await db.websites.insert_one(website_data)
    return website_data

async def test_publishing_with_ssg():
    """Test the complete publishing workflow with SSG integration"""
    print("🧪 Testing Website Publishing with Static Site Generation")
    print("=" * 70)
    
    try:
        # Create test database connection
        db = await create_test_database()
        
        # Clean up any existing test data
        await db.websites.delete_many({"website_id": "test_ssg_website_001"})
        await db.website_deployments.delete_many({"website_id": "test_ssg_website_001"})
        
        # Create test website in database
        print("📝 Creating test website in database...")
        website_data = await create_test_website_in_db(db)
        print(f"   ✅ Created website: {website_data['website_name']}")
        print()
        
        # Initialize the publishing service
        publishing_service = WebsitePublishingService(db)
        
        # Create publish request
        publish_request = WebsitePublishRequest(
            website_id="test_ssg_website_001",
            force_republish=False
        )
        
        print("🚀 Testing website publishing with SSG...")
        start_time = datetime.now()
        
        # Test the publishing process
        result = await publishing_service.publish_website(
            publish_request, 
            "test_restaurant_001"
        )
        
        end_time = datetime.now()
        publish_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Publishing completed in {publish_time:.2f} seconds")
        print()
        
        if result.success:
            print("✅ Website Publishing: SUCCESS")
            print(f"🌐 Live URL: {result.live_url}")
            print(f"🆔 Deployment ID: {result.deployment_id}")
            print(f"⏱️  Estimated Completion: {result.estimated_completion_time}s")
            print()
            
            # Verify website was updated in database
            print("🔍 Verifying database updates...")
            updated_website = await db.websites.find_one({"website_id": "test_ssg_website_001"})
            
            db_checks = [
                ("Status updated to published", updated_website.get("status") == "published"),
                ("Live URL set", updated_website.get("live_url") is not None),
                ("Subdomain generated", updated_website.get("subdomain") is not None),
                ("Published content snapshot", updated_website.get("published_content") is not None),
                ("Last published timestamp", updated_website.get("last_published_at") is not None),
                ("Unpublished changes flag reset", updated_website.get("has_unpublished_changes") == False)
            ]
            
            for check_name, passed in db_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}")
            
            print()
            
            # Verify deployment record was created
            print("📋 Verifying deployment record...")
            deployment = await db.website_deployments.find_one({"deployment_id": result.deployment_id})
            
            if deployment:
                print("   ✅ Deployment record created")
                print(f"   📊 Platform: {deployment.get('platform')}")
                print(f"   🌐 Deployment URL: {deployment.get('deployment_url')}")
                print(f"   📈 Status: {deployment.get('deployment_status')}")
                print(f"   ⏱️  Deployment Time: {deployment.get('deployment_time')}s")
                print(f"   📝 Build Logs: {len(deployment.get('build_logs', []))} entries")
                
                # Check if static site info is included
                static_site_info = deployment.get('static_site_info', {})
                if static_site_info:
                    print("   ✅ Static site generation info included")
                    if static_site_info.get('success'):
                        print(f"   📄 Files Generated: {static_site_info.get('total_files', 0)}")
                        print(f"   📁 Site Directory: {static_site_info.get('site_directory', 'N/A')}")
                    else:
                        print(f"   ❌ Static site generation failed: {static_site_info.get('error')}")
                else:
                    print("   ⚠️  No static site generation info found")
                
                # Display build logs
                print("\n   📝 Build Logs:")
                for i, log_entry in enumerate(deployment.get('build_logs', [])[:10], 1):
                    print(f"      {i:2d}. {log_entry}")
                if len(deployment.get('build_logs', [])) > 10:
                    print(f"      ... and {len(deployment.get('build_logs', [])) - 10} more entries")
            else:
                print("   ❌ Deployment record not found")
            
            print()
            
            # Test publish status endpoint
            print("📊 Testing publish status endpoint...")
            status_response = await publishing_service.get_publish_status(
                "test_ssg_website_001", 
                "test_restaurant_001"
            )
            
            print(f"   ✅ Status: {status_response.status}")
            print(f"   🌐 Live URL: {status_response.live_url}")
            print(f"   📅 Last Published: {status_response.last_published_at}")
            print(f"   🔄 Has Unpublished Changes: {status_response.has_unpublished_changes}")
            print(f"   🚀 Deployment Status: {status_response.deployment_status}")
            
            print()
            
            # Verify static files were actually generated
            print("📁 Verifying static files generation...")
            site_directory = static_site_info.get('site_directory')
            if site_directory and Path(site_directory).exists():
                site_path = Path(site_directory)
                print(f"   ✅ Static site directory exists: {site_directory}")
                
                # Check for key files
                key_files = ['index.html', 'css/main.css', 'js/main.js', 'robots.txt', 'sitemap.xml']
                for file_path in key_files:
                    full_path = site_path / file_path
                    if full_path.exists():
                        file_size = full_path.stat().st_size
                        print(f"   ✅ {file_path} ({file_size} bytes)")
                    else:
                        print(f"   ❌ {file_path} (missing)")
                
                # Calculate total site size
                total_size = sum(f.stat().st_size for f in site_path.rglob('*') if f.is_file())
                print(f"   📊 Total Site Size: {total_size / 1024:.1f} KB")
            else:
                print("   ❌ Static site directory not found or doesn't exist")
            
            print()
            print("🎉 Website Publishing with SSG Test Completed Successfully!")
            print(f"📊 Performance Summary:")
            print(f"   - Total Publishing Time: {publish_time:.2f} seconds")
            print(f"   - Static Files Generated: {static_site_info.get('total_files', 0)}")
            print(f"   - Live URL: {result.live_url}")
            
        else:
            print("❌ Website Publishing: FAILED")
            print(f"Error: {result.message}")
            if result.error_details:
                print(f"Details: {result.error_details}")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        await db.websites.delete_many({"website_id": "test_ssg_website_001"})
        await db.website_deployments.delete_many({"website_id": "test_ssg_website_001"})
        print("   ✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Publishing Test: EXCEPTION")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 Starting Website Publishing with SSG Integration Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    await test_publishing_with_ssg()
    
    print()
    print("✅ All publishing integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main())