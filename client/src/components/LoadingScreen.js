import React from 'react';
import './LoadingScreen.css';

const LoadingScreen = ({ message = "Loading your restaurant's AI-powered marketing platform..." }) => {
  return (
    <div className="loading-screen">
      <div className="loading-container">
        {/* Animated Logo */}
        <div className="loading-logo">
          <div className="rocket-container">
            <div className="rocket">🚀</div>
            <div className="rocket-trail"></div>
          </div>
          <h1 className="loading-brand">Uplift</h1>
        </div>

        {/* Animated Progress Indicators */}
        <div className="loading-progress">
          <div className="progress-dots">
            <div className="dot dot-1"></div>
            <div className="dot dot-2"></div>
            <div className="dot dot-3"></div>
            <div className="dot dot-4"></div>
          </div>
          
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>

        {/* Loading Message */}
        <div className="loading-message">
          <p className="main-message">{message}</p>
          <div className="sub-messages">
            <div className="typing-text">
              <span className="typing-word active">Analyzing your restaurant data</span>
              <span className="typing-word">Optimizing AI recommendations</span>
              <span className="typing-word">Preparing marketing insights</span>
              <span className="typing-word">Enhancing your experience</span>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="floating-elements">
          <div className="float-element element-1">📊</div>
          <div className="float-element element-2">🍽️</div>
          <div className="float-element element-3">📱</div>
          <div className="float-element element-4">✨</div>
          <div className="float-element element-5">🎯</div>
          <div className="float-element element-6">📈</div>
        </div>

        {/* Pulse Rings */}
        <div className="pulse-rings">
          <div className="pulse-ring ring-1"></div>
          <div className="pulse-ring ring-2"></div>
          <div className="pulse-ring ring-3"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;