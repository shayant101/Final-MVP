'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI, adminAnalyticsAPI } from '../services/api';
import AIAnalytics from './AIAnalytics';
import ContentModeration from './ContentModeration';
import FeatureManagement from './FeatureManagement';
import BusinessIntelligence from './BusinessIntelligence';
import RevenueAnalytics from './RevenueAnalytics';
import AIBusinessAssistant from './AIBusinessAssistant';
import SubscriptionManagement from './SubscriptionManagement';
import LoadingScreen from './LoadingScreen';
import { 
  Rocket, 
  BarChart, 
  TrendingUp, 
  DollarSign, 
  Brain, 
  Bot,
  Zap
} from 'lucide-react';
import './AdminDashboard.css';

interface Restaurant {
  restaurant_id: string;
  name: string;
  email: string;
  signup_date: string;
  address?: string;
}

interface DashboardData {
  platformStats: {
    totalRestaurants: number;
    recentCampaigns: number;
    period: string;
  };
  needsAttention: {
    incompleteSetups: number;
  };
}

interface RealTimeMetrics {
  today_requests: number;
  success_rate: number;
  avg_response_time: number;
  daily_cost: string;
  active_requests: number;
  last_updated: string;
}

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetrics | null>(null);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { impersonate, logout } = useAuth();

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
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchRestaurants = async () => {
    try {
      const data = await dashboardAPI.getAllRestaurants(searchTerm);
      setRestaurants(data.restaurants || []);
    } catch (error) {
      console.error('Error fetching restaurants:', error);
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

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRestaurants();
  };

  const handleImpersonate = async (restaurantId: string) => {
    try {
      await impersonate(restaurantId);
      // Force a page refresh to trigger the dashboard switch
      window.location.reload();
    } catch (error) {
      console.error('Error impersonating restaurant:', error);
      setError('Failed to start impersonation');
    }
  };

  const handleDeleteRestaurant = async (restaurantId: string, restaurantName: string) => {
    // Confirm deletion
    const confirmDelete = window.confirm(
      `⚠️ Are you sure you want to delete "${restaurantName}"?\n\nThis action cannot be undone and will permanently remove:\n• Restaurant account\n• All campaign data\n• All analytics data\n• All generated content\n\nType "DELETE" to confirm:`
    );
    
    if (!confirmDelete) return;
    
    const confirmText = window.prompt(
      `To confirm deletion of "${restaurantName}", please type "DELETE" (case sensitive):`
    );
    
    if (confirmText !== 'DELETE') {
      alert('Deletion cancelled - confirmation text did not match.');
      return;
    }

    try {
      setLoading(true);
      
      console.log('Attempting to delete restaurant:', restaurantId);
      
      // Import and use the existing API service
      const { default: api } = await import('../services/api');
      const response = await api.delete(`/admin/restaurants/${restaurantId}`);
      
      console.log('Delete response:', response.data);

      // Success - refresh the restaurants list
      await fetchRestaurants();
      alert(`✅ Restaurant "${restaurantName}" has been successfully deleted.`);
      
    } catch (error: any) {
      console.error('Delete error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to delete restaurant';
      setError(`Failed to delete restaurant: ${errorMessage}`);
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  if (loading && !dashboardData) {
    return <LoadingScreen />;
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
      {/* Left Sidebar Navigation */}
      <div className={`admin-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-title">
            {!sidebarCollapsed && (
              <>
                <h2><Rocket className="inline mr-2" size={24} />Uplit Admin</h2>
                <p>Platform Management</p>
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
          {/* Core Analytics Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title"><BarChart className="inline mr-2" size={16} />Analytics & Intelligence</div>}
            <button
              className={`nav-item ${activeView === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveView('overview')}
              title="Platform Overview"
            >
              <span className="nav-icon"><TrendingUp size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Platform Overview</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'business-intelligence' ? 'active' : ''}`}
              onClick={() => setActiveView('business-intelligence')}
              title="Business Intelligence"
            >
              <span className="nav-icon">🧠</span>
              {!sidebarCollapsed && <span className="nav-label">Business Intelligence</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'revenue-analytics' ? 'active' : ''}`}
              onClick={() => setActiveView('revenue-analytics')}
              title="Revenue Analytics"
            >
              <span className="nav-icon"><DollarSign size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Revenue Analytics</span>}
            </button>
          </div>

          {/* AI & Automation Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title"><Brain className="inline mr-2" size={16} />AI & Automation</div>}
            <button
              className={`nav-item ${activeView === 'ai-assistant' ? 'active' : ''}`}
              onClick={() => setActiveView('ai-assistant')}
              title="AI Business Assistant"
            >
              <span className="nav-icon"><Bot size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">AI Business Assistant</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveView('analytics')}
              title="AI Analytics"
            >
              <span className="nav-icon"><BarChart size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">AI Analytics</span>}
            </button>
          </div>

          {/* Management Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">⚙️ Management</div>}
            <button
              className={`nav-item ${activeView === 'subscriptions' ? 'active' : ''}`}
              onClick={() => setActiveView('subscriptions')}
              title="Subscription Management"
            >
              <span className="nav-icon">💳</span>
              {!sidebarCollapsed && <span className="nav-label">Subscription Management</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'restaurants' ? 'active' : ''}`}
              onClick={() => setActiveView('restaurants')}
              title="Restaurant Management"
            >
              <span className="nav-icon">🏪</span>
              {!sidebarCollapsed && <span className="nav-label">Restaurant Management</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'moderation' ? 'active' : ''}`}
              onClick={() => setActiveView('moderation')}
              title="Content Moderation"
            >
              <span className="nav-icon">🛡️</span>
              {!sidebarCollapsed && <span className="nav-label">Content Moderation</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'features' ? 'active' : ''}`}
              onClick={() => setActiveView('features')}
              title="Feature Management"
            >
              <span className="nav-icon">⚙️</span>
              {!sidebarCollapsed && <span className="nav-label">Feature Management</span>}
            </button>
          </div>

          {/* Logout Section */}
          <div className="nav-section logout-section">
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
      <div className={`admin-main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Header with Real-time Metrics */}
        <div className="main-header">
          <div className="header-title">
            <h1>
              {activeView === 'overview' && 'Platform Overview'}
              {activeView === 'business-intelligence' && 'Business Intelligence'}
              {activeView === 'revenue-analytics' && 'Revenue Analytics'}
              {activeView === 'ai-assistant' && 'AI Business Assistant'}
              {activeView === 'subscriptions' && 'Subscription Management'}
              {activeView === 'analytics' && 'AI Analytics'}
              {activeView === 'moderation' && 'Content Moderation'}
              {activeView === 'features' && 'Feature Management'}
              {activeView === 'restaurants' && 'Restaurant Management'}
            </h1>
            <p>
              {activeView === 'overview' && 'Monitor your restaurant platform performance'}
              {activeView === 'business-intelligence' && 'Advanced business insights and analytics'}
              {activeView === 'revenue-analytics' && 'Revenue forecasting and financial analytics'}
              {activeView === 'ai-assistant' && 'AI-powered business assistance and insights'}
              {activeView === 'subscriptions' && 'Monitor billing, usage, and subscription lifecycle'}
              {activeView === 'analytics' && 'AI performance metrics and analytics'}
              {activeView === 'moderation' && 'Content moderation and safety controls'}
              {activeView === 'features' && 'Platform feature toggles and management'}
              {activeView === 'restaurants' && 'Manage all restaurants on the platform'}
            </p>
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
        </div>

        {/* Content Area */}
        <div className="content-area">
          {activeView === 'overview' && dashboardData && (
            <div className="overview-content">
              <div className="admin-grid">
                {/* Platform Stats */}
                <div className="admin-card stats-card">
                  <div className="card-header">
                    <h3><TrendingUp className="inline mr-2" size={18} />Platform Statistics</h3>
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
                    <h3><Zap className="inline mr-2" size={18} />Quick Actions</h3>
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
                          <div className="restaurant-actions">
                            <button
                              className="impersonate-button"
                              onClick={() => handleImpersonate(restaurant.restaurant_id)}
                            >
                              🎭 Impersonate
                            </button>
                            <button
                              className="delete-button"
                              onClick={() => handleDeleteRestaurant(restaurant.restaurant_id, restaurant.name)}
                              title="Delete Restaurant"
                            >
                              🗑️ Delete
                            </button>
                          </div>
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

          {/* Business Intelligence Tab */}
          {activeView === 'business-intelligence' && (
            <div className="business-intelligence-content">
              <BusinessIntelligence />
            </div>
          )}

          {/* Revenue Analytics Tab */}
          {activeView === 'revenue-analytics' && (
            <div className="revenue-analytics-content">
              <RevenueAnalytics />
            </div>
          )}

          {/* AI Assistant Tab */}
          {activeView === 'ai-assistant' && (
            <div className="ai-assistant-content">
              <AIBusinessAssistant />
            </div>
          )}

          {/* Subscriptions Tab */}
          {activeView === 'subscriptions' && (
            <div className="subscriptions-content">
              <SubscriptionManagement />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;