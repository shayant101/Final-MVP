import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI, adminAnalyticsAPI } from '../services/api';
import AIAnalytics from './AIAnalytics';
import ContentModeration from './ContentModeration';
import FeatureManagement from './FeatureManagement';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  const [restaurants, setRestaurants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('overview'); // 'overview', 'analytics', 'moderation', 'features', 'restaurants'
  const { impersonate } = useAuth();

  useEffect(() => {
    fetchDashboardData();
    if (activeView === 'restaurants') {
      fetchRestaurants();
    }
    
    // Set up real-time metrics updates every 30 seconds
    const interval = setInterval(fetchRealTimeMetrics, 30000);
    return () => clearInterval(interval);
  }, [activeView]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getAdminDashboard();
      setDashboardData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRestaurants = async () => {
    try {
      const data = await dashboardAPI.getAllRestaurants(searchTerm);
      setRestaurants(data.restaurants);
    } catch (error) {
      setError('Failed to fetch restaurants');
    }
  };

  const fetchRealTimeMetrics = async () => {
    try {
      const response = await adminAnalyticsAPI.getRealTimeMetrics();
      setRealTimeMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch real-time metrics:', error);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants();
  };

  const handleImpersonate = async (restaurantId) => {
    try {
      await impersonate(restaurantId);
      // Force a page refresh to trigger the dashboard switch
      window.location.reload();
    } catch (error) {
      setError('Failed to start impersonation');
    }
  };


  if (loading && !dashboardData) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="admin-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Platform Overview</h1>
        <p>Manage your restaurant platform</p>
      </div>

      <div className="admin-nav">
        <button
          className={`nav-button ${activeView === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveView('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-button ${activeView === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveView('analytics')}
        >
          📈 AI Analytics
        </button>
        <button
          className={`nav-button ${activeView === 'moderation' ? 'active' : ''}`}
          onClick={() => setActiveView('moderation')}
        >
          🛡️ Content Moderation
        </button>
        <button
          className={`nav-button ${activeView === 'features' ? 'active' : ''}`}
          onClick={() => setActiveView('features')}
        >
          ⚙️ Feature Management
        </button>
        <button
          className={`nav-button ${activeView === 'restaurants' ? 'active' : ''}`}
          onClick={() => setActiveView('restaurants')}
        >
          🏪 Restaurants
        </button>
      </div>

      {/* Real-time Metrics Bar */}
      {realTimeMetrics && (
        <div className="real-time-metrics-bar">
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.today_requests}</div>
            <div className="metric-label">Today's AI Requests</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.success_rate}%</div>
            <div className="metric-label">Success Rate</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.avg_response_time}ms</div>
            <div className="metric-label">Avg Response Time</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">${realTimeMetrics.daily_cost}</div>
            <div className="metric-label">Daily Cost</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.active_requests}</div>
            <div className="metric-label">Active Requests</div>
          </div>
          <div className="metric-item last-updated">
            <div className="metric-label">
              Last Updated: {new Date(realTimeMetrics.last_updated).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}

      {activeView === 'overview' && dashboardData && (
        <div className="overview-content">
          <div className="admin-grid">
            {/* Platform Stats */}
            <div className="admin-card stats-card">
              <div className="card-header">
                <h3>📈 Platform Statistics</h3>
                <span className="period">{dashboardData.platformStats.period}</span>
              </div>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">{dashboardData.platformStats.totalRestaurants}</div>
                  <div className="stat-label">Total Active Restaurants</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{dashboardData.platformStats.recentCampaigns}</div>
                  <div className="stat-label">Campaigns Launched</div>
                </div>
              </div>
            </div>

            {/* Needs Attention */}
            <div className="admin-card attention-card">
              <div className="card-header">
                <h3>⚠️ Needs Attention</h3>
              </div>
              <div className="attention-items">
                <div className="attention-item">
                  <div className="attention-icon">🔧</div>
                  <div className="attention-content">
                    <div className="attention-title">Incomplete Setups</div>
                    <div className="attention-description">
                      {dashboardData.needsAttention.incompleteSetups} restaurants have pending setup tasks
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="admin-card actions-card">
              <div className="card-header">
                <h3>⚡ Quick Actions</h3>
              </div>
              <div className="admin-actions">
                <button 
                  className="action-button primary"
                  onClick={() => setActiveView('restaurants')}
                >
                  <span className="button-icon">🏪</span>
                  Manage All Restaurants
                </button>
                <button className="action-button secondary" disabled>
                  <span className="button-icon">⚙️</span>
                  Platform Settings
                  <span className="coming-soon">(Coming Soon)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === 'restaurants' && (
        <div className="restaurants-content">
          <div className="restaurants-header">
            <h2>Manage All Restaurants</h2>
            <form onSubmit={handleSearchSubmit} className="search-form">
              <input
                type="text"
                placeholder="Search restaurants by name..."
                value={searchTerm}
                onChange={handleSearch}
                className="search-input"
              />
              <button type="submit" className="search-button">Search</button>
            </form>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="restaurants-table-container">
            <table className="restaurants-table">
              <thead>
                <tr>
                  <th>Restaurant Name</th>
                  <th>Owner Email</th>
                  <th>Signup Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {restaurants.map(restaurant => (
                  <tr key={restaurant.restaurant_id}>
                    <td>
                      <div className="restaurant-info">
                        <div className="restaurant-name">{restaurant.name}</div>
                        {restaurant.address && (
                          <div className="restaurant-address">{restaurant.address}</div>
                        )}
                      </div>
                    </td>
                    <td>{restaurant.email}</td>
                    <td>{new Date(restaurant.signup_date).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="impersonate-button"
                        onClick={() => handleImpersonate(restaurant.restaurant_id)}
                      >
                        🎭 Impersonate
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {restaurants.length === 0 && !loading && (
              <div className="no-restaurants">
                <p>No restaurants found</p>
                {searchTerm && (
                  <p>Try adjusting your search terms</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Analytics Tab */}
      {activeView === 'analytics' && (
        <div className="analytics-content">
          <AIAnalytics />
        </div>
      )}

      {/* Content Moderation Tab */}
      {activeView === 'moderation' && (
        <div className="moderation-content">
          <ContentModeration />
        </div>
      )}

      {/* Feature Management Tab */}
      {activeView === 'features' && (
        <div className="features-content">
          <FeatureManagement />
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;