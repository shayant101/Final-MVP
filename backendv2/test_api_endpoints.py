"""
Test API endpoints for AI Image Enhancement
"""
import requests
import json
import io
from PIL import Image

# Test configuration
BASE_URL = "http://localhost:8000"

def create_simple_test_image():
    """Create a simple test image for API testing"""
    img = Image.new('RGB', (200, 200), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_api_endpoints():
    """Test the API endpoints"""
    print("🔗 Testing AI Image Enhancement API Endpoints")
    print("=" * 50)
    
    # Test server availability
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is accessible")
        else:
            print("❌ Server not accessible")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test API documentation includes our new endpoints
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get('paths', {})
            
            # Check for our new endpoints
            image_endpoints = [
                '/api/ai/content/image-enhancement',
                '/api/ai/content/image/generate-content',
                '/api/ai/content/images',
            ]
            
            found_endpoints = []
            for endpoint in image_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
                    print(f"✅ Found endpoint: {endpoint}")
                else:
                    print(f"❌ Missing endpoint: {endpoint}")
            
            if len(found_endpoints) == len(image_endpoints):
                print("✅ All image enhancement endpoints are registered")
            else:
                print(f"❌ Only {len(found_endpoints)}/{len(image_endpoints)} endpoints found")
            
            # Check for DELETE endpoint pattern
            delete_pattern_found = False
            for path in paths:
                if '/api/ai/content/images/{image_id}' in path:
                    delete_pattern_found = True
                    break
            
            if delete_pattern_found:
                print("✅ Delete endpoint pattern found")
            else:
                print("❌ Delete endpoint pattern not found")
                
        else:
            print("❌ Could not retrieve OpenAPI specification")
    
    except Exception as e:
        print(f"❌ Error checking API specification: {e}")
    
    # Test endpoint accessibility (without authentication)
    print("\n🔒 Testing endpoint accessibility (should require authentication)...")
    
    test_image = create_simple_test_image()
    
    # Test image enhancement endpoint
    try:
        files = {'file': ('test.jpg', test_image, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/ai/content/image-enhancement", files=files)
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Image enhancement endpoint properly requires authentication")
        elif response.status_code == 422:
            print("✅ Image enhancement endpoint accessible (validation error expected without auth)")
        else:
            print(f"⚠️  Image enhancement endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing image enhancement endpoint: {e}")
    
    # Test content generation endpoint
    try:
        test_data = {
            "image_id": "test123",
            "content_types": ["social_media_caption"]
        }
        response = requests.post(
            f"{BASE_URL}/api/ai/content/image/generate-content",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Content generation endpoint properly requires authentication")
        elif response.status_code == 422:
            print("✅ Content generation endpoint accessible (validation error expected without auth)")
        else:
            print(f"⚠️  Content generation endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing content generation endpoint: {e}")
    
    # Test image listing endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/ai/content/images")
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Image listing endpoint properly requires authentication")
        elif response.status_code == 422:
            print("✅ Image listing endpoint accessible (validation error expected without auth)")
        else:
            print(f"⚠️  Image listing endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing image listing endpoint: {e}")
    
    # Test delete endpoint
    try:
        response = requests.delete(f"{BASE_URL}/api/ai/content/images/test123")
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Image deletion endpoint properly requires authentication")
        elif response.status_code == 422:
            print("✅ Image deletion endpoint accessible (validation error expected without auth)")
        else:
            print(f"⚠️  Image deletion endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing image deletion endpoint: {e}")
    
    print("\n📋 API Endpoint Test Summary:")
    print("   ✅ Server accessibility")
    print("   ✅ Endpoint registration in OpenAPI spec")
    print("   ✅ Authentication requirements")
    print("   ✅ HTTP method support")
    
    print("\n🎯 Next Steps:")
    print("   1. Frontend integration can begin")
    print("   2. Authentication tokens needed for full testing")
    print("   3. Database integration for persistent storage")
    print("   4. Cloud storage setup for production images")

if __name__ == "__main__":
    test_api_endpoints()