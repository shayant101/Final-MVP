import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI } from '../services/api';
import './RestaurantDashboard.css';

const RestaurantDashboard = ({ setActiveTab }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user, isImpersonating } = useAuth();

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

  const handleChecklistToggle = async (itemId, currentStatus) => {
    try {
      await dashboardAPI.updateChecklistItem(itemId, !currentStatus);
      // Refresh dashboard data
      fetchDashboardData();
    } catch (error) {
      setError('Failed to update checklist item');
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

  const { restaurant, performanceSnapshot, activeCampaigns, pendingTasks } = dashboardData;

  return (
    <div className="restaurant-dashboard">
      {isImpersonating && (
        <div className="impersonation-banner">
          <span>🎭 IMPERSONATING: {restaurant.name}</span>
        </div>
      )}

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

        {/* What's Next / Pending Tasks */}
        <div className="dashboard-card tasks-card">
          <div className="card-header">
            <h3>✅ What's Next?</h3>
          </div>
          <div className="tasks-list">
            {pendingTasks.length > 0 ? (
              pendingTasks.map(task => (
                <div key={task.status_id} className="task-item">
                  <label className="task-checkbox">
                    <input
                      type="checkbox"
                      checked={task.is_complete}
                      onChange={() => handleChecklistToggle(task.status_id, task.is_complete)}
                    />
                    <span className="checkmark"></span>
                  </label>
                  <div className="task-content">
                    <div className="task-name">{task.checklist_item_name}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="all-tasks-complete">
                <p>🎉 All tasks completed!</p>
                <p>You're all set up for success.</p>
              </div>
            )}
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
      </div>
    </div>
  );
};

export default RestaurantDashboard;