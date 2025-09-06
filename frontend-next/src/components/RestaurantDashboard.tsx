'use client';

import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
// import WebsiteBuilder from './WebsiteBuilder/WebsiteBuilder';
// import GetNewCustomers from './GetNewCustomers';
// import BringBackRegulars from './BringBackRegulars';
// import MarketingFoundations from './MarketingFoundations';
// import AIFeatures from './AIFeatures';
import './RestaurantDashboard.css';

interface RestaurantDashboardProps {
  setActiveTab: (tab: string) => void;
}

interface DashboardData {
  restaurant: {
    name: string;
    email: string;
    status: string;
  };
  performanceSnapshot: {
    period: string;
    newCustomersAcquired: number;
    customersReengaged: number;
  };
  activeCampaigns: Array<{
    campaign_id: string;
    name: string;
    campaign_type: string;
    status: string;
  }>;
  momentumMetrics?: {
    marketingScore: number;
    weeklyRevenuePotential: number;
    completedRevenue: number;
    totalPotential: number;
    foundationalProgress?: {
      percentage: number;
    };
    ongoingProgress?: {
      percentage: number;
    };
  };
}

const RestaurantDashboard: React.FC<RestaurantDashboardProps> = ({ setActiveTab }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getRestaurantDashboard();
      setDashboardData(data);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  const { restaurant, performanceSnapshot, activeCampaigns } = dashboardData!;

  return (
    <div className="restaurant-dashboard">
      {/* Left Sidebar Navigation */}
      <div className={`restaurant-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-title">
            {!sidebarCollapsed && (
              <>
                <h2>🍽️ {restaurant.name}</h2>
                <p>Growth Command Center</p>
              </>
            )}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={toggleSidebar}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {/* Dashboard Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">📊 Dashboard</div>}
            <button
              className={`nav-item ${activeView === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveView('overview')}
              title="Dashboard Overview"
            >
              <span className="nav-icon">📈</span>
              {!sidebarCollapsed && <span className="nav-label">Dashboard Overview</span>}
            </button>
          </div>

          {/* Marketing Tools Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">🚀 Marketing Tools</div>}
            <button
              className={`nav-item ${activeView === 'get-new-customers' ? 'active' : ''}`}
              onClick={() => setActiveView('get-new-customers')}
              title="Get New Customers"
            >
              <span className="nav-icon">🎯</span>
              {!sidebarCollapsed && <span className="nav-label">Get New Customers</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'bring-back-regulars' ? 'active' : ''}`}
              onClick={() => setActiveView('bring-back-regulars')}
              title="Bring Back Regulars"
            >
              <span className="nav-icon">💬</span>
              {!sidebarCollapsed && <span className="nav-label">Bring Back Regulars</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'website-builder' ? 'active' : ''}`}
              onClick={() => setActiveView('website-builder')}
              title="Website Builder"
            >
              <span className="nav-icon">🌐</span>
              {!sidebarCollapsed && <span className="nav-label">Website Builder</span>}
            </button>
          </div>

          {/* AI Features Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">🤖 AI Features</div>}
            <button
              className={`nav-item ${activeView === 'ai-features' ? 'active' : ''}`}
              onClick={() => setActiveView('ai-features')}
              title="AI Features"
            >
              <span className="nav-icon">🧠</span>
              {!sidebarCollapsed && <span className="nav-label">AI Features</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'marketing-foundations' ? 'active' : ''}`}
              onClick={() => setActiveView('marketing-foundations')}
              title="Marketing Foundations"
            >
              <span className="nav-icon">📚</span>
              {!sidebarCollapsed && <span className="nav-label">Marketing Foundations</span>}
            </button>
          </div>

          {/* Account Section */}
          <div className="nav-section logout-section">
            <button
              className="nav-item theme-toggle"
              onClick={toggleTheme}
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              <span className="nav-icon">{isDark ? '☀️' : '🌙'}</span>
              {!sidebarCollapsed && <span className="nav-label">{isDark ? 'Light Mode' : 'Dark Mode'}</span>}
            </button>
            <button
              className="nav-item logout-button"
              onClick={handleLogout}
              title="Logout"
            >
              <span className="nav-icon">🚪</span>
              {!sidebarCollapsed && <span className="nav-label">Logout</span>}
            </button>
          </div>
        </nav>
      </div>

      {/* Main Content Area */}
      <div className={`restaurant-main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Header */}
        <div className="main-header">
          <div className="header-title">
            <h1>
              {activeView === 'overview' && 'Your Growth Command Center'}
              {activeView === 'get-new-customers' && 'Get New Customers'}
              {activeView === 'bring-back-regulars' && 'Bring Back Regulars'}
              {activeView === 'website-builder' && 'Website Builder'}
              {activeView === 'ai-features' && 'AI Features'}
              {activeView === 'marketing-foundations' && 'Marketing Foundations'}
            </h1>
            <p>
              {activeView === 'overview' && `Welcome back to ${restaurant.name}!`}
              {activeView === 'get-new-customers' && 'Launch Facebook ads to attract new customers'}
              {activeView === 'bring-back-regulars' && 'Send SMS campaigns to re-engage customers'}
              {activeView === 'website-builder' && 'Create stunning AI-powered restaurant websites'}
              {activeView === 'ai-features' && 'Unlock AI-powered growth tools'}
              {activeView === 'marketing-foundations' && 'Build your marketing foundation'}
            </p>
          </div>
        </div>

        {/* Content Area */}
        <div className="content-area">
          {activeView === 'overview' && (
            <div className="overview-content">
              <div className="dashboard-grid">
                {/* Analytics */}
                <div className="dashboard-card performance-card">
                  <div className="card-header">
                    <h3>📊 Analytics</h3>
                    <span className="period">{performanceSnapshot.period}</span>
                  </div>
                  <div className="performance-metrics">
                    <div className="metric">
                      <div className="metric-value">{performanceSnapshot.newCustomersAcquired}</div>
                      <div className="metric-label">New Customers Acquired</div>
                    </div>
                    <div className="metric">
                      <div className="metric-value">{performanceSnapshot.customersReengaged}</div>
                      <div className="metric-label">Customers Re-engaged</div>
                    </div>
                  </div>
                  
                  {/* Compact Performance Insights */}
                  <div className="performance-insights-compact">
                    <div className="compact-stats">
                      <div className="compact-stat">
                        <span className="compact-value">${Math.round((performanceSnapshot.newCustomersAcquired * 45) + (performanceSnapshot.customersReengaged * 32))}</span>
                        <span className="compact-label">Revenue Generated</span>
                      </div>
                      <div className="compact-stat">
                        <span className="compact-value">{performanceSnapshot.newCustomersAcquired + performanceSnapshot.customersReengaged}</span>
                        <span className="compact-label">Total Customers</span>
                      </div>
                      <div className="compact-stat">
                        <span className="compact-value">{Math.round(((performanceSnapshot.newCustomersAcquired + performanceSnapshot.customersReengaged) / 25) * 100)}%</span>
                        <span className="compact-label">Growth Rate</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Campaigns */}
                <div className="dashboard-card campaigns-card">
                  <div className="card-header">
                    <h3>🚀 Campaigns</h3>
                    <button
                      className="view-all-button"
                      onClick={() => setActiveView('get-new-customers')}
                    >
                      View All
                    </button>
                  </div>
                  <div className="campaigns-list">
                    {activeCampaigns.length > 0 ? (
                      activeCampaigns.map(campaign => (
                        <div key={campaign.campaign_id} className="campaign-item">
                          <div className="campaign-info">
                            <div className="campaign-name">{campaign.name}</div>
                            <div className="campaign-type">
                              {campaign.campaign_type === 'ad' ? '📱 Facebook Ad' : '💬 SMS Campaign'}
                            </div>
                          </div>
                          <div className="campaign-status">
                            <span className={`status-badge ${campaign.status}`}>
                              {campaign.status}
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="growth-potential-visual">
                        <div className="visual-header">
                          <p>Your progress vs campaign potential</p>
                        </div>
                        <div className="line-chart">
                          <div className="chart-container">
                            <svg className="line-graph" viewBox="0 0 280 100" preserveAspectRatio="xMidYMid meet">
                              {/* Grid lines */}
                              <defs>
                                <pattern id="grid" width="56" height="20" patternUnits="userSpaceOnUse">
                                  <path d="M 56 0 L 0 0 0 20" fill="none" stroke="rgba(1, 90, 246, 0.1)" strokeWidth="0.5"/>
                                </pattern>
                              </defs>
                              <rect width="280" height="100" fill="url(#grid)" />
                              
                              {/* Current progress line (solid) */}
                              <polyline
                                fill="none"
                                stroke="var(--color-brand-blue)"
                                strokeWidth="2"
                                points="20,80 76,70 132,75 188,65 244,60"
                                className="progress-line"
                              />
                              
                              {/* Campaign potential line (dotted) */}
                              <polyline
                                fill="none"
                                stroke="rgba(34, 197, 94, 0.8)"
                                strokeWidth="2"
                                strokeDasharray="4,3"
                                points="20,80 76,60 132,45 188,30 244,20"
                                className="potential-line"
                              />
                              
                              {/* Data points for current progress */}
                              <circle cx="20" cy="80" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="76" cy="70" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="132" cy="75" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="188" cy="65" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="244" cy="60" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              
                              {/* Data points for potential */}
                              <circle cx="244" cy="20" r="3" fill="rgba(34, 197, 94, 0.8)" className="potential-point" />
                            </svg>
                            <div className="chart-labels">
                              <span>Jan</span>
                              <span>Feb</span>
                              <span>Mar</span>
                              <span>Apr</span>
                              <span>May</span>
                            </div>
                            <div className="chart-legend">
                              <div className="legend-item">
                                <div className="legend-line solid"></div>
                                <span>Current Progress</span>
                              </div>
                              <div className="legend-item">
                                <div className="legend-line dotted"></div>
                                <span>With Campaigns</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="growth-stats">
                          <div className="stat-visual">
                            <span className="stat-number">7%</span>
                            <span className="stat-text">Current Growth</span>
                          </div>
                          <div className="stat-visual">
                            <span className="stat-number">29%</span>
                            <span className="stat-text">Potential Growth</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* AI Marketing Features */}
                <div className="dashboard-card ai-marketing-card">
                  {/* Shine layers for enhanced glassmorphism */}
                  <div className="shine-layer-1"></div>
                  <div className="shine-layer-2"></div>
                  <div className="edge-highlight"></div>
                  
                  <div className="card-header">
                    <h3>🤖 AI Marketing</h3>
                    <span className="period">Powered by AI</span>
                  </div>
                  <div className="ai-marketing-content">
                    <div className="ai-marketing-icon">
                      <div className="ai-brain-animation">🤖</div>
                    </div>
                    <div className="ai-marketing-text">
                      <h4>Unlock AI-Powered Growth</h4>
                      <p>Discover intelligent tools to optimize your menu, grade your digital presence, and generate compelling marketing content.</p>
                    </div>
                    <button
                      className="ai-marketing-cta"
                      onClick={() => window.location.href = '/ai-features'}
                    >
                      Explore AI Features
                      <span className="cta-arrow">→</span>
                    </button>
                  </div>
                </div>

                {/* Quick Links */}
                <div className="dashboard-card quick-links-card">
                  <div className="card-header">
                    <h3>⚡ Quick Actions</h3>
                  </div>
                  <div className="quick-links">
                    <button
                      className="quick-link-button primary"
                      onClick={() => setActiveView('get-new-customers')}
                    >
                      <span className="button-icon">🎯</span>
                      Launch New Ad
                    </button>
                    <button
                      className="quick-link-button secondary"
                      onClick={() => setActiveView('bring-back-regulars')}
                    >
                      <span className="button-icon">💬</span>
                      Send SMS Campaign
                    </button>
                    <button
                      className="quick-link-button website-builder"
                      onClick={() => setActiveView('website-builder')}
                    >
                      <span className="button-icon">🌐</span>
                      Build Website
                    </button>
                    <button
                      className="quick-link-button tertiary"
                      onClick={() => setActiveView('marketing-foundations')}
                    >
                      <span className="button-icon">📚</span>
                      Review Marketing Foundations
                    </button>
                  </div>
                </div>

                {/* Marketing Score Card */}
                <div className="dashboard-card marketing-score-card">
                  <div className="card-header">
                    <h3>🎯 Marketing Score</h3>
                    <span className="period">Health Check</span>
                  </div>
                  <div className="marketing-score-content">
                    <div className="score-circle">
                      <svg className="score-ring" width="100" height="100" viewBox="0 0 100 100">
                        <defs>
                          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#1E40AF" />
                            <stop offset="100%" stopColor="#3B82F6" />
                          </linearGradient>
                        </defs>
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#E5E7EB"
                          strokeWidth="8"
                          opacity="0.3"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="url(#scoreGradient)"
                          strokeWidth="8"
                          strokeLinecap="round"
                          strokeDasharray={`${((dashboardData?.momentumMetrics?.marketingScore || 0) / 100) * 251.33} 251.33`}
                          transform="rotate(-90 50 50)"
                          className="score-progress-ring"
                        />
                      </svg>
                      <div className="score-content">
                        <div className="score-value">{dashboardData?.momentumMetrics?.marketingScore || 0}</div>
                        <div className="score-label">Score</div>
                      </div>
                    </div>
                    <div className="score-status">
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 80 && "🏆 Excellent"}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 60 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 80 && "💪 Strong"}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 40 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 60 && "🔥 Growing"}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 20 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 40 && "🌟 Building"}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) < 20 && "🚀 Starting"}
                    </div>
                    <div className="progress-bars">
                      <div className="progress-item">
                        <div className="progress-info">
                          <span className="progress-name">Foundation</span>
                          <span className="progress-percent">{dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0}%</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill foundation"
                            style={{ width: `${dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="progress-item">
                        <div className="progress-info">
                          <span className="progress-name">Ongoing</span>
                          <span className="progress-percent">{dashboardData?.momentumMetrics?.ongoingProgress?.percentage || 0}%</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill ongoing"
                            style={{ width: `${dashboardData?.momentumMetrics?.ongoingProgress?.percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Revenue Potential Card */}
                <div className="dashboard-card revenue-potential-card">
                  <div className="card-header">
                    <h3>💰 Revenue</h3>
                    <span className="period">Weekly Opportunity</span>
                  </div>
                  <div className="revenue-potential-content">
                    <div className="revenue-header">
                      <div className="revenue-icon">💰</div>
                      <div className="revenue-trend">
                        {(dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0) > 0 ? "📈" : "📊"}
                      </div>
                    </div>
                    <div className="revenue-value">${dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0}</div>
                    <div className="revenue-label">Weekly Revenue Potential</div>
                    <div className="revenue-bar">
                      <div
                        className="revenue-fill"
                        style={{
                          width: `${Math.min(((dashboardData?.momentumMetrics?.completedRevenue || 0) / Math.max((dashboardData?.momentumMetrics?.totalPotential || 1), 1)) * 100, 100)}%`
                        }}
                      ></div>
                    </div>
                    <div className="revenue-description">
                      ${dashboardData?.momentumMetrics?.completedRevenue || 0} unlocked of ${dashboardData?.momentumMetrics?.totalPotential || 0} total
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Get New Customers Tab */}
          {activeView === 'get-new-customers' && (
            <div className="get-new-customers-content">
              <div className="placeholder-content">
                <h2>🎯 Get New Customers</h2>
                <p>Launch Facebook ads to attract new customers to your restaurant.</p>
                <button className="btn-primary" onClick={() => setActiveTab('get-new-customers')}>
                  Go to Get New Customers
                </button>
              </div>
            </div>
          )}

          {/* Bring Back Regulars Tab */}
          {activeView === 'bring-back-regulars' && (
            <div className="bring-back-regulars-content">
              <div className="placeholder-content">
                <h2>💬 Bring Back Regulars</h2>
                <p>Send SMS campaigns to re-engage your past customers.</p>
                <button className="btn-primary" onClick={() => setActiveTab('bring-back-regulars')}>
                  Go to Bring Back Regulars
                </button>
              </div>
            </div>
          )}

          {/* Website Builder Tab */}
          {activeView === 'website-builder' && (
            <div className="website-builder-content">
              <div className="placeholder-content">
                <h2>🌐 Website Builder</h2>
                <p>Create stunning AI-powered restaurant websites.</p>
                <button className="btn-primary" onClick={() => window.location.href = '/website-builder'}>
                  Go to Website Builder
                </button>
              </div>
            </div>
          )}

          {/* AI Features Tab */}
          {activeView === 'ai-features' && (
            <div className="ai-features-content">
              <div className="placeholder-content">
                <h2>🤖 AI Features</h2>
                <p>Unlock AI-powered growth tools for your restaurant.</p>
                <button className="btn-primary" onClick={() => window.location.href = '/ai-features'}>
                  Go to AI Features
                </button>
              </div>
            </div>
          )}

          {/* Marketing Foundations Tab */}
          {activeView === 'marketing-foundations' && (
            <div className="marketing-foundations-content">
              <div className="placeholder-content">
                <h2>📚 Marketing Foundations</h2>
                <p>Build your marketing foundation with essential setup tasks.</p>
                <button className="btn-primary" onClick={() => setActiveTab('marketing-foundations')}>
                  Go to Marketing Foundations
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RestaurantDashboard;