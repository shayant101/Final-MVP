import React, { useState, useEffect } from 'react';
import { adminAnalyticsAPI, dashboardAPI } from '../services/api';
import './FeatureManagement.css';

const FeatureManagement = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [featureToggles, setFeatureToggles] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  const availableFeatures = [
    { key: 'image_enhancement', name: 'Image Enhancement', description: 'AI-powered image enhancement and optimization' },
    { key: 'content_generation', name: 'Content Generation', description: 'AI-generated marketing content and descriptions' },
    { key: 'marketing_assistant', name: 'Marketing Assistant', description: 'AI marketing recommendations and campaign assistance' },
    { key: 'menu_optimizer', name: 'Menu Optimizer', description: 'AI-powered menu analysis and optimization' },
    { key: 'digital_grader', name: 'Digital Grader', description: 'Website and digital presence scoring' }
  ];

  useEffect(() => {
    fetchData();
  }, [selectedRestaurant]);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchRestaurants(),
        fetchFeatureToggles()
      ]);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRestaurants = async () => {
    try {
      const response = await dashboardAPI.getAllRestaurants();
      setRestaurants(response.restaurants || []);
    } catch (error) {
      console.error('Failed to fetch restaurants:', error);
    }
  };

  const fetchFeatureToggles = async () => {
    try {
      const restaurantId = selectedRestaurant === 'all' ? null : selectedRestaurant;
      const response = await adminAnalyticsAPI.getFeatureToggles(restaurantId);
      setFeatureToggles(response.data.feature_toggles || []);
    } catch (error) {
      console.error('Failed to fetch feature toggles:', error);
    }
  };

  const handleFeatureToggle = async (restaurantId, featureName, enabled, rateLimits = null) => {
    try {
      setUpdating(true);
      await adminAnalyticsAPI.updateFeatureToggle(restaurantId, featureName, enabled, rateLimits);
      
      // Update local state
      setFeatureToggles(prev => {
        const existing = prev.find(t => t.restaurant_id === restaurantId && t.feature_name === featureName);
        if (existing) {
          return prev.map(t => 
            t.restaurant_id === restaurantId && t.feature_name === featureName
              ? { ...t, enabled, rate_limits: rateLimits || t.rate_limits }
              : t
          );
        } else {
          return [...prev, {
            restaurant_id: restaurantId,
            feature_name: featureName,
            enabled,
            rate_limits: rateLimits || {},
            updated_at: new Date().toISOString()
          }];
        }
      });
    } catch (error) {
      setError(`Failed to update feature toggle: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleRateLimitUpdate = async (restaurantId, featureName, rateLimits) => {
    const toggle = featureToggles.find(t => t.restaurant_id === restaurantId && t.feature_name === featureName);
    const enabled = toggle ? toggle.enabled : true;
    await handleFeatureToggle(restaurantId, featureName, enabled, rateLimits);
  };

  const handleBulkToggle = async (featureName, enabled) => {
    const filteredRestaurants = getFilteredRestaurants();
    
    try {
      setUpdating(true);
      const promises = filteredRestaurants.map(restaurant => 
        handleFeatureToggle(restaurant.restaurant_id, featureName, enabled)
      );
      await Promise.all(promises);
    } catch (error) {
      setError(`Failed to bulk update feature: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const getFilteredRestaurants = () => {
    return restaurants.filter(restaurant => {
      const matchesSearch = searchTerm === '' || 
        restaurant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        restaurant.email.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesFilter = selectedRestaurant === 'all' || restaurant.restaurant_id === selectedRestaurant;
      
      return matchesSearch && matchesFilter;
    });
  };

  const getFeatureStatus = (restaurantId, featureName) => {
    const toggle = featureToggles.find(t => t.restaurant_id === restaurantId && t.feature_name === featureName);
    return toggle ? toggle.enabled : true; // Default to enabled
  };

  const getRateLimits = (restaurantId, featureName) => {
    const toggle = featureToggles.find(t => t.restaurant_id === restaurantId && t.feature_name === featureName);
    return toggle?.rate_limits || {};
  };

  const getFeatureUsageStats = (restaurantId, featureName) => {
    // This would typically come from analytics data
    // For now, return placeholder data
    return {
      daily_usage: Math.floor(Math.random() * 50),
      monthly_usage: Math.floor(Math.random() * 500),
      last_used: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
    };
  };

  if (loading && restaurants.length === 0) {
    return (
      <div className="feature-management-loading">
        <div className="loading-spinner"></div>
        <p>Loading feature management...</p>
      </div>
    );
  }

  const filteredRestaurants = getFilteredRestaurants();

  return (
    <div className="feature-management">
      {/* Header and Controls */}
      <div className="management-header">
        <div className="header-info">
          <h2>Feature Management</h2>
          <p>Control AI features and rate limits for restaurants</p>
        </div>
        
        <div className="management-controls">
          <div className="control-group">
            <label>Restaurant Filter:</label>
            <select 
              value={selectedRestaurant} 
              onChange={(e) => setSelectedRestaurant(e.target.value)}
            >
              <option value="all">All Restaurants</option>
              {restaurants.map(restaurant => (
                <option key={restaurant.restaurant_id} value={restaurant.restaurant_id}>
                  {restaurant.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="search-group">
            <input
              type="text"
              placeholder="Search restaurants..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Bulk Actions */}
      <div className="bulk-actions-section">
        <h3>Bulk Feature Management</h3>
        <div className="bulk-features">
          {availableFeatures.map(feature => (
            <div key={feature.key} className="bulk-feature-item">
              <div className="feature-info">
                <div className="feature-name">{feature.name}</div>
                <div className="feature-description">{feature.description}</div>
              </div>
              <div className="bulk-buttons">
                <button
                  onClick={() => handleBulkToggle(feature.key, true)}
                  disabled={updating}
                  className="bulk-button enable"
                >
                  Enable All
                </button>
                <button
                  onClick={() => handleBulkToggle(feature.key, false)}
                  disabled={updating}
                  className="bulk-button disable"
                >
                  Disable All
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Restaurant Feature Matrix */}
      <div className="feature-matrix">
        <h3>Restaurant Feature Matrix</h3>
        
        {filteredRestaurants.length === 0 ? (
          <div className="no-restaurants">
            <div className="no-content-icon">🏪</div>
            <h3>No Restaurants Found</h3>
            <p>
              {searchTerm 
                ? `No restaurants match your search "${searchTerm}"`
                : 'No restaurants available'
              }
            </p>
          </div>
        ) : (
          <div className="matrix-container">
            <div className="matrix-table">
              <div className="matrix-header">
                <div className="restaurant-column">Restaurant</div>
                {availableFeatures.map(feature => (
                  <div key={feature.key} className="feature-column">
                    {feature.name}
                  </div>
                ))}
              </div>
              
              {filteredRestaurants.map(restaurant => (
                <div key={restaurant.restaurant_id} className="matrix-row">
                  <div className="restaurant-info">
                    <div className="restaurant-name">{restaurant.name}</div>
                    <div className="restaurant-email">{restaurant.email}</div>
                  </div>
                  
                  {availableFeatures.map(feature => {
                    const isEnabled = getFeatureStatus(restaurant.restaurant_id, feature.key);
                    const rateLimits = getRateLimits(restaurant.restaurant_id, feature.key);
                    const usageStats = getFeatureUsageStats(restaurant.restaurant_id, feature.key);
                    
                    return (
                      <div key={feature.key} className="feature-cell">
                        <div className="feature-toggle">
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              checked={isEnabled}
                              onChange={(e) => handleFeatureToggle(
                                restaurant.restaurant_id, 
                                feature.key, 
                                e.target.checked
                              )}
                              disabled={updating}
                            />
                            <span className="toggle-slider"></span>
                          </label>
                        </div>
                        
                        {isEnabled && (
                          <div className="feature-details">
                            <div className="usage-stats">
                              <div className="stat-item">
                                <span className="stat-label">Daily:</span>
                                <span className="stat-value">{usageStats.daily_usage}</span>
                              </div>
                              <div className="stat-item">
                                <span className="stat-label">Monthly:</span>
                                <span className="stat-value">{usageStats.monthly_usage}</span>
                              </div>
                            </div>
                            
                            <div className="rate-limits">
                              <div className="rate-limit-item">
                                <label>Daily Limit:</label>
                                <input
                                  type="number"
                                  value={rateLimits.daily_limit || ''}
                                  onChange={(e) => {
                                    const newLimits = { 
                                      ...rateLimits, 
                                      daily_limit: parseInt(e.target.value) || undefined 
                                    };
                                    handleRateLimitUpdate(restaurant.restaurant_id, feature.key, newLimits);
                                  }}
                                  placeholder="No limit"
                                  className="limit-input"
                                  disabled={updating}
                                />
                              </div>
                              <div className="rate-limit-item">
                                <label>Hourly Limit:</label>
                                <input
                                  type="number"
                                  value={rateLimits.hourly_limit || ''}
                                  onChange={(e) => {
                                    const newLimits = { 
                                      ...rateLimits, 
                                      hourly_limit: parseInt(e.target.value) || undefined 
                                    };
                                    handleRateLimitUpdate(restaurant.restaurant_id, feature.key, newLimits);
                                  }}
                                  placeholder="No limit"
                                  className="limit-input"
                                  disabled={updating}
                                />
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Feature Statistics */}
      <div className="feature-statistics">
        <h3>Feature Statistics</h3>
        <div className="stats-grid">
          {availableFeatures.map(feature => {
            const enabledCount = filteredRestaurants.filter(restaurant => 
              getFeatureStatus(restaurant.restaurant_id, feature.key)
            ).length;
            const totalCount = filteredRestaurants.length;
            const enabledPercentage = totalCount > 0 ? Math.round((enabledCount / totalCount) * 100) : 0;
            
            return (
              <div key={feature.key} className="stat-card">
                <div className="stat-header">
                  <h4>{feature.name}</h4>
                  <div className="stat-percentage">{enabledPercentage}%</div>
                </div>
                <div className="stat-bar">
                  <div 
                    className="stat-fill" 
                    style={{ width: `${enabledPercentage}%` }}
                  ></div>
                </div>
                <div className="stat-details">
                  <span>{enabledCount} of {totalCount} restaurants enabled</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default FeatureManagement;