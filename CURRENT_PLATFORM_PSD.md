# 🏗️ Restaurant Marketing Platform - Product Specification Document (PSD)

## Executive Summary

This document provides a comprehensive technical overview of the current restaurant marketing platform, detailing all existing features, architecture, APIs, and implementation details based on analysis of the codebase.

---

## 🏛️ System Architecture Overview

### **Technology Stack**
```
Frontend: React.js + JavaScript
├── UI Framework: Custom CSS with design system
├── State Management: React Context API
├── HTTP Client: Axios
└── Routing: React Router

Backend: Dual Architecture (Migration in Progress)
├── Legacy: Node.js + Express.js + SQLite
└── Current: Python FastAPI + MongoDB
    ├── Authentication: JWT tokens
    ├── Database: MongoDB with Motor (async)
    ├── API Documentation: FastAPI auto-generated
    └── External Integrations: OpenAI, Twilio, Facebook APIs
```

### **Database Architecture**
```python
# MongoDB Collections (Current System)
collections = {
    'users': 'User authentication and profiles',
    'restaurants': 'Restaurant business information',
    'checklist_categories': 'Marketing checklist categories',
    'checklist_items': 'Individual checklist tasks',
    'restaurant_checklist_status': 'Completion status per restaurant',
    'campaigns': 'Marketing campaigns (Facebook Ads, SMS)',
    'content_generation_logs': 'AI-generated content tracking'
}
```

---

## 🔐 Authentication & User Management System

### **User Roles & Permissions**
```python
class UserRole(str, Enum):
    restaurant = "restaurant"  # Restaurant owners/managers
    admin = "admin"           # Platform administrators

# Authentication Flow
class AuthenticationSystem:
    features = [
        'JWT token-based authentication',
        'Role-based access control',
        'Admin impersonation capability',
        'Secure password hashing',
        'Token expiration handling'
    ]
```

### **User Registration & Login**
- **Registration**: Email + password + restaurant details
- **Login**: Email/password with JWT token generation
- **Admin Features**: User impersonation for support
- **Security**: Password hashing, token validation, role verification

### **Technical Implementation**
```python
# Key Files:
# - backendv2/app/auth.py: Authentication logic
# - backendv2/app/routes/auth.py: Auth endpoints
# - client/src/contexts/AuthContext.js: Frontend auth state
# - client/src/components/Login.js: Login interface
```

---

## 📊 Marketing Foundations & Checklist System

### **Core Concept**
A comprehensive checklist system that guides restaurants through essential marketing tasks, tracking progress and calculating revenue impact.

### **Checklist Architecture**
```python
class ChecklistSystem:
    categories = {
        'foundational': {
            'description': 'Essential one-time setup tasks',
            'weight': 0.7,  # 70% of marketing score
            'examples': [
                'Google Business Profile optimization',
                'Website setup and optimization',
                'Social media account creation',
                'Online ordering integration'
            ]
        },
        'ongoing': {
            'description': 'Continuous marketing activities',
            'weight': 0.3,  # 30% of marketing score
            'examples': [
                'Regular social media posting',
                'Review management',
                'Email marketing campaigns',
                'Promotional activities'
            ]
        }
    }
```

### **Progress Tracking & Scoring**
```python
class MarketingScoreCalculation:
    def calculate_overall_score(self, restaurant_data):
        # Weighted scoring algorithm from MarketingFoundations.js
        foundational_weight = 0.7
        ongoing_weight = 0.3
        critical_bonus = 0.1  # Extra weight for critical items
        
        foundational_score = self.calculate_foundational_score(restaurant_data)
        ongoing_score = self.calculate_ongoing_score(restaurant_data)
        
        total_score = (foundational_score * foundational_weight) + \
                     (ongoing_score * ongoing_weight)
        
        return min(round(total_score), 100)
```

### **Revenue Impact Calculation**
```python
class RevenueImpactEngine:
    revenue_impacts = {
        'google_business_optimization': 450,  # Weekly potential
        'google_reviews_management': 320,
        'social_media_posting': 280,
        'social_media_advertising': 680,
        'online_ordering_setup': 890,
        'menu_optimization': 340,
        'email_campaigns': 380,
        'facebook_advertising': 720,
        # ... additional mappings
    }
    
    def calculate_revenue_potential(self, completed_items, total_items):
        # Maps checklist completion to revenue projections
        return self.map_items_to_revenue_categories(completed_items)
```

### **Technical Implementation**
```javascript
// Key Frontend Components:
// - client/src/components/MarketingFoundations.js: Main checklist interface
// - client/src/components/MarketingFoundations.css: Styling and animations

// Key Backend Services:
// - backendv2/app/routes/checklist.py: Checklist API endpoints
// - backendv2/app/services/checklist_service.py: Business logic
// - backendv2/app/services/dashboard_service.py: Progress calculations
```

---

## 🎯 Campaign Management System

### **Facebook Ads Integration**
```python
class FacebookAdsSystem:
    capabilities = [
        'AI-generated ad copy creation',
        'Campaign preview generation',
        'Budget validation and optimization',
        'Promo code generation',
        'Campaign performance tracking'
    ]
    
    workflow = [
        'User inputs: restaurant name, item to promote, offer, budget',
        'AI generates compelling ad copy using OpenAI',
        'System creates promo code automatically',
        'Campaign submitted to Facebook Ads API (mock implementation)',
        'Performance tracking and reporting'
    ]
```

### **SMS Campaign System**
```python
class SMSCampaignSystem:
    capabilities = [
        'Customer list CSV upload and parsing',
        'Lapsed customer identification',
        'Personalized SMS message generation',
        'Twilio integration for message delivery',
        'Campaign performance analytics'
    ]
    
    workflow = [
        'Upload customer CSV with names, phones, last order dates',
        'AI identifies lapsed customers (>30 days since last order)',
        'Generate personalized SMS messages using OpenAI',
        'Send via Twilio with delivery tracking',
        'Monitor campaign performance and ROI'
    ]
```

### **Campaign Data Models**
```python
class Campaign(BaseModel):
    campaign_id: str
    restaurant_id: str
    campaign_type: CampaignType  # facebook_ad, sms
    status: CampaignStatus       # draft, active, paused, completed
    name: str
    details: Dict                # Campaign-specific data
    budget: Optional[float]
    created_at: datetime
    launched_at: Optional[datetime]
    performance_metrics: Optional[Dict]
```

### **Technical Implementation**
```python
# Key Files:
# - backendv2/app/routes/campaigns.py: Campaign API endpoints
# - backendv2/app/services/campaign_service.py: Campaign business logic
# - backendv2/app/services/twilio_service.py: SMS delivery
# - client/src/components/GetNewCustomers.js: Facebook Ads UI
# - client/src/components/BringBackRegulars.js: SMS Campaigns UI
```

---

## 🤖 AI Content Generation System

### **OpenAI Integration**
```python
class OpenAIContentGeneration:
    models_used = "gpt-3.5-turbo, gpt-4"
    
    content_types = {
        'facebook_ad_copy': {
            'max_tokens': 300,
            'temperature': 0.8,
            'format': 'HEADLINE + BODY + CTA'
        },
        'sms_messages': {
            'max_tokens': 100,
            'temperature': 0.7,
            'constraint': '160 character limit'
        },
        'email_campaigns': {
            'max_tokens': 600,
            'temperature': 0.8,
            'format': 'SUBJECT + PREVIEW + CONTENT + CTA'
        },
        'social_media_posts': {
            'max_tokens': 300,
            'temperature': 0.8,
            'platforms': ['instagram', 'facebook', 'twitter', 'linkedin']
        },
        'menu_descriptions': {
            'max_tokens': 800,
            'temperature': 0.7,
            'focus': 'appetizing, sensory language'
        }
    }
```

### **Content Generation Workflow**
```python
class ContentGenerationWorkflow:
    def generate_content(self, content_type, restaurant_data, context):
        # 1. Build context-aware prompt
        prompt = self.build_prompt(content_type, restaurant_data, context)
        
        # 2. Call OpenAI API with appropriate parameters
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=self.get_max_tokens(content_type),
            temperature=self.get_temperature(content_type)
        )
        
        # 3. Parse and format response
        formatted_content = self.parse_response(response, content_type)
        
        # 4. Apply brand voice and constraints
        final_content = self.apply_brand_voice(formatted_content, restaurant_data)
        
        return final_content
```

### **Technical Implementation**
```python
# Key Files:
# - backendv2/app/services/openai_service.py: Core AI integration
# - backendv2/app/routes/content_generation.py: Content API endpoints
# - backendv2/app/services/mock_openai.py: Fallback mock service
```

---

## 📈 Dashboard & Analytics System

### **Restaurant Dashboard**
```python
class RestaurantDashboard:
    components = {
        'performance_snapshot': {
            'new_customers_acquired': 'Last 7 days metric',
            'customers_reengaged': 'Winback campaign results',
            'period': 'Configurable time range'
        },
        'active_campaigns': {
            'facebook_ads': 'Currently running ad campaigns',
            'sms_campaigns': 'Active SMS promotions',
            'status_tracking': 'Real-time campaign status'
        },
        'pending_tasks': {
            'incomplete_checklist_items': 'Outstanding marketing tasks',
            'priority_ordering': 'Sorted by impact and urgency',
            'quick_actions': 'One-click task completion'
        },
        'momentum_metrics': {
            'marketing_score': 'Overall marketing effectiveness (0-100)',
            'revenue_potential': 'Projected weekly revenue impact',
            'progress_tracking': 'Foundational vs ongoing completion'
        }
    }
```

### **Admin Dashboard**
```python
class AdminDashboard:
    capabilities = [
        'Platform-wide statistics',
        'Restaurant management and search',
        'User impersonation for support',
        'Campaign performance aggregation',
        'System health monitoring'
    ]
    
    metrics = {
        'total_restaurants': 'Platform user count',
        'recent_campaigns': 'Last 7 days activity',
        'incomplete_setups': 'Restaurants needing attention'
    }
```

### **Technical Implementation**
```python
# Key Files:
# - backendv2/app/routes/dashboard.py: Dashboard API endpoints
# - backendv2/app/services/dashboard_service.py: Analytics calculations
# - client/src/components/RestaurantDashboard.js: Restaurant dashboard UI
# - client/src/components/AdminDashboard.js: Admin dashboard UI
# - client/src/components/MainDashboard.js: Dashboard routing
```

---

## 🔌 External API Integrations

### **Current Integrations**
```python
class ExternalAPIs:
    openai = {
        'purpose': 'AI content generation',
        'models': ['gpt-3.5-turbo', 'gpt-4'],
        'fallback': 'Mock service when API unavailable'
    }
    
    twilio = {
        'purpose': 'SMS campaign delivery',
        'features': ['Message sending', 'Delivery tracking', 'Phone validation'],
        'fallback': 'Mock service for development'
    }
    
    facebook_marketing = {
        'purpose': 'Facebook Ads campaign management',
        'status': 'Mock implementation (ready for real API)',
        'features': ['Campaign creation', 'Performance tracking']
    }
```

### **Mock Services (Development)**
```python
class MockServices:
    # Provide realistic responses for development/testing
    services = [
        'mock_openai.py: Simulated AI responses',
        'mock_twilio.py: Simulated SMS delivery',
        'mock_facebook.py: Simulated ad campaign creation'
    ]
```

---

## 🎨 User Interface & Design System

### **Design Architecture**
```css
/* Design System Components */
.design-system {
    color-scheme: {
        primary: '#3b82f6',      /* Blue */
        secondary: '#6c757d',    /* Gray */
        success: '#28a745',      /* Green */
        warning: '#ffc107',      /* Yellow */
        danger: '#dc3545'        /* Red */
    }
    
    typography: {
        font-family: 'Arial, sans-serif',
        heading-sizes: ['2rem', '1.5rem', '1.25rem'],
        body-size: '1rem'
    }
    
    components: {
        glass-cards: 'Translucent card design',
        progress-bars: 'Animated progress indicators',
        circular-progress: 'SVG-based circular progress',
        buttons: 'Consistent button styling',
        forms: 'Standardized form elements'
    }
}
```

### **Key UI Components**
```javascript
// Core Components:
const UIComponents = {
    'MarketingFoundations': 'Main checklist interface with progress tracking',
    'RestaurantDashboard': 'Performance metrics and campaign overview',
    'AdminDashboard': 'Platform management interface',
    'GetNewCustomers': 'Facebook Ads campaign creation',
    'BringBackRegulars': 'SMS campaign management',
    'Login': 'Authentication interface',
    'Navigation': 'App navigation and user menu'
}
```

### **Responsive Design**
- Mobile-first approach with responsive breakpoints
- Touch-friendly interface elements
- Optimized for restaurant owners using mobile devices
- Progressive web app capabilities

---

## 🔄 Data Flow & State Management

### **Frontend State Management**
```javascript
class StateManagement {
    context_providers = {
        'AuthContext': 'User authentication state',
        'RestaurantContext': 'Restaurant-specific data',
        'CampaignContext': 'Campaign management state'
    }
    
    api_layer = {
        'api.js': 'Centralized API client with interceptors',
        'endpoints': {
            'auth': 'Authentication operations',
            'dashboard': 'Dashboard data fetching',
            'checklist': 'Checklist management',
            'campaigns': 'Campaign operations',
            'content': 'AI content generation'
        }
    }
}
```

### **Backend Data Processing**
```python
class DataProcessingFlow:
    request_flow = [
        'API endpoint receives request',
        'Authentication middleware validates JWT',
        'Route handler processes business logic',
        'Service layer interacts with database',
        'External APIs called if needed',
        'Response formatted and returned'
    ]
    
    database_operations = [
        'MongoDB queries with Motor (async)',
        'Data validation with Pydantic models',
        'Error handling and logging',
        'Performance optimization with indexing'
    ]
```

---

## 🚀 Deployment & Infrastructure

### **Current Deployment Setup**
```yaml
# Development Environment
frontend:
  command: "npm start"
  port: 3000
  hot_reload: true

backend_legacy:
  command: "node index.js"
  port: 5000
  database: "SQLite (local)"

backend_current:
  command: "python3.9 run.py"
  port: 8000
  database: "MongoDB Atlas"
  environment: "Development"
```

### **Environment Configuration**
```python
# Environment Variables Required
required_env_vars = [
    'MONGODB_URI',           # Database connection
    'JWT_SECRET_KEY',        # Authentication
    'OPENAI_API_KEY',        # AI content generation
    'TWILIO_ACCOUNT_SID',    # SMS functionality
    'TWILIO_AUTH_TOKEN',     # SMS authentication
    'TWILIO_PHONE_NUMBER'    # SMS sender number
]
```

---

## 📊 Performance & Scalability

### **Current Performance Characteristics**
```python
class PerformanceMetrics:
    api_response_times = {
        'authentication': '< 200ms',
        'dashboard_load': '< 1s',
        'checklist_update': '< 500ms',
        'content_generation': '< 5s (OpenAI dependent)',
        'campaign_creation': '< 3s'
    }
    
    database_performance = {
        'mongodb_queries': 'Optimized with indexes',
        'connection_pooling': 'Motor async driver',
        'caching_strategy': 'In-memory for frequent queries'
    }
    
    scalability_considerations = [
        'Async/await pattern for non-blocking operations',
        'MongoDB horizontal scaling capability',
        'Stateless API design for load balancing',
        'External API rate limiting handling'
    ]
```

---

## 🔧 Development & Testing

### **Code Organization**
```
Project Structure:
├── client/                 # React frontend
│   ├── src/components/     # UI components
│   ├── src/services/       # API integration
│   ├── src/contexts/       # State management
│   └── src/styles/         # Design system
├── backendv2/              # Python FastAPI backend
│   ├── app/routes/         # API endpoints
│   ├── app/services/       # Business logic
│   ├── app/models.py       # Data models
│   └── app/database.py     # Database configuration
└── server/                 # Legacy Node.js backend
    ├── routes/             # API routes
    ├── services/           # External integrations
    └── models/             # Database models
```

### **Testing Infrastructure**
```python
# Testing Files Present:
testing_files = [
    'backendv2/test_dashboard.py',
    'backendv2/test_campaigns.py',
    'backendv2/test_openai_integration.py',
    'backendv2/test_twilio_integration.py'
]

# Testing Approach:
testing_strategy = {
    'unit_tests': 'Individual component testing',
    'integration_tests': 'API endpoint testing',
    'mock_services': 'External API simulation',
    'manual_testing': 'UI and workflow validation'
}
```

---

## 🔒 Security & Compliance

### **Security Measures**
```python
class SecurityImplementation:
    authentication = [
        'JWT token-based authentication',
        'Password hashing with secure algorithms',
        'Token expiration and refresh handling',
        'Role-based access control'
    ]
    
    api_security = [
        'CORS configuration',
        'Request validation with Pydantic',
        'SQL injection prevention (NoSQL)',
        'Rate limiting considerations'
    ]
    
    data_protection = [
        'Environment variable configuration',
        'Secure API key management',
        'Database connection encryption',
        'User data privacy compliance'
    ]
```

---

## 📋 Current System Limitations

### **Known Technical Debt**
```python
class TechnicalLimitations:
    architecture = [
        'Dual backend system (migration in progress)',
        'Limited error handling in some components',
        'Mock implementations for some external APIs',
        'Basic caching strategy'
    ]
    
    scalability = [
        'Single-instance deployment',
        'Limited monitoring and logging',
        'No automated backup strategy',
        'Basic performance optimization'
    ]
    
    features = [
        'Limited analytics and reporting',
        'Basic content generation (no context awareness)',
        'Simple campaign management',
        'Manual content scheduling'
    ]
```

### **Integration Gaps**
```python
class IntegrationGaps:
    missing_integrations = [
        'POS system connections',
        'Inventory management systems',
        'Advanced social media APIs',
        'Email marketing platforms',
        'Analytics and tracking tools'
    ]
```

---

## 🎯 System Strengths

### **Current Competitive Advantages**
```python
class PlatformStrengths:
    core_features = [
        'Comprehensive marketing checklist system',
        'AI-powered content generation',
        'Multi-channel campaign management',
        'Revenue impact tracking',
        'User-friendly interface design'
    ]
    
    technical_strengths = [
        'Modern tech stack (React + FastAPI)',
        'Scalable database architecture (MongoDB)',
        'Async/await performance optimization',
        'Modular, maintainable codebase',
        'Comprehensive API documentation'
    ]
    
    business_value = [
        'Actionable marketing guidance for restaurants',
        'Automated content creation capabilities',
        'Progress tracking with revenue projections',
        'Multi-tenant architecture ready for scale',
        'Admin tools for platform management'
    ]
```

---

## 📈 Usage Analytics & Metrics

### **Current Tracking Capabilities**
```python
class AnalyticsCapabilities:
    user_metrics = [
        'Checklist completion rates',
        'Campaign creation frequency',
        'Content generation usage',
        'Dashboard engagement patterns'
    ]
    
    business_metrics = [
        'Revenue impact calculations',
        'Marketing score improvements',
        'Campaign performance tracking',
        'User retention and engagement'
    ]
    
    technical_metrics = [
        'API response times',
        'Error rates and debugging',
        'External API usage and costs',
        'Database performance monitoring'
    ]
```

---

This Product Specification Document provides a comprehensive technical overview of the current restaurant marketing platform, detailing all implemented features, architecture decisions, and technical capabilities as of the current development state.