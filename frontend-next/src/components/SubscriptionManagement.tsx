import React, { useState, useEffect } from 'react';
import './SubscriptionManagement.css';

const SubscriptionManagement = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [billingData, setBillingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTab, setSelectedTab] = useState('overview'); // 'overview', 'subscriptions', 'usage', 'invoices'

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch billing dashboard data
      const response = await fetch('http://localhost:8000/api/billing/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch subscription data');
      }

      const result = await response.json();
      setBillingData(result.data);
      setError('');
    } catch (err) {
      console.error('Subscription fetch error:', err);
      setError(err.message);
      // Use mock data for demonstration
      setBillingData(getMockBillingData());
      setSubscriptions(getMockSubscriptions());
    } finally {
      setLoading(false);
    }
  };

  const getMockBillingData = () => ({
    total_revenue: 125000,
    active_subscriptions: 45,
    monthly_recurring_revenue: 18500,
    churn_rate: 7.5,
    average_revenue_per_user: 411.11,
    upcoming_renewals: 12,
    overdue_payments: 2,
    total_credits_purchased: 15000,
    credits_used: 12500
  });

  const getMockSubscriptions = () => [
    {
      id: 'sub_001',
      restaurant_name: 'Bella Vista Restaurant',
      email: 'owner@bellavista.com',
      plan: 'Enterprise',
      status: 'active',
      monthly_revenue: 399,
      billing_cycle: 'monthly',
      next_billing_date: '2025-02-15',
      created_date: '2024-08-15',
      usage: {
        ai_content: { used: 450, limit: 500 },
        sms_campaigns: { used: 8, limit: 10 },
        facebook_ads: { used: 3, limit: 5 },
        image_enhancement: { used: 120, limit: 200 }
      },
      credits: { balance: 2500, purchased: 5000, used: 2500 }
    },
    {
      id: 'sub_002',
      restaurant_name: 'Corner Cafe',
      email: 'manager@cornercafe.com',
      plan: 'Professional',
      status: 'active',
      monthly_revenue: 149,
      billing_cycle: 'monthly',
      next_billing_date: '2025-02-20',
      created_date: '2024-09-10',
      usage: {
        ai_content: { used: 180, limit: 200 },
        sms_campaigns: { used: 4, limit: 5 },
        facebook_ads: { used: 2, limit: 3 },
        image_enhancement: { used: 45, limit: 100 }
      },
      credits: { balance: 800, purchased: 2000, used: 1200 }
    },
    {
      id: 'sub_003',
      restaurant_name: 'Metro Bistro',
      email: 'info@metrobistro.com',
      plan: 'Basic',
      status: 'past_due',
      monthly_revenue: 49,
      billing_cycle: 'monthly',
      next_billing_date: '2025-01-28',
      created_date: '2024-11-05',
      usage: {
        ai_content: { used: 95, limit: 100 },
        sms_campaigns: { used: 2, limit: 2 },
        facebook_ads: { used: 1, limit: 1 },
        image_enhancement: { used: 25, limit: 50 }
      },
      credits: { balance: 150, purchased: 500, used: 350 }
    }
  ];

  const handlePlanChange = async (subscriptionId, newPlan) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/billing/subscriptions/${subscriptionId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plan_id: newPlan })
      });

      if (!response.ok) {
        throw new Error('Failed to update subscription');
      }

      // Refresh data
      fetchSubscriptionData();
    } catch (err) {
      console.error('Plan change error:', err);
      setError('Failed to update subscription plan');
    }
  };

  const handleCancelSubscription = async (subscriptionId) => {
    if (!window.confirm('Are you sure you want to cancel this subscription?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/billing/subscriptions/${subscriptionId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cancel_at_period_end: true })
      });

      if (!response.ok) {
        throw new Error('Failed to cancel subscription');
      }

      // Refresh data
      fetchSubscriptionData();
    } catch (err) {
      console.error('Cancellation error:', err);
      setError('Failed to cancel subscription');
    }
  };

  const getUsagePercentage = (used, limit) => {
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return '#EF4444';
    if (percentage >= 75) return '#F59E0B';
    return '#10B981';
  };

  if (loading && !billingData) {
    return (
      <div className="sm-loading">
        <div className="loading-spinner"></div>
        <p>Loading Subscription Management...</p>
      </div>
    );
  }

  if (error && !billingData) {
    return (
      <div className="sm-error">
        <h3>Error Loading Subscriptions</h3>
        <p>{error}</p>
        <button onClick={fetchSubscriptionData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  const data = billingData || getMockBillingData();
  const subscriptionList = subscriptions.length > 0 ? subscriptions : getMockSubscriptions();

  return (
    <div className="subscription-management">
      <div className="sm-header">
        <div className="sm-title-section">
          <h2>💳 Subscription Management</h2>
          <p>Monitor billing, usage, and subscription lifecycle</p>
        </div>
        <div className="sm-actions">
          <button className="export-button">
            📊 Export Report
          </button>
          <button onClick={fetchSubscriptionData} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="sm-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="sm-nav">
        <button
          className={`nav-tab ${selectedTab === 'overview' ? 'active' : ''}`}
          onClick={() => setSelectedTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-tab ${selectedTab === 'subscriptions' ? 'active' : ''}`}
          onClick={() => setSelectedTab('subscriptions')}
        >
          📋 Subscriptions
        </button>
        <button
          className={`nav-tab ${selectedTab === 'usage' ? 'active' : ''}`}
          onClick={() => setSelectedTab('usage')}
        >
          📈 Usage Tracking
        </button>
        <button
          className={`nav-tab ${selectedTab === 'invoices' ? 'active' : ''}`}
          onClick={() => setSelectedTab('invoices')}
        >
          🧾 Invoices
        </button>
      </div>

      {/* Overview Tab */}
      {selectedTab === 'overview' && (
        <div className="overview-content">
          {/* Key Metrics */}
          <div className="sm-metrics-grid">
            <div className="sm-metric-card">
              <div className="metric-icon">💰</div>
              <div className="metric-content">
                <div className="metric-value">${data.total_revenue?.toLocaleString() || '125,000'}</div>
                <div className="metric-label">Total Revenue</div>
                <div className="metric-change positive">+15.2% this month</div>
              </div>
            </div>

            <div className="sm-metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-value">${data.monthly_recurring_revenue?.toLocaleString() || '18,500'}</div>
                <div className="metric-label">Monthly Recurring Revenue</div>
                <div className="metric-change positive">+8.3% growth</div>
              </div>
            </div>

            <div className="sm-metric-card">
              <div className="metric-icon">👥</div>
              <div className="metric-content">
                <div className="metric-value">{data.active_subscriptions || 45}</div>
                <div className="metric-label">Active Subscriptions</div>
                <div className="metric-change positive">+3 new this month</div>
              </div>
            </div>

            <div className="sm-metric-card">
              <div className="metric-icon">💎</div>
              <div className="metric-content">
                <div className="metric-value">${data.average_revenue_per_user?.toFixed(2) || '411.11'}</div>
                <div className="metric-label">Average Revenue Per User</div>
                <div className="metric-change positive">+12.5% increase</div>
              </div>
            </div>
          </div>

          {/* Alerts and Actions */}
          <div className="sm-alerts-grid">
            <div className="alert-card urgent">
              <div className="alert-header">
                <h3>🚨 Requires Attention</h3>
              </div>
              <div className="alert-content">
                <div className="alert-item">
                  <span className="alert-count">{data.overdue_payments || 2}</span>
                  <span className="alert-text">Overdue payments requiring follow-up</span>
                </div>
                <div className="alert-item">
                  <span className="alert-count">{data.upcoming_renewals || 12}</span>
                  <span className="alert-text">Subscriptions renewing in next 7 days</span>
                </div>
              </div>
            </div>

            <div className="alert-card info">
              <div className="alert-header">
                <h3>💡 Opportunities</h3>
              </div>
              <div className="alert-content">
                <div className="alert-item">
                  <span className="alert-count">8</span>
                  <span className="alert-text">Customers ready for plan upgrades</span>
                </div>
                <div className="alert-item">
                  <span className="alert-count">15</span>
                  <span className="alert-text">High usage customers ({'>'}80% limits)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Subscriptions Tab */}
      {selectedTab === 'subscriptions' && (
        <div className="subscriptions-content">
          <div className="subscriptions-table-container">
            <table className="subscriptions-table">
              <thead>
                <tr>
                  <th>Restaurant</th>
                  <th>Plan</th>
                  <th>Status</th>
                  <th>Revenue</th>
                  <th>Next Billing</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {subscriptionList.map((sub) => (
                  <tr key={sub.id}>
                    <td>
                      <div className="restaurant-info">
                        <div className="restaurant-name">{sub.restaurant_name}</div>
                        <div className="restaurant-email">{sub.email}</div>
                      </div>
                    </td>
                    <td>
                      <span className={`plan-badge ${sub.plan.toLowerCase()}`}>
                        {sub.plan}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${sub.status}`}>
                        {sub.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>${sub.monthly_revenue}/mo</td>
                    <td>{new Date(sub.next_billing_date).toLocaleDateString()}</td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="action-btn primary"
                          onClick={() => handlePlanChange(sub.id, 'upgrade')}
                        >
                          Upgrade
                        </button>
                        <button 
                          className="action-btn secondary"
                          onClick={() => handleCancelSubscription(sub.id)}
                        >
                          Cancel
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Usage Tracking Tab */}
      {selectedTab === 'usage' && (
        <div className="usage-content">
          <div className="usage-cards-grid">
            {subscriptionList.map((sub) => (
              <div key={sub.id} className="usage-card">
                <div className="usage-header">
                  <h3>{sub.restaurant_name}</h3>
                  <span className={`plan-badge ${sub.plan.toLowerCase()}`}>
                    {sub.plan}
                  </span>
                </div>
                
                <div className="usage-metrics">
                  {Object.entries(sub.usage).map(([feature, data]) => {
                    const percentage = getUsagePercentage(data.used, data.limit);
                    const color = getUsageColor(percentage);
                    
                    return (
                      <div key={feature} className="usage-metric">
                        <div className="usage-metric-header">
                          <span className="feature-name">
                            {feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                          <span className="usage-numbers">
                            {data.used} / {data.limit}
                          </span>
                        </div>
                        <div className="usage-bar">
                          <div 
                            className="usage-fill" 
                            style={{ 
                              width: `${percentage}%`,
                              backgroundColor: color
                            }}
                          ></div>
                        </div>
                        <div className="usage-percentage" style={{ color }}>
                          {percentage.toFixed(1)}% used
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="credits-section">
                  <h4>Campaign Credits</h4>
                  <div className="credits-info">
                    <div className="credit-item">
                      <span className="credit-label">Balance:</span>
                      <span className="credit-value">{sub.credits.balance.toLocaleString()}</span>
                    </div>
                    <div className="credit-item">
                      <span className="credit-label">Used:</span>
                      <span className="credit-value">{sub.credits.used.toLocaleString()}</span>
                    </div>
                    <div className="credit-item">
                      <span className="credit-label">Purchased:</span>
                      <span className="credit-value">{sub.credits.purchased.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invoices Tab */}
      {selectedTab === 'invoices' && (
        <div className="invoices-content">
          <div className="invoices-header">
            <h3>Recent Invoices</h3>
            <button className="generate-invoice-btn">
              📄 Generate Invoice
            </button>
          </div>
          
          <div className="invoices-table-container">
            <table className="invoices-table">
              <thead>
                <tr>
                  <th>Invoice #</th>
                  <th>Restaurant</th>
                  <th>Amount</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>INV-2025-001</td>
                  <td>Bella Vista Restaurant</td>
                  <td>$399.00</td>
                  <td>Jan 15, 2025</td>
                  <td><span className="status-badge paid">Paid</span></td>
                  <td>
                    <button className="action-btn secondary">View</button>
                  </td>
                </tr>
                <tr>
                  <td>INV-2025-002</td>
                  <td>Corner Cafe</td>
                  <td>$149.00</td>
                  <td>Jan 20, 2025</td>
                  <td><span className="status-badge paid">Paid</span></td>
                  <td>
                    <button className="action-btn secondary">View</button>
                  </td>
                </tr>
                <tr>
                  <td>INV-2025-003</td>
                  <td>Metro Bistro</td>
                  <td>$49.00</td>
                  <td>Jan 28, 2025</td>
                  <td><span className="status-badge overdue">Overdue</span></td>
                  <td>
                    <button className="action-btn primary">Send Reminder</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionManagement;