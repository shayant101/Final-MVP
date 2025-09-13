import React, { useState } from 'react';
import { 
  BarChart, 
  ChefHat, 
  PenTool, 
  Brain,
  Sparkles,
  ArrowRight,
  Play,
  Settings,
  Activity,
  Zap,
  Clock,
  Users,
  TrendingUp
} from 'lucide-react';
import './AIFeatures.css';
import './AIFeaturesLanding.css';

const AIFeaturesLanding = () => {
  const [activePreview, setActivePreview] = useState<string | null>(null);

  const aiFeatures = [
    {
      id: 'grader',
      name: 'Digital Presence Grader',
      icon: <BarChart size={24} />,
      shortDesc: 'Analyze your restaurant\'s online presence',
      description: 'Get a comprehensive analysis of your website, Google Business Profile, and social media presence with actionable recommendations.',
      status: 'active',
      lastUsed: '2 hours ago',
      color: '#4F46E5',
      stats: { score: '72/100', issues: '5 found' },
      features: [
        'Website SEO Analysis',
        'Google Business Profile Review',
        'Social Media Audit',
        'Competitor Analysis'
      ]
    },
    {
      id: 'content',
      name: 'AI Content Creator',
      icon: <PenTool size={24} />,
      shortDesc: 'Generate and enhance marketing content',
      description: 'Create stunning marketing content with AI-powered image enhancement, social media posts, and campaign generation.',
      status: 'active',
      lastUsed: '1 day ago',
      color: '#7C3AED',
      stats: { created: '12 posts', enhanced: '8 images' },
      features: [
        'Image Enhancement & Upscaling',
        'Social Media Content Generation',
        'Marketing Copy Creation',
        'Brand Voice Optimization'
      ]
    },
    {
      id: 'menu',
      name: 'Smart Menu Optimizer',
      icon: <ChefHat size={24} />,
      shortDesc: 'Optimize menu performance and pricing',
      description: 'AI-driven menu analysis with pricing strategies, item recommendations, and profit margin optimization.',
      status: 'coming-soon',
      lastUsed: null,
      color: '#059669',
      stats: { items: '24 analyzed', profit: '+15%' },
      features: [
        'Menu Performance Analytics',
        'Dynamic Pricing Optimization',
        'Item Recommendations',
        'Seasonal Planning'
      ]
    },
    {
      id: 'analytics',
      name: 'AI Analytics Dashboard',
      icon: <Brain size={24} />,
      shortDesc: 'Advanced AI-powered insights',
      description: 'Predictive analytics, customer behavior insights, and automated reporting to optimize your marketing strategies.',
      status: 'coming-soon',
      lastUsed: null,
      color: '#DC2626',
      stats: { insights: '25 generated', accuracy: '94%' },
      features: [
        'Predictive Analytics',
        'Customer Behavior Analysis',
        'Revenue Forecasting',
        'Automated Reporting'
      ]
    }
  ];

  const handleFeatureClick = (featureId: string) => {
    if (featureId === 'grader') {
      const url = new URL(window.location.href);
      url.searchParams.set('view', 'digital-presence-grader');
      window.history.pushState({}, '', url.toString());
      window.location.reload();
    } else if (featureId === 'content') {
      const url = new URL(window.location.href);
      url.searchParams.set('view', 'content-creator');
      window.history.pushState({}, '', url.toString());
      window.location.reload();
    } else {
      alert('This feature is coming soon! Stay tuned for updates.');
    }
  };

  const quickStats = [
    { label: 'Active Features', value: '2', icon: <Activity size={16} /> },
    { label: 'Total Analyses', value: '47', icon: <BarChart size={16} /> },
    { label: 'Content Created', value: '156', icon: <PenTool size={16} /> },
    { label: 'Time Saved', value: '32h', icon: <Clock size={16} /> }
  ];

  return (
    <div className="ai-features-dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div className="header-main">
          <div className="header-title">
            <Sparkles size={28} />
            <div>
              <h1>AI Features</h1>
              <p>Intelligent tools to grow your restaurant business</p>
            </div>
          </div>
          <div className="header-stats">
            {quickStats.map((stat, index) => (
              <div key={index} className="quick-stat">
                <div className="stat-icon">{stat.icon}</div>
                <div className="stat-content">
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-label">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-dashboard-grid">
        {aiFeatures.map((feature) => (
          <div
            key={feature.id}
            className={`feature-dashboard-card ${feature.status === 'coming-soon' ? 'coming-soon' : ''}`}
            onMouseEnter={() => setActivePreview(feature.id)}
            onMouseLeave={() => setActivePreview(null)}
          >
            <div className="feature-card-header">
              <div className="feature-info">
                <div 
                  className="feature-icon"
                  style={{ backgroundColor: feature.color }}
                >
                  {feature.icon}
                </div>
                <div className="feature-title">
                  <h3>{feature.name}</h3>
                  <p className="feature-short-desc">{feature.shortDesc}</p>
                </div>
              </div>
              <div className="feature-status">
                {feature.status === 'active' && (
                  <span className="status-badge active">
                    <div className="status-indicator active"></div>
                    Active
                  </span>
                )}
                {feature.status === 'coming-soon' && (
                  <span className="status-badge coming-soon">Coming Soon</span>
                )}
              </div>
            </div>

            <div className="feature-stats">
              {Object.entries(feature.stats).map(([key, value]) => (
                <div key={key} className="stat-item">
                  <span className="stat-key">{key}:</span>
                  <span className="stat-value">{value}</span>
                </div>
              ))}
            </div>

            {feature.lastUsed && (
              <div className="feature-last-used">
                Last used: {feature.lastUsed}
              </div>
            )}

            <div className="feature-description">
              {feature.description}
            </div>

            {/* Feature Preview - shows on hover */}
            {activePreview === feature.id && (
              <div className="feature-preview">
                <h4>Key Features:</h4>
                <ul>
                  {feature.features.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="feature-actions">
              {feature.status === 'active' ? (
                <>
                  <button 
                    className="action-btn primary"
                    onClick={() => handleFeatureClick(feature.id)}
                    style={{ backgroundColor: feature.color }}
                  >
                    <Play size={16} />
                    Launch
                  </button>
                  <button className="action-btn secondary">
                    <Settings size={16} />
                    Settings
                  </button>
                </>
              ) : (
                <button className="action-btn disabled">
                  <Clock size={16} />
                  Coming Soon
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h2>
          <Activity size={20} />
          Recent Activity
        </h2>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon" style={{ backgroundColor: '#4F46E5' }}>
              <BarChart size={16} />
            </div>
            <div className="activity-content">
              <div className="activity-title">Digital presence analysis completed</div>
              <div className="activity-time">2 hours ago</div>
            </div>
            <div className="activity-result">Score: 72/100</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon" style={{ backgroundColor: '#7C3AED' }}>
              <PenTool size={16} />
            </div>
            <div className="activity-content">
              <div className="activity-title">3 social media posts generated</div>
              <div className="activity-time">1 day ago</div>
            </div>
            <div className="activity-result">Ready to publish</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon" style={{ backgroundColor: '#4F46E5' }}>
              <Sparkles size={16} />
            </div>
            <div className="activity-content">
              <div className="activity-title">Image enhancement completed</div>
              <div className="activity-time">2 days ago</div>
            </div>
            <div className="activity-result">5 images processed</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>
          <Zap size={20} />
          Quick Actions
        </h2>
        <div className="quick-actions-grid">
          <button 
            className="quick-action-btn"
            onClick={() => handleFeatureClick('grader')}
          >
            <BarChart size={20} />
            <span>Run Digital Analysis</span>
            <ArrowRight size={16} />
          </button>
          <button 
            className="quick-action-btn"
            onClick={() => handleFeatureClick('content')}
          >
            <PenTool size={20} />
            <span>Create Content</span>
            <ArrowRight size={16} />
          </button>
          <button className="quick-action-btn disabled">
            <ChefHat size={20} />
            <span>Optimize Menu</span>
            <Clock size={16} />
          </button>
          <button className="quick-action-btn disabled">
            <Brain size={20} />
            <span>View Analytics</span>
            <Clock size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIFeaturesLanding;