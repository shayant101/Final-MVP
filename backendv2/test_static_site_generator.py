#!/usr/bin/env python3
"""
Test Script for Static Site Generator (Phase 2)
Tests the complete SSG system including HTML, CSS, JS generation and publishing integration
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.static_site_generator import StaticSiteGenerator

def create_test_website_data():
    """Create comprehensive test website data"""
    return {
        "website_id": "test_restaurant_001",
        "restaurant_id": "rest_001",
        "website_name": "Bella Vista Restaurant",
        "subdomain": "bella-vista",
        "live_url": "https://bella-vista.ourplatform.com",
        "status": "ready",
        "design_system": {
            "color_palette": {
                "primary": "#8B4513",
                "secondary": "#D2691E",
                "accent": "#FF6347",
                "neutral": "#F5F5DC",
                "text_primary": "#2F4F4F",
                "text_secondary": "#696969"
            },
            "typography": {
                "headings_font": "Playfair Display, serif",
                "body_font": "Open Sans, sans-serif",
                "accent_font": "Dancing Script, cursive"
            },
            "border_radius": "12px",
            "spacing_scale": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem"
            }
        },
        "seo_settings": {
            "site_title": "Bella Vista Restaurant - Authentic Italian Cuisine",
            "site_description": "Experience the finest Italian dining at Bella Vista Restaurant. Fresh ingredients, traditional recipes, and warm hospitality in the heart of the city.",
            "keywords": ["italian restaurant", "fine dining", "pasta", "pizza", "wine", "authentic cuisine"],
            "og_image": "https://bella-vista.ourplatform.com/images/hero/restaurant-hero.jpg",
            "twitter_card": "summary_large_image",
            "analytics_code": "GA_MEASUREMENT_ID",
            "robots_txt": "User-agent: *\nAllow: /\nSitemap: https://bella-vista.ourplatform.com/sitemap.xml"
        },
        "hero_image": "https://bella-vista.ourplatform.com/images/hero/restaurant-hero.jpg",
        "menu_items": [
            {
                "name": "Margherita Pizza",
                "description": "Classic pizza with fresh mozzarella, tomatoes, and basil",
                "price": "18.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/margherita-pizza.jpg",
                "category": "Pizza"
            },
            {
                "name": "Spaghetti Carbonara",
                "description": "Traditional Roman pasta with eggs, cheese, pancetta, and black pepper",
                "price": "22.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/carbonara.jpg",
                "category": "Pasta"
            },
            {
                "name": "Osso Buco",
                "description": "Braised veal shanks with vegetables, white wine, and broth",
                "price": "34.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/osso-buco.jpg",
                "category": "Main Course"
            },
            {
                "name": "Tiramisu",
                "description": "Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
                "price": "9.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/tiramisu.jpg",
                "category": "Dessert"
            },
            {
                "name": "Caesar Salad",
                "description": "Crisp romaine lettuce with parmesan, croutons, and Caesar dressing",
                "price": "14.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/caesar-salad.jpg",
                "category": "Salad"
            },
            {
                "name": "Bruschetta",
                "description": "Grilled bread topped with fresh tomatoes, garlic, and basil",
                "price": "12.99",
                "image": "https://bella-vista.ourplatform.com/images/menu/bruschetta.jpg",
                "category": "Appetizer"
            }
        ],
        "pages": [
            {
                "page_id": "homepage",
                "page_name": "Home",
                "page_slug": "/",
                "page_title": "Bella Vista Restaurant - Authentic Italian Cuisine",
                "meta_description": "Experience the finest Italian dining at Bella Vista Restaurant. Fresh ingredients, traditional recipes, and warm hospitality.",
                "is_homepage": True,
                "published": True,
                "components": [],
                "sections": {
                    "hero": {
                        "title": "Welcome to Bella Vista",
                        "subtitle": "Authentic Italian Cuisine in the Heart of the City",
                        "background_image": "https://bella-vista.ourplatform.com/images/hero/restaurant-hero.jpg"
                    },
                    "about": {
                        "title": "Our Story",
                        "content": "For over 30 years, Bella Vista has been serving authentic Italian cuisine made with the finest ingredients imported directly from Italy."
                    }
                }
            }
        ],
        "integration_settings": {
            "google_analytics": "GA_MEASUREMENT_ID",
            "social_media_links": {
                "facebook": "https://facebook.com/bellavista",
                "instagram": "https://instagram.com/bellavista",
                "twitter": "https://twitter.com/bellavista"
            }
        },
        "performance_settings": {
            "image_optimization": True,
            "lazy_loading": True,
            "minify_css": True,
            "minify_js": True,
            "enable_caching": True,
            "compression_enabled": True
        }
    }

async def test_static_site_generation():
    """Test the complete static site generation process"""
    print("🧪 Testing Static Site Generator (Phase 2)")
    print("=" * 60)
    
    # Initialize the Static Site Generator
    ssg = StaticSiteGenerator(base_path="test_generated_sites")
    
    # Create test website data
    website_data = create_test_website_data()
    
    print(f"📊 Test Website Data:")
    print(f"   - Website: {website_data['website_name']}")
    print(f"   - Subdomain: {website_data['subdomain']}")
    print(f"   - Menu Items: {len(website_data['menu_items'])}")
    print(f"   - Pages: {len(website_data['pages'])}")
    print()
    
    # Test static site generation
    print("🔄 Generating static site...")
    start_time = datetime.now()
    
    try:
        result = await ssg.generate_static_site(website_data)
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Generation completed in {generation_time:.2f} seconds")
        print()
        
        if result['success']:
            print("✅ Static Site Generation: SUCCESS")
            print(f"📁 Site Directory: {result['site_directory']}")
            print(f"📄 Total Files Generated: {result['total_files']}")
            print()
            
            # Display generated files by category
            files_generated = result['files_generated']
            
            print("📋 Generated Files Summary:")
            for category, files in files_generated.items():
                print(f"   {category.upper()}: {len(files)} files")
                for file in files:
                    print(f"      - {file}")
            print()
            
            # Verify file structure
            site_path = Path(result['site_directory'])
            print("🔍 Verifying File Structure:")
            
            # Check for required files
            required_files = [
                'index.html',
                'css/main.css',
                'css/responsive.css',
                'js/main.js',
                'js/performance.js',
                'robots.txt',
                'sitemap.xml',
                'manifest.json',
                'sw.js'
            ]
            
            for file_path in required_files:
                full_path = site_path / file_path
                if full_path.exists():
                    file_size = full_path.stat().st_size
                    print(f"   ✅ {file_path} ({file_size} bytes)")
                else:
                    print(f"   ❌ {file_path} (missing)")
            
            print()
            
            # Check directory structure
            print("📂 Directory Structure:")
            expected_dirs = ['css', 'js', 'images', 'images/hero', 'images/menu', 'images/gallery', 'images/icons']
            
            for dir_path in expected_dirs:
                full_dir = site_path / dir_path
                if full_dir.exists():
                    file_count = len(list(full_dir.iterdir()))
                    print(f"   ✅ {dir_path}/ ({file_count} files)")
                else:
                    print(f"   ❌ {dir_path}/ (missing)")
            
            print()
            
            # Test HTML content quality
            print("🔍 Testing HTML Content Quality:")
            index_file = site_path / 'index.html'
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Check for essential HTML elements
                html_checks = [
                    ('DOCTYPE declaration', '<!DOCTYPE html>' in html_content),
                    ('Meta viewport', 'name="viewport"' in html_content),
                    ('Meta description', 'name="description"' in html_content),
                    ('Open Graph tags', 'property="og:' in html_content),
                    ('Twitter Card tags', 'property="twitter:' in html_content),
                    ('Structured data', 'application/ld+json' in html_content),
                    ('Restaurant name', website_data['website_name'] in html_content),
                    ('Menu items', any(item['name'] in html_content for item in website_data['menu_items'])),
                    ('Accessibility features', 'aria-label' in html_content),
                    ('Semantic HTML', '<main' in html_content and '<section' in html_content)
                ]
                
                for check_name, passed in html_checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
            
            print()
            
            # Test CSS content
            print("🎨 Testing CSS Content:")
            main_css_file = site_path / 'css' / 'main.css'
            if main_css_file.exists():
                with open(main_css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                css_checks = [
                    ('CSS Variables', ':root {' in css_content),
                    ('Custom colors', website_data['design_system']['color_palette']['primary'] in css_content),
                    ('Typography', website_data['design_system']['typography']['headings_font'] in css_content),
                    ('Responsive design', '@media' in css_content),
                    ('Flexbox/Grid', 'display: flex' in css_content or 'display: grid' in css_content),
                    ('Accessibility focus', ':focus' in css_content)
                ]
                
                for check_name, passed in css_checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
            
            print()
            
            # Test JavaScript functionality
            print("⚡ Testing JavaScript Content:")
            main_js_file = site_path / 'js' / 'main.js'
            if main_js_file.exists():
                with open(main_js_file, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                
                js_checks = [
                    ('DOM Content Loaded', 'DOMContentLoaded' in js_content),
                    ('Navigation functionality', 'initializeNavigation' in js_content),
                    ('Smooth scrolling', 'smooth' in js_content),
                    ('Form handling', 'handleFormSubmit' in js_content),
                    ('Lazy loading', 'IntersectionObserver' in js_content),
                    ('Performance monitoring', 'performance' in js_content)
                ]
                
                for check_name, passed in js_checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
            
            print()
            
            # Test SEO files
            print("🔍 Testing SEO Files:")
            
            # Test robots.txt
            robots_file = site_path / 'robots.txt'
            if robots_file.exists():
                with open(robots_file, 'r', encoding='utf-8') as f:
                    robots_content = f.read()
                print(f"   ✅ robots.txt contains sitemap reference: {'Sitemap:' in robots_content}")
            
            # Test sitemap.xml
            sitemap_file = site_path / 'sitemap.xml'
            if sitemap_file.exists():
                with open(sitemap_file, 'r', encoding='utf-8') as f:
                    sitemap_content = f.read()
                print(f"   ✅ sitemap.xml is valid XML: {'<?xml' in sitemap_content}")
                print(f"   ✅ sitemap.xml contains URLs: {'<url>' in sitemap_content}")
            
            print()
            
            # Test PWA files
            print("📱 Testing PWA Files:")
            
            # Test manifest.json
            manifest_file = site_path / 'manifest.json'
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                pwa_checks = [
                    ('Has name', 'name' in manifest_data),
                    ('Has start_url', 'start_url' in manifest_data),
                    ('Has display mode', 'display' in manifest_data),
                    ('Has icons', 'icons' in manifest_data and len(manifest_data['icons']) > 0),
                    ('Has theme color', 'theme_color' in manifest_data)
                ]
                
                for check_name, passed in pwa_checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
            
            # Test service worker
            sw_file = site_path / 'sw.js'
            if sw_file.exists():
                with open(sw_file, 'r', encoding='utf-8') as f:
                    sw_content = f.read()
                print(f"   ✅ Service worker has cache functionality: {'caches.open' in sw_content}")
            
            print()
            print("🎉 Static Site Generation Test Completed Successfully!")
            print(f"📊 Performance Summary:")
            print(f"   - Generation Time: {generation_time:.2f} seconds")
            print(f"   - Files Generated: {result['total_files']}")
            print(f"   - Site Size: {get_directory_size(site_path):.2f} MB")
            
        else:
            print("❌ Static Site Generation: FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Static Site Generation: EXCEPTION")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def get_directory_size(path: Path) -> float:
    """Calculate directory size in MB"""
    total_size = 0
    for file_path in path.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size / (1024 * 1024)  # Convert to MB

async def main():
    """Main test function"""
    print("🚀 Starting Static Site Generator Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    await test_static_site_generation()
    
    print()
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())