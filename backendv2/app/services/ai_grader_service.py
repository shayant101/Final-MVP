"""
AI Digital Presence Grader Service
Analyzes restaurant's digital presence and provides actionable recommendations
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from .openai_service import openai_service

logger = logging.getLogger(__name__)

class AIGraderService:
    def __init__(self):
        self.openai_service = openai_service
        
    async def analyze_digital_presence(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze restaurant's digital presence and generate comprehensive grade
        """
        try:
            # Extract restaurant information
            restaurant_name = restaurant_data.get('name', 'Restaurant')
            website_url = restaurant_data.get('website', '')
            social_media = restaurant_data.get('social_media', {})
            google_business = restaurant_data.get('google_business', {})
            menu_items = restaurant_data.get('menu_items', [])
            current_marketing = restaurant_data.get('current_marketing', {})
            
            # Analyze each component
            website_analysis = await self._analyze_website(restaurant_name, website_url)
            social_analysis = await self._analyze_social_media(restaurant_name, social_media)
            google_analysis = await self._analyze_google_business(restaurant_name, google_business)
            menu_analysis = await self._analyze_menu_optimization(restaurant_name, menu_items)
            marketing_analysis = await self._analyze_marketing_strategy(restaurant_name, current_marketing)
            
            # Calculate overall grade and recommendations
            overall_grade = await self._calculate_overall_grade({
                'website': website_analysis,
                'social': social_analysis,
                'google': google_analysis,
                'menu': menu_analysis,
                'marketing': marketing_analysis
            })
            
            # Generate priority action plan
            action_plan = await self._generate_action_plan(overall_grade, {
                'website': website_analysis,
                'social': social_analysis,
                'google': google_analysis,
                'menu': menu_analysis,
                'marketing': marketing_analysis
            })
            
            return {
                "success": True,
                "overall_grade": overall_grade,
                "component_scores": {
                    "website": website_analysis,
                    "social_media": social_analysis,
                    "google_business": google_analysis,
                    "menu_optimization": menu_analysis,
                    "marketing_strategy": marketing_analysis
                },
                "action_plan": action_plan,
                "revenue_impact": self._calculate_revenue_impact(overall_grade),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze digital presence: {str(e)}")
            return await self._generate_mock_analysis(restaurant_data)
    
    async def _analyze_website(self, restaurant_name: str, website_url: str) -> Dict[str, Any]:
        """Analyze website presence and optimization"""
        try:
            if not website_url:
                return {
                    "score": 20,
                    "grade": "F",
                    "issues": ["No website URL provided"],
                    "recommendations": [
                        "Create a professional restaurant website",
                        "Include menu, hours, location, and contact info",
                        "Optimize for mobile devices",
                        "Add online ordering capability"
                    ],
                    "priority": "HIGH"
                }
            
            # Mock website analysis (in real implementation, would crawl website)
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant digital marketing expert. Analyze the website information provided and give a score from 0-100 with specific recommendations.
                    
                    Consider:
                    - Mobile optimization
                    - Menu accessibility
                    - Contact information clarity
                    - Online ordering integration
                    - SEO optimization
                    - Loading speed
                    - Visual appeal
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze website for {restaurant_name} at {website_url}. Provide detailed assessment and recommendations."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Website analysis failed: {str(e)}")
            return self._get_fallback_website_analysis()
    
    async def _analyze_social_media(self, restaurant_name: str, social_media: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social media presence"""
        try:
            platforms = social_media.keys() if social_media else []
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a social media marketing expert for restaurants. Analyze the social media presence and provide actionable recommendations.
                    
                    Consider:
                    - Platform coverage (Instagram, Facebook, TikTok, etc.)
                    - Content quality and frequency
                    - Engagement rates
                    - Visual consistency
                    - Local community engagement
                    - User-generated content
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze social media presence for {restaurant_name}. Current platforms: {', '.join(platforms) if platforms else 'None'}. Provide detailed assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Social media analysis failed: {str(e)}")
            return self._get_fallback_social_analysis()
    
    async def _analyze_google_business(self, restaurant_name: str, google_business: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Google Business Profile optimization"""
        try:
            has_profile = google_business.get('verified', False)
            reviews_count = google_business.get('reviews_count', 0)
            avg_rating = google_business.get('avg_rating', 0)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a local SEO expert for restaurants. Analyze Google Business Profile optimization and provide recommendations.
                    
                    Consider:
                    - Profile completeness
                    - Review quantity and quality
                    - Photo quality and quantity
                    - Business information accuracy
                    - Response to reviews
                    - Local SEO optimization
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze Google Business Profile for {restaurant_name}. Verified: {has_profile}, Reviews: {reviews_count}, Rating: {avg_rating}/5. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Google Business analysis failed: {str(e)}")
            return self._get_fallback_google_analysis()
    
    async def _analyze_menu_optimization(self, restaurant_name: str, menu_items: List[Dict]) -> Dict[str, Any]:
        """Analyze menu optimization for digital marketing"""
        try:
            menu_count = len(menu_items)
            has_descriptions = any(item.get('description') for item in menu_items)
            has_photos = any(item.get('photo') for item in menu_items)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant menu optimization expert. Analyze menu digital readiness and marketing potential.
                    
                    Consider:
                    - Item descriptions quality
                    - Photo availability and quality
                    - Pricing strategy
                    - Menu organization
                    - Promotional opportunities
                    - Dietary information
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze menu optimization for {restaurant_name}. Items: {menu_count}, Has descriptions: {has_descriptions}, Has photos: {has_photos}. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Menu analysis failed: {str(e)}")
            return self._get_fallback_menu_analysis()
    
    async def _analyze_marketing_strategy(self, restaurant_name: str, current_marketing: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current marketing strategy effectiveness"""
        try:
            active_campaigns = current_marketing.get('active_campaigns', [])
            marketing_budget = current_marketing.get('monthly_budget', 0)
            target_audience = current_marketing.get('target_audience', 'general')
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a restaurant marketing strategist. Analyze current marketing approach and provide strategic recommendations.
                    
                    Consider:
                    - Campaign diversity and effectiveness
                    - Budget allocation
                    - Target audience definition
                    - Marketing channel mix
                    - ROI tracking
                    - Seasonal strategies
                    
                    Format response as:
                    SCORE: [0-100]
                    GRADE: [A-F]
                    ISSUES: [list of issues]
                    RECOMMENDATIONS: [list of recommendations]
                    PRIORITY: [HIGH/MEDIUM/LOW]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze marketing strategy for {restaurant_name}. Active campaigns: {len(active_campaigns)}, Budget: ${marketing_budget}/month, Target: {target_audience}. Provide assessment."
                }
            ]
            
            response = await self.openai_service._make_openai_request(messages, max_tokens=400)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Marketing analysis failed: {str(e)}")
            return self._get_fallback_marketing_analysis()
    
    async def _calculate_overall_grade(self, component_scores: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate overall digital presence grade"""
        try:
            # Weight different components
            weights = {
                'website': 0.25,
                'social': 0.20,
                'google': 0.25,
                'menu': 0.15,
                'marketing': 0.15
            }
            
            total_score = 0
            for component, weight in weights.items():
                score = component_scores.get(component, {}).get('score', 0)
                total_score += score * weight
            
            # Convert to letter grade
            if total_score >= 90:
                letter_grade = 'A'
                status = 'Excellent'
            elif total_score >= 80:
                letter_grade = 'B'
                status = 'Good'
            elif total_score >= 70:
                letter_grade = 'C'
                status = 'Average'
            elif total_score >= 60:
                letter_grade = 'D'
                status = 'Below Average'
            else:
                letter_grade = 'F'
                status = 'Needs Improvement'
            
            return {
                "score": round(total_score, 1),
                "letter_grade": letter_grade,
                "status": status,
                "improvement_potential": round(100 - total_score, 1)
            }
            
        except Exception as e:
            logger.error(f"Grade calculation failed: {str(e)}")
            return {
                "score": 65.0,
                "letter_grade": "D",
                "status": "Needs Assessment",
                "improvement_potential": 35.0
            }
    
    async def _generate_action_plan(self, overall_grade: Dict, component_scores: Dict) -> Dict[str, Any]:
        """Generate prioritized action plan"""
        try:
            # Collect all high-priority recommendations
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for component, analysis in component_scores.items():
                priority = analysis.get('priority', 'MEDIUM')
                recommendations = analysis.get('recommendations', [])
                
                for rec in recommendations:
                    item = {
                        "action": rec,
                        "component": component,
                        "estimated_impact": self._estimate_impact(component, rec),
                        "effort_level": self._estimate_effort(rec)
                    }
                    
                    if priority == 'HIGH':
                        high_priority.append(item)
                    elif priority == 'MEDIUM':
                        medium_priority.append(item)
                    else:
                        low_priority.append(item)
            
            return {
                "immediate_actions": high_priority[:3],  # Top 3 high priority
                "short_term_goals": medium_priority[:5],  # Top 5 medium priority
                "long_term_improvements": low_priority[:3],  # Top 3 low priority
                "estimated_timeline": "2-8 weeks for immediate actions",
                "success_metrics": [
                    "Increase in online visibility",
                    "Higher customer engagement",
                    "Improved review ratings",
                    "More online orders/reservations"
                ]
            }
            
        except Exception as e:
            logger.error(f"Action plan generation failed: {str(e)}")
            return self._get_fallback_action_plan()
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            lines = response.split('\n')
            result = {
                "score": 70,
                "grade": "C",
                "issues": [],
                "recommendations": [],
                "priority": "MEDIUM"
            }
            
            for line in lines:
                if line.startswith("SCORE:"):
                    try:
                        result["score"] = int(line.replace("SCORE:", "").strip())
                    except:
                        pass
                elif line.startswith("GRADE:"):
                    result["grade"] = line.replace("GRADE:", "").strip()
                elif line.startswith("ISSUES:"):
                    issues_text = line.replace("ISSUES:", "").strip()
                    result["issues"] = [issue.strip() for issue in issues_text.split(',') if issue.strip()]
                elif line.startswith("RECOMMENDATIONS:"):
                    rec_text = line.replace("RECOMMENDATIONS:", "").strip()
                    result["recommendations"] = [rec.strip() for rec in rec_text.split(',') if rec.strip()]
                elif line.startswith("PRIORITY:"):
                    result["priority"] = line.replace("PRIORITY:", "").strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            return {
                "score": 65,
                "grade": "D",
                "issues": ["Analysis parsing error"],
                "recommendations": ["Review digital presence manually"],
                "priority": "MEDIUM"
            }
    
    def _calculate_revenue_impact(self, overall_grade: Dict) -> Dict[str, Any]:
        """Calculate potential revenue impact of improvements"""
        current_score = overall_grade.get('score', 65)
        improvement_potential = overall_grade.get('improvement_potential', 35)
        
        # Estimate revenue impact based on digital presence improvements
        monthly_impact_low = improvement_potential * 25  # $25 per point improvement (conservative)
        monthly_impact_high = improvement_potential * 75  # $75 per point improvement (optimistic)
        
        return {
            "monthly_revenue_increase": {
                "low_estimate": f"${monthly_impact_low:,.0f}",
                "high_estimate": f"${monthly_impact_high:,.0f}"
            },
            "annual_potential": {
                "low_estimate": f"${monthly_impact_low * 12:,.0f}",
                "high_estimate": f"${monthly_impact_high * 12:,.0f}"
            },
            "improvement_areas": [
                "Increased online visibility",
                "Better customer engagement",
                "Higher conversion rates",
                "Improved customer retention"
            ]
        }
    
    def _estimate_impact(self, component: str, recommendation: str) -> str:
        """Estimate impact level of a recommendation"""
        high_impact_keywords = ['website', 'google', 'reviews', 'seo', 'online ordering']
        medium_impact_keywords = ['social media', 'content', 'photos', 'menu']
        
        rec_lower = recommendation.lower()
        
        if any(keyword in rec_lower for keyword in high_impact_keywords):
            return "HIGH"
        elif any(keyword in rec_lower for keyword in medium_impact_keywords):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_effort(self, recommendation: str) -> str:
        """Estimate effort level required for a recommendation"""
        high_effort_keywords = ['create', 'build', 'develop', 'redesign', 'implement']
        low_effort_keywords = ['update', 'add', 'optimize', 'improve', 'respond']
        
        rec_lower = recommendation.lower()
        
        if any(keyword in rec_lower for keyword in high_effort_keywords):
            return "HIGH"
        elif any(keyword in rec_lower for keyword in low_effort_keywords):
            return "LOW"
        else:
            return "MEDIUM"
    
    # Fallback methods for when AI analysis fails
    async def _generate_mock_analysis(self, restaurant_data: Dict) -> Dict[str, Any]:
        """Generate mock analysis when AI fails"""
        return {
            "success": True,
            "overall_grade": {
                "score": 68.5,
                "letter_grade": "D+",
                "status": "Needs Improvement",
                "improvement_potential": 31.5
            },
            "component_scores": {
                "website": self._get_fallback_website_analysis(),
                "social_media": self._get_fallback_social_analysis(),
                "google_business": self._get_fallback_google_analysis(),
                "menu_optimization": self._get_fallback_menu_analysis(),
                "marketing_strategy": self._get_fallback_marketing_analysis()
            },
            "action_plan": self._get_fallback_action_plan(),
            "revenue_impact": {
                "monthly_revenue_increase": {
                    "low_estimate": "$785",
                    "high_estimate": "$2,365"
                },
                "annual_potential": {
                    "low_estimate": "$9,420",
                    "high_estimate": "$28,380"
                }
            },
            "generated_at": datetime.now().isoformat(),
            "note": "Mock analysis - AI service unavailable"
        }
    
    def _get_fallback_website_analysis(self) -> Dict[str, Any]:
        return {
            "score": 65,
            "grade": "D",
            "issues": ["Mobile optimization needed", "Missing online ordering"],
            "recommendations": ["Optimize for mobile", "Add online ordering", "Improve loading speed"],
            "priority": "HIGH"
        }
    
    def _get_fallback_social_analysis(self) -> Dict[str, Any]:
        return {
            "score": 70,
            "grade": "C",
            "issues": ["Inconsistent posting", "Low engagement"],
            "recommendations": ["Post daily content", "Engage with followers", "Use local hashtags"],
            "priority": "MEDIUM"
        }
    
    def _get_fallback_google_analysis(self) -> Dict[str, Any]:
        return {
            "score": 75,
            "grade": "C+",
            "issues": ["Need more reviews", "Missing photos"],
            "recommendations": ["Request customer reviews", "Add high-quality photos", "Update business hours"],
            "priority": "HIGH"
        }
    
    def _get_fallback_menu_analysis(self) -> Dict[str, Any]:
        return {
            "score": 60,
            "grade": "D-",
            "issues": ["Missing item descriptions", "No photos"],
            "recommendations": ["Add appetizing descriptions", "Include food photos", "Highlight specials"],
            "priority": "MEDIUM"
        }
    
    def _get_fallback_marketing_analysis(self) -> Dict[str, Any]:
        return {
            "score": 55,
            "grade": "F",
            "issues": ["No clear strategy", "Limited channels"],
            "recommendations": ["Define target audience", "Create marketing calendar", "Track ROI"],
            "priority": "HIGH"
        }
    
    def _get_fallback_action_plan(self) -> Dict[str, Any]:
        return {
            "immediate_actions": [
                {
                    "action": "Optimize Google Business Profile",
                    "component": "google_business",
                    "estimated_impact": "HIGH",
                    "effort_level": "LOW"
                },
                {
                    "action": "Create mobile-friendly website",
                    "component": "website",
                    "estimated_impact": "HIGH",
                    "effort_level": "HIGH"
                },
                {
                    "action": "Start daily social media posting",
                    "component": "social_media",
                    "estimated_impact": "MEDIUM",
                    "effort_level": "LOW"
                }
            ],
            "short_term_goals": [
                {
                    "action": "Add menu item photos and descriptions",
                    "component": "menu_optimization",
                    "estimated_impact": "MEDIUM",
                    "effort_level": "MEDIUM"
                },
                {
                    "action": "Implement customer review strategy",
                    "component": "google_business",
                    "estimated_impact": "HIGH",
                    "effort_level": "LOW"
                }
            ],
            "long_term_improvements": [
                {
                    "action": "Develop comprehensive marketing strategy",
                    "component": "marketing_strategy",
                    "estimated_impact": "HIGH",
                    "effort_level": "HIGH"
                }
            ],
            "estimated_timeline": "2-8 weeks for immediate actions",
            "success_metrics": [
                "Increase in online visibility",
                "Higher customer engagement",
                "Improved review ratings",
                "More online orders/reservations"
            ]
        }

# Create service instance
ai_grader_service = AIGraderService()