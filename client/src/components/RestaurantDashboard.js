import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import './RestaurantDashboard.css';

const RestaurantDashboard = ({ setActiveTab }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getRestaurantDashboard();
      setDashboardData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
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

  const { restaurant, performanceSnapshot, activeCampaigns } = dashboardData;

  return (
    <div className="restaurant-dashboard">
      <div className="dashboard-header">
        <h1>Your Growth Command Center</h1>
        <p>Welcome back to {restaurant.name}!</p>
      </div>

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
              onClick={() => setActiveTab('campaigns')}
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
              onClick={() => setActiveTab('get-new-customers')}
            >
              <span className="button-icon">🎯</span>
              Launch New Ad
            </button>
            <button
              className="quick-link-button secondary"
              onClick={() => setActiveTab('bring-back-regulars')}
            >
              <span className="button-icon">💬</span>
              Send SMS Campaign
            </button>
            <button
              className="quick-link-button tertiary"
              onClick={() => setActiveTab('marketing-foundations')}
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
                  strokeDasharray={`${((dashboardData.momentumMetrics?.marketingScore || 0) / 100) * 251.33} 251.33`}
                  transform="rotate(-90 50 50)"
                  className="score-progress-ring"
                />
              </svg>
              <div className="score-content">
                <div className="score-value">{dashboardData.momentumMetrics?.marketingScore || 0}</div>
                <div className="score-label">Score</div>
              </div>
            </div>
            <div className="score-status">
              {(dashboardData.momentumMetrics?.marketingScore || 0) >= 80 && "🏆 Excellent"}
              {(dashboardData.momentumMetrics?.marketingScore || 0) >= 60 && (dashboardData.momentumMetrics?.marketingScore || 0) < 80 && "💪 Strong"}
              {(dashboardData.momentumMetrics?.marketingScore || 0) >= 40 && (dashboardData.momentumMetrics?.marketingScore || 0) < 60 && "🔥 Growing"}
              {(dashboardData.momentumMetrics?.marketingScore || 0) >= 20 && (dashboardData.momentumMetrics?.marketingScore || 0) < 40 && "🌟 Building"}
              {(dashboardData.momentumMetrics?.marketingScore || 0) < 20 && "🚀 Starting"}
            </div>
            <div className="progress-bars">
              <div className="progress-item">
                <div className="progress-info">
                  <span className="progress-name">Foundation</span>
                  <span className="progress-percent">{dashboardData.momentumMetrics?.foundationalProgress?.percentage || 0}%</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill foundation"
                    style={{ width: `${dashboardData.momentumMetrics?.foundationalProgress?.percentage || 0}%` }}
                  ></div>
                </div>
              </div>
              <div className="progress-item">
                <div className="progress-info">
                  <span className="progress-name">Ongoing</span>
                  <span className="progress-percent">{dashboardData.momentumMetrics?.ongoingProgress?.percentage || 0}%</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill ongoing"
                    style={{ width: `${dashboardData.momentumMetrics?.ongoingProgress?.percentage || 0}%` }}
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
                {(dashboardData.momentumMetrics?.weeklyRevenuePotential || 0) > 0 ? "📈" : "📊"}
              </div>
            </div>
            <div className="revenue-value">${dashboardData.momentumMetrics?.weeklyRevenuePotential || 0}</div>
            <div className="revenue-label">Weekly Revenue Potential</div>
            <div className="revenue-bar">
              <div
                className="revenue-fill"
                style={{
                  width: `${Math.min(((dashboardData.momentumMetrics?.completedRevenue || 0) / Math.max((dashboardData.momentumMetrics?.totalPotential || 1), 1)) * 100, 100)}%`
                }}
              ></div>
            </div>
            <div className="revenue-description">
              ${dashboardData.momentumMetrics?.completedRevenue || 0} unlocked of ${dashboardData.momentumMetrics?.totalPotential || 0} total
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RestaurantDashboard;