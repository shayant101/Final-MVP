import React, { useState, useEffect, useRef } from 'react';
import './AIBusinessAssistant.css';

const AIBusinessAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        id: 1,
        type: 'assistant',
        content: "Hello! I'm your AI Business Assistant. I can help you with strategic insights, revenue analysis, customer behavior patterns, and business optimization recommendations. What would you like to explore today?",
        timestamp: new Date(),
        insights: [],
        recommendations: []
      }
    ]);

    // Fetch initial insights
    fetchInitialInsights();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchInitialInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/ai-assistant/platform-performance?time_period=30d', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        setInsights(result.data);
      }
    } catch (err) {
      console.error('Failed to fetch initial insights:', err);
      // Use mock insights
      setInsights(getMockInsights());
    }
  };

  const getMockInsights = () => ({
    key_metrics: {
      total_revenue: 125000,
      active_customers: 45,
      growth_rate: 15.2,
      churn_rate: 7.5
    },
    trends: [
      "Revenue growth accelerating with 15.2% monthly increase",
      "Customer retention improving - down to 7.5% churn",
      "AI features showing 78% adoption rate",
      "Premium tier upgrades increased 23% this month"
    ],
    alerts: [
      { type: "opportunity", message: "3 customers ready for upselling to premium plans" },
      { type: "warning", message: "2 high-value customers showing declining usage" }
    ]
  });

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/ai-assistant/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: inputMessage,
          context: "business_intelligence",
          include_insights: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const result = await response.json();
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.data.response || getMockResponse(inputMessage),
        timestamp: new Date(),
        insights: result.data.insights || [],
        recommendations: result.data.recommendations || [],
        confidence_score: result.data.confidence_score || 85
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (result.data.recommendations) {
        setRecommendations(result.data.recommendations);
      }

    } catch (err) {
      console.error('Chat error:', err);
      setError('Failed to get response from AI assistant');
      
      // Add mock response for demonstration
      const mockResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        content: getMockResponse(inputMessage),
        timestamp: new Date(),
        insights: getMockInsights().trends.slice(0, 2),
        recommendations: [
          "Consider implementing a customer success program for high-value accounts",
          "Explore upselling opportunities with customers using basic features heavily"
        ],
        confidence_score: 85
      };
      
      setMessages(prev => [...prev, mockResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const getMockResponse = (query) => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('revenue') || lowerQuery.includes('sales')) {
      return "Based on your current revenue trends, you're experiencing strong growth at 15.2% monthly increase. Your total revenue of $125,000 is driven primarily by your Enterprise tier customers who contribute 54% of total revenue. I recommend focusing on customer retention strategies and exploring upselling opportunities with your Professional tier customers.";
    } else if (lowerQuery.includes('customer') || lowerQuery.includes('churn')) {
      return "Your customer metrics show positive trends with 45 active customers and a declining churn rate of 7.5%. The AI features are showing strong adoption at 78%, which correlates with higher retention rates. I suggest implementing proactive outreach for customers showing declining usage patterns.";
    } else if (lowerQuery.includes('growth') || lowerQuery.includes('strategy')) {
      return "For sustainable growth, I recommend focusing on three key areas: 1) Customer success programs to reduce churn, 2) Feature adoption campaigns to increase engagement, and 3) Strategic pricing optimization. Your current growth trajectory suggests you could achieve 200% revenue growth within 12 months with proper execution.";
    } else {
      return "I can help you analyze various aspects of your business including revenue trends, customer behavior, feature performance, and strategic opportunities. What specific area would you like to explore? I can provide insights on revenue optimization, customer retention strategies, or growth opportunities.";
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What are my top revenue opportunities?",
    "Which customers are at risk of churning?",
    "How can I optimize my pricing strategy?",
    "What features drive the most engagement?",
    "Show me growth predictions for next quarter",
    "Analyze my customer segments"
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  return (
    <div className="ai-business-assistant">
      <div className="aba-header">
        <div className="aba-title-section">
          <h2>🤖 AI Business Assistant</h2>
          <p>Strategic insights and recommendations powered by advanced AI</p>
        </div>
        <div className="aba-status">
          <div className="status-indicator online"></div>
          <span>AI Assistant Online</span>
        </div>
      </div>

      {error && (
        <div className="aba-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Insights Panel */}
      {insights && (
        <div className="insights-panel">
          <div className="insights-header">
            <h3>📊 Current Business Insights</h3>
          </div>
          <div className="insights-grid">
            <div className="insight-metric">
              <div className="metric-value">${insights.key_metrics?.total_revenue?.toLocaleString() || '125,000'}</div>
              <div className="metric-label">Total Revenue</div>
            </div>
            <div className="insight-metric">
              <div className="metric-value">{insights.key_metrics?.active_customers || 45}</div>
              <div className="metric-label">Active Customers</div>
            </div>
            <div className="insight-metric">
              <div className="metric-value">{insights.key_metrics?.growth_rate || 15.2}%</div>
              <div className="metric-label">Growth Rate</div>
            </div>
            <div className="insight-metric">
              <div className="metric-value">{insights.key_metrics?.churn_rate || 7.5}%</div>
              <div className="metric-label">Churn Rate</div>
            </div>
          </div>
          
          {insights.alerts && insights.alerts.length > 0 && (
            <div className="insights-alerts">
              {insights.alerts.map((alert, index) => (
                <div key={index} className={`alert-item ${alert.type}`}>
                  <div className="alert-icon">
                    {alert.type === 'opportunity' ? '🎯' : '⚠️'}
                  </div>
                  <div className="alert-message">{alert.message}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                
                {message.insights && message.insights.length > 0 && (
                  <div className="message-insights">
                    <h4>💡 Key Insights:</h4>
                    <ul>
                      {message.insights.map((insight, index) => (
                        <li key={index}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {message.recommendations && message.recommendations.length > 0 && (
                  <div className="message-recommendations">
                    <h4>🎯 Recommendations:</h4>
                    <ul>
                      {message.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="message-meta">
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.confidence_score && (
                    <span className="confidence-score">
                      Confidence: {message.confidence_score}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        <div className="quick-questions">
          <div className="quick-questions-header">
            <span>💭 Quick Questions:</span>
          </div>
          <div className="quick-questions-grid">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                className="quick-question-btn"
                onClick={() => handleQuickQuestion(question)}
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your business performance, revenue optimization, customer insights, or strategic recommendations..."
              className="chat-input"
              rows="3"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="send-button"
            >
              {isLoading ? '⏳' : '🚀'}
            </button>
          </div>
          <div className="input-help">
            <span>💡 Try asking about revenue trends, customer insights, or growth strategies</span>
          </div>
        </div>
      </div>

      {/* Recommendations Panel */}
      {recommendations.length > 0 && (
        <div className="recommendations-panel">
          <div className="recommendations-header">
            <h3>🎯 Strategic Recommendations</h3>
          </div>
          <div className="recommendations-list">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                <div className="recommendation-icon">💡</div>
                <div className="recommendation-content">
                  <div className="recommendation-text">{rec}</div>
                </div>
                <div className="recommendation-actions">
                  <button className="action-btn primary">Implement</button>
                  <button className="action-btn secondary">Learn More</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIBusinessAssistant;