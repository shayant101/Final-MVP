import React, { useState } from 'react';
import { facebookAdsAPI } from '../services/api';
import './GetNewCustomers.css';

const GetNewCustomers = () => {
  const [formData, setFormData] = useState({
    restaurantName: '',
    itemToPromote: '',
    offer: '',
    budget: '10'
  });
  const [dishPhoto, setDishPhoto] = useState(null);
  const [dishPhotoPreview, setDishPhotoPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear previous results when form changes
    if (result) setResult(null);
    if (error) setError(null);
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        setError('Please upload a valid image file (JPEG, PNG, or GIF)');
        return;
      }
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file must be smaller than 5MB');
        return;
      }
      
      setDishPhoto(file);
      
      // Create preview URL for the image
      const previewUrl = URL.createObjectURL(file);
      setDishPhotoPreview(previewUrl);
      
      setError(null);
    } else {
      setDishPhoto(null);
      setDishPhotoPreview(null);
    }
  };

  const generatePreview = async () => {
    if (!formData.restaurantName || !formData.itemToPromote || !formData.offer) {
      setError('Please fill in restaurant name, item to promote, and offer to generate preview');
      return;
    }

    try {
      setLoading(true);
      const previewResult = await facebookAdsAPI.generatePreview({
        restaurantName: formData.restaurantName,
        itemToPromote: formData.itemToPromote,
        offer: formData.offer
      });
      
      setPreview(previewResult.preview);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.restaurantName || !formData.itemToPromote || !formData.offer) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      // Create FormData for file upload
      const submitData = new FormData();
      submitData.append('restaurantName', formData.restaurantName);
      submitData.append('itemToPromote', formData.itemToPromote);
      submitData.append('offer', formData.offer);
      submitData.append('budget', formData.budget);
      
      if (dishPhoto) {
        submitData.append('dishPhoto', dishPhoto);
      }

      const response = await facebookAdsAPI.createCampaign(submitData);
      setResult(response);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="get-new-customers">
      <div className="content-container">
        <div className="section-header">
          <h2>🎯 Get New Customers</h2>
          <p>Launch a Facebook ad campaign to attract new diners to your restaurant</p>
        </div>

        <form onSubmit={handleSubmit} className="campaign-form">
          <div className="form-group">
            <label htmlFor="restaurantName">Restaurant Name *</label>
            <input
              type="text"
              id="restaurantName"
              name="restaurantName"
              value={formData.restaurantName}
              onChange={handleInputChange}
              placeholder="e.g., Tony's Pizzeria"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="itemToPromote">Item to Promote *</label>
            <input
              type="text"
              id="itemToPromote"
              name="itemToPromote"
              value={formData.itemToPromote}
              onChange={handleInputChange}
              placeholder="e.g., Margherita Pizza"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="offer">The Offer *</label>
            <input
              type="text"
              id="offer"
              name="offer"
              value={formData.offer}
              onChange={handleInputChange}
              placeholder="e.g., 20% off your first order"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="dishPhoto">Upload Dish Photo</label>
            <input
              type="file"
              id="dishPhoto"
              accept="image/*"
              onChange={handlePhotoChange}
              className="file-input"
            />
            {dishPhoto && (
              <div className="file-selected">
                📎 {dishPhoto.name}
              </div>
            )}
            <small className="form-help">Optional: Upload a photo of your dish (JPEG, PNG, GIF - Max 5MB)</small>
          </div>

          <div className="form-group">
            <label htmlFor="budget">Daily Ad Budget *</label>
            <select
              id="budget"
              name="budget"
              value={formData.budget}
              onChange={handleInputChange}
              required
            >
              <option value="10">$10</option>
              <option value="20">$20</option>
            </select>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={generatePreview}
              className="btn btn-secondary"
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Preview Ad Copy'}
            </button>
            
            <button
              type="submit"
              className="btn btn-primary launch-button"
              disabled={loading}
            >
              {loading ? 'Launching...' : '🚀 Launch Facebook Ad'}
            </button>
          </div>
        </form>

        {preview && (
          <div className="preview-section">
            <h3>Ad Copy Preview</h3>
            <div className="ad-preview">
              {dishPhotoPreview && (
                <div className="ad-image">
                  <img src={dishPhotoPreview} alt="Dish preview" className="dish-preview-image" />
                </div>
              )}
              <div className="ad-copy">{preview.adCopy}</div>
              <div className="ad-meta">
                <span className="promo-code">Promo Code: <strong>{preview.promoCode}</strong></span>
                <span className="character-count">{preview.characterCount} characters</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="success-section">
            <div className="success-message">
              <h3>🎉 Campaign Created Successfully!</h3>
              <p>{result.message}</p>
            </div>
            
            <div className="campaign-details">
              <h4>Campaign Details</h4>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Promo Code:</label>
                  <span className="promo-code-result">{result.data.promoCode}</span>
                </div>
                <div className="detail-item">
                  <label>Expected Reach:</label>
                  <span>{result.data.expectedReach?.toLocaleString()} people</span>
                </div>
                <div className="detail-item">
                  <label>Estimated Impressions:</label>
                  <span>{result.data.estimatedImpressions?.toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <label>Daily Budget:</label>
                  <span>${result.data.budget}</span>
                </div>
              </div>
              
              <div className="generated-ad-copy">
                <h4>Your Ad Copy</h4>
                <div className="ad-copy-display">{result.data.adCopy}</div>
              </div>
              
              <div className="next-steps">
                <h4>Next Steps</h4>
                <ul>
                  <li>Check your Facebook Ads Manager in a few minutes</li>
                  <li>Track redemptions using promo code: <strong>{result.data.promoCode}</strong></li>
                  <li>Monitor your campaign performance daily</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GetNewCustomers;