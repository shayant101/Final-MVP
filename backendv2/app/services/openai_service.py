"""
OpenAI API service for generating restaurant marketing content
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Try to import OpenAI, fall back gracefully if not available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.fallback_to_mock = False
        
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not installed. Falling back to mock service.")
            self.fallback_to_mock = True
        elif not self.api_key:
            logger.warning("OpenAI API key not found. Falling back to mock service.")
            self.fallback_to_mock = True
        else:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.fallback_to_mock = True

    async def _make_openai_request(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Make a request to OpenAI API with error handling"""
        try:
            if self.fallback_to_mock:
                raise Exception("OpenAI API key not configured - using fallback")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)} - AI website generator will use fallback")
            raise Exception(f"OpenAI service unavailable: {str(e)}")

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Wrapper for chat completion that matches the interface expected by openai_grader_service"""
        return await self._make_openai_request(messages, model, max_tokens, temperature)

    async def generate_ad_copy(self, restaurant_name: str, item_to_promote: str, offer: str, target_audience: str = "local food lovers") -> Dict[str, Any]:
        """Generate Facebook ad copy using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert restaurant marketing copywriter. Create compelling Facebook ad copy that drives customer action. 
                    
                    Guidelines:
                    - Keep headlines under 40 characters for mobile optimization
                    - Body text should be 90-125 characters for best performance
                    - Include emotional triggers and urgency
                    - Use restaurant-specific language and food imagery
                    - Include clear call-to-action
                    - Make it sound authentic and local
                    
                    Format your response as:
                    HEADLINE: [headline]
                    BODY: [body text]
                    CTA: [call to action]"""
                },
                {
                    "role": "user",
                    "content": f"""Create Facebook ad copy for:
                    Restaurant: {restaurant_name}
                    Item to promote: {item_to_promote}
                    Offer: {offer}
                    Target audience: {target_audience}
                    
                    Make it compelling and action-oriented."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=300, temperature=0.8)
            
            # Parse the response
            lines = content.split('\n')
            headline = ""
            body = ""
            cta = ""
            
            for line in lines:
                if line.startswith("HEADLINE:"):
                    headline = line.replace("HEADLINE:", "").strip()
                elif line.startswith("BODY:"):
                    body = line.replace("BODY:", "").strip()
                elif line.startswith("CTA:"):
                    cta = line.replace("CTA:", "").strip()
            
            # Fallback if parsing fails
            if not headline or not body or not cta:
                parts = content.split('\n\n')
                headline = parts[0] if len(parts) > 0 else f"🍽️ {restaurant_name} Special!"
                body = parts[1] if len(parts) > 1 else f"Get our amazing {item_to_promote}! {offer}"
                cta = parts[2] if len(parts) > 2 else "Order now or visit us today!"
            
            full_ad_copy = f"{headline}\n\n{body}\n\n{cta}"
            
            return {
                "success": True,
                "ad_copy": full_ad_copy,
                "components": {
                    "headline": headline,
                    "body": body,
                    "cta": cta
                },
                "metadata": {
                    "character_count": len(full_ad_copy),
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-4",
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate ad copy: {str(e)}")
            # Fallback to mock service
            from .mock_openai import generate_ad_copy as mock_generate_ad_copy
            return await mock_generate_ad_copy(restaurant_name, item_to_promote, offer)

    async def generate_sms_message(self, restaurant_name: str, customer_name: str, offer: str, offer_code: str, message_type: str = "winback") -> Dict[str, Any]:
        """Generate SMS message using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert at writing restaurant SMS marketing messages. Create personalized, engaging SMS messages that drive customer action.
                    
                    Guidelines:
                    - Keep messages under 160 characters (including spaces)
                    - Use the customer's name for personalization
                    - Include the offer and promo code clearly
                    - Create urgency without being pushy
                    - Sound friendly and authentic
                    - Include clear expiration or urgency
                    
                    Message types:
                    - winback: For customers who haven't visited recently
                    - promotion: For general promotional offers
                    - loyalty: For repeat customers
                    - special_event: For special occasions or events"""
                },
                {
                    "role": "user",
                    "content": f"""Create a {message_type} SMS message for:
                    Restaurant: {restaurant_name}
                    Customer: {customer_name}
                    Offer: {offer}
                    Promo code: {offer_code}
                    
                    Make it personal and compelling, under 160 characters."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=100, temperature=0.7)
            
            # Ensure message is under 160 characters
            final_message = content[:157] + "..." if len(content) > 160 else content
            
            return {
                "success": True,
                "sms_message": final_message,
                "metadata": {
                    "character_count": len(final_message),
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-3.5-turbo",
                    "message_type": message_type,
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate SMS message: {str(e)}")
            # Fallback to mock service
            from .mock_openai import generate_sms_message as mock_generate_sms_message
            return await mock_generate_sms_message(restaurant_name, customer_name, offer, offer_code)

    async def generate_email_campaign(self, restaurant_name: str, campaign_type: str, offer: str, target_audience: str = "customers") -> Dict[str, Any]:
        """Generate email campaign content using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert email marketing copywriter for restaurants. Create compelling email campaigns that drive engagement and visits.
                    
                    Guidelines:
                    - Subject lines should be 30-50 characters
                    - Use emotional triggers and urgency
                    - Include clear value proposition
                    - Make it scannable with short paragraphs
                    - Include strong call-to-action
                    - Sound authentic and local
                    
                    Format your response as:
                    SUBJECT: [subject line]
                    PREVIEW: [preview text]
                    CONTENT: [email body content]
                    CTA: [call to action button text]"""
                },
                {
                    "role": "user",
                    "content": f"""Create an email campaign for:
                    Restaurant: {restaurant_name}
                    Campaign type: {campaign_type}
                    Offer: {offer}
                    Target audience: {target_audience}
                    
                    Make it engaging and action-oriented."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=600, temperature=0.8)
            
            # Parse the response
            lines = content.split('\n')
            subject = ""
            preview = ""
            email_content = ""
            cta = ""
            
            current_section = ""
            for line in lines:
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                    current_section = "subject"
                elif line.startswith("PREVIEW:"):
                    preview = line.replace("PREVIEW:", "").strip()
                    current_section = "preview"
                elif line.startswith("CONTENT:"):
                    email_content = line.replace("CONTENT:", "").strip()
                    current_section = "content"
                elif line.startswith("CTA:"):
                    cta = line.replace("CTA:", "").strip()
                    current_section = "cta"
                elif current_section == "content" and line.strip():
                    email_content += "\n" + line
            
            return {
                "success": True,
                "email_campaign": {
                    "subject": subject,
                    "preview": preview,
                    "content": email_content.strip(),
                    "cta": cta
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-4",
                    "campaign_type": campaign_type,
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate email campaign: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate email campaign: {str(e)}",
                "fallback_available": True
            }

    async def generate_social_media_post(self, restaurant_name: str, platform: str, content_type: str, item_to_promote: str = "", offer: str = "") -> Dict[str, Any]:
        """Generate social media post content using OpenAI"""
        try:
            platform_guidelines = {
                "instagram": "Use emojis, hashtags, and visual language. 2200 character limit.",
                "facebook": "Engaging and conversational. 63,206 character limit but keep under 500 for best engagement.",
                "twitter": "Concise and punchy. 280 character limit.",
                "linkedin": "Professional but approachable. 3000 character limit."
            }
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a social media expert for restaurants. Create engaging {platform} posts that drive engagement and visits.
                    
                    Platform guidelines: {platform_guidelines.get(platform, "Keep it engaging and on-brand")}
                    
                    Content types:
                    - promotional: Highlighting offers and specials
                    - behind_scenes: Showing kitchen, staff, preparation
                    - menu_highlight: Featuring specific dishes
                    - community: Engaging with local community
                    - seasonal: Seasonal menu items or themes
                    
                    Include relevant hashtags and emojis where appropriate."""
                },
                {
                    "role": "user",
                    "content": f"""Create a {platform} post for:
                    Restaurant: {restaurant_name}
                    Content type: {content_type}
                    Item to promote: {item_to_promote}
                    Offer: {offer}
                    
                    Make it engaging and platform-appropriate."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=300, temperature=0.8)
            
            return {
                "success": True,
                "social_post": content,
                "metadata": {
                    "platform": platform,
                    "content_type": content_type,
                    "character_count": len(content),
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-3.5-turbo",
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate social media post: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate social media post: {str(e)}",
                "fallback_available": True
            }

    async def generate_menu_descriptions(self, restaurant_name: str, cuisine_type: str, items: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate appealing menu item descriptions using OpenAI"""
        try:
            items_text = "\n".join([f"- {item['name']}: {item.get('ingredients', 'No ingredients provided')}" for item in items])
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a professional menu writer for restaurants. Create appetizing, descriptive menu item descriptions that make customers want to order.
                    
                    Guidelines:
                    - Use sensory language (taste, texture, aroma)
                    - Highlight unique ingredients or preparation methods
                    - Keep descriptions concise but enticing (20-40 words)
                    - Avoid overused words like "delicious" or "amazing"
                    - Focus on what makes each dish special
                    - Use active voice and vivid adjectives"""
                },
                {
                    "role": "user",
                    "content": f"""Create menu descriptions for {restaurant_name} ({cuisine_type} cuisine):
                    
                    {items_text}
                    
                    Make each description appetizing and unique."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=800, temperature=0.7)
            
            return {
                "success": True,
                "menu_descriptions": content,
                "metadata": {
                    "restaurant_name": restaurant_name,
                    "cuisine_type": cuisine_type,
                    "items_count": len(items),
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-4",
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate menu descriptions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate menu descriptions: {str(e)}",
                "fallback_available": True
            }

    async def generate_campaign_suggestions(self, restaurant_name: str, campaign_type: str, business_goals: List[str] = None) -> Dict[str, Any]:
        """Generate campaign suggestions using OpenAI"""
        try:
            goals_text = ", ".join(business_goals) if business_goals else "increase sales and customer engagement"
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant marketing strategist. Provide actionable campaign suggestions based on industry best practices and current trends.
                    
                    Include:
                    - Specific campaign ideas
                    - Target audience recommendations
                    - Budget suggestions (small: $10-25, medium: $25-75, large: $75-200)
                    - Timing recommendations
                    - Success metrics to track
                    
                    Format as JSON-like structure for easy parsing."""
                },
                {
                    "role": "user",
                    "content": f"""Generate {campaign_type} campaign suggestions for:
                    Restaurant: {restaurant_name}
                    Business goals: {goals_text}
                    
                    Provide 3-5 specific campaign ideas with details."""
                }
            ]
            
            content = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=800, temperature=0.7)
            
            return {
                "success": True,
                "suggestions": content,
                "metadata": {
                    "campaign_type": campaign_type,
                    "business_goals": business_goals,
                    "generated_at": datetime.now().isoformat(),
                    "model": "gpt-4",
                    "service": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate campaign suggestions: {str(e)}")
            # Fallback to mock service
            from .mock_openai import generate_campaign_suggestions as mock_generate_campaign_suggestions
            return await mock_generate_campaign_suggestions(restaurant_name, campaign_type)

    async def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        try:
            if self.fallback_to_mock:
                return {
                    "success": False,
                    "message": "OpenAI API key not configured, using mock service",
                    "service": "mock"
                }
            
            # Simple test request
            messages = [
                {
                    "role": "user",
                    "content": "Respond with 'OpenAI connection successful' if you can read this."
                }
            ]
            
            response = await self._make_openai_request(messages, model="gpt-3.5-turbo", max_tokens=20, temperature=0)
            
            return {
                "success": True,
                "message": "OpenAI API connection successful",
                "response": response,
                "service": "openai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"OpenAI API connection failed: {str(e)}",
                "service": "error"
            }

# Create service instance
openai_service = OpenAIService()