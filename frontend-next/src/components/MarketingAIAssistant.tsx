import React, { useState } from 'react';
import './MarketingAIAssistant.css';
import MarketingChatModal from './MarketingChatModal';

const MarketingAIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Marketing AI Assistant Button */}
      <div className="marketing-ai-container">
        <button 
          className="marketing-ai-button"
          onClick={toggleChat}
          title="Learn about Uplit - Chat with our Marketing AI"
        >
          <span className="marketing-ai-icon">✨</span>
          <div className="marketing-pulse-ring"></div>
          <div className="marketing-pulse-ring-2"></div>
        </button>
        
        {/* Tooltip */}
        <div className="marketing-ai-tooltip">
          <span>Learn about Uplit</span>
          <div className="marketing-tooltip-arrow"></div>
        </div>
      </div>

      {/* Chat Modal */}
      {isOpen && (
        <MarketingChatModal 
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default MarketingAIAssistant;