import React, { useState, useRef, useEffect } from 'react';
import './MarketingChatModal.css';

const MarketingChatModal = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "👋 Hi there! I'm Uplit's Marketing AI Assistant. I'm here to help you understand how Uplit can transform your restaurant's marketing and boost your revenue. What would you like to know about our platform?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const lastMessageRef = useRef(null);

  const quickQuestions = [
    "What does Uplit do for restaurants?",
    "How can Uplit help me get more customers?",
    "What marketing features do you offer?",
    "How much does it cost?",
    "How do I get started?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToLastMessage = () => {
    lastMessageRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  useEffect(() => {
    // If the last message is from assistant, scroll to its beginning
    // Otherwise, scroll to bottom for user messages
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.type === 'assistant') {
      setTimeout(() => scrollToLastMessage(), 100);
    } else {
      scrollToBottom();
    }
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
      const response = generateMarketingResponse(messageText);
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1800);
  };

  const generateMarketingResponse = (question) => {
    const lowerQuestion = question.toLowerCase();
    
    // What does Uplit do?
    if (lowerQuestion.includes('what') && (lowerQuestion.includes('uplit') || lowerQuestion.includes('do') || lowerQuestion.includes('platform'))) {
      return `🚀 **Uplit is your complete restaurant marketing platform!**\n\n• Smart marketing automation & social media\n• Google Business optimization for local discovery\n• AI-powered insights & growth recommendations\n• Step-by-step marketing checklist\n\n**Result:** 25-40% increase in new customers within 90 days!\n\nReady to see how it works for your restaurant?`;
    }
    
    // Customer acquisition questions
    if (lowerQuestion.includes('customer') || lowerQuestion.includes('more business') || lowerQuestion.includes('grow') || lowerQuestion.includes('acquire')) {
      return `🎯 **Get more customers with proven strategies:**\n\n• **Local Discovery:** Optimize Google Business Profile\n• **Social Media:** Automated posting & engagement\n• **Targeted Ads:** Facebook & Google ads for your area\n• **SMS Retention:** Win back repeat customers\n\n**Success Story:** Tony's Pizza increased revenue by $8,400/month in 3 months!\n\nWhich strategy interests you most?`;
    }
    
    // Marketing features questions
    if (lowerQuestion.includes('feature') || lowerQuestion.includes('marketing') || lowerQuestion.includes('tool') || lowerQuestion.includes('capability')) {
      return `🛠️ **Complete Marketing Toolkit:**\n\n• **AI Marketing Assistant** - 24/7 personalized advice\n• **Momentum Score** - Track marketing effectiveness 0-100\n• **Smart Checklist** - Prioritized tasks for maximum impact\n• **Campaign Management** - Social media & SMS automation\n• **Analytics** - Revenue tracking & ROI analysis\n\nAll integrated in one easy dashboard - no juggling multiple tools!\n\nWhich feature would help your restaurant most?`;
    }
    
    // Pricing questions
    if (lowerQuestion.includes('cost') || lowerQuestion.includes('price') || lowerQuestion.includes('pricing') || lowerQuestion.includes('expensive') || lowerQuestion.includes('affordable')) {
      return `💰 **Affordable Plans for Every Restaurant:**\n\n• **Starter:** $97/month - Marketing checklist & automation\n• **Growth:** $197/month - Full campaigns & SMS (Most Popular)\n• **Pro:** $297/month - Advanced analytics & dedicated support\n\n**ROI Guarantee:** Average $3-5 return for every $1 spent!\n\n**🎁 Special Offer:** 14-day free trial + 50% off first month\n\nReady to start your free trial?`;
    }
    
    // Getting started questions
    if (lowerQuestion.includes('start') || lowerQuestion.includes('begin') || lowerQuestion.includes('setup') || lowerQuestion.includes('onboard') || lowerQuestion.includes('sign up')) {
      return `🚀 **Getting Started is Easy:**\n\n1. **Sign Up** (2 min) - Click "Create Account" above\n2. **Quick Setup** (15 min) - Connect your accounts\n3. **AI Analysis** (Automatic) - Get your marketing score\n4. **Start Growing** (Same day) - Follow your checklist\n\n**You're Not Alone:** Dedicated onboarding + 24/7 support\n\nClick "Create Account" to start your free trial - no credit card required!\n\nAny questions about setup?`;
    }
    
    // Success stories / case studies
    if (lowerQuestion.includes('success') || lowerQuestion.includes('result') || lowerQuestion.includes('example') || lowerQuestion.includes('case study') || lowerQuestion.includes('proof')) {
      return `🏆 **Real Success Stories:**\n\n• **Tony's Pizza:** +70% revenue ($8,400/month increase)\n• **Maria's Tacos:** +200% new customers in 2 months\n• **Sakura Ramen:** Score improved 23→87, +$6,800/month\n\n**Average Results:** 35% more customers, $4,200 monthly increase\n\n**Why It Works:** Based on 10,000+ successful restaurant campaigns\n\nWant to be our next success story?`;
    }
    
    // Competition / alternatives
    if (lowerQuestion.includes('competitor') || lowerQuestion.includes('alternative') || lowerQuestion.includes('vs') || lowerQuestion.includes('compare') || lowerQuestion.includes('different')) {
      return `🥇 **Why Choose Uplit:**\n\n• **vs Marketing Agencies:** 10x more affordable ($97 vs $3,000+)\n• **vs DIY Tools:** All-in-one platform, no juggling\n• **vs Social Schedulers:** Complete growth system, not just posts\n• **vs Generic Platforms:** Built specifically for restaurants\n\n**What Makes Us Unique:** Restaurant-specific AI + proven checklist + guaranteed results\n\nReady to see the difference?`;
    }
    
    // Default response with call-to-action
    return `Great question! I can help you understand how Uplit transforms restaurant marketing.\n\n**Ask me about:**\n• What Uplit does for restaurants\n• How to get more customers\n• Marketing features & tools\n• Pricing & ROI\n• Success stories\n• Getting started\n\n**Quick Facts:** 10,000+ restaurants, 35% average customer increase, 14-day free trial\n\n**🎁 Special Offer:** Start free trial + 50% off first month!\n\nWhat would you like to know first?`;
  };

  const handleQuickQuestion = (question) => {
    handleSendMessage(question);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="marketing-chat-modal-overlay" onClick={onClose}>
      <div className="marketing-chat-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="marketing-chat-header">
          <div className="marketing-chat-header-info">
            <div className="marketing-assistant-avatar">✨</div>
            <div>
              <h3>Uplit Marketing AI</h3>
              <p>Learn how we help restaurants grow</p>
            </div>
          </div>
          <button className="marketing-close-button" onClick={onClose}>×</button>
        </div>

        {/* Messages */}
        <div className="marketing-chat-messages">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`marketing-message ${message.type}`}
              ref={index === messages.length - 1 ? lastMessageRef : null}
            >
              <div className="marketing-message-content">
                {message.content.split('\n').map((line, index) => (
                  <div key={index}>{line}</div>
                ))}
              </div>
              <div className="marketing-message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="marketing-message assistant">
              <div className="marketing-message-content marketing-typing-indicator">
                <div className="marketing-typing-dots">
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
        <div className="marketing-quick-questions">
          <p>Popular questions:</p>
          <div className="marketing-quick-questions-grid">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                className="marketing-quick-question-btn"
                onClick={() => handleQuickQuestion(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="marketing-chat-input-container">
          <div className="marketing-chat-input-wrapper">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Uplit's restaurant marketing platform..."
              className="marketing-chat-input"
              rows="1"
            />
            <button 
              className="marketing-send-button"
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

export default MarketingChatModal;