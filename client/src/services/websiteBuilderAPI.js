/**
 * Website Builder API Service
 * Centralized API service for all website builder functionality
 * Uses the same pattern as working features for consistency
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.text().catch(() => 'Unknown error');
    throw new Error(`API Error (${response.status}): ${errorData}`);
  }
  return response.json();
};

export const websiteBuilderAPI = {
  // List all websites for the current restaurant
  getWebsites: async (page = 1, perPage = 10, status = null) => {
    const url = new URL(`${API_BASE_URL}/api/website-builder/websites`);
    url.searchParams.append('page', page);
    url.searchParams.append('per_page', perPage);
    if (status) url.searchParams.append('status', status);

    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Get details for a specific website
  getWebsiteDetails: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Generate a new website using AI
  generateWebsite: async (requestData) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(requestData)
    });
    
    return handleResponse(response);
  },

  // Get generation progress for an ongoing website generation
  getGenerationProgress: async (generationId) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/generation/${generationId}/progress`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Update website settings and content
  updateWebsite: async (websiteId, updateData) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updateData)
    });
    
    return handleResponse(response);
  },

  // Regenerate website with new requirements
  regenerateWebsite: async (websiteId, regenerateData) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}/regenerate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(regenerateData)
    });
    
    return handleResponse(response);
  },

  // Generate website preview
  generatePreview: async (websiteId, previewRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}/preview`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(previewRequest)
    });
    
    return handleResponse(response);
  },

  // Publish website
  publishWebsite: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}/publish`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Get website templates
  getTemplates: async (category = null) => {
    const url = new URL(`${API_BASE_URL}/api/website-builder/templates`);
    if (category) url.searchParams.append('category', category);

    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Create website from template
  createFromTemplate: async (templateData) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/templates/create`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(templateData)
    });
    
    return handleResponse(response);
  },

  // Get website builder dashboard data
  getDashboard: async () => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/dashboard`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Delete website (if implemented in backend)
  deleteWebsite: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites/${websiteId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  }
};

export default websiteBuilderAPI;