'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI } from '../services/api';
import LoadingScreen from './LoadingScreen';
import './AdminDashboard.css';

interface Restaurant {
  id: string;
  name: string;
  email: string;
  created_at: string;
  status: string;
}

interface DashboardData {
  restaurants: Restaurant[];
  totalRestaurants: number;
  activeRestaurants: number;
  totalCampaigns: number;
  systemHealth: string;
}

const AdminDashboard = () => {
  const { user, impersonate } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getAdminDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching admin dashboard:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleImpersonate = async (restaurantId: string) => {
    try {
      await impersonate(restaurantId);
      // The AuthContext will handle the redirect
    } catch (error) {
      console.error('Error impersonating restaurant:', error);
      alert('Failed to impersonate restaurant');
    }
  };

  const filteredRestaurants = dashboardData?.restaurants?.filter(restaurant =>
    restaurant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    restaurant.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error-state">
          <h2>Error Loading Dashboard</h2>
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Welcome back, {user?.email}</p>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">🏪</div>
          <div className="metric-content">
            <h3>Total Restaurants</h3>
            <div className="metric-value">{dashboardData?.totalRestaurants || 0}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <h3>Active Restaurants</h3>
            <div className="metric-value">{dashboardData?.activeRestaurants || 0}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <h3>Total Campaigns</h3>
            <div className="metric-value">{dashboardData?.totalCampaigns || 0}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">🔧</div>
          <div className="metric-content">
            <h3>System Health</h3>
            <div className="metric-value">{dashboardData?.systemHealth || 'Good'}</div>
          </div>
        </div>
      </div>

      {/* Restaurant Management */}
      <div className="restaurants-section">
        <div className="section-header">
          <h2>Restaurant Management</h2>
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search restaurants..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        <div className="restaurants-table">
          <div className="table-header">
            <div className="table-cell">Restaurant</div>
            <div className="table-cell">Email</div>
            <div className="table-cell">Created</div>
            <div className="table-cell">Status</div>
            <div className="table-cell">Actions</div>
          </div>
          
          {filteredRestaurants.length === 0 ? (
            <div className="empty-state">
              <p>No restaurants found</p>
            </div>
          ) : (
            filteredRestaurants.map((restaurant) => (
              <div key={restaurant.id} className="table-row">
                <div className="table-cell">
                  <div className="restaurant-info">
                    <div className="restaurant-name">{restaurant.name}</div>
                  </div>
                </div>
                <div className="table-cell">{restaurant.email}</div>
                <div className="table-cell">
                  {new Date(restaurant.created_at).toLocaleDateString()}
                </div>
                <div className="table-cell">
                  <span className={`status-badge ${restaurant.status}`}>
                    {restaurant.status}
                  </span>
                </div>
                <div className="table-cell">
                  <button
                    onClick={() => handleImpersonate(restaurant.id)}
                    className="impersonate-button"
                  >
                    Impersonate
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <button className="action-button">
            <span className="action-icon">📊</span>
            <span>View Analytics</span>
          </button>
          <button className="action-button">
            <span className="action-icon">🔧</span>
            <span>System Settings</span>
          </button>
          <button className="action-button">
            <span className="action-icon">📈</span>
            <span>Revenue Reports</span>
          </button>
          <button className="action-button">
            <span className="action-icon">👥</span>
            <span>User Management</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;