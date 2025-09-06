import requests
import os
from PIL import Image

# --- Test Configuration ---
BASE_URL = "http://localhost:8000"
UPLOAD_URL = f"{BASE_URL}/api/website-builder/upload-image-v2"
IMAGE_DIR = "backendv2/uploads/images/"
TEST_IMAGE_NAME = "test_upload_v2.png"
TEST_IMAGE_PATH = os.path.join(IMAGE_DIR, TEST_IMAGE_NAME)

def create_test_image():
    """Creates a simple dummy image for testing if one doesn't exist."""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    if not os.path.exists(TEST_IMAGE_PATH):
        try:
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(TEST_IMAGE_PATH)
            print(f"✅ Created test image: {TEST_IMAGE_PATH}")
        except Exception as e:
            print(f"❌ Failed to create test image: {e}")
            exit(1)

def test_image_upload():
    """Tests the entire image upload and retrieval process."""
    print("🚀 Starting V2 Image Upload Test...")

    # 1. Create a test image
    create_test_image()

    # 2. Prepare the file for upload
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_NAME, f, 'image/png')}
            payload = {'image_type': 'test'}
            
            # 3. Send the upload request
            print(f"📤 Uploading {TEST_IMAGE_NAME} to {UPLOAD_URL}...")
            response = requests.post(UPLOAD_URL, files=files, data=payload)
            
            # 4. Validate the upload response
            if response.status_code == 200:
                print("✅ Upload successful!")
                upload_data = response.json()
                print(f"   - Response: {upload_data}")
                
                filename = upload_data.get("filename")
                image_url = upload_data.get("image_url")

                if not filename or not image_url:
                    print("❌ Error: Filename or image_url missing in response.")
                    return

                # 5. Test the serving endpoint
                print(f"📥 Testing image serving endpoint: {BASE_URL}{image_url}")
                image_response = requests.get(f"{BASE_URL}{image_url}")

                if image_response.status_code == 200:
                    print("✅ Image served successfully!")
                    # Check if content is image-like
                    content_type = image_response.headers.get('content-type', '')
                    if 'image' in content_type:
                        print(f"   - Content-Type: {content_type} (Correct)")
                        print("🎉 Test Passed: New image upload system is working!")
                    else:
                        print(f"❌ Test Failed: Served content is not an image (Content-Type: {content_type})")
                else:
                    print(f"❌ Test Failed: Failed to retrieve image. Status: {image_response.status_code}")
                    print(f"   - Response: {image_response.text}")

            else:
                print(f"❌ Test Failed: Upload failed. Status: {response.status_code}")
                print(f"   - Response: {response.text}")

    except FileNotFoundError:
        print(f"❌ Test Failed: Could not find test image at {TEST_IMAGE_PATH}")
    except requests.exceptions.ConnectionError:
        print("❌ Test Failed: Connection refused. Is the backend server running?")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_image_upload()