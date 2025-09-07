'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import { dashboardAPI } from '../../../services/api';
import LoadingScreen from '../../../components/LoadingScreen';
import '../../../components/AdminDashboard.css';

interface Restaurant {
  restaurant_id: string;
  name: string;
  email: string;
  signup_date: string;
  address?: string;
}

const AdminRestaurantsPage = () => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { impersonate } = useAuth();

  useEffect(() => {
    fetchRestaurants();
  }, []);

  const fetchRestaurants = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getAllRestaurants(searchTerm);
      setRestaurants(data.restaurants || []);
    } catch (error) {
      console.error('Error fetching restaurants:', error);
      setError('Failed to fetch restaurants');
    } finally {
      setLoading(false);
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
      const { default: api } = await import('../../../services/api');
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

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-main-content">
        <div className="main-header">
          <div className="header-title">
            <h1>Restaurant Management</h1>
            <p>Manage all restaurants on the platform</p>
          </div>
        </div>
        
        <div className="content-area">
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
        </div>
      </div>
    </div>
  );
};

export default AdminRestaurantsPage;