'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import './WebsiteBuilder.css'; // Reuse existing styles
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';
import { Eye, Edit, Trash2 } from 'lucide-react';

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

const MyWebsites: React.FC = () => {
  const router = useRouter();
  const [websites, setWebsites] = useState<Website[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWebsites();
  }, []);

  const fetchWebsites = async () => {
    try {
      console.log('🔍 DEBUG: My Websites - Starting fetchWebsites using centralized API service');
      
      // Use the same centralized API service as WebsiteBuilder
      const data = await websiteBuilderAPI.getWebsites();
      console.log('🔍 DEBUG: My Websites - Response data:', JSON.stringify(data, null, 2));
      
      setWebsites(data.websites || []);
    } catch (error) {
      console.error('🔍 DEBUG: My Websites - Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (websiteId: string) => {
    router.push(`/website-builder/edit/${websiteId}`);
  };

  const handlePreview = (websiteId: string) => {
    router.push(`/website-builder/preview/${websiteId}`);
  };

  const handleDelete = async (websiteId: string, websiteName: string) => {
    if (window.confirm(`Are you sure you want to delete "${websiteName}"? This action cannot be undone.`)) {
      try {
        console.log('🔍 DEBUG: My Websites - Deleting website:', websiteId);
        await websiteBuilderAPI.deleteWebsite(websiteId);
        console.log('🔍 DEBUG: My Websites - Website deleted successfully');
        
        // Refresh the websites list
        await fetchWebsites();
      } catch (error: any) {
        console.error('🔍 DEBUG: My Websites - Delete error:', error);
        alert(`Error deleting website: ${error.message}`);
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your websites...</p>
      </div>
    );
  }

  return (
    <div className="my-websites">
      <div className="websites-grid">
        {websites.map((website) => (
          <div key={website.website_id} className="website-card">
            <div className="website-preview">
              <div className="preview-placeholder">
                <div className="website-mockup">
                  <div className="mockup-header">
                    <div className="mockup-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                  <div className="mockup-content">
                    <div className="mockup-hero"></div>
                    <div className="mockup-section"></div>
                    <div className="mockup-section"></div>
                  </div>
                </div>
              </div>
              <div className="website-overlay">
                <div className={`status-dot ${website.status}`}></div>
              </div>
            </div>
            
            <div className="website-info">
              <div className="website-content">
                <div className="website-header">
                  <h3>{website.website_name}</h3>
                  <span className={`status-badge ${website.status}`}>
                    {website.status === 'published' ? '🟢 Published' : '🟡 Draft'}
                  </span>
                </div>
                
                <div className="website-meta">
                  <p className="website-category">
                    <span className="category-icon">
                      {website.design_category === 'fine_dining' ? '🍷' : 
                       website.design_category === 'casual_dining' ? '🍔' : 
                       website.design_category === 'fast_food' ? '🍕' : '☕'}
                    </span>
                    {website.design_category.replace('_', ' ')}
                  </p>
                  <p className="website-date">Created {website.created_at}</p>
                </div>
              </div>
              
              <div className="website-actions">
                <button 
                  className="btn-icon-only btn-preview"
                  onClick={() => handlePreview(website.website_id)}
                  title="Preview website"
                >
                  <Eye size={16} />
                </button>
                <button 
                  className="btn-icon-only btn-edit"
                  onClick={() => handleEdit(website.website_id)}
                  title="Edit website"
                >
                  <Edit size={16} />
                </button>
                <button 
                  className="btn-icon-only btn-delete"
                  onClick={() => handleDelete(website.website_id, website.website_name)}
                  title="Delete website"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {websites.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🌐</div>
            <h3>No websites yet</h3>
            <p>Create your first website to get started</p>
            <button 
              className="btn-primary"
              onClick={() => router.push('/dashboard?view=website-builder')}
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyWebsites;