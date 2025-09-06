import React, { useState, useEffect } from 'react';
import { adminAnalyticsAPI } from '../services/api';
import './ContentModeration.css';

const ContentModeration = () => {
  const [flaggedContent, setFlaggedContent] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [statusFilter, setStatusFilter] = useState('flagged');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [moderating, setModerating] = useState(false);

  useEffect(() => {
    fetchFlaggedContent();
  }, [statusFilter]);

  const fetchFlaggedContent = async () => {
    try {
      setLoading(true);
      const response = await adminAnalyticsAPI.getFlaggedContent(statusFilter, 100);
      setFlaggedContent(response.data.flagged_content || []);
      setSelectedItems([]);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectItem = (moderationId) => {
    setSelectedItems(prev => 
      prev.includes(moderationId)
        ? prev.filter(id => id !== moderationId)
        : [...prev, moderationId]
    );
  };

  const handleSelectAll = () => {
    const filteredContent = getFilteredContent();
    if (selectedItems.length === filteredContent.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredContent.map(item => item.moderation_id));
    }
  };

  const handleModerateItem = async (moderationId, action, reason = null) => {
    try {
      setModerating(true);
      await adminAnalyticsAPI.moderateContent(moderationId, action, reason);
      
      // Update the item in the local state
      setFlaggedContent(prev => 
        prev.map(item => 
          item.moderation_id === moderationId
            ? { ...item, status: action === 'approve' ? 'approved' : 'rejected', reviewed_at: new Date().toISOString() }
            : item
        )
      );
      
      // Remove from selected items
      setSelectedItems(prev => prev.filter(id => id !== moderationId));
    } catch (error) {
      setError(`Failed to ${action} content: ${error.message}`);
    } finally {
      setModerating(false);
    }
  };

  const handleBulkModerate = async (action) => {
    if (selectedItems.length === 0) return;

    try {
      setModerating(true);
      const reason = prompt(`Enter reason for bulk ${action} (optional):`);
      
      await adminAnalyticsAPI.bulkModerateContent(selectedItems, action, reason);
      
      // Update local state
      setFlaggedContent(prev => 
        prev.map(item => 
          selectedItems.includes(item.moderation_id)
            ? { ...item, status: action === 'approve' ? 'approved' : 'rejected', reviewed_at: new Date().toISOString() }
            : item
        )
      );
      
      setSelectedItems([]);
    } catch (error) {
      setError(`Failed to bulk ${action}: ${error.message}`);
    } finally {
      setModerating(false);
    }
  };

  const getFilteredContent = () => {
    return flaggedContent.filter(item => {
      const matchesSearch = searchTerm === '' || 
        item.content_data?.text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.content_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.restaurant_id.toLowerCase().includes(searchTerm.toLowerCase());
      
      return matchesSearch;
    });
  };

  const getContentPreview = (contentData, contentType) => {
    if (!contentData) return 'No content data available';

    switch (contentType) {
      case 'generated_text':
        return contentData.text || contentData.content || 'No text content';
      case 'image_description':
        return contentData.description || contentData.alt_text || 'No description';
      case 'marketing_copy':
        return contentData.headline || contentData.copy || 'No marketing copy';
      default:
        return JSON.stringify(contentData).substring(0, 100) + '...';
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      flagged: { class: 'status-flagged', text: '🚩 Flagged' },
      approved: { class: 'status-approved', text: '✅ Approved' },
      rejected: { class: 'status-rejected', text: '❌ Rejected' }
    };
    
    const badge = badges[status] || { class: 'status-unknown', text: status };
    return <span className={`status-badge ${badge.class}`}>{badge.text}</span>;
  };

  const getContentTypeBadge = (contentType) => {
    const types = {
      generated_text: { class: 'type-text', text: '📝 Text' },
      image_description: { class: 'type-image', text: '🖼️ Image' },
      marketing_copy: { class: 'type-marketing', text: '📢 Marketing' },
      menu_item: { class: 'type-menu', text: '🍽️ Menu' }
    };
    
    const type = types[contentType] || { class: 'type-other', text: contentType };
    return <span className={`content-type-badge ${type.class}`}>{type.text}</span>;
  };

  if (loading && flaggedContent.length === 0) {
    return (
      <div className="content-moderation-loading">
        <div className="loading-spinner"></div>
        <p>Loading flagged content...</p>
      </div>
    );
  }

  const filteredContent = getFilteredContent();

  return (
    <div className="content-moderation">
      {/* Header and Controls */}
      <div className="moderation-header">
        <div className="header-info">
          <h2>Content Moderation</h2>
          <p>Review and moderate AI-generated content</p>
        </div>
        
        <div className="moderation-controls">
          <div className="control-group">
            <label>Status Filter:</label>
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="flagged">Flagged Content</option>
              <option value="approved">Approved Content</option>
              <option value="rejected">Rejected Content</option>
            </select>
          </div>
          
          <div className="search-group">
            <input
              type="text"
              placeholder="Search content, type, or restaurant..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="bulk-actions">
          <div className="bulk-info">
            <span>{selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected</span>
          </div>
          <div className="bulk-buttons">
            <button 
              onClick={() => handleBulkModerate('approve')}
              disabled={moderating}
              className="bulk-button approve"
            >
              ✅ Bulk Approve
            </button>
            <button 
              onClick={() => handleBulkModerate('reject')}
              disabled={moderating}
              className="bulk-button reject"
            >
              ❌ Bulk Reject
            </button>
            <button 
              onClick={() => setSelectedItems([])}
              className="bulk-button clear"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Content List */}
      <div className="content-list">
        {filteredContent.length > 0 && (
          <div className="list-header">
            <div className="select-all">
              <input
                type="checkbox"
                checked={selectedItems.length === filteredContent.length && filteredContent.length > 0}
                onChange={handleSelectAll}
                id="select-all"
              />
              <label htmlFor="select-all">Select All</label>
            </div>
            <div className="results-count">
              {filteredContent.length} item{filteredContent.length !== 1 ? 's' : ''} found
            </div>
          </div>
        )}

        {filteredContent.length === 0 ? (
          <div className="no-content">
            <div className="no-content-icon">🔍</div>
            <h3>No Content Found</h3>
            <p>
              {searchTerm 
                ? `No content matches your search "${searchTerm}"`
                : `No ${statusFilter} content available`
              }
            </p>
          </div>
        ) : (
          <div className="content-items">
            {filteredContent.map((item) => (
              <div key={item.moderation_id} className="content-item">
                <div className="item-header">
                  <div className="item-select">
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(item.moderation_id)}
                      onChange={() => handleSelectItem(item.moderation_id)}
                      id={`item-${item.moderation_id}`}
                    />
                  </div>
                  
                  <div className="item-meta">
                    <div className="item-badges">
                      {getStatusBadge(item.status)}
                      {getContentTypeBadge(item.content_type)}
                    </div>
                    <div className="item-info">
                      <span className="restaurant-id">Restaurant: {item.restaurant_id}</span>
                      <span className="flagged-date">
                        Flagged: {new Date(item.flagged_at).toLocaleDateString()}
                      </span>
                      {item.reviewed_at && (
                        <span className="reviewed-date">
                          Reviewed: {new Date(item.reviewed_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="item-content">
                  <div className="content-preview">
                    <h4>Content Preview:</h4>
                    <div className="preview-text">
                      {getContentPreview(item.content_data, item.content_type)}
                    </div>
                  </div>

                  {item.flags && item.flags.length > 0 && (
                    <div className="content-flags">
                      <h4>Flags:</h4>
                      <div className="flag-list">
                        {item.flags.map((flag, index) => (
                          <span key={index} className="flag-item">{flag}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {item.content_data && Object.keys(item.content_data).length > 1 && (
                    <div className="content-metadata">
                      <h4>Metadata:</h4>
                      <div className="metadata-grid">
                        {Object.entries(item.content_data).map(([key, value]) => (
                          key !== 'text' && key !== 'content' && (
                            <div key={key} className="metadata-item">
                              <span className="metadata-key">{key}:</span>
                              <span className="metadata-value">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          )
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {item.status === 'flagged' && (
                  <div className="item-actions">
                    <button
                      onClick={() => handleModerateItem(item.moderation_id, 'approve')}
                      disabled={moderating}
                      className="action-button approve"
                    >
                      ✅ Approve
                    </button>
                    <button
                      onClick={() => {
                        const reason = prompt('Enter reason for rejection (optional):');
                        handleModerateItem(item.moderation_id, 'reject', reason);
                      }}
                      disabled={moderating}
                      className="action-button reject"
                    >
                      ❌ Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentModeration;