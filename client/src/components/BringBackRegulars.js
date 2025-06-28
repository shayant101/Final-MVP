import React, { useState } from 'react';
import { smsCampaignsAPI } from '../services/api';
import './BringBackRegulars.css';

const BringBackRegulars = ({ onBackToDashboard }) => {
  const [formData, setFormData] = useState({
    restaurantName: '',
    offer: '',
    offerCode: ''
  });
  const [customerFile, setCustomerFile] = useState(null);
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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setError('Please upload a CSV file');
        return;
      }
      
      // Validate file size (2MB max)
      if (file.size > 2 * 1024 * 1024) {
        setError('CSV file must be smaller than 2MB');
        return;
      }
      
      setCustomerFile(file);
      setError(null);
    }
  };

  const downloadSampleCSV = async () => {
    try {
      await smsCampaignsAPI.downloadSampleCSV();
    } catch (err) {
      setError(err.message);
    }
  };

  const generatePreview = async () => {
    if (!formData.restaurantName || !formData.offer || !formData.offerCode) {
      setError('Please fill in all fields to generate preview');
      return;
    }

    try {
      setLoading(true);
      
      // Create FormData for preview
      const previewData = new FormData();
      previewData.append('restaurantName', formData.restaurantName);
      previewData.append('offer', formData.offer);
      previewData.append('offerCode', formData.offerCode);
      
      if (customerFile) {
        previewData.append('customerList', customerFile);
      }

      const previewResult = await smsCampaignsAPI.generatePreview(previewData);
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
    if (!formData.restaurantName || !formData.offer || !formData.offerCode) {
      setError('Please fill in all required fields');
      return;
    }

    if (!customerFile) {
      setError('Please upload a customer list CSV file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      // Create FormData for file upload
      const submitData = new FormData();
      submitData.append('restaurantName', formData.restaurantName);
      submitData.append('offer', formData.offer);
      submitData.append('offerCode', formData.offerCode);
      submitData.append('customerList', customerFile);

      const response = await smsCampaignsAPI.createCampaign(submitData);
      setResult(response);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bring-back-regulars">
      <div className="section-header">
        <h2>📱 Bring Back Regulars</h2>
        <p>Send personalized SMS campaigns to win back lapsed customers</p>
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
          <label htmlFor="customerList">Upload Customer List (CSV) *</label>
          <input
            type="file"
            id="customerList"
            accept=".csv"
            onChange={handleFileChange}
            className="file-input"
            required
          />
          <div className="form-help">
            <small>CSV format: customer_name, phone_number, last_order_date (YYYY-MM-DD)</small>
            <button
              type="button"
              onClick={downloadSampleCSV}
              className="link-button"
            >
              Download sample CSV
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="offer">Your 'We Miss You' Offer *</label>
          <input
            type="text"
            id="offer"
            name="offer"
            value={formData.offer}
            onChange={handleInputChange}
            placeholder="e.g., 20% off your next order"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="offerCode">Offer Code (for tracking) *</label>
          <input
            type="text"
            id="offerCode"
            name="offerCode"
            value={formData.offerCode}
            onChange={handleInputChange}
            placeholder="e.g., WELCOME20"
            required
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={generatePreview}
            className="btn btn-secondary"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Preview SMS'}
          </button>
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Sending SMS Campaign...' : 'Send SMS to Lapsed Customers'}
          </button>
        </div>
      </form>

      {preview && (
        <div className="preview-section">
          <h3>SMS Preview</h3>
          <div className="sms-preview">
            <div className="sms-message">{preview.sampleMessage}</div>
            <div className="sms-meta">
              <span className="character-count">{preview.characterCount}/160 characters</span>
              <span className="target-customers">{preview.targetCustomers} lapsed customers found</span>
              <span className="estimated-cost">Estimated cost: ${preview.estimatedCost}</span>
            </div>
            {preview.csvStats && (
              <div className="csv-stats">
                <h4>CSV Analysis</h4>
                <p>Total customers uploaded: {preview.csvStats.totalUploaded}</p>
                <p>Lapsed customers ({'>'}30 days): {preview.csvStats.lapsedCustomers}</p>
                {preview.csvStats.errors > 0 && (
                  <p className="error-count">Rows with errors: {preview.csvStats.errors}</p>
                )}
              </div>
            )}
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
            <h3>📱 SMS Campaign Sent Successfully!</h3>
            <p>{result.message}</p>
          </div>
          
          <div className="campaign-details">
            <h4>Campaign Results</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Offer Code:</label>
                <span className="offer-code-result">{result.data.offerCode}</span>
              </div>
              <div className="detail-item">
                <label>Messages Sent:</label>
                <span>{result.data.messagesSent}</span>
              </div>
              <div className="detail-item">
                <label>Delivery Rate:</label>
                <span>{result.data.deliveryRate}</span>
              </div>
              <div className="detail-item">
                <label>Total Cost:</label>
                <span>${result.data.totalCost}</span>
              </div>
            </div>
            
            <div className="customer-stats">
              <h4>Customer Analysis</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-number">{result.data.totalCustomersUploaded}</span>
                  <span className="stat-label">Total Customers Uploaded</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{result.data.lapsedCustomersFound}</span>
                  <span className="stat-label">Lapsed Customers Found</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">{result.data.messagesSent}</span>
                  <span className="stat-label">Messages Successfully Sent</span>
                </div>
              </div>
            </div>
            
            {result.data.sampleMessage && (
              <div className="sample-message">
                <h4>Sample Message Sent</h4>
                <div className="message-display">{result.data.sampleMessage}</div>
              </div>
            )}
            
            <div className="next-steps">
              <h4>Next Steps</h4>
              <ul>
                <li>Track redemptions using offer code: <strong>{result.data.offerCode}</strong></li>
                <li>Monitor responses and prepare for increased orders</li>
                <li>Follow up with customers who redeem the offer</li>
                {result.data.csvErrors && result.data.csvErrors.length > 0 && (
                  <li className="error-note">Review and fix {result.data.csvErrors.length} CSV errors for future campaigns</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BringBackRegulars;