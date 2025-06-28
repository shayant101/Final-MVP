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
        <h1>Your Momentum Hub</h1>
        <p>Welcome back to {restaurant.name}!</p>
      </div>

      <div className="dashboard-grid">
        {/* Performance Snapshot */}
        <div className="dashboard-card performance-card">
          <div className="card-header">
            <h3>📊 Performance Snapshot</h3>
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
        </div>

        {/* Active Campaigns */}
        <div className="dashboard-card campaigns-card">
          <div className="card-header">
            <h3>🚀 Active Campaigns</h3>
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
              <div className="no-campaigns">
                <p>No active campaigns yet</p>
                <button 
                  className="start-campaign-button"
                  onClick={() => setActiveTab('get-new-customers')}
                >
                  Launch Your First Campaign
                </button>
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
            <h3>🧠 AI Marketing</h3>
            <span className="period">Powered by AI</span>
          </div>
          <div className="ai-marketing-content">
            <div className="ai-marketing-icon">
              <div className="ai-brain-animation">🧠</div>
            </div>
            <div className="ai-marketing-text">
              <h4>Unlock AI-Powered Growth</h4>
              <p>Discover intelligent tools to optimize your menu, grade your digital presence, and generate compelling marketing content.</p>
            </div>
            <button
              className="ai-marketing-cta"
              onClick={() => window.location.href = '/ai-features'}
            >
              <span className="cta-icon">✨</span>
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
            <h3>💰 Revenue Potential</h3>
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