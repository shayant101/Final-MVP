import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './WebsiteEditor.css';
import { websiteBuilderAPI } from '../../services/websiteBuilderAPI';

const WebsiteEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [website, setWebsite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('content'); // content, design, settings
  const [hasChanges, setHasChanges] = useState(false);

  // Editable content state
  const [editableContent, setEditableContent] = useState({
    website_name: '',
    html: '',
    css: '',
    custom_requirements: '',
    design_preferences: {}
  });

  const fetchWebsiteData = useCallback(async () => {
    try {
      console.log('🔍 DEBUG: WebsiteEditor - Starting fetchWebsiteData using centralized API service');
      console.log('🔍 DEBUG: WebsiteEditor - Website ID:', id);
      
      // Use the centralized API service
      const data = await websiteBuilderAPI.getWebsiteDetails(id);
      console.log('🔍 DEBUG: WebsiteEditor - Response data:', data);
      
      setWebsite(data);
      
      // Initialize editable content
      setEditableContent({
        website_name: data.website_name || '',
        html: data.generated_content?.html || '',
        css: data.generated_content?.css || '',
        custom_requirements: data.custom_requirements || '',
        design_preferences: data.design_preferences || {}
      });
      
      console.log('🔍 DEBUG: WebsiteEditor - Website data loaded successfully');
    } catch (error) {
      console.error('🔍 DEBUG: WebsiteEditor - Error fetching website:', error);
      setError('Error loading website: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchWebsiteData();
  }, [fetchWebsiteData]);

  const handleContentChange = (field, value) => {
    setEditableContent(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      console.log('🔍 DEBUG: WebsiteEditor - Starting save using centralized API service');
      
      const updateData = {
        website_name: editableContent.website_name,
        generated_content: {
          html: editableContent.html,
          css: editableContent.css
        },
        custom_requirements: editableContent.custom_requirements,
        design_preferences: editableContent.design_preferences
      };
      
      // Use the centralized API service
      await websiteBuilderAPI.updateWebsite(id, updateData);
      
      setHasChanges(false);
      alert('Website saved successfully!');
      fetchWebsiteData(); // Refresh data
      console.log('🔍 DEBUG: WebsiteEditor - Save completed successfully');
    } catch (error) {
      console.error('🔍 DEBUG: WebsiteEditor - Error saving website:', error);
      alert('Error saving website: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handlePreview = () => {
    navigate(`/website-builder/preview/${id}`);
  };

  const handleRegenerate = async () => {
    if (!window.confirm('This will regenerate the entire website and overwrite your changes. Are you sure?')) {
      return;
    }

    try {
      console.log('🔍 DEBUG: WebsiteEditor - Starting regenerate using centralized API service');
      
      const regenerateData = {
        custom_requirements: editableContent.custom_requirements,
        design_preferences: editableContent.design_preferences
      };
      
      // Use the centralized API service
      await websiteBuilderAPI.regenerateWebsite(id, regenerateData);
      
      alert('Website regeneration started! You will be redirected when complete.');
      // Could implement polling here similar to the generation progress
      setTimeout(() => {
        fetchWebsiteData();
      }, 5000);
      console.log('🔍 DEBUG: WebsiteEditor - Regenerate started successfully');
    } catch (error) {
      console.error('🔍 DEBUG: WebsiteEditor - Error regenerating website:', error);
      alert('Error regenerating website: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="editor-loading">
        <div className="loading-spinner"></div>
        <p>Loading website editor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="editor-error">
        <div className="error-icon">⚠️</div>
        <h3>Error Loading Editor</h3>
        <p>{error}</p>
        <button className="btn-primary" onClick={() => navigate('/website-builder')}>
          Back to Website Builder
        </button>
      </div>
    );
  }

  return (
    <div className="website-editor">
      {/* Header */}
      <div className="editor-header">
        <div className="editor-title">
          <button 
            className="back-btn"
            onClick={() => navigate('/website-builder')}
          >
            ← Back
          </button>
          <div className="title-info">
            <h1>Edit: {website?.website_name || 'Website'}</h1>
            {hasChanges && <span className="changes-indicator">• Unsaved changes</span>}
          </div>
        </div>

        <div className="editor-actions">
          <button className="btn-secondary" onClick={handlePreview}>
            👁️ Preview
          </button>
          <button 
            className="btn-secondary" 
            onClick={handleRegenerate}
            title="Regenerate entire website with AI"
          >
            🔄 Regenerate
          </button>
          <button 
            className="btn-primary" 
            onClick={handleSave}
            disabled={saving || !hasChanges}
          >
            {saving ? 'Saving...' : '💾 Save Changes'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="editor-tabs">
        <button 
          className={`tab-btn ${activeTab === 'content' ? 'active' : ''}`}
          onClick={() => setActiveTab('content')}
        >
          📝 Content
        </button>
        <button 
          className={`tab-btn ${activeTab === 'design' ? 'active' : ''}`}
          onClick={() => setActiveTab('design')}
        >
          🎨 Design
        </button>
        <button 
          className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      {/* Editor Content */}
      <div className="editor-content">
        {activeTab === 'content' && (
          <div className="content-editor">
            <div className="editor-section">
              <h3>Website Name</h3>
              <input
                type="text"
                value={editableContent.website_name}
                onChange={(e) => handleContentChange('website_name', e.target.value)}
                placeholder="Enter website name"
                className="form-input"
              />
            </div>

            <div className="editor-section">
              <h3>HTML Content</h3>
              <textarea
                value={editableContent.html}
                onChange={(e) => handleContentChange('html', e.target.value)}
                placeholder="HTML content will appear here..."
                className="code-editor html-editor"
                rows="15"
              />
              <p className="editor-help">
                💡 Edit the HTML structure of your website. Be careful with the markup structure.
              </p>
            </div>

            <div className="editor-section">
              <h3>Custom Requirements</h3>
              <textarea
                value={editableContent.custom_requirements}
                onChange={(e) => handleContentChange('custom_requirements', e.target.value)}
                placeholder="Describe any specific requirements or changes you'd like..."
                className="form-textarea"
                rows="4"
              />
              <p className="editor-help">
                💡 These requirements will be used when regenerating the website.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'design' && (
          <div className="design-editor">
            <div className="editor-section">
              <h3>CSS Styles</h3>
              <textarea
                value={editableContent.css}
                onChange={(e) => handleContentChange('css', e.target.value)}
                placeholder="CSS styles will appear here..."
                className="code-editor css-editor"
                rows="20"
              />
              <p className="editor-help">
                💡 Customize the visual appearance of your website with CSS.
              </p>
            </div>

            <div className="editor-section">
              <h3>Quick Style Options</h3>
              <div className="style-options">
                <div className="style-group">
                  <label>Primary Color</label>
                  <input
                    type="color"
                    value={editableContent.design_preferences.primary_color || '#667eea'}
                    onChange={(e) => handleContentChange('design_preferences', {
                      ...editableContent.design_preferences,
                      primary_color: e.target.value
                    })}
                    className="color-input"
                  />
                </div>
                <div className="style-group">
                  <label>Secondary Color</label>
                  <input
                    type="color"
                    value={editableContent.design_preferences.secondary_color || '#764ba2'}
                    onChange={(e) => handleContentChange('design_preferences', {
                      ...editableContent.design_preferences,
                      secondary_color: e.target.value
                    })}
                    className="color-input"
                  />
                </div>
                <div className="style-group">
                  <label>Font Family</label>
                  <select
                    value={editableContent.design_preferences.font_family || 'default'}
                    onChange={(e) => handleContentChange('design_preferences', {
                      ...editableContent.design_preferences,
                      font_family: e.target.value
                    })}
                    className="form-select"
                  >
                    <option value="default">Default</option>
                    <option value="serif">Serif</option>
                    <option value="sans-serif">Sans Serif</option>
                    <option value="monospace">Monospace</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings-editor">
            <div className="editor-section">
              <h3>Website Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <label>Website ID:</label>
                  <span>{website?.website_id}</span>
                </div>
                <div className="info-item">
                  <label>Status:</label>
                  <span className={`status-badge ${website?.status}`}>
                    {website?.status}
                  </span>
                </div>
                <div className="info-item">
                  <label>Created:</label>
                  <span>{website?.created_at ? new Date(website.created_at).toLocaleString() : 'Unknown'}</span>
                </div>
                <div className="info-item">
                  <label>Last Updated:</label>
                  <span>{website?.updated_at ? new Date(website.updated_at).toLocaleString() : 'Never'}</span>
                </div>
              </div>
            </div>

            <div className="editor-section">
              <h3>Actions</h3>
              <div className="action-buttons">
                <button 
                  className="btn-warning"
                  onClick={handleRegenerate}
                >
                  🔄 Regenerate Website
                </button>
                <button 
                  className="btn-danger"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this website? This action cannot be undone.')) {
                      // Implement delete functionality
                      alert('Delete functionality would be implemented here');
                    }
                  }}
                >
                  🗑️ Delete Website
                </button>
              </div>
            </div>

            {website?.generation_details && (
              <div className="editor-section">
                <h3>Generation Details</h3>
                <div className="generation-info">
                  {website.generation_details.ai_model && (
                    <p><strong>AI Model:</strong> {website.generation_details.ai_model}</p>
                  )}
                  {website.generation_details.generation_time && (
                    <p><strong>Generation Time:</strong> {website.generation_details.generation_time}s</p>
                  )}
                  {website.generation_details.features_used && (
                    <div>
                      <strong>Features Used:</strong>
                      <ul>
                        {website.generation_details.features_used.map((feature, index) => (
                          <li key={index}>{feature}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebsiteEditor;