'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import './WebsiteBuilder.css';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';

interface WebsiteBuilderProps {
  onBackToDashboard?: () => void;
}

interface Website {
  website_id: string;
  website_name: string;
  status: string;
  design_category: string;
  created_at: string;
  hero_image?: string;
  restaurant_id: string;
  restaurant_name?: string;
}

interface GenerationProgress {
  generation_id: string;
  status: string;
  progress_percentage: number;
  current_operation: string;
  website_id?: string;
  error_details?: string;
}

const WebsiteBuilder: React.FC<WebsiteBuilderProps> = ({ onBackToDashboard }) => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generationProgress, setGenerationProgress] = useState<GenerationProgress | null>(null);
  const [currentWebsiteIndex, setCurrentWebsiteIndex] = useState(0);
  const router = useRouter();

  const handleBackToDashboard = () => {
    if (onBackToDashboard) {
      onBackToDashboard();
    } else {
      // Fallback navigation
      router.push('/dashboard');
    }
  };

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    try {
      console.log('🔍 DEBUG: Website Builder - Starting fetchWebsites using centralized API service');
      
      // Use the centralized API service
      const data = await websiteBuilderAPI.getWebsites();
      console.log('🔍 DEBUG: Website Builder - Response data:', JSON.stringify(data, null, 2));
      console.log('🔍 DEBUG: Website Builder - Websites array:', JSON.stringify(data.websites, null, 2));
      console.log('🔍 DEBUG: Website Builder - Websites count:', data.websites ? data.websites.length : 0);
      
      // Log each website's structure for debugging
      if (data.websites && data.websites.length > 0) {
        data.websites.forEach((website: Website, index: number) => {
          console.log(`🔍 DEBUG: Website ${index + 1}:`, JSON.stringify({
            id: website.website_id,
            name: website.website_name,
            status: website.status,
            category: website.design_category,
            created: website.created_at,
            hero_image: website.hero_image,
            restaurant_id: website.restaurant_id
          }, null, 2));
        });
      } else {
        console.log('🔍 DEBUG: Website Builder - No websites found, showing empty state');
      }
      
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

  const handleEditWebsite = (websiteId: string) => {
    router.push(`/website-builder/edit/${websiteId}`);
  };

  const handlePreviewWebsite = (websiteId: string) => {
    router.push(`/website-builder/preview/${websiteId}`);
  };

  const handleDeleteWebsite = async (websiteId: string, websiteName: string) => {
    if (window.confirm(`Are you sure you want to delete "${websiteName}"? This action cannot be undone.`)) {
      try {
        console.log('🔍 DEBUG: Website Builder - Deleting website:', websiteId);
        await websiteBuilderAPI.deleteWebsite(websiteId);
        console.log('🔍 DEBUG: Website Builder - Website deleted successfully');
        
        // Refresh the websites list
        await fetchWebsites();
        
        // Adjust current index if necessary
        if (currentWebsiteIndex >= websites.length - 1 && websites.length > 1) {
          setCurrentWebsiteIndex(currentWebsiteIndex - 1);
        }
      } catch (error: any) {
        console.error('🔍 DEBUG: Website Builder - Delete error:', error);
        alert(`Error deleting website: ${error.message}`);
      }
    }
  };

  const handlePreviousWebsite = () => {
    setCurrentWebsiteIndex((prev) =>
      prev === 0 ? websites.length - 1 : prev - 1
    );
  };

  const handleNextWebsite = () => {
    setCurrentWebsiteIndex((prev) =>
      prev === websites.length - 1 ? 0 : prev + 1
    );
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
        <div className="header-top">
          <button
            className="back-button"
            onClick={handleBackToDashboard}
            title="Back to Dashboard"
          >
            <span className="back-icon">←</span>
            Back to Dashboard
          </button>
        </div>
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
              onClick={() => router.push('/website-builder/templates')}
            >
              🎨 Browse Templates
            </button>
          </div>
        </div>
      </div>

      {/* Website Carousel */}
      <div className="websites-carousel">
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
          <div className="carousel-container">
            {/* Navigation Arrows */}
            {websites.length > 1 && (
              <>
                <button
                  className="carousel-arrow carousel-arrow-left"
                  onClick={handlePreviousWebsite}
                  title="Previous website"
                >
                  <span>‹</span>
                </button>
                <button
                  className="carousel-arrow carousel-arrow-right"
                  onClick={handleNextWebsite}
                  title="Next website"
                >
                  <span>›</span>
                </button>
              </>
            )}

            {/* Current Website Display */}
            <div className="carousel-website">
              {(() => {
                const website = websites[currentWebsiteIndex];
                if (!website) return null;
                
                return (
                  <div className="website-card-fullscreen">
                    <div className="website-preview-fullscreen">
                      {website.hero_image ? (
                        <img
                          key={`${website.website_id}-${currentWebsiteIndex}`}
                          src={`${website.hero_image.startsWith('http') ? website.hero_image : `http://localhost:8000${website.hero_image}`}?t=${Date.now()}`}
                          alt={`${website.website_name} preview`}
                          className="website-preview-image-fullscreen"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            console.log(`🔍 DEBUG: Image failed to load: ${target.src}`);
                            target.style.display = 'none';
                            const placeholder = target.nextSibling as HTMLElement;
                            if (placeholder) {
                              placeholder.style.display = 'flex';
                            }
                          }}
                          onLoad={(e) => {
                            const target = e.target as HTMLImageElement;
                            console.log(`🔍 DEBUG: Image loaded successfully: ${target.src}`);
                            target.style.display = 'block';
                            const placeholder = target.nextSibling as HTMLElement;
                            if (placeholder) {
                              placeholder.style.display = 'none';
                            }
                          }}
                        />
                      ) : null}
                      <div className="preview-placeholder-fullscreen" style={{ display: website.hero_image ? 'none' : 'flex' }}>
                        <div className="website-mockup-fullscreen">
                          <div className="mockup-header-fullscreen">
                            <div className="mockup-dots">
                              <span></span>
                              <span></span>
                              <span></span>
                            </div>
                            <div className="mockup-url-fullscreen">🌐 {website.website_name?.toLowerCase().replace(/\s+/g, '') || 'website'}.com</div>
                          </div>
                          <div className="mockup-content-fullscreen">
                            <div className="mockup-hero-fullscreen">
                              <div className="mockup-hero-background">
                                <div className="mockup-hero-overlay"></div>
                                <div className="mockup-hero-content">
                                  <div className="mockup-logo-fullscreen">🍽️</div>
                                  <div className="mockup-title-fullscreen">{website.website_name || 'Restaurant'}</div>
                                  <div className="mockup-subtitle-fullscreen">{website.design_category?.replace('_', ' ') || 'Fine Dining'}</div>
                                  <div className="mockup-hero-buttons">
                                    <div className="mockup-btn-primary">View Menu</div>
                                    <div className="mockup-btn-secondary">Book Table</div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="mockup-navigation">
                              <div className="mockup-nav-item">Home</div>
                              <div className="mockup-nav-item">Menu</div>
                              <div className="mockup-nav-item">About</div>
                              <div className="mockup-nav-item">Contact</div>
                            </div>
                            <div className="mockup-sections-fullscreen">
                              <div className="mockup-section-fullscreen mockup-section-menu">
                                <div className="mockup-section-title">Our Menu</div>
                                <div className="mockup-menu-items">
                                  <div className="mockup-menu-item"></div>
                                  <div className="mockup-menu-item"></div>
                                  <div className="mockup-menu-item"></div>
                                </div>
                              </div>
                              <div className="mockup-section-fullscreen mockup-section-about">
                                <div className="mockup-section-title">About Us</div>
                                <div className="mockup-about-content"></div>
                              </div>
                              <div className="mockup-section-fullscreen mockup-section-contact">
                                <div className="mockup-section-title">Contact</div>
                                <div className="mockup-contact-info"></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="website-overlay-fullscreen">
                        <div className="status-indicator">
                          <span className={`status-dot ${website.status || 'draft'}`}></span>
                          <span className="status-text">{(website.status || 'draft').toUpperCase()}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="website-info-fullscreen">
                      <div className="website-header-fullscreen">
                        <h3>{website.website_name || 'Untitled Website'}</h3>
                        <span className={`status-badge ${website.status || 'draft'}`}>
                          {(website.status || 'draft').toUpperCase()}
                        </span>
                      </div>
                      <div className="website-details-fullscreen">
                        <p className="website-category">
                          <span className="category-icon">🏷️</span>
                          {website.design_category?.replace('_', ' ') || 'Restaurant Website'}
                        </p>
                        <p className="website-date">
                          <span className="date-icon">📅</span>
                          Created {website.created_at ? new Date(website.created_at).toLocaleDateString() : 'Recently'}
                        </p>
                        {website.restaurant_name && (
                          <p className="website-restaurant">
                            <span className="restaurant-icon">🏪</span>
                            {website.restaurant_name}
                          </p>
                        )}
                      </div>

                      <div className="website-actions-fullscreen">
                        <button
                          className="btn-secondary"
                          onClick={() => handlePreviewWebsite(website.website_id)}
                          title="Preview website"
                        >
                          <span className="btn-icon">👁️</span>
                          Preview
                        </button>
                        <button
                          className="btn-primary"
                          onClick={() => handleEditWebsite(website.website_id)}
                          title="Edit website"
                        >
                          <span className="btn-icon">✏️</span>
                          Edit
                        </button>
                        <button
                          className="btn-delete"
                          onClick={() => handleDeleteWebsite(website.website_id, website.website_name)}
                          title="Delete website"
                        >
                          <span className="btn-icon">🗑️</span>
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Carousel Indicators */}
            {websites.length > 1 && (
              <div className="carousel-indicators">
                {websites.map((_, index) => (
                  <button
                    key={index}
                    className={`carousel-indicator ${index === currentWebsiteIndex ? 'active' : ''}`}
                    onClick={() => setCurrentWebsiteIndex(index)}
                    title={`Go to website ${index + 1}`}
                  />
                ))}
              </div>
            )}

            {/* Website Counter */}
            {websites.length > 1 && (
              <div className="carousel-counter">
                <span>{currentWebsiteIndex + 1} of {websites.length}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {showGenerateModal && (
        <GenerateWebsiteModal 
          onClose={() => setShowGenerateModal(false)}
          onGenerate={(data: GenerationProgress) => {
            setGenerationProgress(data);
            setShowGenerateModal(false);
          }}
        />
      )}

      {generationProgress && (
        <GenerationProgressModal
          progress={generationProgress}
          onComplete={(websiteId?: string) => {
            setGenerationProgress(null);
            fetchWebsites();
            // Redirect to preview after successful generation
            if (websiteId) {
              router.push(`/website-builder/preview/${websiteId}`);
            }
          }}
        />
      )}
    </div>
  );
};

interface GenerateWebsiteModalProps {
  onClose: () => void;
  onGenerate: (data: GenerationProgress) => void;
}

const GenerateWebsiteModal: React.FC<GenerateWebsiteModalProps> = ({ onClose, onGenerate }) => {
  const [formData, setFormData] = useState({
    website_name: '',
    design_preferences: {},
    content_preferences: {},
    custom_requirements: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
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

      // Use the centralized API service
      const result = await websiteBuilderAPI.generateWebsite(requestData);
      console.log('🔍 DEBUG: Website Generation - Generation result:', result);
      onGenerate(result);
    } catch (error: any) {
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
              rows={3}
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

interface GenerationProgressModalProps {
  progress: GenerationProgress;
  onComplete: (websiteId?: string) => void;
}

const GenerationProgressModal: React.FC<GenerationProgressModalProps> = ({ progress, onComplete }) => {
  const [currentProgress, setCurrentProgress] = useState(progress);

  useEffect(() => {
    if (!progress?.generation_id) return;

    const pollProgress = async () => {
      try {
        // Use the centralized API service
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