import React, { useState } from 'react';
import './AIFeatures.css';

const AIFeatures = () => {
  const [activeFeature, setActiveFeature] = useState('grader');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [restaurantData, setRestaurantData] = useState({
    name: 'Demo Restaurant',
    website: 'https://demo-restaurant.com',
    cuisine_type: 'Italian',
    location: 'San Francisco, CA'
  });

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
      color: '#059669'
    },
    {
      id: 'marketing',
      name: 'AI Marketing Assistant',
      icon: '🎯',
      description: 'Get personalized marketing recommendations',
      color: '#DC2626'
    },
    {
      id: 'content',
      name: 'Content Generation Engine',
      icon: '✨',
      description: 'Generate marketing content across all channels',
      color: '#7C3AED'
    }
  ];

  const handleQuickAnalysis = async () => {
    setLoading(true);
    try {
      // Simulate API call with mock data
      await new Promise(resolve => setTimeout(resolve, 2000));
      
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
        marketing: {
          campaign_recommendations: {
            recommended_campaigns: [
              { name: 'Local Social Media Campaign', budget_allocation: 200, target_metrics: { reach: '10,000+' } },
              { name: 'Google Ads Local Search', budget_allocation: 150, target_metrics: { ctr: '3%+' } }
            ]
          },
          roi_projections: {
            estimated_monthly_revenue_increase: '$1,800',
            projected_roi: '240%'
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

      setAnalysisResult(mockResults[activeFeature]);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderFeatureContent = () => {
    const feature = aiFeatures.find(f => f.id === activeFeature);
    
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
            className="analyze-button"
            onClick={handleQuickAnalysis}
            disabled={loading}
            style={{ backgroundColor: feature.color }}
          >
            {loading ? 'Analyzing...' : `Run ${feature.name} Demo`}
          </button>
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
      case 'marketing':
        return renderMarketingResults();
      case 'content':
        return renderContentResults();
      default:
        return null;
    }
  };

  const renderGraderResults = () => (
    <div className="analysis-results">
      <h4>Digital Presence Analysis Results</h4>
      
      <div className="overall-grade">
        <div className="grade-circle">
          <span className="grade-letter">{analysisResult.overall_grade.letter_grade}</span>
          <span className="grade-score">{analysisResult.overall_grade.score}/100</span>
        </div>
        <div className="grade-info">
          <h5>Overall Grade: {analysisResult.overall_grade.status}</h5>
          <p>Revenue Impact: {analysisResult.revenue_impact.monthly_revenue_increase.low_estimate} - {analysisResult.revenue_impact.monthly_revenue_increase.high_estimate}/month</p>
        </div>
      </div>

      <div className="component-scores">
        <h5>Component Breakdown</h5>
        {Object.entries(analysisResult.component_scores).map(([component, score]) => (
          <div key={component} className="score-item">
            <span className="component-name">{component.replace('_', ' ').toUpperCase()}</span>
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${score.score}%` }}></div>
            </div>
            <span className="score-value">{score.score}/100</span>
            <span className={`priority ${score.priority.toLowerCase()}`}>{score.priority}</span>
          </div>
        ))}
      </div>

      <div className="action-plan">
        <h5>Immediate Action Plan</h5>
        {analysisResult.action_plan.immediate_actions.map((action, index) => (
          <div key={index} className="action-item">
            <div className="action-text">{action.action}</div>
            <div className="action-metrics">
              <span className={`impact ${action.impact.toLowerCase()}`}>Impact: {action.impact}</span>
              <span className={`effort ${action.effort.toLowerCase()}`}>Effort: {action.effort}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMenuResults = () => (
    <div className="analysis-results">
      <h4>Menu Optimization Analysis</h4>
      
      <div className="menu-performance">
        <div className="performance-section">
          <h5>🏆 Top Performers</h5>
          {analysisResult.item_performance.high_performers.map((item, index) => (
            <div key={index} className="menu-item">
              <span className="item-name">{item.name}</span>
              <span className="performance-score">Score: {item.performance_score}/100</span>
              <span className="profit-margin">Margin: {(item.profit_margin * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div className="performance-section">
          <h5>💎 Hidden Gems</h5>
          {analysisResult.item_performance.hidden_gems.map((item, index) => (
            <div key={index} className="menu-item">
              <span className="item-name">{item.name}</span>
              <span className="performance-score">Score: {item.performance_score}/100</span>
              <span className="profit-margin">Margin: {(item.profit_margin * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>

        <div className="performance-section">
          <h5>⚠️ Needs Attention</h5>
          {analysisResult.item_performance.underperformers.map((item, index) => (
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
        {analysisResult.promotional_strategies.recommended_campaigns.map((campaign, index) => (
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

  const renderMarketingResults = () => (
    <div className="analysis-results">
      <h4>Marketing Strategy Recommendations</h4>
      
      <div className="campaign-recommendations">
        <h5>Recommended Campaigns</h5>
        {analysisResult.campaign_recommendations.recommended_campaigns.map((campaign, index) => (
          <div key={index} className="campaign-card">
            <div className="campaign-header">
              <h6>{campaign.name}</h6>
              <span className="budget">${campaign.budget_allocation}/month</span>
            </div>
            <div className="campaign-metrics">
              {Object.entries(campaign.target_metrics).map(([metric, value]) => (
                <span key={metric} className="metric">
                  {metric.replace('_', ' ').toUpperCase()}: {value}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="roi-projection">
        <h5>ROI Projections</h5>
        <div className="roi-item">
          <span>Monthly Revenue Increase:</span>
          <span className="amount">{analysisResult.roi_projections.estimated_monthly_revenue_increase}</span>
        </div>
        <div className="roi-item">
          <span>Projected ROI:</span>
          <span className="percentage">{analysisResult.roi_projections.projected_roi}</span>
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
          {Object.entries(analysisResult.generated_content.social_media.platform_content).map(([platform, posts]) => (
            <div key={platform} className="platform-section">
              <h6>{platform.toUpperCase()}</h6>
              {posts.map((post, index) => (
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
        <h2>🧠 AI-Powered Restaurant Marketing</h2>
        <p>Transform your restaurant's marketing with intelligent AI analysis and recommendations</p>
      </div>

      <div className="feature-tabs">
        {aiFeatures.map(feature => (
          <button
            key={feature.id}
            className={`feature-tab ${activeFeature === feature.id ? 'active' : ''}`}
            onClick={() => {
              setActiveFeature(feature.id);
              setAnalysisResult(null); // Clear previous results when switching features
            }}
            style={{
              borderColor: activeFeature === feature.id ? feature.color : '#e5e7eb',
              color: activeFeature === feature.id ? feature.color : '#6b7280'
            }}
          >
            <span className="tab-icon">{feature.icon}</span>
            <span className="tab-name">{feature.name}</span>
          </button>
        ))}
      </div>

      {renderFeatureContent()}

      <div className="ai-benefits">
        <h3>Why Choose AI-Powered Marketing?</h3>
        <div className="benefits-grid">
          <div className="benefit-item">
            <div className="benefit-icon">📈</div>
            <h4>Increase Revenue</h4>
            <p>AI-driven insights can increase restaurant revenue by 15-30% through optimized marketing strategies</p>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">⏰</div>
            <h4>Save Time</h4>
            <p>Automate content creation and campaign management, saving 10+ hours per week</p>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">🎯</div>
            <h4>Better Targeting</h4>
            <p>Reach the right customers with personalized messaging and optimized ad spend</p>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">📊</div>
            <h4>Data-Driven Decisions</h4>
            <p>Make informed decisions based on AI analysis of your restaurant's performance data</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFeatures;