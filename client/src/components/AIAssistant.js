import React, { useState } from 'react';
import './AIAssistant.css';
import ChatModal from './ChatModal';

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating AI Assistant Button */}
      <div className="ai-assistant-container">
        <button 
          className="ai-assistant-button"
          onClick={toggleChat}
          title="Chat with your AI Marketing Assistant"
        >
          <span className="ai-icon">✨</span>
          <div className="pulse-ring"></div>
          <div className="pulse-ring-2"></div>
        </button>
        
        {/* Tooltip */}
        <div className="ai-tooltip">
          <span>AI Assistant</span>
          <div className="tooltip-arrow"></div>
        </div>
      </div>

      {/* Chat Modal */}
      {isOpen && (
        <ChatModal 
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default AIAssistant;