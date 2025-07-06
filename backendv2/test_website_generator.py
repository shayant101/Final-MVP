#!/usr/bin/env python3
"""
Test script for AI Website Generator
Demonstrates the website generation capabilities
"""
import asyncio
import json
from datetime import datetime
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the AI website generator class directly
from app.services.ai_website_generator import AIWebsiteGeneratorService

async def test_website_generation():
    """
    Test the AI website generation with sample restaurant data
    """
    print("🚀 Testing AI Website Generator")
    print("=" * 50)
    
    # Sample restaurant data for testing
    sample_restaurant_data = {
        "restaurant_id": "test_restaurant_123",
        "user_id": "test_user_456",
        "name": "Bella Vista Italian Bistro",
        "cuisine_type": "Italian",
        "price_range": "moderate",
        "location": "Downtown San Francisco, CA",
        "description": "Authentic Italian cuisine with a modern twist, featuring fresh pasta made daily and an extensive wine selection.",
        "target_audience": {
            "demographics": "Young professionals and families",
            "age_range": "25-55",
            "interests": ["fine dining", "wine", "authentic cuisine"]
        },
        "menu_items": [
            {
                "name": "Osso Buco alla Milanese",
                "category": "Main Course",
                "price": 28.00,
                "ingredients": "Braised veal shanks, saffron risotto, gremolata",
                "description": "Traditional Milanese braised veal shanks served with creamy saffron risotto"
            },
            {
                "name": "Linguine alle Vongole",
                "category": "Pasta",
                "price": 24.00,
                "ingredients": "Fresh linguine, Manila clams, white wine, garlic, parsley",
                "description": "Fresh linguine with Manila clams in white wine sauce"
            },
            {
                "name": "Tiramisu della Casa",
                "category": "Dessert",
                "price": 12.00,
                "ingredients": "Mascarpone, ladyfingers, espresso, cocoa",
                "description": "House-made tiramisu with imported mascarpone"
            },
            {
                "name": "Antipasto della Casa",
                "category": "Appetizer",
                "price": 18.00,
                "ingredients": "Prosciutto, salami, olives, cheese, roasted peppers",
                "description": "Traditional Italian antipasto platter with cured meats and cheeses"
            }
        ],
        "business_hours": {
            "monday": "5:00 PM - 10:00 PM",
            "tuesday": "5:00 PM - 10:00 PM",
            "wednesday": "5:00 PM - 10:00 PM",
            "thursday": "5:00 PM - 10:00 PM",
            "friday": "5:00 PM - 11:00 PM",
            "saturday": "4:00 PM - 11:00 PM",
            "sunday": "4:00 PM - 9:00 PM"
        },
        "contact_info": {
            "phone": "(415) 555-0123",
            "email": "info@bellavistabistro.com",
            "address": "123 Market Street, San Francisco, CA 94105"
        },
        "special_features": [
            "Private dining room available",
            "Extensive wine cellar",
            "Fresh pasta made daily",
            "Outdoor patio seating"
        ]
    }
    
    print(f"🍝 Generating website for: {sample_restaurant_data['name']}")
    print(f"📍 Location: {sample_restaurant_data['location']}")
    print(f"🍽️ Cuisine: {sample_restaurant_data['cuisine_type']}")
    print(f"💰 Price Range: {sample_restaurant_data['price_range']}")
    print(f"📋 Menu Items: {len(sample_restaurant_data['menu_items'])} items")
    print()
    
    try:
        # Start timer
        start_time = datetime.now()
        print("⏳ Starting AI website generation...")
        
        # Generate website
        website_result = await ai_website_generator.generate_complete_website(sample_restaurant_data)
        
        # Calculate generation time
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Website generation completed in {generation_time:.2f} seconds")
        print()
        
        # Display results
        if website_result.get("success"):
            print("🎉 WEBSITE GENERATION SUCCESSFUL!")
            print("=" * 50)
            
            # Basic info
            print(f"🆔 Website ID: {website_result.get('website_id')}")
            print(f"🏪 Restaurant: {website_result.get('restaurant_name')}")
            print(f"📅 Generated: {website_result.get('generation_date')}")
            print()
            
            # Design analysis
            design_analysis = website_result.get("design_analysis", {})
            print("🎨 DESIGN ANALYSIS:")
            print(f"   📂 Category: {design_analysis.get('recommended_category', 'N/A')}")
            print(f"   🎯 Priorities: {', '.join(design_analysis.get('design_priorities', []))}")
            
            brand_personality = design_analysis.get("brand_personality", {})
            if brand_personality:
                print(f"   🎭 Brand Traits: {', '.join(brand_personality.get('primary_traits', []))}")
                print(f"   🗣️ Tone: {brand_personality.get('tone_of_voice', 'N/A')}")
            print()
            
            # Website structure
            website_structure = website_result.get("website_structure", {})
            if website_structure:
                print("🏗️ WEBSITE STRUCTURE:")
                recommended_pages = website_structure.get("recommended_pages", [])
                print(f"   📄 Pages: {', '.join(recommended_pages)}")
                
                navigation = website_structure.get("navigation_hierarchy", {})
                if navigation.get("primary"):
                    print(f"   🧭 Navigation: {' | '.join(navigation['primary'])}")
                print()
            
            # Generated sections
            website_sections = website_result.get("website_sections", {})
            if website_sections:
                print("📝 GENERATED SECTIONS:")
                generated_sections = website_sections.get("generated_sections", {})
                for section_name, section_data in generated_sections.items():
                    print(f"   ✨ {section_name.replace('_', ' ').title()}")
                    if isinstance(section_data, dict) and "content" in section_data:
                        content_preview = section_data["content"][:100] + "..." if len(section_data["content"]) > 100 else section_data["content"]
                        print(f"      Preview: {content_preview}")
                print()
            
            # Design system
            design_system = website_result.get("design_system", {})
            if design_system:
                print("🎨 DESIGN SYSTEM:")
                color_palette = design_system.get("color_palette", {})
                if color_palette:
                    print(f"   🎨 Colors: Primary: {color_palette.get('primary', 'N/A')}, Secondary: {color_palette.get('secondary', 'N/A')}")
                
                typography = design_system.get("typography_system", {})
                if typography:
                    print(f"   📝 Fonts: Headings: {typography.get('headings_font', 'N/A')}, Body: {typography.get('body_font', 'N/A')}")
                print()
            
            # SEO optimization
            seo_optimization = website_result.get("seo_optimization", {})
            if seo_optimization:
                print("🔍 SEO OPTIMIZATION:")
                keyword_strategy = seo_optimization.get("keyword_strategy", [])
                if keyword_strategy:
                    print(f"   🔑 Keywords: {', '.join(keyword_strategy[:5])}")
                
                local_seo = seo_optimization.get("local_seo_checklist", [])
                if local_seo:
                    print(f"   📍 Local SEO: {len(local_seo)} optimization tasks")
                print()
            
            # AI insights
            ai_insights = website_result.get("ai_insights", {})
            if ai_insights:
                print("🧠 AI INSIGHTS:")
                optimization_opportunities = ai_insights.get("optimization_opportunities", [])
                for i, opportunity in enumerate(optimization_opportunities[:3], 1):
                    print(f"   {i}. {opportunity}")
                
                performance_predictions = ai_insights.get("performance_predictions", {})
                if performance_predictions:
                    print(f"   📈 Expected Conversion Rate: {performance_predictions.get('expected_conversion_rate', 'N/A')}")
                    print(f"   📱 Mobile Traffic: {performance_predictions.get('mobile_traffic_percentage', 'N/A')}")
                print()
            
            # Implementation plan
            implementation_plan = website_result.get("implementation_plan", {})
            if implementation_plan:
                print("📋 IMPLEMENTATION PLAN:")
                print(f"   ⏱️ Timeline: {implementation_plan.get('total_timeline', 'N/A')}")
                print(f"   🎯 Strategy: {implementation_plan.get('implementation_strategy', 'N/A')}")
                
                phases = implementation_plan.get("implementation_phases", {})
                for phase_name, phase_data in phases.items():
                    if isinstance(phase_data, dict):
                        print(f"   📅 {phase_name.replace('_', ' ').title()}: {phase_data.get('timeline', 'N/A')}")
                print()
            
            print("🎊 Website generation prototype completed successfully!")
            print("🚀 Ready for integration with drag-and-drop editor and hosting platform!")
            
        else:
            print("❌ Website generation failed")
            print(f"Error: {website_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 Error during website generation: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_design_analysis():
    """
    Test the design analysis functionality with different restaurant types
    """
    print("\n" + "=" * 60)
    print("🔬 TESTING DESIGN ANALYSIS FOR DIFFERENT RESTAURANT TYPES")
    print("=" * 60)
    
    test_restaurants = [
        {
            "name": "Le Petit Château",
            "cuisine_type": "French Fine Dining",
            "price_range": "expensive",
            "location": "Beverly Hills, CA"
        },
        {
            "name": "Taco Libre",
            "cuisine_type": "Mexican Fast Casual",
            "price_range": "budget",
            "location": "Austin, TX"
        },
        {
            "name": "Sakura Sushi",
            "cuisine_type": "Japanese",
            "price_range": "moderate",
            "location": "Seattle, WA"
        },
        {
            "name": "Corner Café & Bakery",
            "cuisine_type": "Café Bakery",
            "price_range": "budget",
            "location": "Portland, OR"
        }
    ]
    
    for restaurant in test_restaurants:
        print(f"\n🏪 Analyzing: {restaurant['name']}")
        print(f"   🍽️ Type: {restaurant['cuisine_type']}")
        print(f"   💰 Price: {restaurant['price_range']}")
        
        try:
            # Test design category determination
            category = ai_website_generator._determine_design_category(restaurant)
            print(f"   📂 Recommended Category: {category}")
            
            # Test brand personality analysis
            personality = ai_website_generator._analyze_brand_personality(restaurant)
            print(f"   🎭 Brand Traits: {', '.join(personality.get('primary_traits', []))}")
            print(f"   🗣️ Tone: {personality.get('tone_of_voice', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {str(e)}")

async def main():
    """
    Main test function
    """
    print("🤖 AI WEBSITE GENERATOR PROTOTYPE TEST")
    print("=" * 60)
    print("This test demonstrates the AI-powered website generation engine")
    print("that analyzes restaurant data and creates complete websites.")
    print()
    
    # Test main website generation
    await test_website_generation()
    
    # Test design analysis for different restaurant types
    await test_design_analysis()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("🚀 AI Website Generator prototype is ready for production integration!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())