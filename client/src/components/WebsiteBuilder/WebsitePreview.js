import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './WebsitePreview.css';

const WebsitePreview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [website, setWebsite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewMode, setPreviewMode] = useState('desktop'); // desktop, tablet, mobile

  useEffect(() => {
    fetchWebsiteData();
  }, [id]);

  const fetchWebsiteData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/website-builder/websites/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setWebsite(data.website);
      } else {
        setError('Failed to load website data');
      }
    } catch (error) {
      console.error('Error fetching website:', error);
      setError('Error loading website');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    navigate(`/website-builder/edit/${id}`);
  };

  const handlePublish = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/website-builder/websites/${id}/publish`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Website published successfully!');
        fetchWebsiteData(); // Refresh data
      } else {
        alert('Failed to publish website');
      }
    } catch (error) {
      console.error('Error publishing website:', error);
      alert('Error publishing website');
    }
  };

  const renderWebsiteContent = () => {
    if (!website?.generated_content) {
      return (
        <div className="preview-placeholder">
          <div className="placeholder-icon">🌐</div>
          <h3>No content available</h3>
          <p>This website hasn't been generated yet or the content is missing.</p>
        </div>
      );
    }

    const content = website.generated_content;
    
    // Create a complete HTML document with the generated content
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${website.website_name || 'Restaurant Website'}</title>
        <style>
          ${content.css || ''}
          
          /* Additional responsive styles */
          body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          }
          
          .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
          }
          
          @media (max-width: 768px) {
            .container {
              padding: 0 15px;
            }
          }
        </style>
      </head>
      <body>
        ${content.html || '<div class="container"><h1>Welcome to ' + (website.website_name || 'Our Restaurant') + '</h1><p>Your website content will appear here.</p></div>'}
        
        <script>
          // Prevent forms from submitting in preview
          document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
              form.addEventListener('submit', function(e) {
                e.preventDefault();
                alert('This is a preview - forms are disabled');
              });
            });
            
            // Prevent external links from navigating
            const links = document.querySelectorAll('a[href^="http"]');
            links.forEach(link => {
              link.addEventListener('click', function(e) {
                e.preventDefault();
                alert('External links are disabled in preview mode');
              });
            });
          });
        </script>
      </body>
      </html>
    `;

    return (
      <iframe
        className={`website-iframe ${previewMode}`}
        srcDoc={htmlContent}
        title="Website Preview"
        sandbox="allow-scripts allow-same-origin"
      />
    );
  };

  if (loading) {
    return (
      <div className="preview-loading">
        <div className="loading-spinner"></div>
        <p>Loading website preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-error">
        <div className="error-icon">⚠️</div>
        <h3>Error Loading Preview</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => navigate('/website-builder')}>
          Back to Website Builder
        </button>
      </div>
    );
  }

  return (
    <div className="website-preview">
      {/* Header with controls */}
      <div className="preview-header">
        <div className="preview-title">
          <button 
            className="back-btn"
            onClick={() => navigate('/website-builder')}
          >
            ← Back
          </button>
          <div className="title-info">
            <h1>{website?.website_name || 'Website Preview'}</h1>
            <span className={`status-badge ${website?.status}`}>
              {website?.status || 'draft'}
            </span>
          </div>
        </div>

        <div className="preview-actions">
          <div className="device-selector">
            <button 
              className={`device-btn ${previewMode === 'desktop' ? 'active' : ''}`}
              onClick={() => setPreviewMode('desktop')}
              title="Desktop View"
            >
              🖥️
            </button>
            <button 
              className={`device-btn ${previewMode === 'tablet' ? 'active' : ''}`}
              onClick={() => setPreviewMode('tablet')}
              title="Tablet View"
            >
              📱
            </button>
            <button 
              className={`device-btn ${previewMode === 'mobile' ? 'active' : ''}`}
              onClick={() => setPreviewMode('mobile')}
              title="Mobile View"
            >
              📱
            </button>
          </div>

          <div className="action-buttons">
            <button className="btn-secondary" onClick={handleEdit}>
              ✏️ Edit
            </button>
            {website?.status !== 'published' && (
              <button className="btn-primary" onClick={handlePublish}>
                🚀 Publish
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Website info panel */}
      <div className="website-info-panel">
        <div className="info-item">
          <span className="info-label">Created:</span>
          <span className="info-value">
            {website?.created_at ? new Date(website.created_at).toLocaleDateString() : 'Unknown'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Category:</span>
          <span className="info-value">
            {website?.design_category?.replace('_', ' ') || 'General'}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Last Updated:</span>
          <span className="info-value">
            {website?.updated_at ? new Date(website.updated_at).toLocaleDateString() : 'Never'}
          </span>
        </div>
      </div>

      {/* Preview container */}
      <div className="preview-container">
        {renderWebsiteContent()}
      </div>

      {/* Generation details (if available) */}
      {website?.generation_details && (
        <div className="generation-details">
          <h3>Generation Details</h3>
          <div className="details-grid">
            {website.generation_details.features_used && (
              <div className="detail-item">
                <strong>Features Used:</strong>
                <ul>
                  {website.generation_details.features_used.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            )}
            {website.generation_details.ai_model && (
              <div className="detail-item">
                <strong>AI Model:</strong> {website.generation_details.ai_model}
              </div>
            )}
            {website.generation_details.generation_time && (
              <div className="detail-item">
                <strong>Generation Time:</strong> {website.generation_details.generation_time}s
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WebsitePreview;