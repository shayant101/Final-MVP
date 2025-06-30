#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from app.services.ai_grader_service import ai_grader_service

async def test_bad_website():
    restaurant_data = {
        'name': 'Test Restaurant',
        'website': 'https://nonexistent-website-12345.com',
        'google_business_url': 'invalid-url',
        'user_id': 'test'
    }
    result = await ai_grader_service.analyze_digital_presence(restaurant_data)
    website = result.get('component_scores', {}).get('website', {})
    google = result.get('component_scores', {}).get('google_business', {})
    print(f'Bad Website Score: {website.get("score", "N/A")}/100')
    print(f'Bad Website Accessible: {website.get("validation_data", {}).get("accessible", "N/A")}')
    print(f'Bad Google URL Valid: {google.get("url_format_valid", "N/A")}')

asyncio.run(test_bad_website())