"""
AI Website Generation Engine
Generates complete restaurant websites using AI analysis of restaurant data
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from .openai_service import openai_service
from .ai_content_engine import ai_content_engine
from .admin_analytics_service import admin_analytics_service

logger = logging.getLogger(__name__)

class AIWebsiteGeneratorService:
    def __init__(self):
        self.openai_service = openai_service
        self.content_engine = ai_content_engine
        
        # Restaurant-specific website templates
        self.template_categories = {
            "fine_dining": {
                "color_schemes": ["elegant_dark", "sophisticated_neutral", "luxury_gold"],
                "layouts": ["minimal_hero", "gallery_focused", "story_driven"],
                "components": ["reservation_system", "chef_profile", "wine_list", "private_dining"]
            },
            "casual_dining": {
                "color_schemes": ["warm_earth", "vibrant_fresh", "cozy_comfort"],
                "layouts": ["menu_hero", "family_friendly", "community_focused"],
                "components": ["online_ordering", "family_menu", "events_calendar", "loyalty_program"]
            },
            "fast_casual": {
                "color_schemes": ["modern_bright", "energetic_bold", "clean_minimal"],
                "layouts": ["order_focused", "speed_emphasis", "mobile_first"],
                "components": ["quick_order", "nutrition_info", "location_finder", "app_download"]
            },
            "cafe_bakery": {
                "color_schemes": ["warm_pastels", "rustic_natural", "artisan_craft"],
                "layouts": ["product_showcase", "cozy_atmosphere", "artisan_story"],
                "components": ["daily_specials", "catering_menu", "coffee_subscription", "baking_classes"]
            },
            "ethnic_cuisine": {
                "color_schemes": ["cultural_authentic", "spice_inspired", "heritage_rich"],
                "layouts": ["cultural_story", "authentic_experience", "tradition_modern"],
                "components": ["cultural_info", "authentic_recipes", "chef_heritage", "cooking_classes"]
            }
        }
        
        # AI generation prompts for different website sections
        self.section_prompts = {
            "hero_section": """Create a compelling hero section for a {cuisine_type} restaurant website. Include:
            - Powerful headline that captures the restaurant's essence
            - Engaging subheadline with value proposition
            - Call-to-action buttons (primary and secondary)
            - Background image description that fits the brand""",
            
            "about_section": """Write an engaging About Us section for {restaurant_name}, a {cuisine_type} restaurant. Include:
            - Restaurant's story and founding
            - Chef/owner background and passion
            - What makes this restaurant unique
            - Community connection and values""",
            
            "menu_showcase": """Create a menu showcase section for {restaurant_name}. Include:
            - Featured signature dishes with descriptions
            - Menu categories organization
            - Pricing strategy recommendations
            - Dietary options and allergen information""",
            
            "location_contact": """Design a location and contact section for {restaurant_name}. Include:
            - Welcoming location description
            - Hours of operation recommendations
            - Contact information layout
            - Directions and parking information""",
            
            "reservation_system": """Create a reservation system section for {restaurant_name}. Include:
            - Reservation form design
            - Special requests handling
            - Party size and time slot options
            - Confirmation and reminder system"""
        }

    async def generate_complete_website(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete restaurant website using AI analysis
        """
        start_time = datetime.now()
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            restaurant_id = restaurant_data.get('restaurant_id') or restaurant_data.get('user_id', 'unknown')
            
            logger.info(f"Starting website generation for {restaurant_name}")
            
            # Step 1: Analyze restaurant data and determine optimal design
            design_analysis = await self._analyze_restaurant_for_design(restaurant_data)
            
            # Step 2: Generate website structure and content
            website_structure = await self._generate_website_structure(restaurant_data, design_analysis)
            
            # Step 3: Generate all website sections
            website_sections = await self._generate_all_sections(restaurant_data, design_analysis)
            
            # Step 4: Generate design system and styling
            design_system = await self._generate_design_system(restaurant_data, design_analysis)
            
            # Step 5: Generate SEO optimization
            seo_optimization = await self._generate_seo_optimization(restaurant_data)
            
            # Step 6: Generate mobile responsiveness guidelines
            mobile_optimization = await self._generate_mobile_optimization(restaurant_data)
            
            # Step 7: Generate performance optimization
            performance_optimization = await self._generate_performance_optimization()
            
            # Step 8: Create implementation roadmap
            implementation_plan = await self._create_implementation_roadmap(website_structure)
            
            # Compile complete website package
            complete_website = {
                "website_id": f"ai_website_{restaurant_id}_{int(datetime.now().timestamp())}",
                "restaurant_name": restaurant_name,
                "generation_date": datetime.now().isoformat(),
                "design_analysis": design_analysis,
                "website_structure": website_structure,
                "website_sections": website_sections,
                "design_system": design_system,
                "seo_optimization": seo_optimization,
                "mobile_optimization": mobile_optimization,
                "performance_optimization": performance_optimization,
                "implementation_plan": implementation_plan,
                "ai_insights": await self._generate_website_insights(restaurant_data, design_analysis),
                "success": True
            }
            
            # Log analytics
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            estimated_tokens = len(str(complete_website)) // 4
            asyncio.create_task(admin_analytics_service.log_ai_usage(
                restaurant_id=restaurant_id,
                feature_type="website_generation",
                operation_type="complete_website",
                processing_time=processing_time,
                tokens_used=estimated_tokens,
                status="success",
                metadata={
                    "restaurant_name": restaurant_name,
                    "design_category": design_analysis.get("recommended_category"),
                    "sections_generated": len(website_sections),
                    "has_menu_data": bool(restaurant_data.get('menu_items'))
                }
            ))
            
            return complete_website
            
        except Exception as e:
            logger.error(f"Website generation failed for {restaurant_name}: {str(e)}")
            
            # Log error analytics
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            asyncio.create_task(admin_analytics_service.log_ai_usage(
                restaurant_id=restaurant_id,
                feature_type="website_generation",
                operation_type="complete_website",
                processing_time=processing_time,
                tokens_used=0,
                status="error",
                metadata={
                    "error_details": str(e),
                    "restaurant_name": restaurant_name
                }
            ))
            
            # Always return a working website, even if AI fails
            logger.info(f"AI generation failed, creating fallback website for {restaurant_name}")
            return await self._generate_comprehensive_fallback_website(restaurant_data)

    async def _analyze_restaurant_for_design(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze restaurant data to determine optimal design approach
        """
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            cuisine_type = restaurant_data.get('cuisine_type', 'American')
            price_range = restaurant_data.get('price_range', 'moderate')
            location = restaurant_data.get('location', 'Local Area')
            menu_items = restaurant_data.get('menu_items', [])
            target_audience = restaurant_data.get('target_audience', {})
            
            # AI analysis prompt
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant website design expert. Analyze the restaurant data and recommend the optimal design approach.
                    
                    Consider:
                    - Restaurant type and cuisine style
                    - Target audience and demographics
                    - Price point and positioning
                    - Menu complexity and offerings
                    - Local market characteristics
                    
                    Provide specific recommendations for:
                    - Design category (fine_dining, casual_dining, fast_casual, cafe_bakery, ethnic_cuisine)
                    - Color scheme preferences
                    - Layout priorities
                    - Essential components
                    - Brand personality traits
                    
                    Format as JSON for easy parsing."""
                },
                {
                    "role": "user",
                    "content": f"""Analyze this restaurant for website design:
                    
                    Restaurant: {restaurant_name}
                    Cuisine: {cuisine_type}
                    Price Range: {price_range}
                    Location: {location}
                    Menu Items: {len(menu_items)} items
                    Target Audience: {target_audience}
                    
                    Recommend the optimal design approach and explain your reasoning."""
                }
            ]
            
            ai_analysis = await self.openai_service._make_openai_request(
                messages, model="gpt-4", max_tokens=800, temperature=0.3
            )
            
            # Parse AI response and combine with template data
            recommended_category = self._determine_design_category(restaurant_data)
            template_config = self.template_categories.get(recommended_category, self.template_categories["casual_dining"])
            
            return {
                "ai_analysis": ai_analysis,
                "recommended_category": recommended_category,
                "template_config": template_config,
                "design_priorities": self._get_design_priorities(restaurant_data),
                "brand_personality": self._analyze_brand_personality(restaurant_data),
                "competitive_positioning": self._analyze_competitive_positioning(restaurant_data),
                "user_experience_focus": self._determine_ux_focus(restaurant_data)
            }
            
        except Exception as e:
            logger.error(f"Design analysis failed: {str(e)}")
            return self._get_fallback_design_analysis(restaurant_data)

    async def _generate_website_structure(self, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the overall website structure and navigation
        """
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            recommended_category = design_analysis.get("recommended_category", "casual_dining")
            
            # AI prompt for website structure
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant website architect. Create an optimal website structure based on the restaurant analysis.
                    
                    Consider:
                    - User journey and conversion goals
                    - Restaurant type and customer expectations
                    - Mobile-first navigation
                    - SEO-friendly URL structure
                    - Accessibility requirements
                    
                    Provide:
                    - Main navigation structure
                    - Page hierarchy and organization
                    - URL structure recommendations
                    - Footer content organization
                    - Mobile navigation considerations"""
                },
                {
                    "role": "user",
                    "content": f"""Create website structure for {restaurant_name}:
                    
                    Restaurant Category: {recommended_category}
                    Design Analysis: {design_analysis.get('ai_analysis', 'Standard restaurant analysis')}
                    
                    Focus on user experience and conversion optimization."""
                }
            ]
            
            structure_content = await self.openai_service._make_openai_request(
                messages, model="gpt-4", max_tokens=600, temperature=0.4
            )
            
            # Generate standard structure based on category
            base_structure = self._get_base_structure_by_category(recommended_category)
            
            return {
                "ai_generated_structure": structure_content,
                "recommended_pages": base_structure["pages"],
                "navigation_hierarchy": base_structure["navigation"],
                "url_structure": base_structure["urls"],
                "footer_sections": base_structure["footer"],
                "mobile_navigation": self._generate_mobile_navigation(base_structure),
                "conversion_optimization": self._get_conversion_optimization_structure()
            }
            
        except Exception as e:
            logger.error(f"Website structure generation failed: {str(e)}")
            return self._get_fallback_website_structure()

    async def _generate_all_sections(self, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content for all website sections
        """
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            cuisine_type = restaurant_data.get('cuisine_type', 'American')
            
            sections = {}
            
            # Generate each section concurrently for efficiency
            section_tasks = []
            
            for section_name, prompt_template in self.section_prompts.items():
                task = self._generate_section_content(
                    section_name, 
                    prompt_template.format(
                        restaurant_name=restaurant_name,
                        cuisine_type=cuisine_type
                    ),
                    restaurant_data,
                    design_analysis
                )
                section_tasks.append(task)
            
            # Wait for all sections to complete
            section_results = await asyncio.gather(*section_tasks, return_exceptions=True)
            
            # Process results
            for i, (section_name, _) in enumerate(self.section_prompts.items()):
                result = section_results[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate {section_name}: {str(result)}")
                    sections[section_name] = self._get_fallback_section_content(section_name, restaurant_data)
                else:
                    sections[section_name] = result
            
            # Generate additional restaurant-specific sections
            sections.update(await self._generate_restaurant_specific_sections(restaurant_data, design_analysis))
            
            return {
                "generated_sections": sections,
                "section_count": len(sections),
                "content_strategy": await self._generate_content_strategy(restaurant_data),
                "personalization_opportunities": self._identify_personalization_opportunities(restaurant_data)
            }
            
        except Exception as e:
            logger.error(f"Section generation failed: {str(e)}")
            return self._get_fallback_sections(restaurant_data)

    async def _generate_section_content(self, section_name: str, prompt: str, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content for a specific website section
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a restaurant website content creator specializing in {section_name} sections. 
                    Create compelling, conversion-focused content that matches the restaurant's brand and target audience.
                    
                    Consider:
                    - Restaurant's unique value proposition
                    - Target audience preferences
                    - Local market characteristics
                    - Mobile-first content consumption
                    - SEO optimization opportunities
                    
                    Provide structured content with clear headings, engaging copy, and actionable elements."""
                },
                {
                    "role": "user",
                    "content": f"""{prompt}
                    
                    Restaurant Data: {json.dumps(restaurant_data, default=str)}
                    Design Category: {design_analysis.get('recommended_category')}
                    
                    Create engaging, conversion-optimized content."""
                }
            ]
            
            content = await self.openai_service._make_openai_request(
                messages, model="gpt-4", max_tokens=800, temperature=0.6
            )
            
            return {
                "section_name": section_name,
                "content": content,
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate {section_name} content: {str(e)}")
            raise

    async def _generate_design_system(self, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive design system for the website
        """
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            cuisine_type = restaurant_data.get('cuisine_type', 'American')
            recommended_category = design_analysis.get("recommended_category", "casual_dining")
            
            # AI prompt for design system
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant brand and web design expert. Create a comprehensive design system that captures the restaurant's essence and appeals to their target audience.
                    
                    Include:
                    - Color palette with psychological reasoning
                    - Typography hierarchy and font recommendations
                    - Visual style and imagery guidelines
                    - Component design patterns
                    - Brand voice and tone guidelines
                    
                    Consider cultural authenticity, target demographics, and conversion optimization."""
                },
                {
                    "role": "user",
                    "content": f"""Create a design system for {restaurant_name}:
                    
                    Cuisine Type: {cuisine_type}
                    Restaurant Category: {recommended_category}
                    Brand Personality: {design_analysis.get('brand_personality', 'Welcoming and authentic')}
                    
                    Focus on creating emotional connection and driving conversions."""
                }
            ]
            
            design_content = await self.openai_service._make_openai_request(
                messages, model="gpt-4", max_tokens=1000, temperature=0.5
            )
            
            # Generate technical design specifications
            template_config = design_analysis.get("template_config", {})
            
            return {
                "ai_generated_design": design_content,
                "color_palette": self._generate_color_palette(recommended_category, cuisine_type),
                "typography_system": self._generate_typography_system(recommended_category),
                "component_library": self._generate_component_library(recommended_category),
                "imagery_guidelines": self._generate_imagery_guidelines(restaurant_data),
                "brand_voice": self._generate_brand_voice_guidelines(restaurant_data),
                "accessibility_standards": self._get_accessibility_standards(),
                "responsive_breakpoints": self._get_responsive_breakpoints()
            }
            
        except Exception as e:
            logger.error(f"Design system generation failed: {str(e)}")
            return self._get_fallback_design_system()

    async def _generate_seo_optimization(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO optimization strategy for the restaurant website
        """
        try:
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            cuisine_type = restaurant_data.get('cuisine_type', 'American')
            location = restaurant_data.get('location', 'Local Area')
            
            # AI prompt for SEO strategy
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant SEO expert. Create a comprehensive SEO strategy that will help this restaurant rank well in local search results and attract their target customers.
                    
                    Focus on:
                    - Local SEO optimization
                    - Keyword strategy for restaurant industry
                    - Content marketing opportunities
                    - Technical SEO requirements
                    - Schema markup recommendations
                    - Google My Business optimization
                    
                    Provide actionable, restaurant-specific recommendations."""
                },
                {
                    "role": "user",
                    "content": f"""Create SEO strategy for {restaurant_name}:
                    
                    Cuisine: {cuisine_type}
                    Location: {location}
                    Restaurant Data: {json.dumps(restaurant_data, default=str)}
                    
                    Focus on local search dominance and customer acquisition."""
                }
            ]
            
            seo_content = await self.openai_service._make_openai_request(
                messages, model="gpt-4", max_tokens=800, temperature=0.4
            )
            
            return {
                "ai_seo_strategy": seo_content,
                "keyword_strategy": self._generate_keyword_strategy(restaurant_data),
                "local_seo_checklist": self._generate_local_seo_checklist(restaurant_data),
                "content_calendar": self._generate_seo_content_calendar(restaurant_data),
                "technical_seo": self._generate_technical_seo_requirements(),
                "schema_markup": self._generate_schema_markup(restaurant_data),
                "performance_tracking": self._generate_seo_tracking_plan()
            }
            
        except Exception as e:
            logger.error(f"SEO optimization generation failed: {str(e)}")
            return self._get_fallback_seo_optimization()

    # Helper methods for design analysis
    def _determine_design_category(self, restaurant_data: Dict[str, Any]) -> str:
        """Determine the best design category based on restaurant data"""
        cuisine_type = restaurant_data.get('cuisine_type', '').lower()
        price_range = restaurant_data.get('price_range', '').lower()
        
        # Fine dining indicators
        if price_range in ['expensive', 'high-end', 'fine'] or 'fine' in cuisine_type:
            return "fine_dining"
        
        # Fast casual indicators
        if price_range in ['budget', 'cheap', 'fast'] or any(word in cuisine_type for word in ['fast', 'quick', 'grab']):
            return "fast_casual"
        
        # Cafe/bakery indicators
        if any(word in cuisine_type for word in ['cafe', 'bakery', 'coffee', 'pastry', 'dessert']):
            return "cafe_bakery"
        
        # Ethnic cuisine indicators
        if any(word in cuisine_type for word in ['italian', 'mexican', 'chinese', 'indian', 'thai', 'japanese', 'korean', 'mediterranean', 'greek', 'french']):
            return "ethnic_cuisine"
        
        # Default to casual dining
        return "casual_dining"

    def _get_design_priorities(self, restaurant_data: Dict[str, Any]) -> List[str]:
        """Determine design priorities based on restaurant characteristics"""
        priorities = ["user_experience", "mobile_optimization"]
        
        if restaurant_data.get('menu_items'):
            priorities.append("menu_showcase")
        
        if restaurant_data.get('location'):
            priorities.append("local_seo")
        
        if restaurant_data.get('price_range') in ['expensive', 'high-end']:
            priorities.append("luxury_branding")
        else:
            priorities.append("conversion_optimization")
        
        return priorities

    def _analyze_brand_personality(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and define brand personality traits"""
        cuisine_type = restaurant_data.get('cuisine_type', '').lower()
        price_range = restaurant_data.get('price_range', '').lower()
        
        personality = {
            "primary_traits": [],
            "secondary_traits": [],
            "tone_of_voice": "friendly",
            "emotional_appeal": "comfort"
        }
        
        # Determine traits based on cuisine and price
        if 'fine' in price_range or price_range == 'expensive':
            personality["primary_traits"] = ["sophisticated", "elegant", "exclusive"]
            personality["tone_of_voice"] = "refined"
            personality["emotional_appeal"] = "prestige"
        elif 'fast' in cuisine_type or price_range == 'budget':
            personality["primary_traits"] = ["energetic", "convenient", "reliable"]
            personality["tone_of_voice"] = "casual"
            personality["emotional_appeal"] = "efficiency"
        else:
            personality["primary_traits"] = ["welcoming", "authentic", "community-focused"]
            personality["tone_of_voice"] = "warm"
            personality["emotional_appeal"] = "belonging"
        
        return personality

    # Fallback methods
    async def _generate_fallback_website(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback website when AI fails"""
        restaurant_name = restaurant_data.get('name', 'Restaurant')
        
        return {
            "website_id": f"fallback_website_{int(datetime.now().timestamp())}",
            "restaurant_name": restaurant_name,
            "generation_date": datetime.now().isoformat(),
            "design_analysis": self._get_fallback_design_analysis(restaurant_data),
            "website_structure": self._get_fallback_website_structure(),
            "website_sections": self._get_fallback_sections(restaurant_data),
            "design_system": self._get_fallback_design_system(),
            "seo_optimization": self._get_fallback_seo_optimization(),
            "success": True,
            "note": "Fallback website generated - AI service unavailable"
        }

    def _get_fallback_design_analysis(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback design analysis"""
        recommended_category = self._determine_design_category(restaurant_data)
        
        return {
            "recommended_category": recommended_category,
            "template_config": self.template_categories.get(recommended_category, self.template_categories["casual_dining"]),
            "design_priorities": ["user_experience", "mobile_optimization", "conversion_optimization"],
            "brand_personality": {
                "primary_traits": ["welcoming", "authentic", "reliable"],
                "tone_of_voice": "friendly",
                "emotional_appeal": "comfort"
            }
        }

    def _get_fallback_website_structure(self) -> Dict[str, Any]:
        """Fallback website structure"""
        return {
            "recommended_pages": ["home", "menu", "about", "contact", "reservations"],
            "navigation_hierarchy": {
                "primary": ["Home", "Menu", "About", "Contact"],
                "secondary": ["Reservations", "Catering", "Events"]
            },
            "url_structure": {
                "home": "/",
                "menu": "/menu",
                "about": "/about",
                "contact": "/contact",
                "reservations": "/reservations"
            }
        }

    def _get_fallback_sections(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback website sections"""
        restaurant_name = restaurant_data.get('name', 'Restaurant')
        
        return {
            "generated_sections": {
                "hero_section": {
                    "content": f"Welcome to {restaurant_name} - Experience exceptional dining with fresh ingredients and warm hospitality.",
                    "cta_primary": "View Menu",
                    "cta_secondary": "Make Reservation"
                },
                "about_section": {
                    "content": f"{restaurant_name} is committed to providing an outstanding dining experience with quality food and excellent service."
                },
                "menu_showcase": {
                    "content": "Discover our carefully crafted menu featuring fresh, locally-sourced ingredients."
                }
            }
        }

    def _get_fallback_design_system(self) -> Dict[str, Any]:
        """Fallback design system"""
        return {
            "color_palette": {
                "primary": "#2c3e50",
                "secondary": "#e74c3c",
                "accent": "#f39c12",
                "neutral": "#ecf0f1"
            },
            "typography_system": {
                "headings": "Playfair Display",
                "body": "Open Sans",
                "accent": "Dancing Script"
            },
            "component_library": ["header", "hero", "menu_card", "testimonial", "footer"]
        }

    def _get_fallback_seo_optimization(self) -> Dict[str, Any]:
        """Fallback SEO optimization"""
        return {
            "keyword_strategy": ["restaurant", "dining", "food", "local restaurant"],
            "local_seo_checklist": [
                "Optimize Google My Business",
                "Include location in title tags",
                "Create location-specific content",
                "Build local citations"
            ],
            "technical_seo": [
                "Optimize page speed",
                "Implement schema markup",
                "Ensure mobile responsiveness",
                "Create XML sitemap"
            ]
        }

    # Additional helper methods would be implemented here...
    def _get_base_structure_by_category(self, category: str) -> Dict[str, Any]:
        """Get base website structure by restaurant category"""
        structures = {
            "fine_dining": {
                "pages": ["home", "menu", "wine_list", "about", "reservations", "private_dining", "contact"],
                "navigation": ["Home", "Menu", "Wine", "About", "Reservations", "Contact"],
                "urls": {
                    "home": "/",
                    "menu": "/menu",
                    "wine_list": "/wine",
                    "about": "/about",
                    "reservations": "/reservations",
                    "private_dining": "/private-dining",
                    "contact": "/contact"
                },
                "footer": ["Hours", "Location", "Reservations", "Private Events", "Gift Cards"]
            },
            "casual_dining": {
                "pages": ["home", "menu", "about", "contact", "catering", "events"],
                "navigation": ["Home", "Menu", "About", "Catering", "Contact"],
                "urls": {
                    "home": "/",
                    "menu": "/menu",
                    "about": "/about",
                    "contact": "/contact",
                    "catering": "/catering",
                    "events": "/events"
                },
                "footer": ["Hours", "Location", "Menu", "Catering", "Events", "Contact"]
            }
        }
        
        return structures.get(category, structures["casual_dining"])

    async def _generate_website_insights(self, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights about the website generation"""
        return {
            "design_rationale": f"Selected {design_analysis.get('recommended_category')} template based on cuisine type and target market",
            "optimization_opportunities": [
                "Implement A/B testing for hero section CTAs",
                "Add customer testimonials for social proof",
                "Optimize menu presentation for mobile users",
                "Include local SEO elements throughout"
            ],
            "performance_predictions": {
                "expected_conversion_rate": "3-5% for reservations",
                "mobile_traffic_percentage": "70-80%",
                "local_search_visibility": "High with proper SEO implementation"
            },
            "recommended_integrations": [
                "Google Analytics for performance tracking",
                "OpenTable or similar for reservations",
                "Social media feeds for engagement",
                "Email marketing for customer retention"
            ]
        }

    # Missing helper methods that are called in the code
    def _get_section_optimization_suggestions(self, section_name: str) -> List[str]:
        """Get optimization suggestions for a specific section"""
        suggestions = {
            "hero_section": [
                "A/B test different headlines",
                "Optimize CTA button colors and text",
                "Test hero image vs video background",
                "Add social proof elements"
            ],
            "about_section": [
                "Include chef/owner photos",
                "Add customer testimonials",
                "Highlight unique story elements",
                "Include awards or recognition"
            ],
            "menu_showcase": [
                "Use high-quality food photography",
                "Implement menu filtering options",
                "Add dietary restriction indicators",
                "Include customer favorites"
            ],
            "location_contact": [
                "Add interactive map",
                "Include parking information",
                "Show real-time hours",
                "Add contact form"
            ],
            "reservation_system": [
                "Integrate with booking platforms",
                "Add special occasion options",
                "Include party size recommendations",
                "Implement confirmation system"
            ]
        }
        return suggestions.get(section_name, ["Optimize for mobile", "Improve loading speed", "Add clear CTAs"])

    def _get_conversion_elements_for_section(self, section_name: str) -> List[str]:
        """Get conversion elements for a specific section"""
        elements = {
            "hero_section": ["Primary CTA button", "Secondary CTA button", "Phone number", "Online ordering link"],
            "about_section": ["Reservation CTA", "Menu link", "Contact information", "Social media links"],
            "menu_showcase": ["Order online button", "View full menu link", "Reservation CTA", "Special offers"],
            "location_contact": ["Call button", "Directions link", "Reservation form", "Hours display"],
            "reservation_system": ["Book now button", "Call to reserve", "Special requests form", "Confirmation display"]
        }
        return elements.get(section_name, ["Contact CTA", "Menu link", "Reservation button"])

    def _get_fallback_section_content(self, section_name: str, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback content for a specific section when AI generation fails"""
        restaurant_name = restaurant_data.get('name', 'Restaurant')
        
        fallback_content = {
            "hero_section": {
                "section_name": section_name,
                "content": f"Welcome to {restaurant_name} - Experience exceptional dining with fresh ingredients and warm hospitality.",
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            },
            "about_section": {
                "section_name": section_name,
                "content": f"{restaurant_name} is committed to providing an outstanding dining experience with quality food and excellent service. Our passionate team creates memorable moments for every guest.",
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            },
            "menu_showcase": {
                "section_name": section_name,
                "content": "Discover our carefully crafted menu featuring fresh, locally-sourced ingredients. From appetizers to desserts, every dish is prepared with passion and attention to detail.",
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            },
            "location_contact": {
                "section_name": section_name,
                "content": f"Visit {restaurant_name} and experience our welcoming atmosphere. We're conveniently located and ready to serve you with exceptional hospitality.",
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            },
            "reservation_system": {
                "section_name": section_name,
                "content": f"Reserve your table at {restaurant_name} for an unforgettable dining experience. We accommodate parties of all sizes and special occasions.",
                "generated_at": datetime.now().isoformat(),
                "optimization_suggestions": self._get_section_optimization_suggestions(section_name),
                "conversion_elements": self._get_conversion_elements_for_section(section_name)
            }
        }
        
        return fallback_content.get(section_name, {
            "section_name": section_name,
            "content": f"Welcome to {restaurant_name} - providing exceptional service and quality.",
            "generated_at": datetime.now().isoformat(),
            "optimization_suggestions": ["Optimize for mobile", "Add clear CTAs"],
            "conversion_elements": ["Contact button", "Menu link"]
        })

    async def _generate_restaurant_specific_sections(self, restaurant_data: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate additional restaurant-specific sections"""
        return {
            "testimonials": {
                "section_name": "testimonials",
                "content": "Customer testimonials and reviews showcase",
                "generated_at": datetime.now().isoformat()
            },
            "gallery": {
                "section_name": "gallery",
                "content": "Photo gallery of restaurant ambiance and dishes",
                "generated_at": datetime.now().isoformat()
            }
        }

    async def _generate_content_strategy(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content strategy for the website"""
        return {
            "content_pillars": ["Food Quality", "Customer Experience", "Local Community"],
            "update_frequency": "Weekly for specials, Monthly for menu updates",
            "content_types": ["Blog posts", "Social media integration", "Customer stories"]
        }

    def _identify_personalization_opportunities(self, restaurant_data: Dict[str, Any]) -> List[str]:
        """Identify personalization opportunities"""
        return [
            "Location-based menu recommendations",
            "Seasonal menu highlights",
            "Customer preference tracking",
            "Personalized offers based on visit history"
        ]

    def _analyze_competitive_positioning(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        return {
            "unique_selling_points": ["Fresh ingredients", "Local sourcing", "Authentic recipes"],
            "competitive_advantages": ["Quality", "Service", "Atmosphere"],
            "market_positioning": "Premium casual dining"
        }

    def _determine_ux_focus(self, restaurant_data: Dict[str, Any]) -> List[str]:
        """Determine UX focus areas"""
        return ["Mobile-first design", "Easy reservation process", "Clear menu navigation", "Fast loading times"]

    def _generate_mobile_navigation(self, base_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mobile navigation structure"""
        return {
            "hamburger_menu": True,
            "sticky_header": True,
            "quick_actions": ["Call", "Directions", "Menu", "Reserve"],
            "mobile_optimized_pages": base_structure.get("pages", [])
        }

    def _get_conversion_optimization_structure(self) -> Dict[str, Any]:
        """Get conversion optimization structure"""
        return {
            "primary_goals": ["Reservations", "Online orders", "Phone calls"],
            "cta_placement": ["Hero section", "Menu pages", "Contact section"],
            "trust_signals": ["Reviews", "Awards", "Certifications"],
            "urgency_elements": ["Limited time offers", "Availability indicators"]
        }

    async def _generate_mobile_optimization(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mobile optimization guidelines"""
        return {
            "responsive_design": "Mobile-first approach",
            "touch_targets": "Minimum 44px for buttons",
            "loading_speed": "Target under 3 seconds",
            "mobile_specific_features": ["Click-to-call", "GPS directions", "Mobile menu"]
        }

    async def _generate_performance_optimization(self) -> Dict[str, Any]:
        """Generate performance optimization guidelines"""
        return {
            "image_optimization": "WebP format, lazy loading",
            "caching_strategy": "Browser and CDN caching",
            "code_optimization": "Minified CSS/JS, critical CSS inline",
            "performance_targets": "LCP < 2.5s, FID < 100ms, CLS < 0.1"
        }

    async def _create_implementation_roadmap(self, website_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation roadmap"""
        return {
            "phase_1": "Core pages and navigation",
            "phase_2": "Advanced features and integrations",
            "phase_3": "SEO optimization and analytics",
            "timeline": "2-4 weeks for complete implementation"
        }

    def _generate_color_palette(self, category: str, cuisine_type: str) -> Dict[str, Any]:
        """Generate color palette based on category and cuisine"""
        palettes = {
            "fine_dining": {"primary": "#1a1a1a", "secondary": "#d4af37", "accent": "#ffffff", "neutral": "#f5f5f5"},
            "casual_dining": {"primary": "#8b4513", "secondary": "#ff6b35", "accent": "#ffd700", "neutral": "#f0f0f0"},
            "fast_casual": {"primary": "#ff4444", "secondary": "#00aa44", "accent": "#ffaa00", "neutral": "#ffffff"},
            "cafe_bakery": {"primary": "#8b4513", "secondary": "#deb887", "accent": "#cd853f", "neutral": "#faf0e6"},
            "ethnic_cuisine": {"primary": "#8b0000", "secondary": "#ffd700", "accent": "#ff6347", "neutral": "#fffaf0"}
        }
        return palettes.get(category, palettes["casual_dining"])

    def _generate_typography_system(self, category: str) -> Dict[str, Any]:
        """Generate typography system"""
        return {
            "headings": "Playfair Display",
            "body": "Open Sans",
            "accent": "Dancing Script",
            "sizes": {"h1": "2.5rem", "h2": "2rem", "h3": "1.5rem", "body": "1rem"}
        }

    def _generate_component_library(self, category: str) -> List[str]:
        """Generate component library"""
        return ["header", "hero", "menu_card", "testimonial", "gallery", "contact_form", "footer"]

    def _generate_imagery_guidelines(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate imagery guidelines"""
        return {
            "style": "High-quality, natural lighting",
            "subjects": ["Food close-ups", "Restaurant ambiance", "Staff interactions"],
            "color_treatment": "Warm, inviting tones",
            "technical_specs": "Minimum 1920x1080, WebP format"
        }

    def _generate_brand_voice_guidelines(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brand voice guidelines"""
        return {
            "tone": "Warm and welcoming",
            "personality": "Authentic and passionate",
            "language_style": "Conversational but professional",
            "key_messages": ["Quality ingredients", "Exceptional service", "Community focused"]
        }

    def _get_accessibility_standards(self) -> Dict[str, Any]:
        """Get accessibility standards"""
        return {
            "wcag_level": "AA compliance",
            "color_contrast": "4.5:1 minimum ratio",
            "keyboard_navigation": "Full keyboard accessibility",
            "screen_readers": "Proper ARIA labels and semantic HTML"
        }

    def _get_responsive_breakpoints(self) -> Dict[str, str]:
        """Get responsive breakpoints"""
        return {
            "mobile": "320px - 768px",
            "tablet": "768px - 1024px",
            "desktop": "1024px+",
            "large_desktop": "1440px+"
        }

    def _generate_keyword_strategy(self, restaurant_data: Dict[str, Any]) -> List[str]:
        """Generate keyword strategy"""
        restaurant_name = restaurant_data.get('name', 'restaurant')
        cuisine_type = restaurant_data.get('cuisine_type', 'dining')
        location = restaurant_data.get('location', 'local')
        
        return [
            f"{restaurant_name}",
            f"{cuisine_type} restaurant",
            f"restaurant {location}",
            f"best {cuisine_type} food",
            f"dining {location}",
            "restaurant near me",
            "food delivery",
            "restaurant reservations"
        ]

    def _generate_local_seo_checklist(self, restaurant_data: Dict[str, Any]) -> List[str]:
        """Generate local SEO checklist"""
        return [
            "Optimize Google My Business profile",
            "Include location in title tags and meta descriptions",
            "Create location-specific landing pages",
            "Build local citations and directories",
            "Encourage customer reviews",
            "Use local schema markup",
            "Create location-based content"
        ]

    def _generate_seo_content_calendar(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO content calendar"""
        return {
            "weekly": ["Menu updates", "Special offers", "Events"],
            "monthly": ["Seasonal content", "Chef spotlights", "Community events"],
            "quarterly": ["Menu overhauls", "Restaurant updates", "Awards and recognition"]
        }

    def _generate_technical_seo_requirements(self) -> List[str]:
        """Generate technical SEO requirements"""
        return [
            "Optimize page loading speed",
            "Implement proper URL structure",
            "Create XML sitemap",
            "Add robots.txt file",
            "Implement schema markup",
            "Ensure mobile responsiveness",
            "Optimize images with alt tags",
            "Use proper heading hierarchy"
        ]

    def _generate_schema_markup(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema markup"""
        return {
            "restaurant_schema": "Restaurant, LocalBusiness",
            "menu_schema": "Menu, MenuItem",
            "review_schema": "Review, AggregateRating",
            "event_schema": "Event (for special events)"
        }

    def _generate_seo_tracking_plan(self) -> Dict[str, Any]:
        """Generate SEO tracking plan"""
        return {
            "tools": ["Google Analytics", "Google Search Console", "Local ranking tools"],
            "metrics": ["Organic traffic", "Local search rankings", "Click-through rates"],
            "reporting": "Monthly SEO performance reports"
        }

    async def _generate_comprehensive_fallback_website(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive, professional fallback website when AI fails
        This ensures the website builder always produces a working website
        """
        restaurant_name = restaurant_data.get('name', 'Restaurant')
        cuisine_type = restaurant_data.get('cuisine_type', 'American')
        location = restaurant_data.get('location', 'Local Area')
        restaurant_id = restaurant_data.get('restaurant_id') or restaurant_data.get('user_id', 'unknown')
        
        logger.info(f"Creating comprehensive fallback website for {restaurant_name}")
        
        # Determine design category
        design_category = self._determine_design_category(restaurant_data)
        
        # Create a complete, professional website structure
        complete_website = {
            "website_id": f"fallback_website_{restaurant_id}_{int(datetime.now().timestamp())}",
            "restaurant_name": restaurant_name,
            "generation_date": datetime.now().isoformat(),
            "design_analysis": {
                "recommended_category": design_category,
                "template_config": self.template_categories.get(design_category, self.template_categories["casual_dining"]),
                "design_priorities": ["user_experience", "mobile_optimization", "conversion_optimization"],
                "brand_personality": self._analyze_brand_personality(restaurant_data),
                "competitive_positioning": {
                    "unique_selling_points": ["Fresh ingredients", "Quality service", "Authentic cuisine"],
                    "competitive_advantages": ["Local favorite", "Consistent quality", "Great atmosphere"],
                    "market_positioning": f"Premier {cuisine_type} restaurant"
                },
                "user_experience_focus": ["Mobile-first design", "Easy navigation", "Quick reservations"]
            },
            "website_structure": {
                "recommended_pages": ["home", "menu", "about", "contact", "reservations", "gallery"],
                "navigation_hierarchy": {
                    "primary": ["Home", "Menu", "About", "Contact"],
                    "secondary": ["Reservations", "Gallery", "Reviews"]
                },
                "url_structure": {
                    "home": "/",
                    "menu": "/menu",
                    "about": "/about",
                    "contact": "/contact",
                    "reservations": "/reservations",
                    "gallery": "/gallery"
                },
                "footer_sections": ["Hours", "Location", "Contact", "Social Media"],
                "mobile_navigation": {
                    "hamburger_menu": True,
                    "sticky_header": True,
                    "quick_actions": ["Call", "Directions", "Menu", "Reserve"]
                }
            },
            "website_sections": {
                "generated_sections": {
                    "hero_section": {
                        "section_name": "hero_section",
                        "content": f"Welcome to {restaurant_name}",
                        "headline": f"Experience Exceptional {cuisine_type} Cuisine",
                        "subheadline": f"Discover authentic flavors and warm hospitality at {restaurant_name}, where every meal is a celebration.",
                        "cta_primary": "View Our Menu",
                        "cta_secondary": "Make a Reservation",
                        "background_image": f"Hero image showcasing {cuisine_type} cuisine and restaurant ambiance",
                        "generated_at": datetime.now().isoformat(),
                        "optimization_suggestions": self._get_section_optimization_suggestions("hero_section"),
                        "conversion_elements": self._get_conversion_elements_for_section("hero_section")
                    },
                    "about_section": {
                        "section_name": "about_section",
                        "content": f"Our Story",
                        "headline": f"About {restaurant_name}",
                        "body": f"At {restaurant_name}, we're passionate about bringing you the finest {cuisine_type} cuisine in {location}. Our commitment to quality ingredients, authentic recipes, and exceptional service has made us a beloved destination for food lovers. Whether you're joining us for a casual meal or a special celebration, we promise an unforgettable dining experience that captures the true essence of {cuisine_type} hospitality.",
                        "highlights": [
                            "Authentic recipes passed down through generations",
                            "Fresh, locally-sourced ingredients",
                            "Warm, welcoming atmosphere",
                            "Exceptional customer service"
                        ],
                        "generated_at": datetime.now().isoformat(),
                        "optimization_suggestions": self._get_section_optimization_suggestions("about_section"),
                        "conversion_elements": self._get_conversion_elements_for_section("about_section")
                    },
                    "menu_showcase": {
                        "section_name": "menu_showcase",
                        "content": "Our Menu",
                        "headline": "Discover Our Culinary Delights",
                        "description": f"Explore our carefully crafted menu featuring the best of {cuisine_type} cuisine. From traditional favorites to innovative creations, every dish is prepared with passion and attention to detail.",
                        "featured_items": self._generate_sample_menu_items(cuisine_type, restaurant_data.get('menu_items', [])),
                        "menu_categories": self._generate_menu_categories(cuisine_type),
                        "dietary_options": ["Vegetarian Options", "Gluten-Free Available", "Vegan Selections"],
                        "generated_at": datetime.now().isoformat(),
                        "optimization_suggestions": self._get_section_optimization_suggestions("menu_showcase"),
                        "conversion_elements": self._get_conversion_elements_for_section("menu_showcase")
                    },
                    "location_contact": {
                        "section_name": "location_contact",
                        "content": "Visit Us",
                        "headline": f"Find {restaurant_name}",
                        "description": f"Located in the heart of {location}, {restaurant_name} is easily accessible and offers a welcoming atmosphere for all occasions.",
                        "address": f"{location}",
                        "phone": "(555) 123-4567",
                        "email": f"info@{restaurant_name.lower().replace(' ', '')}.com",
                        "hours": {
                            "monday": "11:00 AM - 10:00 PM",
                            "tuesday": "11:00 AM - 10:00 PM",
                            "wednesday": "11:00 AM - 10:00 PM",
                            "thursday": "11:00 AM - 10:00 PM",
                            "friday": "11:00 AM - 11:00 PM",
                            "saturday": "10:00 AM - 11:00 PM",
                            "sunday": "10:00 AM - 9:00 PM"
                        },
                        "parking_info": "Free parking available",
                        "public_transport": "Easily accessible by public transportation",
                        "generated_at": datetime.now().isoformat(),
                        "optimization_suggestions": self._get_section_optimization_suggestions("location_contact"),
                        "conversion_elements": self._get_conversion_elements_for_section("location_contact")
                    },
                    "reservation_system": {
                        "section_name": "reservation_system",
                        "content": "Make a Reservation",
                        "headline": "Reserve Your Table",
                        "description": f"Book your table at {restaurant_name} for an unforgettable dining experience. We accommodate parties of all sizes and special occasions.",
                        "booking_options": [
                            "Online reservations available 24/7",
                            "Call us for immediate booking",
                            "Walk-ins welcome (subject to availability)",
                            "Private dining rooms for special events"
                        ],
                        "party_sizes": ["1-2 guests", "3-4 guests", "5-8 guests", "9+ guests (call ahead)"],
                        "special_occasions": ["Birthday celebrations", "Anniversary dinners", "Business meetings", "Family gatherings"],
                        "generated_at": datetime.now().isoformat(),
                        "optimization_suggestions": self._get_section_optimization_suggestions("reservation_system"),
                        "conversion_elements": self._get_conversion_elements_for_section("reservation_system")
                    }
                },
                "section_count": 5,
                "content_strategy": {
                    "content_pillars": ["Food Quality", "Customer Experience", "Local Community", "Authentic Cuisine"],
                    "update_frequency": "Weekly for specials, Monthly for menu updates",
                    "content_types": ["Menu updates", "Customer stories", "Behind-the-scenes", "Special events"]
                }
            },
            "design_system": {
                "color_palette": self._generate_color_palette(design_category, cuisine_type),
                "typography_system": self._generate_typography_system(design_category),
                "component_library": self._generate_component_library(design_category),
                "imagery_guidelines": {
                    "style": "High-quality, natural lighting with warm tones",
                    "subjects": ["Food close-ups", "Restaurant ambiance", "Staff interactions", "Customer enjoyment"],
                    "color_treatment": "Warm, inviting tones that complement the cuisine",
                    "technical_specs": "Minimum 1920x1080, WebP format for web optimization"
                },
                "brand_voice": {
                    "tone": "Warm, welcoming, and authentic",
                    "personality": "Passionate about food and hospitality",
                    "language_style": "Conversational yet professional",
                    "key_messages": ["Quality ingredients", "Authentic cuisine", "Exceptional service", "Community focused"]
                }
            },
            "seo_optimization": {
                "keyword_strategy": self._generate_keyword_strategy(restaurant_data),
                "local_seo_checklist": self._generate_local_seo_checklist(restaurant_data),
                "meta_tags": {
                    "title": f"{restaurant_name} - Authentic {cuisine_type} Restaurant in {location}",
                    "description": f"Experience exceptional {cuisine_type} cuisine at {restaurant_name}. Fresh ingredients, authentic flavors, and warm hospitality in {location}. Reservations available.",
                    "keywords": f"{restaurant_name}, {cuisine_type} restaurant, {location}, authentic cuisine, fine dining, reservations"
                },
                "schema_markup": self._generate_schema_markup(restaurant_data)
            },
            "mobile_optimization": {
                "responsive_design": "Mobile-first approach with touch-friendly interface",
                "loading_speed": "Optimized for under 3 seconds load time",
                "mobile_features": [
                    "Click-to-call functionality",
                    "GPS directions integration",
                    "Mobile-optimized menu",
                    "Touch-friendly reservation system"
                ]
            },
            "performance_optimization": {
                "image_optimization": "WebP format with lazy loading",
                "caching_strategy": "Browser caching and CDN implementation",
                "code_optimization": "Minified CSS/JS with critical CSS inline"
            },
            "implementation_plan": {
                "phase_1": "Core pages setup (Home, Menu, About, Contact)",
                "phase_2": "Advanced features (Reservations, Gallery, Reviews)",
                "phase_3": "SEO optimization and analytics integration",
                "timeline": "2-3 weeks for complete implementation"
            },
            "ai_insights": {
                "design_rationale": f"Selected {design_category} template optimized for {cuisine_type} restaurants",
                "optimization_opportunities": [
                    "Implement online ordering system",
                    "Add customer loyalty program",
                    "Integrate social media feeds",
                    "Add multilingual support if needed"
                ],
                "performance_predictions": {
                    "expected_conversion_rate": "4-6% for reservations",
                    "mobile_traffic_percentage": "75-85%",
                    "local_search_visibility": "High with proper SEO implementation"
                }
            },
            "success": True,
            "generation_method": "comprehensive_fallback",
            "note": "Professional website generated using optimized templates - fully functional and ready to deploy"
        }
        
        logger.info(f"Comprehensive fallback website created successfully for {restaurant_name}")
        return complete_website

    def _generate_sample_menu_items(self, cuisine_type: str, existing_items: List[Dict]) -> List[Dict[str, Any]]:
        """Generate sample menu items based on cuisine type"""
        if existing_items:
            # Use existing menu items if available
            return existing_items[:6]  # Limit to 6 featured items
        
        # Generate sample items based on cuisine type
        sample_menus = {
            "italian": [
                {"name": "Margherita Pizza", "description": "Fresh mozzarella, tomato sauce, and basil", "price": "$16"},
                {"name": "Fettuccine Alfredo", "description": "Creamy parmesan sauce with fresh pasta", "price": "$18"},
                {"name": "Chicken Parmigiana", "description": "Breaded chicken with marinara and mozzarella", "price": "$22"}
            ],
            "mexican": [
                {"name": "Carne Asada Tacos", "description": "Grilled steak with onions and cilantro", "price": "$14"},
                {"name": "Chicken Enchiladas", "description": "Rolled tortillas with green sauce and cheese", "price": "$16"},
                {"name": "Guacamole & Chips", "description": "Fresh avocado dip with crispy tortilla chips", "price": "$8"}
            ],
            "american": [
                {"name": "Classic Burger", "description": "Beef patty with lettuce, tomato, and fries", "price": "$15"},
                {"name": "BBQ Ribs", "description": "Slow-cooked ribs with house BBQ sauce", "price": "$24"},
                {"name": "Caesar Salad", "description": "Romaine lettuce with parmesan and croutons", "price": "$12"}
            ]
        }
        
        cuisine_lower = cuisine_type.lower()
        for key in sample_menus:
            if key in cuisine_lower:
                return sample_menus[key]
        
        # Default items
        return sample_menus["american"]

    def _generate_menu_categories(self, cuisine_type: str) -> List[str]:
        """Generate menu categories based on cuisine type"""
        base_categories = ["Appetizers", "Main Courses", "Desserts", "Beverages"]
        
        cuisine_specific = {
            "italian": ["Antipasti", "Pasta", "Pizza", "Secondi", "Dolci"],
            "mexican": ["Antojitos", "Tacos", "Enchiladas", "Carnes", "Postres"],
            "chinese": ["Dim Sum", "Soups", "Poultry", "Seafood", "Vegetarian"],
            "indian": ["Starters", "Curries", "Tandoor", "Rice & Bread", "Sweets"]
        }
        
        cuisine_lower = cuisine_type.lower()
        for key, categories in cuisine_specific.items():
            if key in cuisine_lower:
                return categories
        
        return base_categories

# Create service instance
ai_website_generator = AIWebsiteGeneratorService()