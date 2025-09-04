import requests
import os

# Define the base URL for the API
API_BASE_URL = "http://localhost:8000/api"
UPLOAD_URL = f"{API_BASE_URL}/website-builder/upload-image"

# This is a placeholder for a valid JWT token.
# You can obtain a valid token by logging in through the application.
# Replace "your_jwt_token_here" with a real token.
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg1ZjZlNjFmNWU5YjVhYjEwOGU5ZjkyIiwiZW1haWwiOiJyb21hdHJhdHRvcmlhQHlhaG9vLmNvbSIsInJvbGUiOiJyZXN0YXVyYW50IiwiZXhwIjoxNzU3MDk3MDM1fQ.NdMo9aHzU1i7-SuoiwITgcpjEp02p82sNah3FKTo2HE"

def create_dummy_image(filename="dummy_image.jpg"):
    """Creates a small dummy image file for testing."""
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(filename)
    return filename

def test_image_upload():
    """
    Tests the image upload functionality by sending a POST request
    with a dummy image to the specified upload endpoint.
    """
    image_filename = create_dummy_image()
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    with open(image_filename, "rb") as f:
        files = {"file": (image_filename, f, "image/jpeg")}
        
        try:
            response = requests.post(UPLOAD_URL, headers=headers, files=files)
            
            print(f"Status Code: {response.status_code}")
            
            if response.ok:
                print("✅ Image upload successful!")
                print("Response JSON:", response.json())
            else:
                print("❌ Image upload failed.")
                print("Response Text:", response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            
    # Clean up the dummy image file
    os.remove(image_filename)

if __name__ == "__main__":
    # Before running, make sure to replace "your_jwt_token_here" with a valid token.
    if JWT_TOKEN == "your_jwt_token_here":
        print("👉 Please replace 'your_jwt_token_here' with a valid JWT token in the script.")
    else:
        test_image_upload()