import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import MarketingAIAssistant from './MarketingAIAssistant';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="landing-container">
      {/* Enhanced Geometric Background Elements */}
      <div className="geometric-bg">
        {/* Grid pattern overlay */}
        <div className="geo-grid-pattern"></div>
        
        {/* Original enhanced shapes */}
        <div className="geo-shape geo-circle-1"></div>
        <div className="geo-shape geo-triangle-1"></div>
        <div className="geo-shape geo-square-1"></div>
        <div className="geo-shape geo-circle-2"></div>
        
        {/* New geometric elements */}
        <div className="geo-shape geo-hexagon-1"></div>
        <div className="geo-shape geo-diamond-1"></div>
        
        {/* Circuit pattern */}
        <div className="geo-circuit-pattern">
          <div className="circuit-line circuit-line-1"></div>
          <div className="circuit-line circuit-line-2"></div>
          <div className="circuit-line circuit-line-3"></div>
          <div className="circuit-node circuit-node-1"></div>
          <div className="circuit-node circuit-node-2"></div>
        </div>
        
        {/* Dot matrix pattern */}
        <div className="geo-dots-pattern"></div>
      </div>
      
      {/* Fixed Header */}
      <header className="landing-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-container">
              <div className="logo-icon">🚀</div>
              <h1 className="logo">Uplit</h1>
            </div>
          </div>
          <nav className="header-nav">
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
              <div className="theme-toggle-track">
                <div className="theme-toggle-thumb">
                  <span className="theme-toggle-icon">
                    {theme === 'dark' ? '🌙' : '☀️'}
                  </span>
                </div>
              </div>
            </button>
            <button className="login-btn" onClick={handleLogin}>
              <span>Login</span>
              <div className="btn-glow"></div>
            </button>
          </nav>
        </div>
      </header>

      {/* Marketing AI Assistant for customer acquisition */}
      <MarketingAIAssistant />

      {/* Main Content Wrapper */}
      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            {/* AI Badge - Prominently positioned at top */}
            <div className="hero-badge">
              <span className="badge-icon">🤖</span>
              <span>AI-Powered Restaurant Marketing</span>
            </div>
            
            {/* Improved headline with better line breaks and balance - Option B (Emphasizing Action) */}
            <h1 className="hero-title">
              <span className="title-line-1">Transform</span>
              <span className="title-line-2">Your Restaurant with</span>
              <span className="title-line-3"><span className="gradient-text">Intelligent Automation</span></span>
            </h1>
            
            {/* Enhanced subtitle with better hierarchy */}
            <div className="hero-subtitle-container">
              <p className="hero-subtitle-main">
                Advanced AI marketing platform designed exclusively for restaurants
              </p>
              <p className="hero-subtitle-secondary">
                Automate customer acquisition, optimize retention, and scale revenue with precision-engineered technology
              </p>
            </div>
            
            {/* Performance stats with improved spacing */}
            <div className="hero-stats">
              <div className="stat-pill">
                <span className="stat-number">3.2x</span>
                <span className="stat-text">Revenue Growth</span>
              </div>
              <div className="stat-pill">
                <span className="stat-number">89%</span>
                <span className="stat-text">Time Saved</span>
              </div>
              <div className="stat-pill">
                <span className="stat-number">24/7</span>
                <span className="stat-text">Automation</span>
              </div>
            </div>
            
            {/* CTA buttons with better prominence */}
            <div className="hero-cta">
              <button className="cta-button primary" onClick={handleGetStarted}>
                <span>Launch Platform</span>
                <div className="btn-arrow">→</div>
              </button>
              <button className="cta-button secondary">
                <span>View Demo</span>
              </button>
            </div>
            
            {/* Trust indicators with better organization */}
            <div className="hero-trust-indicators">
              <p className="cta-subtext">
                <span className="security-badge">🔒</span>
                Enterprise-grade security • No setup fees • 14-day trial
              </p>
            </div>
          </div>
          <div className="hero-visual">
            <div className="dashboard-preview">
              <div className="dashboard-header">
                <div className="dashboard-controls">
                  <div className="control-dot red"></div>
                  <div className="control-dot yellow"></div>
                  <div className="control-dot green"></div>
                </div>
                <div className="dashboard-title">Restaurant Intelligence Hub</div>
              </div>
              <div className="dashboard-content">
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">📊</span>
                    <span className="metric-label">Customer Acquisition</span>
                  </div>
                  <div className="metric-value">+247%</div>
                  <div className="metric-trend">↗ +32% this week</div>
                </div>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">💰</span>
                    <span className="metric-label">Revenue Impact</span>
                  </div>
                  <div className="metric-value">$18.4K</div>
                  <div className="metric-trend">↗ +156% ROI</div>
                </div>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-icon">🎯</span>
                    <span className="metric-label">Campaign Performance</span>
                  </div>
                  <div className="metric-value">94.2%</div>
                  <div className="metric-trend">↗ Above industry avg</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </section>

        {/* Technology Features Section */}
        <section className="tech-features-section">
        <div className="tech-content">
          <div className="section-header">
            <h2 className="section-title">Restaurant-Focused AI Technology</h2>
            <p className="section-subtitle">
              Purpose-built algorithms that understand restaurant operations, customer behavior, and market dynamics
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-container">
                <div className="feature-icon">🧠</div>
                <div className="icon-glow"></div>
              </div>
              <h3>Predictive Customer Analytics</h3>
              <p>Machine learning models analyze dining patterns, preferences, and lifetime value to optimize targeting strategies.</p>
              <div className="feature-tech">
                <span className="tech-tag">ML</span>
                <span className="tech-tag">Predictive Analytics</span>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon-container">
                <div className="feature-icon">⚡</div>
                <div className="icon-glow"></div>
              </div>
              <h3>Real-Time Campaign Optimization</h3>
              <p>Automated A/B testing and performance optimization across all marketing channels with instant adjustments.</p>
              <div className="feature-tech">
                <span className="tech-tag">Real-time</span>
                <span className="tech-tag">Auto-optimization</span>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon-container">
                <div className="feature-icon">🎯</div>
                <div className="icon-glow"></div>
              </div>
              <h3>Hyper-Personalized Messaging</h3>
              <p>AI-generated content tailored to individual customer preferences, dining history, and behavioral triggers.</p>
              <div className="feature-tech">
                <span className="tech-tag">NLP</span>
                <span className="tech-tag">Personalization</span>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon-container">
                <div className="feature-icon">📡</div>
                <div className="icon-glow"></div>
              </div>
              <h3>Omnichannel Integration</h3>
              <p>Seamless coordination across SMS, email, social media, and review platforms with unified customer profiles.</p>
              <div className="feature-tech">
                <span className="tech-tag">API Integration</span>
                <span className="tech-tag">Multi-channel</span>
              </div>
            </div>
          </div>
        </div>
        </section>

        {/* Performance Metrics Section */}
        <section className="metrics-section">
        <div className="metrics-content">
          <div className="metrics-header">
            <h2 className="section-title">Measurable Restaurant Growth</h2>
            <p className="section-subtitle">Data-driven results from restaurants using our platform</p>
          </div>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-visual">
                <div className="metric-chart">
                  <div className="chart-bar" style={{height: '85%'}}></div>
                  <div className="chart-bar" style={{height: '92%'}}></div>
                  <div className="chart-bar" style={{height: '78%'}}></div>
                  <div className="chart-bar" style={{height: '95%'}}></div>
                </div>
              </div>
              <div className="metric-number">1,247</div>
              <div className="metric-label">Restaurants Powered</div>
            </div>
            <div className="metric-item">
              <div className="metric-visual">
                <div className="metric-circle">
                  <div className="circle-progress" style={{'--progress': '89%'}}></div>
                  <span className="circle-text">89%</span>
                </div>
              </div>
              <div className="metric-number">$4.2M+</div>
              <div className="metric-label">Additional Revenue Generated</div>
            </div>
            <div className="metric-item">
              <div className="metric-visual">
                <div className="metric-trend">
                  <div className="trend-line"></div>
                  <div className="trend-points">
                    <div className="trend-point"></div>
                    <div className="trend-point"></div>
                    <div className="trend-point active"></div>
                  </div>
                </div>
              </div>
              <div className="metric-number">312%</div>
              <div className="metric-label">Average ROI Increase</div>
            </div>
            <div className="metric-item">
              <div className="metric-visual">
                <div className="metric-gauge">
                  <div className="gauge-arc"></div>
                  <div className="gauge-needle"></div>
                </div>
              </div>
              <div className="metric-number">4.8/5</div>
              <div className="metric-label">Platform Satisfaction Score</div>
            </div>
          </div>
        </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
        <div className="cta-content">
          <div className="cta-visual">
            <div className="cta-icon">🚀</div>
            <div className="cta-particles">
              <div className="particle"></div>
              <div className="particle"></div>
              <div className="particle"></div>
            </div>
          </div>
          <h2 className="cta-title">Ready to Scale Your Restaurant?</h2>
          <p className="cta-subtitle">
            Join the next generation of data-driven restaurants. Deploy enterprise-grade marketing automation in minutes.
          </p>
          <div className="cta-buttons">
            <button className="cta-button primary large" onClick={handleGetStarted}>
              <span>Start Free Trial</span>
              <div className="btn-arrow">→</div>
            </button>
            <button className="cta-button secondary large">
              <span>Schedule Demo</span>
            </button>
          </div>
          <div className="cta-features">
            <div className="cta-feature">
              <span className="feature-check">✓</span>
              <span>14-day free trial</span>
            </div>
            <div className="cta-feature">
              <span className="feature-check">✓</span>
              <span>No setup fees</span>
            </div>
            <div className="cta-feature">
              <span className="feature-check">✓</span>
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">
              <div className="logo-icon">🚀</div>
              <h3>Uplit</h3>
            </div>
            <p>Next-generation marketing automation for restaurants</p>
            <div className="footer-social">
              <a href="#" className="social-link">LinkedIn</a>
              <a href="#" className="social-link">Twitter</a>
              <a href="#" className="social-link">GitHub</a>
            </div>
          </div>
          <div className="footer-links">
            <div className="link-group">
              <h4>Platform</h4>
              <a href="#features">AI Features</a>
              <a href="#analytics">Analytics</a>
              <a href="#integrations">Integrations</a>
              <a href="#api">API Docs</a>
            </div>
            <div className="link-group">
              <h4>Solutions</h4>
              <a href="#restaurants">Restaurants</a>
              <a href="#chains">Restaurant Chains</a>
              <a href="#franchises">Franchises</a>
              <a href="#enterprise">Enterprise</a>
            </div>
            <div className="link-group">
              <h4>Resources</h4>
              <a href="#docs">Documentation</a>
              <a href="#support">Support</a>
              <a href="#blog">Blog</a>
              <a href="#case-studies">Case Studies</a>
            </div>
            <div className="link-group">
              <h4>Company</h4>
              <a href="#about">About</a>
              <a href="#careers">Careers</a>
              <a href="#privacy">Privacy</a>
              <a href="#terms">Terms</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p>&copy; 2025 Uplit Technologies. All rights reserved.</p>
            <div className="footer-badges">
              <span className="security-badge">🔒 SOC 2 Compliant</span>
              <span className="security-badge">🛡️ GDPR Ready</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;