import React, { useState, useRef, useEffect } from 'react';
import { dashboardAPI, checklistAPI } from '../services/api';
import './ChatModal.css';

const ChatModal = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hi! I'm your AI Marketing Assistant. I'm here to help you grow your restaurant business and improve your Momentum Orchestrator score. How can I assist you today?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [checklistData, setChecklistData] = useState(null);
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    "What's my Momentum Orchestrator score?",
    "Show me my checklist progress",
    "How can I improve my marketing score?",
    "What should I complete next?",
    "Help me understand my revenue potential"
  ];

  // Fetch dashboard and checklist data when modal opens
  useEffect(() => {
    if (isOpen && !dashboardData) {
      fetchDashboardData();
      fetchChecklistData();
    }
  }, [isOpen, dashboardData]);

  const fetchDashboardData = async () => {
    try {
      const data = await dashboardAPI.getRestaurantDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const fetchChecklistData = async () => {
    try {
      const data = await checklistAPI.getCategoriesWithItems();
      setChecklistData(data);
    } catch (error) {
      console.error('Failed to fetch checklist data:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText = inputValue) => {
    if (!messageText.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const response = generateResponse(messageText);
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const generateResponse = (question) => {
    const lowerQuestion = question.toLowerCase();
    
    // Momentum Orchestrator Score Questions
    if (lowerQuestion.includes('momentum') || lowerQuestion.includes('orchestrator') || (lowerQuestion.includes('score') && !lowerQuestion.includes('digital'))) {
      const marketingScore = dashboardData?.momentumMetrics?.marketingScore || 0;
      const foundationProgress = dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0;
      const ongoingProgress = dashboardData?.momentumMetrics?.ongoingProgress?.percentage || 0;
      const weeklyRevenue = dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0;
      
      return `🎯 **Your Momentum Orchestrator Score: ${marketingScore}/100**\n\n**Score Breakdown:**\n• Foundation Progress: ${foundationProgress}% (Essential setup tasks)\n• Ongoing Progress: ${ongoingProgress}% (Growth activities)\n\n**What this means:**\n${marketingScore >= 80 ? "🏆 Excellent - You're crushing it!" : marketingScore >= 60 ? "💪 Strong - Great momentum building!" : marketingScore >= 40 ? "🔥 Growing - You're on the right track!" : marketingScore >= 20 ? "🌟 Building - Good foundation started!" : "🚀 Starting - Let's build your momentum!"}\n\n**Weekly Revenue Potential:** $${weeklyRevenue}\n\n**Next Steps:**\n${foundationProgress < 100 ? "• Complete foundational tasks first (Google Business, website basics)\n" : ""}${ongoingProgress < 100 ? "• Focus on ongoing growth activities (social media, campaigns)\n" : ""}• Check your checklist for specific action items\n\nWould you like me to show you exactly what to complete next?`;
    }
    
    // Checklist Progress Questions
    if (lowerQuestion.includes('checklist') || lowerQuestion.includes('progress') || lowerQuestion.includes('complete') || lowerQuestion.includes('next')) {
      if (!checklistData || !checklistData.categories) {
        return "I'm still loading your checklist data. Please try again in a moment, or ask me about your Momentum Orchestrator score while I fetch your checklist information.";
      }
      
      const foundationalItems = checklistData.categories.find(cat => cat.type === 'foundational')?.items || [];
      const ongoingItems = checklistData.categories.find(cat => cat.type === 'ongoing')?.items || [];
      
      const foundationalComplete = foundationalItems.filter(item => item.status === 'completed').length;
      const foundationalTotal = foundationalItems.length;
      const ongoingComplete = ongoingItems.filter(item => item.status === 'completed').length;
      const ongoingTotal = ongoingItems.length;
      
      const nextFoundational = foundationalItems.find(item => item.status !== 'completed');
      const nextOngoing = ongoingItems.find(item => item.status !== 'completed');
      
      let response = `📋 **Your Checklist Progress:**\n\n**Foundation Tasks:** ${foundationalComplete}/${foundationalTotal} completed (${Math.round((foundationalComplete/foundationalTotal)*100)}%)\n**Ongoing Tasks:** ${ongoingComplete}/${ongoingTotal} completed (${Math.round((ongoingComplete/ongoingTotal)*100)}%)\n\n`;
      
      if (nextFoundational) {
        response += `🎯 **Priority Action:** ${nextFoundational.name}\n${nextFoundational.description}\n\n💡 **Why this matters:** Foundational tasks have the biggest impact on your Momentum Orchestrator score!\n\n`;
      } else if (nextOngoing) {
        response += `🎯 **Next Growth Step:** ${nextOngoing.name}\n${nextOngoing.description}\n\n🚀 **Impact:** This will help maintain and grow your momentum!\n\n`;
      } else {
        response += `🎉 **Congratulations!** You've completed all your checklist items!\n\nYour Momentum Orchestrator score should be looking fantastic. Keep up the great work with ongoing marketing activities!\n\n`;
      }
      
      if (foundationalComplete < foundationalTotal || ongoingComplete < ongoingTotal) {
        response += `**Your Next 3 Action Items:**\n`;
        const incompleteItems = [...foundationalItems, ...ongoingItems]
          .filter(item => item.status !== 'completed')
          .slice(0, 3);
        
        incompleteItems.forEach((item, index) => {
          response += `${index + 1}. ${item.name}\n   📝 ${item.description}\n\n`;
        });
        
        response += `**Pro Tip:** Focus on foundational tasks first - they unlock the biggest score improvements and revenue potential!\n\n`;
      }
      
      response += `**Score Impact:** Each completed task directly boosts your Momentum Orchestrator score and unlocks more weekly revenue potential!`;
      
      return response;
    }
    
    // Revenue Potential Questions
    if (lowerQuestion.includes('revenue') || lowerQuestion.includes('potential') || lowerQuestion.includes('money') || lowerQuestion.includes('earn')) {
      const weeklyRevenue = dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0;
      const completedRevenue = dashboardData?.momentumMetrics?.completedRevenue || 0;
      const totalPotential = dashboardData?.momentumMetrics?.totalPotential || 0;
      const monthlyRevenue = dashboardData?.restaurant?.monthly_revenue || 0;
      
      return `💰 **Your Revenue Potential Analysis:**\n\n**Current Weekly Potential:** $${weeklyRevenue}\n**Monthly Baseline:** $${monthlyRevenue}\n**Unlocked Revenue:** $${completedRevenue} of $${totalPotential} total\n\n**Revenue Opportunities:**\n• Complete foundational tasks: +$${Math.round((totalPotential - completedRevenue) * 0.4)}/week\n• Launch marketing campaigns: +$${Math.round((totalPotential - completedRevenue) * 0.6)}/week\n• Optimize digital presence: +$${Math.round(weeklyRevenue * 0.3)}/week\n\n**Action Plan:**\n1. Focus on high-impact checklist items first\n2. Set up Google Business Profile optimization\n3. Launch targeted social media campaigns\n4. Implement customer retention strategies\n\nEach completed task moves you closer to your full revenue potential. Would you like specific guidance on the highest-impact actions?`;
    }
    
    // Digital Presence/Marketing Score Questions
    if (lowerQuestion.includes('digital presence') || lowerQuestion.includes('marketing score') || lowerQuestion.includes('improve')) {
      const marketingScore = dashboardData?.momentumMetrics?.marketingScore || 0;
      const foundationProgress = dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0;
      
      return `📊 **Your Marketing Score: ${marketingScore}/100**\n\n**Current Status:** ${marketingScore >= 80 ? "🏆 Excellent" : marketingScore >= 60 ? "💪 Strong" : marketingScore >= 40 ? "🔥 Growing" : marketingScore >= 20 ? "🌟 Building" : "🚀 Starting"}\n\n**To Improve Your Score:**\n\n${foundationProgress < 100 ? "**Foundation (Priority):**\n• Set up Google My Business profile\n• Optimize your website basics\n• Create social media accounts\n• Add online ordering capability\n\n" : ""}**Growth Activities:**\n• Post regularly on social media (3-4x/week)\n• Collect and respond to customer reviews\n• Run targeted advertising campaigns\n• Engage with your local community\n\n**Quick Wins (This Week):**\n• Upload 5 high-quality food photos\n• Update your business hours and contact info\n• Respond to recent customer reviews\n• Post about today's special\n\nEach improvement directly impacts your Momentum Orchestrator score and revenue potential!`;
    }
    
    // Campaign and Marketing Strategy Questions
    if (lowerQuestion.includes('marketing') || lowerQuestion.includes('campaign') || lowerQuestion.includes('customers')) {
      const activeCampaigns = dashboardData?.activeCampaigns?.length || 0;
      const newCustomers = dashboardData?.performanceSnapshot?.newCustomersAcquired || 0;
      
      return `🚀 **Marketing Strategy Recommendations:**\n\n**Current Status:**\n• Active Campaigns: ${activeCampaigns}\n• New Customers This Month: ${newCustomers}\n\n**Recommended Campaigns:**\n\n**1. Local Social Media Boost** 📱\n• Target customers within 5 miles\n• Showcase your best dishes with photos\n• Estimated ROI: 240% over 30 days\n• Budget: $200-350/month\n\n**2. Google Ads for Local Search** 🔍\n• Capture "restaurants near me" searches\n• Promote lunch/dinner specials\n• Estimated new customers: 15-25/month\n\n**3. Customer Retention SMS** 💬\n• Re-engage past customers\n• Send weekly specials and updates\n• Increase repeat visits by 35%\n\n**Next Steps:**\n1. Complete your Google Business setup first\n2. Gather customer phone numbers/emails\n3. Launch with social media campaign\n4. Scale successful campaigns\n\nWould you like me to help you set up any of these campaigns?`;
    }
    
    // Default response with personalized data
    const marketingScore = dashboardData?.momentumMetrics?.marketingScore || 0;
    const restaurantName = dashboardData?.restaurant?.name || "your restaurant";
    
    return `That's a great question! I'm here to help ${restaurantName} grow with personalized insights.\n\n**I can help you with:**\n\n🎯 **Momentum Orchestrator Score** (Currently: ${marketingScore}/100)\n📋 **Checklist Progress** - See what to complete next\n💰 **Revenue Potential** - Unlock growth opportunities\n📊 **Marketing Strategy** - Campaigns that work for your business\n🔧 **Digital Presence** - Optimize your online visibility\n\n**Quick Actions:**\n• Ask "What's my Momentum Orchestrator score?"\n• Ask "Show me my checklist progress"\n• Ask "How can I increase revenue?"\n• Ask "What should I complete next?"\n\nWhat specific area would you like to focus on first?`;
  };

  const handleQuickQuestion = (question) => {
    handleSendMessage(question);
  };

  const handleCompleteChecklistItem = async (itemId, itemName) => {
    try {
      // Add user message about completing the item
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: `Mark "${itemName}" as completed`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setIsTyping(true);

      // Update the checklist item
      await checklistAPI.updateStatus(dashboardData?.restaurant?.id, itemId, 'completed');
      
      // Refresh data
      await fetchDashboardData();
      await fetchChecklistData();

      // Add success response
      setTimeout(() => {
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: `🎉 Excellent! I've marked "${itemName}" as completed.\n\nThis will boost your Momentum Orchestrator score! Your progress is looking great.\n\nWould you like me to show you what to work on next?`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      }, 1000);

    } catch (error) {
      setIsTyping(false);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I had trouble updating that checklist item. Please try again or check your connection.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-info">
            <div className="assistant-avatar">✨</div>
            <div>
              <h3>AI Marketing Assistant</h3>
              <p>Always here to help grow your business</p>
            </div>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                {message.content.split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message assistant">
              <div className="message-content typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        <div className="quick-questions">
          <p>Quick questions:</p>
          <div className="quick-questions-grid">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                className="quick-question-btn"
                onClick={() => handleQuickQuestion(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your restaurant marketing..."
              className="chat-input"
              rows="1"
            />
            <button 
              className="send-button"
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim()}
            >
              <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatModal;