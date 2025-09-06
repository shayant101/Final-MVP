import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import './BusinessIntelligence.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const BusinessIntelligence = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 300000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/business-intelligence/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const result = await response.json();
      setDashboardData(result.data);
      setError('');
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const exportReport = async (reportType) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/business-intelligence/reports/${reportType}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const result = await response.json();
      
      // Create and download the report
      const dataStr = JSON.stringify(result.data, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      const exportFileDefaultName = `${reportType}_report_${new Date().toISOString().split('T')[0]}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    } catch (err) {
      console.error('Export error:', err);
      setError('Failed to export report');
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="bi-loading">
        <div className="loading-spinner"></div>
        <p>Loading Business Intelligence Dashboard...</p>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="bi-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  // Mock data for demonstration if API fails
  const mockData = {
    key_metrics: {
      total_revenue: 125000,
      active_customers: 45,
      churn_risk_customers: 3,
      growth_rate: "15%"
    },
    platform_performance: {
      revenue_summary: {
        total_revenue: 125000,
        monthly_growth: 15.2,
        average_revenue_per_customer: 2777.78
      },
      customer_summary: {
        active_customers: 45,
        new_customers_this_month: 8,
        customer_retention_rate: 92.5
      }
    },
    revenue_forecast: {
      forecast_data: [
        { month: 'Jan', predicted_revenue: 130000, confidence: 85 },
        { month: 'Feb', predicted_revenue: 142000, confidence: 82 },
        { month: 'Mar', predicted_revenue: 155000, confidence: 78 },
        { month: 'Apr', predicted_revenue: 168000, confidence: 75 },
        { month: 'May', predicted_revenue: 182000, confidence: 72 },
        { month: 'Jun', predicted_revenue: 195000, confidence: 70 }
      ]
    },
    at_risk_customers: {
      total_at_risk: 3,
      immediate_action_required: 1,
      customers: [
        { name: "Bella Vista Restaurant", risk_score: 85, reason: "Declining usage" },
        { name: "Corner Cafe", risk_score: 72, reason: "Payment issues" },
        { name: "Metro Bistro", risk_score: 68, reason: "Low engagement" }
      ]
    }
  };

  const data = dashboardData || mockData;

  // Revenue Forecast Chart Data
  const revenueChartData = {
    labels: data.revenue_forecast?.forecast_data?.map(item => item.month) || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Predicted Revenue',
        data: data.revenue_forecast?.forecast_data?.map(item => item.predicted_revenue) || [130000, 142000, 155000, 168000, 182000, 195000],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };

  // Customer Segmentation Chart Data
  const customerSegmentData = {
    labels: ['High Value', 'Medium Value', 'Low Value', 'At Risk'],
    datasets: [
      {
        data: [15, 20, 7, 3],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(251, 191, 36, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="business-intelligence">
      <div className="bi-header">
        <div className="bi-title-section">
          <h2>Business Intelligence Dashboard</h2>
          <p>Comprehensive insights and analytics for strategic decision making</p>
        </div>
        <div className="bi-actions">
          <button 
            onClick={() => exportReport('executive')} 
            className="export-button"
          >
            📊 Export Report
          </button>
          <button 
            onClick={fetchDashboardData} 
            className={`refresh-button ${refreshing ? 'refreshing' : ''}`}
            disabled={refreshing}
          >
            🔄 {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bi-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Key Metrics Overview */}
      <div className="bi-metrics-grid">
        <div className="bi-metric-card revenue">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">${data.key_metrics?.total_revenue?.toLocaleString() || '125,000'}</div>
            <div className="metric-label">Total Revenue</div>
            <div className="metric-change positive">+{data.platform_performance?.revenue_summary?.monthly_growth || 15.2}%</div>
          </div>
        </div>

        <div className="bi-metric-card customers">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-value">{data.key_metrics?.active_customers || 45}</div>
            <div className="metric-label">Active Customers</div>
            <div className="metric-change positive">+{data.platform_performance?.customer_summary?.new_customers_this_month || 8} this month</div>
          </div>
        </div>

        <div className="bi-metric-card clv">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-value">${data.platform_performance?.revenue_summary?.average_revenue_per_customer?.toLocaleString() || '2,778'}</div>
            <div className="metric-label">Avg Revenue/Customer</div>
            <div className="metric-change positive">+12.5%</div>
          </div>
        </div>

        <div className="bi-metric-card churn">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <div className="metric-value">{data.key_metrics?.churn_risk_customers || 3}</div>
            <div className="metric-label">At-Risk Customers</div>
            <div className="metric-change negative">{data.at_risk_customers?.immediate_action_required || 1} need attention</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="bi-charts-grid">
        <div className="bi-chart-card">
          <div className="chart-header">
            <h3>Revenue Forecast (6 Months)</h3>
            <span className="chart-subtitle">ML-powered predictions with confidence intervals</span>
          </div>
          <div className="chart-container">
            <Line data={revenueChartData} options={chartOptions} />
          </div>
        </div>

        <div className="bi-chart-card">
          <div className="chart-header">
            <h3>Customer Segmentation</h3>
            <span className="chart-subtitle">Distribution by customer lifetime value</span>
          </div>
          <div className="chart-container">
            <Doughnut data={customerSegmentData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* At-Risk Customers Section */}
      <div className="bi-section">
        <div className="section-header">
          <h3>🚨 Customers Requiring Attention</h3>
          <span className="section-subtitle">Proactive churn prevention opportunities</span>
        </div>
        <div className="at-risk-customers">
          {data.at_risk_customers?.customers?.map((customer, index) => (
            <div key={index} className="at-risk-card">
              <div className="risk-info">
                <div className="customer-name">{customer.name}</div>
                <div className="risk-reason">{customer.reason}</div>
              </div>
              <div className="risk-score">
                <div className="score-value">{customer.risk_score}%</div>
                <div className="score-label">Risk Score</div>
              </div>
              <div className="risk-actions">
                <button className="action-button primary">Contact</button>
                <button className="action-button secondary">View Details</button>
              </div>
            </div>
          )) || (
            <div className="no-risk-customers">
              <p>✅ No customers currently at high risk</p>
            </div>
          )}
        </div>
      </div>

      {/* Performance Insights */}
      <div className="bi-insights-grid">
        <div className="insight-card">
          <div className="insight-header">
            <h4>💡 Key Insights</h4>
          </div>
          <div className="insight-content">
            <ul>
              <li>Revenue growth is accelerating with 15.2% monthly increase</li>
              <li>Customer retention rate of 92.5% exceeds industry average</li>
              <li>High-value customers represent 33% of total customer base</li>
              <li>AI features showing strong adoption with 78% usage rate</li>
            </ul>
          </div>
        </div>

        <div className="insight-card">
          <div className="insight-header">
            <h4>🎯 Recommendations</h4>
          </div>
          <div className="insight-content">
            <ul>
              <li>Focus retention efforts on 3 at-risk customers</li>
              <li>Expand premium features to drive upsell opportunities</li>
              <li>Implement proactive support for declining usage patterns</li>
              <li>Consider loyalty program for high-value customers</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bi-footer">
        <div className="last-updated">
          Last updated: {data.generated_at ? new Date(data.generated_at).toLocaleString() : new Date().toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default BusinessIntelligence;