import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for API calls
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Facebook Ads API calls
export const facebookAdsAPI = {
  createCampaign: async (formData) => {
    try {
      const response = await api.post('/campaigns/facebook-ads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create Facebook ad campaign');
    }
  },

  generatePreview: async (data) => {
    try {
      const response = await api.post('/campaigns/facebook-ads/preview', data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate ad preview');
    }
  },

  getCampaignStatus: async (campaignId) => {
    try {
      const response = await api.get(`/campaigns/facebook-ads/status/${campaignId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch campaign status');
    }
  }
};

// SMS Campaigns API calls
export const smsCampaignsAPI = {
  createCampaign: async (formData) => {
    try {
      const response = await api.post('/campaigns/sms', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create SMS campaign');
    }
  },

  generatePreview: async (formData) => {
    try {
      const response = await api.post('/campaigns/sms/preview', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate SMS preview');
    }
  },

  downloadSampleCSV: async () => {
    try {
      const response = await api.get('/campaigns/sms/sample-csv', {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'sample-customer-list.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      throw new Error('Failed to download sample CSV');
    }
  },

  getCampaignStatus: async (campaignId) => {
    try {
      const response = await api.get(`/campaigns/sms/status/${campaignId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch SMS campaign status');
    }
  }
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Server is not responding');
  }
};

// Authentication API calls
export const authAPI = {
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get user info');
    }
  },

  impersonate: async (restaurantId) => {
    try {
      const response = await api.post(`/auth/impersonate/${restaurantId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Impersonation failed');
    }
  },

  endImpersonation: async () => {
    try {
      const response = await api.post('/auth/end-impersonation');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to end impersonation');
    }
  }
};

// Dashboard API calls
export const dashboardAPI = {
  getRestaurantDashboard: async () => {
    try {
      const response = await api.get('/dashboard/restaurant');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch restaurant dashboard');
    }
  },

  getAdminDashboard: async () => {
    try {
      const response = await api.get('/dashboard/admin');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch admin dashboard');
    }
  },

  getAllRestaurants: async (search = '') => {
    try {
      const response = await api.get('/dashboard/restaurants', {
        params: { search }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch restaurants');
    }
  },

  getCampaigns: async () => {
    try {
      const response = await api.get('/dashboard/campaigns');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch campaigns');
    }
  },

  updateChecklistItem: async (itemId, isComplete) => {
    try {
      const response = await api.put(`/dashboard/checklist/${itemId}`, {
        is_complete: isComplete
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update checklist item');
    }
  }
};

// Admin Analytics API calls
export const adminAnalyticsAPI = {
  // Real-time metrics
  getRealTimeMetrics: async () => {
    try {
      const response = await api.get('/admin/analytics/real-time');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch real-time metrics');
    }
  },

  // Usage analytics
  getUsageAnalytics: async (days = 7, featureType = null) => {
    try {
      const params = { days };
      if (featureType) params.feature_type = featureType;
      const response = await api.get('/admin/analytics/usage', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch usage analytics');
    }
  },

  // Restaurant analytics
  getRestaurantAnalytics: async (restaurantId, days = 30) => {
    try {
      const response = await api.get(`/admin/analytics/restaurant/${restaurantId}`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch restaurant analytics');
    }
  },

  // Dashboard summary
  getDashboardSummary: async () => {
    try {
      const response = await api.get('/admin/dashboard/summary');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch dashboard summary');
    }
  },

  // Flagged content
  getFlaggedContent: async (status = 'flagged', limit = 50) => {
    try {
      const response = await api.get('/admin/moderation/flagged-content', {
        params: { status, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch flagged content');
    }
  },

  // Moderate content
  moderateContent: async (moderationId, action, reason = null) => {
    try {
      const response = await api.post('/admin/moderation/moderate-content', null, {
        params: { moderation_id: moderationId, action, reason }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to moderate content');
    }
  },

  // Bulk moderate content
  bulkModerateContent: async (contentIds, action, reason = null) => {
    try {
      const response = await api.post('/admin/moderation/bulk-moderate', {
        content_ids: contentIds,
        action,
        reason
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to bulk moderate content');
    }
  },

  // Feature toggles
  getFeatureToggles: async (restaurantId = null) => {
    try {
      const params = restaurantId ? { restaurant_id: restaurantId } : {};
      const response = await api.get('/admin/features/toggles', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch feature toggles');
    }
  },

  // Update feature toggle
  updateFeatureToggle: async (restaurantId, featureName, enabled, rateLimits = null) => {
    try {
      const response = await api.post('/admin/features/toggle', {
        restaurant_id: restaurantId,
        feature_name: featureName,
        enabled,
        rate_limits: rateLimits
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update feature toggle');
    }
  },

  // Check feature status
  checkFeatureStatus: async (restaurantId, featureName) => {
    try {
      const response = await api.get(`/admin/features/check/${restaurantId}/${featureName}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to check feature status');
    }
  }
};

// Checklist API calls
export const checklistAPI = {
  // Get all categories with optional type filter
  getCategories: async (type = null) => {
    try {
      const params = type ? { type } : {};
      const response = await api.get('/checklist/categories', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch categories');
    }
  },

  // Get items for a specific category
  getItems: async (categoryId) => {
    try {
      const response = await api.get(`/checklist/items/${categoryId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch items');
    }
  },

  // Get checklist status for restaurant
  getStatus: async (restaurantId) => {
    try {
      const response = await api.get(`/checklist/status/${restaurantId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch status');
    }
  },

  // Update item status
  updateStatus: async (restaurantId, itemId, status, notes = null) => {
    try {
      const params = { status };
      if (notes) params.notes = notes;
      
      const response = await api.put(`/checklist/status/${restaurantId}/${itemId}`, null, {
        params
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update status');
    }
  },

  // Get progress statistics
  getProgress: async (restaurantId, type = null) => {
    try {
      const params = type ? { type } : {};
      const response = await api.get(`/checklist/progress/${restaurantId}`, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch progress');
    }
  },

  // Get all categories with their items and status
  getCategoriesWithItems: async (type = null, restaurantId = null) => {
    try {
      const params = {};
      if (type) params.type = type;
      if (restaurantId) params.restaurantId = restaurantId;
      
      const response = await api.get('/checklist/categories-with-items', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch categories with items');
    }
  }
};

// AI Image Enhancement API calls
export const imageEnhancementAPI = {
  // Upload and enhance image
  enhanceImage: async (formData, onProgress = null) => {
    try {
      console.log('API: Starting image enhancement request...');
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 15000, // 15 seconds for image processing
      };

      if (onProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log('API: Upload progress:', percentCompleted + '%');
          onProgress(percentCompleted);
        };
      }

      console.log('API: Making POST request to /ai/content/image-enhancement');
      const response = await api.post('/ai/content/image-enhancement', formData, config);
      console.log('API: Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('API: Image enhancement error:', error);
      console.error('API: Error response:', error.response?.data);
      console.error('API: Error status:', error.response?.status);
      throw new Error(error.response?.data?.error || error.message || 'Image enhancement failed');
    }
  },

  // Generate marketing content from image
  generateContent: async (requestData) => {
    try {
      const response = await api.post('/ai/content/image/generate-content', requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 45000, // 45 seconds for content generation
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Content generation failed');
    }
  },

  // Get user's enhanced images
  getImages: async () => {
    try {
      const response = await api.get('/ai/content/images');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch images');
    }
  },

  // Delete an image
  deleteImage: async (imageId) => {
    try {
      const response = await api.delete(`/ai/content/images/${imageId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to delete image');
    }
  },

  // Get image details
  getImageDetails: async (imageId) => {
    try {
      const response = await api.get(`/ai/content/images/${imageId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch image details');
    }
  }
};

export default api;