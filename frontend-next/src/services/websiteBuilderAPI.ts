/**
 * Website Builder API Service
 * Centralized API service for all website builder functionality
 * Uses the same pattern as working features for consistency
 */

// Determine the correct API base URL based on environment
const getApiBaseUrl = () => {
  // Next.js environment variables (client-side must be prefixed with NEXT_PUBLIC_)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Production environment detection
  if (process.env.NODE_ENV === 'production') {
    // Use the production backend URL
    return 'https://final-mvp-jc3a.onrender.com/api';
  }
  
  // Development fallback
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.text().catch(() => 'Unknown error');
    throw new Error(`API Error (${response.status}): ${errorData}`);
  }
  return response.json();
};

export const websiteBuilderAPI = {
  // List all websites for the current restaurant
  getWebsites: async (page = 1, perPage = 10, status = null) => {
    const url = new URL(`${API_BASE_URL}/website-builder/websites`);
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
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Generate a new website using AI
  generateWebsite: async (requestData) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(requestData)
    });
    
    return handleResponse(response);
  },

  // Get generation progress for an ongoing website generation
  getGenerationProgress: async (generationId) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/generation/${generationId}/progress`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Update website settings and content
  updateWebsite: async (websiteId, updateData) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updateData)
    });
    
    return handleResponse(response);
  },

  // Regenerate website with new requirements
  regenerateWebsite: async (websiteId, regenerateData) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/regenerate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(regenerateData)
    });
    
    return handleResponse(response);
  },

  // Generate website preview
  generatePreview: async (websiteId, previewRequest) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/preview`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(previewRequest)
    });
    
    return handleResponse(response);
  },

  // Publish website
  publishWebsite: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/publish`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Get website templates
  getTemplates: async (category = null) => {
    const url = new URL(`${API_BASE_URL}/website-builder/templates`);
    if (category) url.searchParams.append('category', category);

    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Create website from template
  createFromTemplate: async (templateData) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/templates/create`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(templateData)
    });
    
    return handleResponse(response);
  },

  // Get website builder dashboard data
  getDashboard: async () => {
    const response = await fetch(`${API_BASE_URL}/website-builder/dashboard`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Delete website (if implemented in backend)
  deleteWebsite: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Update website content (for inline editing)
  updateContent: async (websiteId, contentUpdates) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/content`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(contentUpdates)
    });
    
    return handleResponse(response);
  },

  // Media Upload Methods
  
  // Upload image
  uploadImage: async (file, imageType = 'general', websiteId = null, onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('image_type', imageType);
    if (websiteId) {
      formData.append('website_id', websiteId);
    }

    const token = localStorage.getItem('token');
    const headers = {
      'Authorization': `Bearer ${token}`
      // Don't set Content-Type for FormData, let browser set it with boundary
    };

    // Use XMLHttpRequest for progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed: Network error'));
      });

      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload failed: Request timeout'));
      });

      xhr.timeout = 30000; // 30 seconds

      xhr.open('POST', `${API_BASE_URL}/website-builder/upload-image`);
      
      // Set headers
      Object.keys(headers).forEach(key => {
        xhr.setRequestHeader(key, headers[key]);
      });

      xhr.send(formData);
    });
  },

  // New V2 Image Upload
  uploadImageV2: async (file, imageType = 'general', onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('image_type', imageType);

    const token = localStorage.getItem('token');
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('Upload failed: Network error')));
      xhr.addEventListener('timeout', () => reject(new Error('Upload failed: Request timeout')));

      xhr.timeout = 30000;

      xhr.open('POST', `${API_BASE_URL}/website-builder/upload-image-v2`);
      
      Object.keys(headers).forEach(key => {
        xhr.setRequestHeader(key, headers[key]);
      });

      xhr.send(formData);
    });
  },

  getImageV2: (filename) => {
    return `${API_BASE_URL}/website-builder/images-v2/${filename}`;
  },

  // Get image
  getImage: (filename) => {
    return `${API_BASE_URL}/website-builder/images/${filename}`;
  },

  // Get thumbnail
  getThumbnail: (filename, size = 'medium', format = 'jpeg') => {
    return `${API_BASE_URL}/website-builder/images/thumbnail/${filename}?size=${size}&format=${format}`;
  },

  // List images
  listImages: async (imageType = null, websiteId = null) => {
    const url = new URL(`${API_BASE_URL}/website-builder/images`);
    if (imageType) url.searchParams.append('image_type', imageType);
    if (websiteId) url.searchParams.append('website_id', websiteId);

    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Delete image
  deleteImage: async (imageId) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/images/${imageId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Color Theme Methods
  
  // Update color theme
  updateColorTheme: async (websiteId, colorUpdates) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/colors`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(colorUpdates)
    });
    
    return handleResponse(response);
  },

  // Get color theme
  getColorTheme: async (websiteId) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/colors`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Apply color preset
  applyColorPreset: async (websiteId, presetName) => {
    const response = await fetch(`${API_BASE_URL}/website-builder/websites/${websiteId}/colors/preset`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ preset_name: presetName })
    });
    
    return handleResponse(response);
  }
};

export default websiteBuilderAPI;