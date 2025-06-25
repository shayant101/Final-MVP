import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

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
      const response = await api.post('/facebook-ads/create-campaign', formData, {
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
      const response = await api.post('/facebook-ads/generate-preview', data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate ad preview');
    }
  },

  getCampaignStatus: async (campaignId) => {
    try {
      const response = await api.get(`/facebook-ads/campaign-status/${campaignId}`);
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
      const response = await api.post('/sms-campaigns/create-campaign', formData, {
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
      const response = await api.post('/sms-campaigns/preview', formData, {
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
      const response = await api.get('/sms-campaigns/sample-csv', {
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
      const response = await api.get(`/sms-campaigns/campaign-status/${campaignId}`);
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

export default api;