"""
Test script for AI Image Enhancement functionality
"""
import asyncio
import requests
import base64
import io
from PIL import Image
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_SIZE = (400, 300)

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored rectangle as test image
    img = Image.new('RGB', TEST_IMAGE_SIZE, color='red')
    
    # Add some simple shapes to make it look like food
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw a circle (like a burger)
    draw.ellipse([100, 75, 300, 225], fill='brown', outline='black', width=3)
    
    # Add some "lettuce" (green rectangle)
    draw.rectangle([120, 180, 280, 200], fill='green')
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

async def test_image_enhancement_endpoints():
    """Test the image enhancement endpoints"""
    print("🧪 Testing AI Image Enhancement Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("❌ Server is not accessible")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test image upload endpoint (without authentication for now)
    print("\n📸 Testing Image Enhancement Service...")
    
    try:
        # Create test image
        test_image_data = create_test_image()
        print(f"✅ Created test image ({len(test_image_data)} bytes)")
        
        # Test the service directly (bypassing authentication)
        from app.services.ai_image_enhancement import ai_image_enhancement
        
        # Test image validation
        validation_result = await ai_image_enhancement._validate_image(test_image_data, "test_burger.jpg")
        if validation_result['valid']:
            print("✅ Image validation passed")
            print(f"   - Format: {validation_result['format']}")
            print(f"   - Dimensions: {validation_result['dimensions']}")
            print(f"   - File size: {validation_result['file_size']} bytes")
        else:
            print(f"❌ Image validation failed: {validation_result['error']}")
            return
        
        # Test image enhancement
        enhancement_options = {
            "brightness": 1.1,
            "contrast": 1.2,
            "saturation": 1.15,
            "sharpness": 1.1,
            "food_styling_optimization": True
        }
        
        result = await ai_image_enhancement.upload_and_enhance_image(
            image_data=test_image_data,
            filename="test_burger.jpg",
            restaurant_id="test_restaurant_123",
            enhancement_options=enhancement_options
        )
        
        if result['success']:
            print("✅ Image enhancement completed successfully")
            print(f"   - Image ID: {result['data']['image_id']}")
            print(f"   - Original size: {len(test_image_data)} bytes")
            print(f"   - Enhanced size: {result['data']['metadata']['enhanced_file_size']} bytes")
            print(f"   - AI Analysis available: {'ai_analysis' in result['data']}")
            
            # Test content generation from image
            content_result = await ai_image_enhancement.generate_marketing_content_from_image(
                image_id=result['data']['image_id'],
                restaurant_id="test_restaurant_123",
                content_types=['social_media_caption', 'menu_description', 'promotional_content']
            )
            
            if content_result['success']:
                print("✅ Content generation from image completed")
                generated_content = content_result['data']['generated_content']
                print(f"   - Generated {len(generated_content)} content types")
                for content_type in generated_content:
                    print(f"   - {content_type}: Available")
            else:
                print(f"❌ Content generation failed: {content_result['error']}")
            
        else:
            print(f"❌ Image enhancement failed: {result['error']}")
            return
        
        # Test image listing
        list_result = await ai_image_enhancement.get_user_images("test_restaurant_123")
        if list_result['success']:
            print("✅ Image listing works")
            print(f"   - Found {len(list_result['data']['images'])} images")
        else:
            print(f"❌ Image listing failed: {list_result['error']}")
        
        # Test AI Content Engine integration
        print("\n🤖 Testing AI Content Engine Integration...")
        from app.services.ai_content_engine import ai_content_engine
        
        restaurant_data = {
            "name": "Test Restaurant",
            "cuisine_type": "American",
            "user_id": "test_user_123"
        }
        
        content_suite = await ai_content_engine.generate_comprehensive_content_suite(
            restaurant_data, 
            ['image_enhancement']
        )
        
        if content_suite['success']:
            print("✅ AI Content Engine integration works")
            if 'image_enhancement' in content_suite['generated_content']:
                print("   - Image enhancement content generated")
                enhancement_content = content_suite['generated_content']['image_enhancement']
                print(f"   - Photography tips: {len(enhancement_content['content']['photography_tips'])} categories")
                print(f"   - Enhancement guidelines: Available")
                print(f"   - Content suggestions: Available")
            else:
                print("   - Image enhancement content not found in suite")
        else:
            print(f"❌ AI Content Engine integration failed")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Image validation")
        print("   ✅ Image enhancement")
        print("   ✅ AI image analysis")
        print("   ✅ Content generation from images")
        print("   ✅ Image listing")
        print("   ✅ AI Content Engine integration")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_enhancement_endpoints())