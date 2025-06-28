# 🚀 AI Features MVP - Weekend Implementation Plan

## Executive Summary

This document outlines a weekend-implementable MVP that showcases the full potential of our comprehensive AI strategy. The MVP focuses on demonstrating core AI capabilities with mock data and simplified integrations while building the foundation for the full implementation.

**Goal**: Create a compelling demo that highlights what the full AI platform will be capable of, implementable in 2-3 days.

---

## 🎯 MVP Objectives

### **Primary Goals**
1. **Demonstrate AI Capabilities**: Show the power of AI-driven restaurant marketing
2. **Validate User Experience**: Test core workflows and user interactions
3. **Showcase Vision**: Illustrate the full potential of the comprehensive plan
4. **Build Foundation**: Create reusable components for full implementation
5. **Generate Excitement**: Create compelling demo for stakeholders and users

### **Success Criteria**
- [ ] Working AI features with realistic mock data
- [ ] Smooth user experience across all MVP features
- [ ] Clear demonstration of value proposition
- [ ] Foundation for full implementation
- [ ] Compelling demo-ready platform

---

## 🏗️ MVP Architecture Overview

### **Technical Approach**
```
Frontend: React components with mock data integration
Backend: Enhanced OpenAI service with mock external APIs
Database: Minimal schema additions for MVP data
AI Integration: OpenAI GPT-4 for real content generation
External APIs: Mock services with realistic responses
```

### **MVP Features (4 Core Features)**
1. **AI Content Generator Pro** (Enhanced existing feature)
2. **Smart Task Recommender** (New AI-powered recommendations)
3. **Digital Presence Analyzer** (Mock comprehensive analysis)
4. **AI Marketing Assistant** (Basic conversational interface)

---

## 📋 Day 1: Backend AI Services & Mock Data

### **Morning (4 hours): Enhanced AI Content Generation**

#### **Task 1.1: Upgrade OpenAI Service (2 hours)**
**File**: `backendv2/app/services/openai_service.py`

```python
# Add new methods to existing OpenAIService class
class OpenAIService:
    # ... existing methods ...
    
    async def generate_multi_channel_content(self, restaurant_data, campaign_type, context=None):
        """Generate content for multiple channels simultaneously"""
        channels = ['social_media', 'email', 'sms', 'ads']
        content = {}
        
        for channel in channels:
            content[channel] = await self.generate_channel_specific_content(
                restaurant_data, campaign_type, channel, context
            )
        
        return {
            'success': True,
            'multi_channel_content': content,
            'campaign_strategy': self.suggest_campaign_strategy(campaign_type),
            'estimated_reach': self.calculate_estimated_reach(restaurant_data),
            'generated_at': datetime.now().isoformat()
        }
    
    async def generate_channel_specific_content(self, restaurant_data, campaign_type, channel, context):
        """Generate content optimized for specific channel"""
        # Channel-specific prompts and constraints
        channel_specs = {
            'social_media': {'max_length': 280, 'hashtags': True, 'emojis': True},
            'email': {'subject_line': True, 'preview_text': True, 'html_format': True},
            'sms': {'max_length': 160, 'personalization': True, 'urgency': True},
            'ads': {'headline': True, 'description': True, 'cta': True}
        }
        
        # Generate content with OpenAI
        prompt = self.build_channel_prompt(restaurant_data, campaign_type, channel, context)
        response = await self._make_openai_request([
            {"role": "system", "content": self.get_channel_system_prompt(channel)},
            {"role": "user", "content": prompt}
        ])
        
        return self.format_channel_content(response, channel, channel_specs[channel])
```

#### **Task 1.2: Smart Task Recommender Service (2 hours)**
**File**: `backendv2/app/services/task_recommender.py` (New)

```python
class SmartTaskRecommender:
    def __init__(self):
        self.openai_service = openai_service
        
    async def get_next_best_task(self, restaurant_id, user_context):
        """AI-powered next task recommendation"""
        
        # Get restaurant data and completion status
        restaurant_data = await self.get_restaurant_context(restaurant_id)
        completion_data = await self.get_completion_context(restaurant_id)
        
        # Generate AI recommendation
        recommendation = await self.generate_task_recommendation(
            restaurant_data, completion_data, user_context
        )
        
        return {
            'success': True,
            'recommended_task': recommendation['task'],
            'reasoning': recommendation['reasoning'],
            'impact_score': recommendation['impact_score'],
            'estimated_time': recommendation['estimated_time'],
            'revenue_potential': recommendation['revenue_potential'],
            'priority_level': recommendation['priority_level']
        }
    
    async def generate_task_recommendation(self, restaurant_data, completion_data, context):
        """Use AI to analyze and recommend next best task"""
        
        prompt = f"""
        Analyze this restaurant's marketing progress and recommend the next best task:
        
        Restaurant: {restaurant_data['name']}
        Marketing Score: {completion_data['marketing_score']}/100
        Completed Tasks: {len(completion_data['completed_tasks'])}
        Pending Critical Tasks: {len(completion_data['critical_pending'])}
        
        Recent Activity: {context.get('recent_activity', 'None')}
        Business Goals: {context.get('goals', 'Increase revenue and customers')}
        
        Recommend the single most impactful next task with clear reasoning.
        """
        
        response = await self.openai_service._make_openai_request([
            {"role": "system", "content": "You are an expert restaurant marketing strategist. Provide specific, actionable task recommendations with clear business reasoning."},
            {"role": "user", "content": prompt}
        ])
        
        return self.parse_recommendation_response(response)
```

### **Afternoon (4 hours): Mock External Services**

#### **Task 1.3: Digital Presence Analyzer (Mock) (2 hours)**
**File**: `backendv2/app/services/mock_digital_analyzer.py` (New)

```python
class MockDigitalPresenceAnalyzer:
    """Mock service that simulates comprehensive digital presence analysis"""
    
    def __init__(self):
        self.analysis_templates = self.load_analysis_templates()
    
    async def analyze_digital_presence(self, restaurant_inputs):
        """Simulate comprehensive digital analysis with realistic results"""
        
        # Simulate analysis delay
        await asyncio.sleep(2)  # Realistic processing time
        
        # Generate realistic scores based on inputs
        scores = self.generate_realistic_scores(restaurant_inputs)
        recommendations = self.generate_recommendations(scores, restaurant_inputs)
        
        return {
            'success': True,
            'overall_grade': scores['overall'],
            'category_scores': {
                'google_business': scores['google_business'],
                'website': scores['website'],
                'social_media': scores['social_media'],
                'delivery_platforms': scores['delivery_platforms'],
                'review_management': scores['review_management']
            },
            'recommendations': recommendations,
            'revenue_impact_estimate': self.calculate_revenue_impact(scores),
            'analysis_details': self.generate_detailed_analysis(restaurant_inputs),
            'generated_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    def generate_realistic_scores(self, inputs):
        """Generate realistic scores based on provided URLs and data"""
        base_scores = {
            'google_business': random.randint(45, 85),
            'website': random.randint(40, 90),
            'social_media': random.randint(35, 80),
            'delivery_platforms': random.randint(50, 85),
            'review_management': random.randint(40, 75)
        }
        
        # Adjust scores based on provided inputs
        if inputs.get('google_business_url'):
            base_scores['google_business'] += 10
        if inputs.get('website_url'):
            base_scores['website'] += 15
        if inputs.get('instagram_handle'):
            base_scores['social_media'] += 20
            
        # Calculate overall score
        weights = {'google_business': 0.3, 'website': 0.25, 'social_media': 0.2, 
                  'delivery_platforms': 0.15, 'review_management': 0.1}
        
        overall = sum(base_scores[key] * weights[key] for key in base_scores)
        base_scores['overall'] = round(overall)
        
        return base_scores
    
    def generate_recommendations(self, scores, inputs):
        """Generate actionable recommendations based on scores"""
        recommendations = []
        
        for category, score in scores.items():
            if category == 'overall':
                continue
                
            if score < 60:
                recommendations.extend(self.get_improvement_recommendations(category, score))
            elif score < 80:
                recommendations.extend(self.get_optimization_recommendations(category, score))
        
        # Sort by impact and return top 5
        return sorted(recommendations, key=lambda x: x['impact_score'], reverse=True)[:5]
```

#### **Task 1.4: Basic AI Assistant Backend (2 hours)**
**File**: `backendv2/app/services/ai_assistant.py` (New)

```python
class BasicAIAssistant:
    """Basic conversational AI for restaurant marketing assistance"""
    
    def __init__(self):
        self.openai_service = openai_service
        self.task_recommender = SmartTaskRecommender()
        self.content_generator = openai_service
        
    async def process_message(self, user_message, restaurant_id, conversation_context):
        """Process user message and generate appropriate response"""
        
        # Classify intent
        intent = await self.classify_intent(user_message)
        
        # Route to appropriate handler
        if intent == 'content_generation':
            return await self.handle_content_request(user_message, restaurant_id)
        elif intent == 'task_recommendation':
            return await self.handle_task_request(user_message, restaurant_id)
        elif intent == 'performance_analysis':
            return await self.handle_analysis_request(user_message, restaurant_id)
        elif intent == 'general_marketing':
            return await self.handle_general_marketing(user_message, restaurant_id)
        else:
            return await self.handle_general_query(user_message, restaurant_id)
    
    async def classify_intent(self, message):
        """Classify user intent using OpenAI"""
        prompt = f"""
        Classify the intent of this restaurant marketing message:
        "{message}"
        
        Possible intents:
        - content_generation: User wants to create marketing content
        - task_recommendation: User wants task suggestions
        - performance_analysis: User wants to know how they're doing
        - general_marketing: General marketing questions
        - other: Everything else
        
        Respond with just the intent name.
        """
        
        response = await self.openai_service._make_openai_request([
            {"role": "system", "content": "You are an intent classifier. Respond with only the intent name."},
            {"role": "user", "content": prompt}
        ])
        
        return response.strip().lower()
    
    async def handle_content_request(self, message, restaurant_id):
        """Handle content generation requests"""
        # Extract content type and details from message
        content_details = await self.extract_content_details(message)
        
        # Generate content
        content = await self.content_generator.generate_multi_channel_content(
            await self.get_restaurant_data(restaurant_id),
            content_details['campaign_type'],
            content_details.get('context')
        )
        
        return {
            'type': 'content_generation',
            'message': f"I've generated marketing content for your {content_details['campaign_type']} campaign!",
            'content': content,
            'actions': ['review_content', 'edit_content', 'schedule_content']
        }
```

---

## 📋 Day 2: Frontend Components & Integration

### **Morning (4 hours): Enhanced UI Components**

#### **Task 2.1: AI Content Generator Pro Component (2 hours)**
**File**: `client/src/components/AIContentGeneratorPro.js` (New)

```javascript
import React, { useState } from 'react';
import { api } from '../services/api';

const AIContentGeneratorPro = () => {
  const [campaignType, setCampaignType] = useState('promotion');
  const [context, setContext] = useState('');
  const [generatedContent, setGeneratedContent] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const generateMultiChannelContent = async () => {
    setIsGenerating(true);
    try {
      const response = await api.post('/ai/generate-multi-channel-content', {
        campaignType,
        context,
        channels: ['social_media', 'email', 'sms', 'ads']
      });
      
      setGeneratedContent(response.data);
    } catch (error) {
      console.error('Content generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="ai-content-generator-pro">
      <div className="generator-header">
        <h3>🤖 AI Content Generator Pro</h3>
        <p>Generate marketing content across all channels simultaneously</p>
      </div>

      <div className="campaign-setup">
        <div className="form-group">
          <label>Campaign Type</label>
          <select value={campaignType} onChange={(e) => setCampaignType(e.target.value)}>
            <option value="promotion">Promotional Campaign</option>
            <option value="seasonal">Seasonal Special</option>
            <option value="new_item">New Menu Item</option>
            <option value="event">Special Event</option>
          </select>
        </div>

        <div className="form-group">
          <label>Additional Context (Optional)</label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g., 20% off pasta dishes, limited time offer..."
            rows={3}
          />
        </div>

        <button 
          onClick={generateMultiChannelContent}
          disabled={isGenerating}
          className="generate-button"
        >
          {isGenerating ? 'Generating Content...' : '✨ Generate Multi-Channel Content'}
        </button>
      </div>

      {generatedContent && (
        <div className="generated-content">
          <div className="content-tabs">
            {Object.keys(generatedContent.multi_channel_content).map(channel => (
              <div key={channel} className="content-tab">
                <h4>{channel.replace('_', ' ').toUpperCase()}</h4>
                <div className="content-preview">
                  {generatedContent.multi_channel_content[channel].content}
                </div>
                <div className="content-actions">
                  <button>Edit</button>
                  <button>Schedule</button>
                  <button>Use Now</button>
                </div>
              </div>
            ))}
          </div>

          <div className="campaign-insights">
            <h4>📊 Campaign Insights</h4>
            <div className="insight-cards">
              <div className="insight-card">
                <span className="metric">Estimated Reach</span>
                <span className="value">{generatedContent.estimated_reach}</span>
              </div>
              <div className="insight-card">
                <span className="metric">Strategy</span>
                <span className="value">{generatedContent.campaign_strategy}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIContentGeneratorPro;
```

#### **Task 2.2: Smart Task Recommender Component (2 hours)**
**File**: `client/src/components/SmartTaskRecommender.js` (New)

```javascript
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const SmartTaskRecommender = () => {
  const [recommendation, setRecommendation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userContext, setUserContext] = useState({
    goals: 'Increase revenue and customers',
    timeAvailable: '30 minutes'
  });

  const getSmartRecommendation = async () => {
    setIsLoading(true);
    try {
      const response = await api.post('/ai/next-task-recommendation', {
        context: userContext
      });
      
      setRecommendation(response.data);
    } catch (error) {
      console.error('Recommendation failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    getSmartRecommendation();
  }, []);

  return (
    <div className="smart-task-recommender">
      <div className="recommender-header">
        <h3>🎯 Smart Task Recommender</h3>
        <p>AI-powered recommendations for your next best marketing action</p>
      </div>

      <div className="context-inputs">
        <div className="form-group">
          <label>Current Goals</label>
          <select 
            value={userContext.goals} 
            onChange={(e) => setUserContext({...userContext, goals: e.target.value})}
          >
            <option value="Increase revenue and customers">Increase Revenue & Customers</option>
            <option value="Improve online presence">Improve Online Presence</option>
            <option value="Launch new promotion">Launch New Promotion</option>
            <option value="Engage existing customers">Engage Existing Customers</option>
          </select>
        </div>

        <div className="form-group">
          <label>Time Available</label>
          <select 
            value={userContext.timeAvailable} 
            onChange={(e) => setUserContext({...userContext, timeAvailable: e.target.value})}
          >
            <option value="15 minutes">15 minutes</option>
            <option value="30 minutes">30 minutes</option>
            <option value="1 hour">1 hour</option>
            <option value="2+ hours">2+ hours</option>
          </select>
        </div>

        <button onClick={getSmartRecommendation} disabled={isLoading}>
          {isLoading ? 'Analyzing...' : '🔄 Get New Recommendation'}
        </button>
      </div>

      {recommendation && (
        <div className="recommendation-card">
          <div className="recommendation-header">
            <div className="priority-badge">{recommendation.priority_level}</div>
            <div className="impact-score">
              Impact Score: {recommendation.impact_score}/100
            </div>
          </div>

          <div className="recommendation-content">
            <h4>{recommendation.recommended_task}</h4>
            <p className="reasoning">{recommendation.reasoning}</p>
            
            <div className="recommendation-metrics">
              <div className="metric">
                <span className="label">Estimated Time:</span>
                <span className="value">{recommendation.estimated_time}</span>
              </div>
              <div className="metric">
                <span className="label">Revenue Potential:</span>
                <span className="value">{recommendation.revenue_potential}</span>
              </div>
            </div>

            <div className="recommendation-actions">
              <button className="primary-action">Start This Task</button>
              <button className="secondary-action">Learn More</button>
              <button className="tertiary-action">Skip & Get Another</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartTaskRecommender;
```

### **Afternoon (4 hours): Advanced Components**

#### **Task 2.3: Digital Presence Analyzer Component (2 hours)**
**File**: `client/src/components/DigitalPresenceAnalyzer.js` (New)

```javascript
import React, { useState } from 'react';
import { api } from '../services/api';

const DigitalPresenceAnalyzer = () => {
  const [analysisInputs, setAnalysisInputs] = useState({
    restaurantName: '',
    googleBusinessUrl: '',
    websiteUrl: '',
    instagramHandle: '',
    facebookPage: '',
    yelpUrl: ''
  });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const runDigitalAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const response = await api.post('/ai/analyze-digital-presence', analysisInputs);
      setAnalysisResults(response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="digital-presence-analyzer">
      <div className="analyzer-header">
        <h3>🔍 Digital Presence Analyzer</h3>
        <p>Comprehensive AI analysis of your restaurant's digital footprint</p>
      </div>

      <div className="analysis-form">
        <div className="form-section">
          <h4>Restaurant Information</h4>
          <input
            type="text"
            placeholder="Restaurant Name"
            value={analysisInputs.restaurantName}
            onChange={(e) => setAnalysisInputs({...analysisInputs, restaurantName: e.target.value})}
          />
        </div>

        <div className="form-section">
          <h4>Digital Presence URLs (Optional)</h4>
          <input
            type="url"
            placeholder="Google Business Profile URL"
            value={analysisInputs.googleBusinessUrl}
            onChange={(e) => setAnalysisInputs({...analysisInputs, googleBusinessUrl: e.target.value})}
          />
          <input
            type="url"
            placeholder="Website URL"
            value={analysisInputs.websiteUrl}
            onChange={(e) => setAnalysisInputs({...analysisInputs, websiteUrl: e.target.value})}
          />
          <input
            type="text"
            placeholder="Instagram Handle (@username)"
            value={analysisInputs.instagramHandle}
            onChange={(e) => setAnalysisInputs({...analysisInputs, instagramHandle: e.target.value})}
          />
        </div>

        <button 
          onClick={runDigitalAnalysis}
          disabled={!analysisInputs.restaurantName || isAnalyzing}
          className="analyze-button"
        >
          {isAnalyzing ? 'Analyzing Digital Presence...' : '🚀 Analyze Digital Presence'}
        </button>
      </div>

      {isAnalyzing && (
        <div className="analysis-progress">
          <div className="progress-steps">
            <div className="step active">Scanning Google Business Profile</div>
            <div className="step active">Analyzing Website Performance</div>
            <div className="step active">Checking Social Media Presence</div>
            <div className="step">Generating Recommendations</div>
          </div>
        </div>
      )}

      {analysisResults && (
        <div className="analysis-results">
          <div className="overall-grade">
            <div className="grade-circle">
              <span className="grade-number">{analysisResults.overall_grade}</span>
              <span className="grade-label">DIGITAL SCORE</span>
            </div>
            <div className="grade-description">
              <h4>Your Digital Presence Grade</h4>
              <p>Revenue Impact Potential: ${analysisResults.revenue_impact_estimate}/month</p>
            </div>
          </div>

          <div className="category-scores">
            {Object.entries(analysisResults.category_scores).map(([category, score]) => (
              <div key={category} className="category-score">
                <div className="category-info">
                  <span className="category-name">{category.replace('_', ' ')}</span>
                  <span className="score-number">{score}/100</span>
                </div>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="recommendations">
            <h4>🎯 Priority Recommendations</h4>
            {analysisResults.recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                <div className="rec-header">
                  <span className="impact-badge">${rec.revenue_impact}/month</span>
                  <span className="difficulty-badge">{rec.difficulty}</span>
                </div>
                <h5>{rec.title}</h5>
                <p>{rec.description}</p>
                <div className="rec-actions">
                  <button>Implement Now</button>
                  <button>Learn More</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DigitalPresenceAnalyzer;
```

#### **Task 2.4: Basic AI Assistant Component (2 hours)**
**File**: `client/src/components/AIAssistant.js` (New)

```javascript
import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: "Hi! I'm your AI Marketing Assistant. I can help you with content creation, task recommendations, and marketing insights. What would you like to work on today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await api.post('/ai/assistant/message', {
        message: inputMessage,
        conversation_context: messages.slice(-5) // Last 5 messages for context
      });

      // Add assistant response
      const assistantMessage = {
        type: 'assistant',
        content: response.data.message,
        data: response.data.data,
        actions: response.data.actions,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Assistant message failed:', error);
      const errorMessage = {
        type: 'assistant',
        content: "I'm sorry, I'm having trouble processing that request right now. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = (action) => {
    setInputMessage(action);
    sendMessage();
  };

  return (
    <div className="ai-assistant">
      <div className="assistant-header">
        <h3>🤖 AI Marketing Assistant</h3>
        <div className="status-indicator">
          <span className="status-dot active"></span>
          <span>Online</span>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                <p>{message.content}</p>
                
                {message.data && message.type === 'assistant' && (
                  <div className="message-data">
                    {message.data.type === 'content_generation' && (
                      <div className="content-preview">
                        <h5>Generated Content:</h5>
                        <div className="content-tabs">
                          {Object.entries(message.data.content.multi_channel_content).map(([channel, content]) => (
                            <div key={channel} className="content-tab-mini">
                              <strong>{channel}:</strong>
                              <p>{content.content?.substring(0, 100)}...</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {message.actions && (
                  <div className="message-actions">
                    {message.actions.map((action, actionIndex) => (
                      <button 
                        key={actionIndex}
                        onClick={() => handleQuickAction(action)}
                        className="action-button"
                      >
                        {action.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message assistant typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="quick-actions">
          <button onClick={() => handleQuickAction("What should I promote this week?")}>
            📈 What to promote?
          </button>
          <button onClick={() => handleQuickAction("Create a social media post for our lunch special")}>
            📱 Create social post
          </button>
          <button onClick={() => handleQuickAction("How is my marketing performance?")}>
            📊 Check performance
          </button>
          <button onClick={() => handleQuickAction("Generate an email campaign")}>
            📧 Email campaign
          </button>
        </div>

        <div className="message-input">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything about your restaurant marketing..."
            disabled={isTyping}
          />
          <button onClick={sendMessage} disabled={!inputMessage.trim() || isTyping}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
```

---

## 📋 Day 3: Integration & Polish

### **Morning (4 hours): API Routes & Integration**

#### **Task 3.1: New API Routes (2 hours)**
**File**: `backendv2/app/routes/ai_features.py` (