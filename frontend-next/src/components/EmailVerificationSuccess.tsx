'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import './EmailVerificationSuccess.css';

const EmailVerificationSuccess = () => {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [verificationStatus, setVerificationStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [animationPhase, setAnimationPhase] = useState(0);
  const token = searchParams.get('token');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setVerificationStatus('error');
        return;
      }

      try {
        const response = await fetch('/api/auth/verify-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        if (response.ok) {
          setVerificationStatus('success');
          // Start the animation sequence
          setTimeout(() => setAnimationPhase(1), 500);
          setTimeout(() => setAnimationPhase(2), 1500);
          setTimeout(() => setAnimationPhase(3), 2500);
          setTimeout(() => setAnimationPhase(4), 3500);
        } else {
          setVerificationStatus('error');
        }
      } catch (error) {
        console.error('Verification error:', error);
        setVerificationStatus('error');
      }
    };

    verifyEmail();
  }, [token]);

  const handleContinue = () => {
    router.push('/login');
  };

  if (verificationStatus === 'verifying') {
    return (
      <div className="verification-container">
        <div className="verification-content">
          <div className="loading-animation">
            <div className="loading-spinner"></div>
            <div className="loading-particles">
              {[...Array(8)].map((_, i) => (
                <div key={i} className={`particle particle-${i}`}></div>
              ))}
            </div>
          </div>
          <h2>Verifying your email...</h2>
          <p>Please wait while we confirm your account</p>
        </div>
      </div>
    );
  }

  if (verificationStatus === 'error') {
    return (
      <div className="verification-container error">
        <div className="verification-content">
          <div className="error-icon">❌</div>
          <h2>Verification Failed</h2>
          <p>The verification link is invalid or has expired.</p>
          <button className="retry-button" onClick={() => router.push('/login')}>
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="verification-container success">
      {/* Animated Background Elements */}
      <div className="success-bg">
        <div className="success-particles">
          {[...Array(20)].map((_, i) => (
            <div key={i} className={`bg-particle bg-particle-${i}`}></div>
          ))}
        </div>
        <div className="success-waves">
          <div className="wave wave-1"></div>
          <div className="wave wave-2"></div>
          <div className="wave wave-3"></div>
        </div>
        <div className="success-grid"></div>
      </div>

      <div className="verification-content">
        {/* Main Success Animation */}
        <div className={`success-animation phase-${animationPhase}`}>
          {/* Checkmark Animation */}
          <div className="checkmark-container">
            <div className="checkmark-circle">
              <div className="checkmark-stem"></div>
              <div className="checkmark-kick"></div>
            </div>
            <div className="checkmark-glow"></div>
          </div>

          {/* Floating Icons */}
          <div className="floating-icons">
            <div className="float-icon icon-1">🚀</div>
            <div className="float-icon icon-2">⚡</div>
            <div className="float-icon icon-3">🎯</div>
            <div className="float-icon icon-4">💰</div>
            <div className="float-icon icon-5">📊</div>
            <div className="float-icon icon-6">🔥</div>
          </div>

          {/* Success Burst */}
          <div className="success-burst">
            {[...Array(12)].map((_, i) => (
              <div key={i} className={`burst-ray ray-${i}`}></div>
            ))}
          </div>
        </div>

        {/* Text Content */}
        <div className={`success-text phase-${animationPhase}`}>
          <h1 className="success-title">
            <span className="title-line-1">Email Verified!</span>
            <span className="title-line-2">Welcome to the Future</span>
          </h1>
          
          <div className="success-subtitle">
            <p>Your restaurant's AI-powered journey begins now</p>
          </div>

          {/* Feature Teasers */}
          <div className={`feature-teasers phase-${animationPhase}`}>
            <div className="teaser-card teaser-1">
              <div className="teaser-icon">🧠</div>
              <span>AI Marketing</span>
            </div>
            <div className="teaser-card teaser-2">
              <div className="teaser-icon">📈</div>
              <span>Growth Analytics</span>
            </div>
            <div className="teaser-card teaser-3">
              <div className="teaser-icon">🎨</div>
              <span>Website Builder</span>
            </div>
          </div>

          {/* CTA Button */}
          <div className={`success-cta phase-${animationPhase}`}>
            <button className="continue-button" onClick={handleContinue}>
              <span className="button-text">Launch Your Platform</span>
              <div className="button-glow"></div>
              <div className="button-particles">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className={`btn-particle btn-particle-${i}`}></div>
                ))}
              </div>
            </button>
          </div>

          {/* Bottom Message */}
          <div className={`bottom-message phase-${animationPhase}`}>
            <p>🔥 Ready to transform your restaurant business?</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationSuccess;