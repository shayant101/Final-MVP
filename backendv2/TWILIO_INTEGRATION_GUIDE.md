# Twilio SMS Integration Guide

## Overview

The application now includes full Twilio SMS integration for sending SMS campaigns to customers. The integration supports both real Twilio API calls and graceful fallback to mock implementation when credentials are not configured.

## Features

✅ **Real Twilio SMS Sending**: Send actual SMS messages using Twilio API  
✅ **Phone Number Validation**: Validate and format phone numbers to E.164 format  
✅ **Error Handling**: Comprehensive error handling with detailed error messages  
✅ **Cost Tracking**: Track SMS costs and delivery statistics  
✅ **Graceful Fallback**: Falls back to mock implementation when Twilio is not configured  
✅ **Rate Limiting**: Built-in delays to prevent API rate limiting  
✅ **Personalization**: Personalized messages with customer names  

## Configuration

### 1. Twilio Account Setup

1. Sign up for a Twilio account at [https://www.twilio.com](https://www.twilio.com)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a Twilio phone number for sending SMS

### 2. Environment Variables

Update the `.env` file in the `backendv2` directory with your Twilio credentials:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=OR18152382fc04134fcb4cb65ae2dcbb18  # Your actual Account SID
TWILIO_AUTH_TOKEN=your-actual-auth-token-here           # Your actual Auth Token
TWILIO_PHONE_NUMBER=+1234567890                        # Your Twilio phone number
```

**Important**: Replace the placeholder values with your actual Twilio credentials:
- `TWILIO_ACCOUNT_SID`: Already provided (OR18152382fc04134fcb4cb65ae2dcbb18)
- `TWILIO_AUTH_TOKEN`: Get this from your Twilio Console
- `TWILIO_PHONE_NUMBER`: Your purchased Twilio phone number in E.164 format

### 3. Dependencies

The Twilio SDK is already installed. If you need to reinstall:

```bash
cd backendv2
pip3 install twilio
```

## Usage

### SMS Campaign Creation

1. **Via API Endpoint**: `POST /api/campaigns/sms`
   - Upload a CSV file with customer data
   - Provide restaurant name, offer, and offer code
   - The system will automatically send SMS to lapsed customers

2. **CSV Format**: Customer list should include:
   ```csv
   customer_name,phone_number,last_order_date
   John Doe,+1234567890,2024-01-15
   Jane Smith,1987654321,2024-02-20
   ```

### Phone Number Formats Supported

- `1234567890` → Formatted to `+11234567890`
- `+1234567890` → Used as-is
- `(123) 456-7890` → Formatted to `+11234567890`
- `123-456-7890` → Formatted to `+11234567890`

### Message Personalization

Messages automatically include customer names:
```
Hi {customer_name}! We miss you at [Restaurant Name]! [Offer] Use code [OfferCode]
```

## API Endpoints

### Create SMS Campaign
```http
POST /api/campaigns/sms
Content-Type: multipart/form-data

restaurantName: "Your Restaurant"
offer: "Get 20% off your next order!"
offerCode: "SAVE20"
customerList: [CSV file]
```

### Get SMS Campaign Status
```http
GET /api/campaigns/sms/status/{campaign_id}
```

### SMS Preview
```http
POST /api/campaigns/sms/preview
Content-Type: multipart/form-data

restaurantName: "Your Restaurant"
offer: "Get 20% off your next order!"
offerCode: "SAVE20"
customerList: [CSV file] (optional)
```

## Testing

### Test the Integration

Run the test script to verify everything is working:

```bash
cd backendv2
python3.9 test_twilio_integration.py
```

This will test:
- Phone number validation and formatting
- SMS campaign sending
- Delivery report generation
- Configuration status

### Expected Output

When properly configured:
```
🧪 Testing Twilio SMS Integration
==================================================

📞 Testing phone number validation and formatting:
  1234567890           -> Valid: True  | Formatted: +11234567890
  +1234567890          -> Valid: True  | Formatted: +11234567890

📱 Testing SMS campaign sending:
  ✅ Campaign Results:
    Campaign ID: sms_1234567890_abc123
    Messages sent: 2
    Messages failed: 1
    Total cost: $0.0150

🔧 Twilio Configuration:
  Account SID: OR18152382...
  Auth Token: Configured
  Phone Number: +1234567890
  Client initialized: Yes
```

## Error Handling

### Common Errors and Solutions

1. **"Twilio credentials not fully configured"**
   - Solution: Update `.env` file with actual Twilio credentials

2. **"Invalid phone number format"**
   - Solution: Ensure phone numbers are in valid format (10+ digits)

3. **"Message blocked by carrier"**
   - Solution: Check message content for spam triggers

4. **"Insufficient funds"**
   - Solution: Add funds to your Twilio account

### Graceful Fallback

When Twilio credentials are not configured, the system automatically falls back to mock implementation:
- SMS campaigns will simulate sending
- All API endpoints remain functional
- No actual SMS messages are sent
- Costs are simulated

## Security Considerations

1. **Environment Variables**: Never commit actual credentials to version control
2. **Rate Limiting**: Built-in delays prevent API abuse
3. **Phone Validation**: All phone numbers are validated before sending
4. **Error Logging**: Errors are logged for monitoring

## Cost Management

- **Per Message Cost**: $0.0075 per SMS (Twilio standard pricing)
- **Cost Tracking**: Real-time cost calculation and reporting
- **Budget Control**: Monitor costs through campaign reports

## Monitoring and Analytics

### Campaign Metrics
- Total messages sent/failed/pending
- Delivery rates
- Cost per campaign
- Customer engagement tracking

### Delivery Reports
- Individual message status
- Error codes and messages
- Delivery timestamps
- Cost breakdown

## Troubleshooting

### Check Configuration
```python
from app.services.twilio_service import twilio_service
print(f"Account SID: {twilio_service.account_sid}")
print(f"Client initialized: {twilio_service.client is not None}")
```

### Test Phone Number
```python
from app.services.twilio_service import validate_phone_number, format_phone_number
number = "+1234567890"
print(f"Valid: {validate_phone_number(number)}")
print(f"Formatted: {format_phone_number(number)}")
```

## Support

For Twilio-specific issues:
- [Twilio Documentation](https://www.twilio.com/docs)
- [Twilio Support](https://support.twilio.com)

For application-specific issues:
- Check the logs in the backend console
- Run the test script to diagnose issues
- Verify environment variables are correctly set