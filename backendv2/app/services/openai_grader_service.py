"""
OpenAI Digital Presence Grader Service
"""
import logging
import json
from typing import Dict, Any
from pathlib import Path

from .openai_service import openai_service
from .web_scraper_service import web_scraper_service
from .google_business_scraper import google_business_scraper

logger = logging.getLogger(__name__)

class OpenAIGraderService:
    def __init__(self):
        self.openai_service = openai_service
        self.system_prompt = ""
        self.user_prompt_template = ""
        self._load_prompts()

    def _load_prompts(self):
        try:
            prompt_file_path = Path(__file__).parent.parent.parent.parent / "digital_presence_prompts.md"
            with open(prompt_file_path, "r") as f:
                content = f.read()
            
            # This is a simplified parser. A more robust solution might use regex
            # or a markdown parsing library if the format becomes more complex.
            system_prompt_start = content.find("## System Prompt")
            user_prompt_start = content.find("## User Prompt & Output Structure")
            
            if system_prompt_start == -1 or user_prompt_start == -1:
                raise ValueError("Could not find prompt sections in digital_presence_prompts.md")

            system_prompt_content = content[system_prompt_start:user_prompt_start].strip()
            user_prompt_content = content[user_prompt_start:].strip()

            # Extract the core system prompt text
            self.system_prompt = system_prompt_content.split("## System Prompt")[1].strip()
            
            # Extract the user prompt template
            user_prompt_template_start = user_prompt_content.find("`{{google_business_profile_url}}`")
            if user_prompt_template_start != -1:
                 # Find the start of the user prompt text, which is before the placeholder
                prompt_text_start = user_prompt_content.rfind('\n', 0, user_prompt_template_start) + 1
                self.user_prompt_template = user_prompt_content[prompt_text_start:].split("`{{google_business_profile_url}}`")[0].strip()
                self.user_prompt_template += " `{{google_business_profile_url}}`" # re-add placeholder
            else:
                raise ValueError("Could not find user prompt template placeholder.")

            logger.info("Successfully loaded OpenAI grader prompts.")

        except Exception as e:
            logger.error(f"Failed to load prompts for OpenAIGraderService: {e}")
            # Fallback to basic prompts if loading fails
            self.system_prompt = "You are a digital marketing analyst for restaurants."
            self.user_prompt_template = "Analyze the digital presence for the restaurant with this Google Business Profile: `{{google_business_profile_url}}`"

    async def analyze_digital_presence(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        google_business_url = restaurant_data.get('google_business_url')
        if not google_business_url:
            return {"success": False, "error": "Google Business Profile URL is required for OpenAI analysis."}

        try:
            # Use enhanced prompt if real data is available, otherwise use template
            if restaurant_data.get('enhanced_prompt'):
                logger.info("🧠 Using enhanced prompt with real scraped data for OpenAI analysis")
                user_prompt = restaurant_data.get('enhanced_prompt')
                logger.info(f"📝 Enhanced prompt content (first 500 chars): {user_prompt[:500]}...")
            else:
                logger.info("⚠️ Using basic template - may result in dummy data")
                # Construct the final user prompt
                user_prompt = self.user_prompt_template.replace("{{google_business_profile_url}}", google_business_url)

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Call OpenAI API
            # Using a higher max_tokens for the detailed JSON structure expected
            openai_response_str = await self.openai_service.chat_completion(messages, max_tokens=4096)

            # The response from OpenAI should be a JSON string. We need to parse it.
            # It might be wrapped in markdown code blocks ```json ... ```
            logger.info(f"Raw OpenAI response: {openai_response_str[:500]}...")
            
            if openai_response_str.strip().startswith("```json"):
                json_str = openai_response_str.strip()[7:-3].strip()
            else:
                json_str = openai_response_str

            logger.info(f"Parsed JSON string: {json_str[:500]}...")
            analysis_result = json.loads(json_str)
            logger.info(f"Successfully parsed OpenAI analysis with keys: {list(analysis_result.keys())}")

            return {
                "success": True,
                "data": analysis_result,
                "provider": "openai"
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from OpenAI: {e}")
            logger.error(f"Raw OpenAI response: {openai_response_str}")
            return {"success": False, "error": "Failed to parse analysis from OpenAI.", "raw_response": openai_response_str}
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI digital presence analysis: {e}")
            return {"success": False, "error": str(e)}

openai_grader_service = OpenAIGraderService()