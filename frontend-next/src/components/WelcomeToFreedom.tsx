'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import './WelcomeToFreedom.css';

const WelcomeToFreedom = () => {
  const router = useRouter();
  const [animationPhase, setAnimationPhase] = useState(0);
  const [showTransformation, setShowTransformation] = useState(false);

  useEffect(() => {
    // Epic animation sequence
    const sequence = [
      { phase: 1, delay: 1000 },   // Show stress scene
      { phase: 2, delay: 3000 },   // Start transformation
      { phase: 3, delay: 5000 },   // AI takes over
      { phase: 4, delay: 7000 },   // Beach scene appears
      { phase: 5, delay: 9000 },   // Final celebration
    ];

    sequence.forEach(({ phase, delay }) => {
      setTimeout(() => setAnimationPhase(phase), delay);
    });

    // Show transformation effect
    setTimeout(() => setShowTransformation(true), 4000);
  }, []);

  const handleContinue = () => {
    router.push('/dashboard');
  };

  const handleCheckEmail = () => {
    // Could open email client or show instructions
    alert('Please check your email for the verification link!');
  };

  return (
    <div className="freedom-container">
      {/* Animated Background */}
      <div className="freedom-bg">
        {/* Stress particles (red/orange) */}
        <div className={`stress-particles ${animationPhase >= 1 ? 'active' : ''}`}>
          {[...Array(15)].map((_, i) => (
            <div key={i} className={`stress-particle stress-particle-${i}`}>
              {['😰', '😤', '🔥', '💸', '⏰'][i % 5]}
            </div>
          ))}
        </div>

        {/* Transformation wave */}
        <div className={`transformation-wave ${showTransformation ? 'active' : ''}`}>
          <div className="wave-layer wave-1"></div>
          <div className="wave-layer wave-2"></div>
          <div className="wave-layer wave-3"></div>
        </div>

        {/* Beach particles (blue/green) */}
        <div className={`beach-particles ${animationPhase >= 4 ? 'active' : ''}`}>
          {[...Array(20)].map((_, i) => (
            <div key={i} className={`beach-particle beach-particle-${i}`}>
              {['🌊', '🏖️', '🌴', '☀️', '🍹', '😎'][i % 6]}
            </div>
          ))}
        </div>

        {/* Floating AI elements */}
        <div className={`ai-elements ${animationPhase >= 3 ? 'active' : ''}`}>
          {[...Array(8)].map((_, i) => (
            <div key={i} className={`ai-element ai-element-${i}`}>
              {['🤖', '⚡', '🎯', '📊', '💡', '🚀', '⭐', '🔮'][i]}
            </div>
          ))}
        </div>
      </div>

      <div className="freedom-content">
        {/* Scene 1: Stress */}
        <div className={`scene stress-scene ${animationPhase >= 1 ? 'active' : ''}`}>
          <div className="scene-visual">
            <div className="stress-restaurant">
              <div className="stress-icon">🏪</div>
              <div className="stress-effects">
                <div className="stress-line stress-line-1"></div>
                <div className="stress-line stress-line-2"></div>
                <div className="stress-line stress-line-3"></div>
              </div>
            </div>
          </div>
          <div className="scene-text">
            <h2>Before: Endless Restaurant Stress</h2>
            <div className="stress-problems">
              <div className="problem-item">😰 Manual marketing chaos</div>
              <div className="problem-item">📱 Social media overwhelm</div>
              <div className="problem-item">💸 Wasted ad spending</div>
              <div className="problem-item">⏰ No time for yourself</div>
            </div>
          </div>
        </div>

        {/* Scene 2: AI Transformation */}
        <div className={`scene transformation-scene ${animationPhase >= 3 ? 'active' : ''}`}>
          <div className="ai-takeover">
            <div className="ai-brain">
              <div className="brain-core">🧠</div>
              <div className="brain-waves">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className={`brain-wave wave-${i}`}></div>
                ))}
              </div>
            </div>
            <div className="ai-text">
              <h2>AI Takes Over Everything!</h2>
              <div className="ai-powers">
                <div className="power-item">🤖 Automated campaigns</div>
                <div className="power-item">📊 Smart analytics</div>
                <div className="power-item">🎯 Perfect targeting</div>
                <div className="power-item">⚡ 24/7 optimization</div>
              </div>
            </div>
          </div>
        </div>

        {/* Scene 3: Beach Freedom */}
        <div className={`scene beach-scene ${animationPhase >= 4 ? 'active' : ''}`}>
          <div className="beach-visual">
            <div className="beach-setup">
              <div className="beach-chair">🏖️</div>
              <div className="beach-umbrella">🏖️</div>
              <div className="beach-drink">🍹</div>
              <div className="beach-sun">☀️</div>
              <div className="beach-waves">
                <div className="ocean-wave wave-1">🌊</div>
                <div className="ocean-wave wave-2">🌊</div>
                <div className="ocean-wave wave-3">🌊</div>
              </div>
            </div>
            <div className="relaxed-owner">😎</div>
          </div>
          <div className="beach-text">
            <h1 className="freedom-title">
              <span className="title-line-1">Welcome to</span>
              <span className="title-line-2">FREEDOM!</span>
            </h1>
            <p className="freedom-subtitle">
              You just made the smartest decision of your life
            </p>
          </div>
        </div>

        {/* Final CTA */}
        <div className={`final-cta ${animationPhase >= 5 ? 'active' : ''}`}>
          <div className="cta-content">
            <div className="success-message">
              <div className="success-icon">🎉</div>
              <h3>Account Created Successfully!</h3>
              <p>Check your email to verify and unlock your AI-powered future</p>
            </div>
            
            <div className="cta-buttons">
              <button className="primary-cta" onClick={handleCheckEmail}>
                <span>Check Email & Verify</span>
                <div className="button-sparkles">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className={`sparkle sparkle-${i}`}>✨</div>
                  ))}
                </div>
              </button>
              
              <button className="secondary-cta" onClick={handleContinue}>
                <span>Continue to Dashboard</span>
                <div className="button-arrow">→</div>
              </button>
            </div>

            <div className="next-steps">
              <div className="step-item">
                <span className="step-number">1</span>
                <span>Verify your email</span>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <span>Set up your restaurant</span>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <span>Watch AI work its magic</span>
              </div>
              <div className="step-item">
                <span className="step-number">4</span>
                <span>Enjoy your freedom! 🏖️</span>
              </div>
            </div>
          </div>
        </div>

        {/* Floating celebration elements */}
        <div className={`celebration-elements ${animationPhase >= 5 ? 'active' : ''}`}>
          {[...Array(12)].map((_, i) => (
            <div key={i} className={`celebration-item celebration-${i}`}>
              {['🎉', '🎊', '⭐', '💫', '🌟', '✨'][i % 6]}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeToFreedom;