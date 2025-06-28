"""
Test script to verify Twilio integration
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.twilio_service import twilio_service, validate_phone_number, format_phone_number

async def test_twilio_integration():
    """Test the Twilio integration"""
    print("🧪 Testing Twilio SMS Integration")
    print("=" * 50)
    
    # Test phone number validation and formatting
    print("\n📞 Testing phone number validation and formatting:")
    test_numbers = [
        "1234567890",
        "+1234567890", 
        "(123) 456-7890",
        "123-456-7890",
        "invalid",
        "+44 20 7946 0958"  # UK number
    ]
    
    for number in test_numbers:
        is_valid = validate_phone_number(number)
        formatted = format_phone_number(number)
        print(f"  {number:<20} -> Valid: {is_valid:<5} | Formatted: {formatted}")
    
    # Test SMS sending with mock data
    print("\n📱 Testing SMS campaign sending:")
    test_customers = [
        {"customer_name": "John Doe", "phone_number": "+1234567890"},
        {"customer_name": "Jane Smith", "phone_number": "+1987654321"},
        {"customer_name": "Bob Johnson", "phone_number": "invalid_number"}
    ]
    
    test_message = "Hi {customer_name}! We miss you at Test Restaurant! Get 20% off your next order with code TEST20"
    test_offer_code = "TEST20"
    
    print(f"  Sending to {len(test_customers)} customers...")
    print(f"  Message template: {test_message}")
    print(f"  Offer code: {test_offer_code}")
    
    try:
        result = await twilio_service.send_sms_campaign(test_customers, test_message, test_offer_code)
        
        print(f"\n✅ Campaign Results:")
        print(f"  Campaign ID: {result['campaign']['id']}")
        print(f"  Total customers: {result['delivery']['total_customers']}")
        print(f"  Messages sent: {result['delivery']['sent']}")
        print(f"  Messages failed: {result['delivery']['failed']}")
        print(f"  Messages pending: {result['delivery']['pending']}")
        print(f"  Total cost: ${result['costs']['total_cost']}")
        
        print(f"\n📋 Individual Results:")
        for detail in result['details']:
            status_emoji = "✅" if detail['status'] == 'sent' else "❌" if detail['status'] == 'failed' else "⏳"
            print(f"  {status_emoji} {detail['customer_name']:<15} ({detail['phone_number']:<15}) - {detail['status']}")
            if detail.get('error_message'):
                print(f"      Error: {detail['error_message']}")
        
    except Exception as e:
        print(f"❌ Error testing SMS campaign: {str(e)}")
    
    # Test delivery report
    print(f"\n📊 Testing delivery report:")
    try:
        report = await twilio_service.get_sms_delivery_report("test_campaign_123")
        print(f"  Report generated: {report.get('success', False)}")
        if 'report' in report:
            print(f"  Report data: {report['report']}")
    except Exception as e:
        print(f"❌ Error testing delivery report: {str(e)}")
    
    # Check Twilio configuration
    print(f"\n🔧 Twilio Configuration:")
    print(f"  Account SID: {twilio_service.account_sid[:10]}..." if twilio_service.account_sid else "  Account SID: Not configured")
    print(f"  Auth Token: {'Configured' if twilio_service.auth_token else 'Not configured'}")
    print(f"  Phone Number: {twilio_service.phone_number if twilio_service.phone_number else 'Not configured'}")
    print(f"  Client initialized: {'Yes' if twilio_service.client else 'No (will use mock)'}")
    
    print(f"\n🎉 Twilio integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_twilio_integration())