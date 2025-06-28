"""
Direct SMS Test - Send actual SMS using Twilio
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.twilio_service import TwilioSMSService

def test_direct_sms():
    """Test sending a direct SMS message"""
    print("📱 Testing Direct SMS Sending")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Twilio service
    twilio_service = TwilioSMSService()
    
    # Test phone number
    test_phone = "+19499102531"  # Adding +1 country code
    
    # Test message
    test_message = """🍕 Test SMS from Momentum Growth!

Hi! This is a test message from your restaurant marketing platform.

If you received this, the Twilio SMS integration is working perfectly!

Reply STOP to opt out."""
    
    print(f"📞 Sending SMS to: {test_phone}")
    print(f"💬 Message: {test_message}")
    print("\n🚀 Sending...")
    
    try:
        # Send the SMS
        result = twilio_service.send_sms(test_phone, test_message)
        
        if result['success']:
            print("✅ SMS sent successfully!")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
            print(f"   To: {result['to']}")
            print(f"   From: {result['from']}")
        else:
            print("❌ SMS sending failed!")
            print(f"   Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
    
    print(f"\n🎉 Direct SMS test completed!")

if __name__ == "__main__":
    test_direct_sms()