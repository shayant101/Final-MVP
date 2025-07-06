import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './WebsiteBuilder.css';

// Import the centralized API service like working features do
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create API helper that matches working features pattern
const websiteBuilderAPI = {
  getWebsites: async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/website-builder/websites`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Failed to fetch websites: ${errorData}`);
    }
    
    return response.json();
  },
  
  generateWebsite: async (requestData) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/website-builder/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to generate website');
    }
    
    return response.json();
  },
  
  getGenerationProgress: async (generationId) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/website-builder/generation/${generationId}/progress`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error('Failed to get generation progress');
    }
    
    return response.json();
  }
};

const WebsiteBuilder = () => {
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    try {
      console.log('🔍 DEBUG: Website Builder - Starting fetchWebsites using new API pattern');
      
      // Use the new API helper that matches working features
      const data = await websiteBuilderAPI.getWebsites();
      console.log('🔍 DEBUG: Website Builder - Response data:', data);
      setWebsites(data.websites || []);
    } catch (error) {
      console.error('🔍 DEBUG: Website Builder - Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateWebsite = () => {
    setShowGenerateModal(true);
  };

  const handleEditWebsite = (websiteId) => {
    navigate(`/website-builder/edit/${websiteId}`);
  };

  const handlePreviewWebsite = (websiteId) => {
    navigate(`/website-builder/preview/${websiteId}`);
  };

  if (loading) {
    return (
      <div className="website-builder-loading">
        <div className="loading-spinner"></div>
        <p>Loading your websites...</p>
      </div>
    );
  }

  return (
    <div className="website-builder">
      <div className="website-builder-header">
        <h1>🌐 Website Builder</h1>
        <p>Create stunning restaurant websites with AI-powered design or choose from professional templates</p>
        
        {/* Builder Options */}
        <div className="builder-options">
          <div className="builder-option">
            <div className="option-icon">🤖</div>
            <h3>AI-Powered Website Builder</h3>
            <p>Let AI create a custom website based on your restaurant's unique needs</p>
            <button
              className="btn-primary option-btn"
              onClick={handleGenerateWebsite}
            >
              ✨ Generate with AI
            </button>
          </div>
          
          <div className="builder-option">
            <div className="option-icon">📋</div>
            <h3>Template-Based Website Builder</h3>
            <p>Choose from professionally designed restaurant templates and customize them</p>
            <button
              className="btn-secondary option-btn"
              onClick={() => navigate('/website-builder/templates')}
            >
              🎨 Browse Templates
            </button>
          </div>
        </div>
      </div>

      <div className="websites-grid">
        {websites.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🌐</div>
            <h3>No websites yet</h3>
            <p>Create your first AI-powered restaurant website</p>
            <button 
              className="btn-primary"
              onClick={handleGenerateWebsite}
            >
              Get Started
            </button>
          </div>
        ) : (
          websites.map(website => (
            <div key={website.website_id} className="website-card">
              <div className="website-preview">
                <div className="preview-placeholder">
                  <span>🍽️</span>
                </div>
              </div>
              
              <div className="website-info">
                <h3>{website.website_name}</h3>
                <p className="website-status">
                  <span className={`status-badge ${website.status}`}>
                    {website.status}
                  </span>
                </p>
                <p className="website-category">
                  {website.design_category?.replace('_', ' ')}
                </p>
                <p className="website-date">
                  Created {new Date(website.created_at).toLocaleDateString()}
                </p>
              </div>

              <div className="website-actions">
                <button 
                  className="btn-secondary"
                  onClick={() => handlePreviewWebsite(website.website_id)}
                >
                  👁️ Preview
                </button>
                <button 
                  className="btn-primary"
                  onClick={() => handleEditWebsite(website.website_id)}
                >
                  ✏️ Edit
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {showGenerateModal && (
        <GenerateWebsiteModal 
          onClose={() => setShowGenerateModal(false)}
          onGenerate={(data) => {
            setGenerationProgress(data);
            setShowGenerateModal(false);
          }}
        />
      )}

      {generationProgress && (
        <GenerationProgressModal
          progress={generationProgress}
          onComplete={(websiteId) => {
            setGenerationProgress(null);
            fetchWebsites();
            // Redirect to preview after successful generation
            if (websiteId) {
              navigate(`/website-builder/preview/${websiteId}`);
            }
          }}
        />
      )}
    </div>
  );
};

const GenerateWebsiteModal = ({ onClose, onGenerate }) => {
  const [formData, setFormData] = useState({
    website_name: '',
    design_preferences: {},
    content_preferences: {},
    custom_requirements: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log('🔍 DEBUG: Website Generation - Starting using working feature pattern');
      
      // Use the same pattern as working features - import and use the centralized API
      const { dashboardAPI } = await import('../../services/api');
      
      // Get restaurant data using the same successful method as working features
      const restaurantData = await dashboardAPI.getRestaurantDashboard();
      console.log('🔍 DEBUG: Website Generation - Restaurant data from dashboard API:', restaurantData);
      
      if (!restaurantData || !restaurantData.restaurant || !restaurantData.restaurant.restaurant_id) {
        console.error('🔍 DEBUG: Website Generation - Invalid restaurant data structure');
        alert('No restaurant found. Please create a restaurant first.');
        return;
      }
      
      // Use the restaurant ID from the dashboard data (same as working features)
      const restaurant_id = restaurantData.restaurant.restaurant_id;
      console.log('🔍 DEBUG: Website Generation - Using restaurant_id:', restaurant_id);
      
      const requestData = {
        restaurant_id: restaurant_id,
        ...formData
      };

      // Use the new API helper that matches working features pattern
      const result = await websiteBuilderAPI.generateWebsite(requestData);
      console.log('🔍 DEBUG: Website Generation - Generation result:', result);
      onGenerate(result);
    } catch (error) {
      console.error('Error generating website:', error);
      alert(`Error generating website: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal generate-modal">
        <div className="modal-header">
          <h2>✨ Generate New Website</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="generate-form">
          <div className="form-group">
            <label>Website Name</label>
            <input
              type="text"
              value={formData.website_name}
              onChange={(e) => setFormData({...formData, website_name: e.target.value})}
              placeholder="My Restaurant Website"
              required
            />
          </div>

          <div className="form-group">
            <label>Special Requirements (Optional)</label>
            <textarea
              value={formData.custom_requirements}
              onChange={(e) => setFormData({...formData, custom_requirements: e.target.value})}
              placeholder="Any specific features or design preferences..."
              rows="3"
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Generating...' : '🚀 Generate Website'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const GenerationProgressModal = ({ progress, onComplete }) => {
  const [currentProgress, setCurrentProgress] = useState(progress);

  useEffect(() => {
    if (!progress?.generation_id) return;

    const pollProgress = async () => {
      try {
        // Use the new API helper that matches working features pattern
        const data = await websiteBuilderAPI.getGenerationProgress(progress.generation_id);
        setCurrentProgress(data);

        if (data.status === 'completed') {
          setTimeout(() => onComplete(data.website_id), 2000); // Show completion for 2 seconds
        } else if (data.status === 'failed') {
          alert('Website generation failed: ' + data.error_details);
          onComplete();
        }
      } catch (error) {
        console.error('Error polling progress:', error);
      }
    };

    const interval = setInterval(pollProgress, 2000);
    return () => clearInterval(interval);
  }, [progress?.generation_id, onComplete]);

  return (
    <div className="modal-overlay">
      <div className="modal progress-modal">
        <div className="modal-header">
          <h2>🤖 Generating Your Website</h2>
        </div>

        <div className="progress-content">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${currentProgress?.progress_percentage || 0}%` }}
            />
          </div>
          
          <p className="progress-text">
            {currentProgress?.progress_percentage?.toFixed(0) || 0}% Complete
          </p>
          
          <p className="current-step">
            {currentProgress?.current_operation || 'Initializing...'}
          </p>

          {currentProgress?.status === 'completed' && (
            <div className="completion-message">
              <div className="success-icon">✅</div>
              <p>Website generated successfully!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WebsiteBuilder;