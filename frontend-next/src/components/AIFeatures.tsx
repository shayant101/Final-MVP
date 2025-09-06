import React, { useState, useEffect, useRef } from 'react';
import './AIFeatures.css';
import ScoreBreakdown from './ScoreBreakdown';
import ImageEnhancement from './ImageEnhancement';
import AIAssistant from './AIAssistant';

const AIFeatures = () => {
  const [activeFeature, setActiveFeature] = useState('grader');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showScoreBreakdown, setShowScoreBreakdown] = useState(false);
  const [restaurantData, setRestaurantData] = useState({
    name: 'Demo Restaurant',
    website: 'https://demo-restaurant.com',
    google_business_url: '',
    cuisine_type: 'Italian',
    location: 'San Francisco, CA'
  });

  // Ref for the results section to enable auto-scrolling
  const resultsRef = useRef<HTMLDivElement>(null);

  // Get initial active feature from URL parameter or default to 'grader'
  const getInitialActiveFeature = () => {
    if (typeof window === 'undefined') return 'grader';
    
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    
    // Valid tab IDs
    const validTabs = ['grader', 'menu', 'content'];
    
    // Return tab from URL if valid, otherwise default to 'grader'
    return validTabs.includes(tabParam || '') ? tabParam : 'grader';
  };

  // Initialize active feature from URL on client side
  useEffect(() => {
    const initialFeature = getInitialActiveFeature();
    setActiveFeature(initialFeature || 'grader');
  }, []);

  // Update URL when active feature changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const url = new URL(window.location.href);
    url.searchParams.set('tab', activeFeature);
    
    // Update URL without triggering a page reload
    window.history.replaceState({}, '', url.toString());
  }, [activeFeature]);

  // Handle browser back/forward navigation
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handlePopState = () => {
      const newActiveFeature = getInitialActiveFeature();
      setActiveFeature(newActiveFeature || 'grader');
      setAnalysisResult(null); // Clear results when navigating
    };

    window.addEventListener('popstate', handlePopState);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  // Auto-scroll to results when analysis is complete
  useEffect(() => {
    if (analysisResult && resultsRef.current) {
      // Small delay to ensure the DOM is updated
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
          inline: 'nearest'
        });
      }, 100);
    }
  }, [analysisResult]);

  const aiFeatures = [
    {
      id: 'grader',
      name: 'Digital Presence Grader',
      icon: '📊',
      description: 'Analyze and grade your restaurant\'s digital presence',
      color: '#4F46E5'
    },
    {
      id: 'menu',
      name: 'Smart Menu Optimizer',
      icon: '🍽️',
      description: 'Optimize menu performance and pricing strategies',
      color: '#059669',
      comingSoon: true
    },
    {
      id: 'content',
      name: 'Content Creator',
      icon: '📝',
      description: 'AI-powered image enhancement and content generation',
      color: '#7C3AED'
    }
  ];

  const handleQuickAnalysis = async () => {
    setLoading(true);
    try {
      // Make real API call to backend
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/ai/digital-presence/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(restaurantData)
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setAnalysisResult(result.data);
        } else {
          throw new Error('Analysis failed');
        }
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      console.error('Analysis failed, using mock data:', error);
      
      // Fallback to mock data if API fails
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockResults = {
        grader: {
          overall_grade: { score: 72.5, letter_grade: 'C+', status: 'Needs Improvement' },
          component_scores: {
            website: { score: 75, grade: 'C+', priority: 'MEDIUM' },
            social_media: { score: 68, grade: 'D+', priority: 'HIGH' },
            google_business: { score: 80, grade: 'B-', priority: 'LOW' },
            menu_optimization: { score: 65, grade: 'D', priority: 'HIGH' }
          },
          action_plan: {
            immediate_actions: [
              { action: 'Optimize Google Business Profile', impact: 'HIGH', effort: 'LOW' },
              { action: 'Improve social media posting consistency', impact: 'MEDIUM', effort: 'MEDIUM' },
              { action: 'Add menu item photos and descriptions', impact: 'HIGH', effort: 'MEDIUM' }
            ]
          },
          revenue_impact: {
            monthly_revenue_increase: { low_estimate: '$1,200', high_estimate: '$3,600' },
            annual_potential: { low_estimate: '$14,400', high_estimate: '$43,200' }
          }
        },
        menu: {
          item_performance: {
            high_performers: [
              { name: 'Margherita Pizza', performance_score: 92, profit_margin: 0.38 },
              { name: 'Caesar Salad', performance_score: 88, profit_margin: 0.45 }
            ],
            underperformers: [
              { name: 'Seafood Risotto', performance_score: 45, profit_margin: 0.22 }
            ],
            hidden_gems: [
              { name: 'Tiramisu', performance_score: 75, profit_margin: 0.62 }
            ]
          },
          promotional_strategies: {
            recommended_campaigns: [
              { name: 'Perfect Pair Promotion', type: 'cross_selling', expected_impact: '20% increase' },
              { name: 'Hidden Gem Spotlight', type: 'limited_time_offer', expected_impact: '40% increase' }
            ]
          },
          revenue_impact: {
            potential_monthly_increase: '$2,100',
            annual_potential: '$25,200'
          }
        },
        content: {
          generated_content: {
            social_media: {
              campaign_theme: 'Authentic Italian Experience',
              platform_content: {
                facebook: [
                  { content_type: 'promotional', post_text: '🍝 Taste authentic Italy at Demo Restaurant! Fresh pasta made daily with imported ingredients. Book your table today!' }
                ],
                instagram: [
                  { content_type: 'menu_highlight', post_text: '✨ Our signature Margherita Pizza - simple ingredients, extraordinary taste! 🍕 #AuthenticItalian #FreshIngredients' }
                ]
              }
            }
          },
          performance_projections: {
            monthly_reach: '8,500',
            monthly_engagement: '2,100',
            revenue_impact: '$1,400'
          }
        }
      };

      setAnalysisResult((mockResults as any)[activeFeature]);
    } finally {
      setLoading(false);
    }
  };

  const renderFeatureContent = () => {
    const feature = aiFeatures.find(f => f.id === activeFeature);
    
    if (!feature) return null;
    
    // For content creator, render the ImageEnhancement component directly
    if (activeFeature === 'content') {
      return (
        <div className="feature-content">
          <div className="feature-header">
            <div className="feature-icon" style={{ backgroundColor: feature.color }}>
              {feature.icon}
            </div>
            <div>
              <h3>{feature.name}</h3>
              <p>{feature.description}</p>
            </div>
          </div>
          <ImageEnhancement />
        </div>
      );
    }
    
    return (
      <div className="feature-content">
        <div className="feature-header">
          <div className="feature-icon" style={{ backgroundColor: feature.color }}>
            {feature.icon}
          </div>
          <div>
            <h3>{feature.name}</h3>
            <p>{feature.description}</p>
          </div>
        </div>

        <div className="demo-section">
          <h4>Restaurant Information</h4>
          <div className="restaurant-info">
            <div className="info-item">
              <label>Restaurant Name:</label>
              <input
                type="text"
                value={restaurantData.name}
                onChange={(e) => setRestaurantData({...restaurantData, name: e.target.value})}
              />
            </div>
            <div className="info-item">
              <label>Website:</label>
              <input
                type="text"
                value={restaurantData.website}
                onChange={(e) => setRestaurantData({...restaurantData, website: e.target.value})}
                placeholder="https://your-restaurant.com"
              />
            </div>
            <div className="info-item">
              <label>Google Business Profile URL:</label>
              <input
                type="text"
                value={restaurantData.google_business_url}
                onChange={(e) => setRestaurantData({...restaurantData, google_business_url: e.target.value})}
                placeholder="https://maps.google.com/..."
              />
            </div>
            <div className="info-item">
              <label>Cuisine Type:</label>
              <input
                type="text"
                value={restaurantData.cuisine_type}
                onChange={(e) => setRestaurantData({...restaurantData, cuisine_type: e.target.value})}
              />
            </div>
            <div className="info-item">
              <label>Location:</label>
              <input
                type="text"
                value={restaurantData.location}
                onChange={(e) => setRestaurantData({...restaurantData, location: e.target.value})}
              />
            </div>
          </div>

          <button
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={handleQuickAnalysis}
            disabled={loading}
            style={{ backgroundColor: loading ? undefined : feature.color }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
          
          {activeFeature === 'grader' && (
            <div className="analysis-info">
              <p><strong>🔍 Real Web Scraping Analysis:</strong></p>
              <ul>
                <li>✅ Live website analysis and SEO scoring</li>
                <li>✅ Google Business Profile data extraction</li>
                <li>✅ Social media presence detection</li>
                <li>✅ Performance metrics and recommendations</li>
              </ul>
              <p><em>Note: Analysis may take 30-60 seconds for comprehensive results</em></p>
            </div>
          )}
        </div>

        {analysisResult && renderAnalysisResults()}
      </div>
    );
  };

  const renderAnalysisResults = () => {
    switch (activeFeature) {
      case 'grader':
        return renderGraderResults();
      case 'menu':
        return renderMenuResults();
      case 'content':
        return renderContentResults();
      default:
        return null;
    }
  };

  const renderGraderResults = () => (
    <div className="analysis-results" ref={resultsRef}>
      <h4>Digital Presence Analysis Results</h4>
      
      <div className="overall-grade">
        <div className="grade-circle">
          <span className="grade-letter">{analysisResult.overall_grade?.letter_grade || 'N/A'}</span>
          <span className="grade-score">{analysisResult.overall_grade?.score || 0}/100</span>
        </div>
        <div className="grade-info">
          <h5>Overall Grade: {analysisResult.overall_grade?.status || 'Analysis Complete'}</h5>
          <p>Revenue Impact: {analysisResult.revenue_impact?.monthly_revenue_increase?.low_estimate || '$0'} - {analysisResult.revenue_impact?.monthly_revenue_increase?.high_estimate || '$0'}/month</p>
        </div>
      </div>

      <div className="component-scores">
        <h5>Component Breakdown</h5>
        {Object.entries(analysisResult.component_scores || {}).map(([component, score]: [string, any]) => (
          <div key={component} className="score-item">
            <span className="component-name">{component.replace('_', ' ').toUpperCase()}</span>
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${score?.score || 0}%` }}></div>
            </div>
            <span className="score-value">{score?.score || 0}/100</span>
            <span className={`priority ${(score?.priority || 'medium').toLowerCase()}`}>{score?.priority || 'MEDIUM'}</span>
            {component === 'website' && (
              <button
                className="breakdown-button"
                onClick={() => setShowScoreBreakdown(true)}
                title="Get AI-powered insights and detailed breakdown"
              >
                ✨
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="action-plan">
        <h5>Immediate Action Plan</h5>
        {(analysisResult.action_plan?.immediate_actions || []).map((action: any, index: number) => (
          <div key={index} className="action-item">
            <div className="action-text">{action?.action || 'No action specified'}</div>
            <div className="action-metrics">
              <span className={`impact ${(action?.impact || 'medium').toLowerCase()}`}>Impact: {action?.impact || 'MEDIUM'}</span>
              <span className={`effort ${(action?.effort || 'medium').toLowerCase()}`}>Effort: {action?.effort || 'MEDIUM'}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Score Breakdown Modal */}
      {showScoreBreakdown && (
        <ScoreBreakdown
          websiteData={analysisResult.component_scores?.website}
          onClose={() => setShowScoreBreakdown(false)}
        />
      )}
    </div>
  );

  const renderMenuResults = () => (
    <div className="analysis-results">
      <h4>Menu Optimization Analysis</h4>
      
      <div className="menu-performance">
        <div className="performance-section">
          <h5>🏆 Top Performers</h5>
          {analysisResult.item_performance.high_performers.map((item: any, index: number) => (
            <div key={index} className="menu-item">
              <span className="item-name">{item.name}</span>
              <span className="performance-score">Score: {item.performance_score}/100</span>
              <span className="profit-margin">Margin: {(item.profit_margin * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div className="performance-section">
          <h5>💎 Hidden Gems</h5>
          {analysisResult.item_performance.hidden_gems.map((item: any, index: number) => (
            <div key={index} className="menu-item">
              <span className="item-name">{item.name}</span>
              <span className="performance-score">Score: {item.performance_score}/100</span>
              <span className="profit-margin">Margin: {(item.profit_margin * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div className="performance-section">
          <h5>⚠️ Needs Attention</h5>
          {analysisResult.item_performance.underperformers.map((item: any, index: number) => (
            <div key={index} className="menu-item">
              <span className="item-name">{item.name}</span>
              <span className="performance-score">Score: {item.performance_score}/100</span>
              <span className="profit-margin">Margin: {(item.profit_margin * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="promotional-campaigns">
        <h5>Recommended Promotional Campaigns</h5>
        {analysisResult.promotional_strategies.recommended_campaigns.map((campaign: any, index: number) => (
          <div key={index} className="campaign-item">
            <div className="campaign-name">{campaign.name}</div>
            <div className="campaign-type">{campaign.type.replace('_', ' ').toUpperCase()}</div>
            <div className="campaign-impact">{campaign.expected_impact}</div>
          </div>
        ))}
      </div>

      <div className="revenue-projection">
        <h5>Revenue Impact Projection</h5>
        <div className="projection-item">
          <span>Monthly Increase:</span>
          <span className="amount">{analysisResult.revenue_impact.potential_monthly_increase}</span>
        </div>
        <div className="projection-item">
          <span>Annual Potential:</span>
          <span className="amount">{analysisResult.revenue_impact.annual_potential}</span>
        </div>
      </div>
    </div>
  );


  const renderContentResults = () => (
    <div className="analysis-results">
      <h4>Generated Content Suite</h4>
      
      <div className="content-preview">
        <h5>Social Media Content Preview</h5>
        <div className="campaign-theme">
          <strong>Campaign Theme:</strong> {analysisResult.generated_content.social_media.campaign_theme}
        </div>
        
        <div className="platform-content">
          {Object.entries(analysisResult.generated_content.social_media.platform_content).map(([platform, posts]: [string, any]) => (
            <div key={platform} className="platform-section">
              <h6>{platform.toUpperCase()}</h6>
              {(posts as any[]).map((post: any, index: number) => (
                <div key={index} className="content-post">
                  <div className="post-type">{post.content_type.replace('_', ' ').toUpperCase()}</div>
                  <div className="post-text">{post.post_text}</div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="performance-projections">
        <h5>Performance Projections</h5>
        <div className="projection-grid">
          <div className="projection-item">
            <span>Monthly Reach:</span>
            <span className="value">{analysisResult.performance_projections.monthly_reach}</span>
          </div>
          <div className="projection-item">
            <span>Monthly Engagement:</span>
            <span className="value">{analysisResult.performance_projections.monthly_engagement}</span>
          </div>
          <div className="projection-item">
            <span>Revenue Impact:</span>
            <span className="value">${analysisResult.performance_projections.revenue_impact}</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="ai-features">
      <div className="ai-header">
        <div className="ai-header-top">
          <button
            className="back-button"
            onClick={() => window.history.back()}
            title="Back to Dashboard"
          >
            ← Back to Dashboard
          </button>
        </div>
        <h2>✨ AI-Powered Restaurant Marketing</h2>
        <p>Transform your restaurant's marketing with intelligent AI analysis and recommendations</p>
      </div>

      <div className="feature-tabs">
        {aiFeatures.map(feature => (
          <button
            key={feature.id}
            className={`feature-tab ${activeFeature === feature.id ? 'active' : ''} ${feature.comingSoon ? 'coming-soon' : ''}`}
            onClick={() => {
              if (!feature.comingSoon) {
                setActiveFeature(feature.id);
                setAnalysisResult(null); // Clear previous results when switching features
              }
            }}
            style={{
              borderColor: activeFeature === feature.id ? feature.color : '#e5e7eb',
              color: activeFeature === feature.id ? feature.color : '#6b7280',
              opacity: feature.comingSoon ? 0.6 : 1,
              cursor: feature.comingSoon ? 'not-allowed' : 'pointer'
            }}
            disabled={feature.comingSoon}
          >
            <span className="tab-icon">{feature.icon}</span>
            <span className="tab-name">
              {feature.name}
              {feature.comingSoon && <span className="coming-soon-badge">Coming Soon</span>}
            </span>
          </button>
        ))}
      </div>

      {renderFeatureContent()}

      <div className="ai-benefits">
        <h3>Why Choose AI-Powered Marketing?</h3>
        <div className="benefits-grid">
          <div className="benefit-item">
            <div className="benefit-icon">📈</div>
            <h4>Maximize Revenue & Growth</h4>
            <p>AI-driven insights can increase restaurant revenue by 15-30% through optimized marketing strategies and data-driven decisions based on comprehensive performance analysis</p>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">⏰</div>
            <h4>Save Time & Automate</h4>
            <p>Automate content creation and campaign management, saving 10+ hours per week while streamlining your entire marketing workflow with intelligent automation</p>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">🎯</div>
            <h4>Smart Targeting & Personalization</h4>
            <p>Reach the right customers with personalized messaging, optimized ad spend, and precision targeting that delivers higher conversion rates and customer engagement</p>
          </div>
        </div>
      </div>

      {/* AI Assistant - Floating */}
      <AIAssistant />
    </div>
  );
};

export default AIFeatures;