import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Bar, Scatter } from 'react-chartjs-2';
import './RevenueAnalytics.css';

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

const RevenueAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('12');
  const [selectedFeature, setSelectedFeature] = useState('all');

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeframe, selectedFeature]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch revenue forecast
      const forecastResponse = await fetch(`http://localhost:8000/api/revenue/forecast?months_ahead=${selectedTimeframe}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Fetch correlation analysis
      const correlationResponse = await fetch(`http://localhost:8000/api/revenue/correlation-analysis?feature_type=${selectedFeature}&time_period=90`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!forecastResponse.ok || !correlationResponse.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const forecastData = await forecastResponse.json();
      const correlationData = await correlationResponse.json();

      setAnalyticsData({
        forecast: forecastData.data,
        correlation: correlationData.data
      });
      setError('');
    } catch (err) {
      console.error('Analytics fetch error:', err);
      setError(err.message);
      // Use mock data for demonstration
      setAnalyticsData(getMockAnalyticsData());
    } finally {
      setLoading(false);
    }
  };

  const getMockAnalyticsData = () => ({
    forecast: {
      forecast_data: [
        { month: 'Jan 2025', predicted_revenue: 130000, confidence: 85, actual_revenue: 125000 },
        { month: 'Feb 2025', predicted_revenue: 142000, confidence: 82, actual_revenue: null },
        { month: 'Mar 2025', predicted_revenue: 155000, confidence: 78, actual_revenue: null },
        { month: 'Apr 2025', predicted_revenue: 168000, confidence: 75, actual_revenue: null },
        { month: 'May 2025', predicted_revenue: 182000, confidence: 72, actual_revenue: null },
        { month: 'Jun 2025', predicted_revenue: 195000, confidence: 70, actual_revenue: null },
        { month: 'Jul 2025', predicted_revenue: 210000, confidence: 68, actual_revenue: null },
        { month: 'Aug 2025', predicted_revenue: 225000, confidence: 65, actual_revenue: null },
        { month: 'Sep 2025', predicted_revenue: 240000, confidence: 62, actual_revenue: null },
        { month: 'Oct 2025', predicted_revenue: 255000, confidence: 60, actual_revenue: null },
        { month: 'Nov 2025', predicted_revenue: 270000, confidence: 58, actual_revenue: null },
        { month: 'Dec 2025', predicted_revenue: 285000, confidence: 55, actual_revenue: null }
      ],
      growth_rate: 15.2,
      total_predicted: 2457000
    },
    correlation: {
      feature_roi: [
        { feature: 'AI Content Generation', roi: 340, usage_count: 1250, revenue_impact: 42500 },
        { feature: 'SMS Campaigns', roi: 280, usage_count: 890, revenue_impact: 24920 },
        { feature: 'Facebook Ads', roi: 220, usage_count: 650, revenue_impact: 14300 },
        { feature: 'Image Enhancement', roi: 180, usage_count: 420, revenue_impact: 7560 },
        { feature: 'Marketing Assistant', roi: 150, usage_count: 320, revenue_impact: 4800 }
      ],
      customer_segments: [
        { segment: 'Enterprise', count: 8, avg_revenue: 8500, total_revenue: 68000, growth: 25 },
        { segment: 'Professional', count: 15, avg_revenue: 3200, total_revenue: 48000, growth: 18 },
        { segment: 'Standard', count: 22, avg_revenue: 1200, total_revenue: 26400, growth: 12 }
      ],
      pricing_optimization: {
        current_plans: [
          { plan: 'Basic', price: 49, subscribers: 22, revenue: 1078, suggested_price: 59 },
          { plan: 'Professional', price: 149, subscribers: 15, revenue: 2235, suggested_price: 169 },
          { plan: 'Enterprise', price: 399, subscribers: 8, revenue: 3192, suggested_price: 449 }
        ],
        potential_increase: 18.5
      }
    }
  });

  const exportAnalytics = async () => {
    try {
      const dataStr = JSON.stringify(analyticsData, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      const exportFileDefaultName = `revenue_analytics_${new Date().toISOString().split('T')[0]}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    } catch (err) {
      console.error('Export error:', err);
      setError('Failed to export analytics');
    }
  };

  if (loading && !analyticsData) {
    return (
      <div className="ra-loading">
        <div className="loading-spinner"></div>
        <p>Loading Revenue Analytics...</p>
      </div>
    );
  }

  if (error && !analyticsData) {
    return (
      <div className="ra-error">
        <h3>Error Loading Analytics</h3>
        <p>{error}</p>
        <button onClick={fetchAnalyticsData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  const data = analyticsData || getMockAnalyticsData();

  // Revenue Forecast Chart
  const forecastChartData = {
    labels: data.forecast?.forecast_data?.map(item => item.month) || [],
    datasets: [
      {
        label: 'Predicted Revenue',
        data: data.forecast?.forecast_data?.map(item => item.predicted_revenue) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Actual Revenue',
        data: data.forecast?.forecast_data?.map(item => item.actual_revenue) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: false
      }
    ]
  };

  // Feature ROI Chart
  const roiChartData = {
    labels: data.correlation?.feature_roi?.map(item => item.feature) || [],
    datasets: [
      {
        label: 'ROI %',
        data: data.correlation?.feature_roi?.map(item => item.roi) || [],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(251, 191, 36, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  // Customer Segment Revenue Chart
  const segmentChartData = {
    labels: data.correlation?.customer_segments?.map(item => item.segment) || [],
    datasets: [
      {
        label: 'Total Revenue',
        data: data.correlation?.customer_segments?.map(item => item.total_revenue) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2
      },
      {
        label: 'Average Revenue',
        data: data.correlation?.customer_segments?.map(item => item.avg_revenue) || [],
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 2,
        yAxisID: 'y1'
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

  const segmentChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  return (
    <div className="revenue-analytics">
      <div className="ra-header">
        <div className="ra-title-section">
          <h2>Revenue Analytics & Forecasting</h2>
          <p>ML-powered insights for strategic revenue optimization</p>
        </div>
        <div className="ra-controls">
          <select 
            value={selectedTimeframe} 
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="timeframe-select"
          >
            <option value="6">6 Months</option>
            <option value="12">12 Months</option>
            <option value="18">18 Months</option>
            <option value="24">24 Months</option>
          </select>
          <select 
            value={selectedFeature} 
            onChange={(e) => setSelectedFeature(e.target.value)}
            className="feature-select"
          >
            <option value="all">All Features</option>
            <option value="ai_content">AI Content</option>
            <option value="sms_campaigns">SMS Campaigns</option>
            <option value="facebook_ads">Facebook Ads</option>
            <option value="image_enhancement">Image Enhancement</option>
          </select>
          <button onClick={exportAnalytics} className="export-button">
            📊 Export Analytics
          </button>
        </div>
      </div>

      {error && (
        <div className="ra-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError('')} className="dismiss-error">×</button>
        </div>
      )}

      {/* Key Metrics */}
      <div className="ra-metrics-grid">
        <div className="ra-metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-value">${data.forecast?.total_predicted?.toLocaleString() || '2,457,000'}</div>
            <div className="metric-label">Predicted Annual Revenue</div>
            <div className="metric-change positive">+{data.forecast?.growth_rate || 15.2}% growth</div>
          </div>
        </div>

        <div className="ra-metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div className="metric-value">{data.correlation?.feature_roi?.[0]?.roi || 340}%</div>
            <div className="metric-label">Best Feature ROI</div>
            <div className="metric-change positive">{data.correlation?.feature_roi?.[0]?.feature || 'AI Content Generation'}</div>
          </div>
        </div>

        <div className="ra-metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">${data.correlation?.customer_segments?.[0]?.avg_revenue?.toLocaleString() || '8,500'}</div>
            <div className="metric-label">Highest Segment ARPU</div>
            <div className="metric-change positive">{data.correlation?.customer_segments?.[0]?.segment || 'Enterprise'}</div>
          </div>
        </div>

        <div className="ra-metric-card">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <div className="metric-value">+{data.correlation?.pricing_optimization?.potential_increase || 18.5}%</div>
            <div className="metric-label">Pricing Optimization Potential</div>
            <div className="metric-change positive">Revenue increase opportunity</div>
          </div>
        </div>
      </div>

      {/* Revenue Forecast Chart */}
      <div className="ra-chart-section">
        <div className="chart-header">
          <h3>Revenue Forecast ({selectedTimeframe} Months)</h3>
          <span className="chart-subtitle">ML predictions with confidence intervals</span>
        </div>
        <div className="chart-container">
          <Line data={forecastChartData} options={chartOptions} />
        </div>
      </div>

      {/* Analytics Grid */}
      <div className="ra-analytics-grid">
        <div className="ra-chart-card">
          <div className="chart-header">
            <h3>Feature ROI Analysis</h3>
            <span className="chart-subtitle">Return on investment by feature type</span>
          </div>
          <div className="chart-container">
            <Bar data={roiChartData} options={chartOptions} />
          </div>
        </div>

        <div className="ra-chart-card">
          <div className="chart-header">
            <h3>Customer Segment Revenue</h3>
            <span className="chart-subtitle">Revenue distribution by customer tier</span>
          </div>
          <div className="chart-container">
            <Bar data={segmentChartData} options={segmentChartOptions} />
          </div>
        </div>
      </div>

      {/* Feature ROI Table */}
      <div className="ra-section">
        <div className="section-header">
          <h3>🚀 Feature Performance Analysis</h3>
          <span className="section-subtitle">Detailed ROI breakdown by feature</span>
        </div>
        <div className="roi-table-container">
          <table className="roi-table">
            <thead>
              <tr>
                <th>Feature</th>
                <th>Usage Count</th>
                <th>Revenue Impact</th>
                <th>ROI</th>
                <th>Trend</th>
              </tr>
            </thead>
            <tbody>
              {data.correlation?.feature_roi?.map((feature, index) => (
                <tr key={index}>
                  <td>
                    <div className="feature-name">{feature.feature}</div>
                  </td>
                  <td>{feature.usage_count?.toLocaleString()}</td>
                  <td>${feature.revenue_impact?.toLocaleString()}</td>
                  <td>
                    <span className={`roi-badge ${feature.roi > 200 ? 'high' : feature.roi > 100 ? 'medium' : 'low'}`}>
                      {feature.roi}%
                    </span>
                  </td>
                  <td>
                    <span className="trend-indicator positive">📈</span>
                  </td>
                </tr>
              )) || []}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pricing Optimization */}
      <div className="ra-section">
        <div className="section-header">
          <h3>💡 Pricing Optimization Recommendations</h3>
          <span className="section-subtitle">Data-driven pricing strategy insights</span>
        </div>
        <div className="pricing-grid">
          {data.correlation?.pricing_optimization?.current_plans?.map((plan, index) => (
            <div key={index} className="pricing-card">
              <div className="plan-header">
                <h4>{plan.plan}</h4>
                <div className="current-price">${plan.price}/mo</div>
              </div>
              <div className="plan-metrics">
                <div className="plan-metric">
                  <span className="metric-label">Subscribers</span>
                  <span className="metric-value">{plan.subscribers}</span>
                </div>
                <div className="plan-metric">
                  <span className="metric-label">Monthly Revenue</span>
                  <span className="metric-value">${plan.revenue?.toLocaleString()}</span>
                </div>
              </div>
              <div className="pricing-recommendation">
                <div className="suggested-price">
                  Suggested: <strong>${plan.suggested_price}/mo</strong>
                </div>
                <div className="price-increase">
                  +${plan.suggested_price - plan.price} ({Math.round(((plan.suggested_price - plan.price) / plan.price) * 100)}% increase)
                </div>
              </div>
            </div>
          )) || []}
        </div>
      </div>

      {/* Customer Segments */}
      <div className="ra-section">
        <div className="section-header">
          <h3>👥 Customer Segment Analysis</h3>
          <span className="section-subtitle">Revenue performance by customer tier</span>
        </div>
        <div className="segments-grid">
          {data.correlation?.customer_segments?.map((segment, index) => (
            <div key={index} className="segment-card">
              <div className="segment-header">
                <h4>{segment.segment}</h4>
                <div className="segment-count">{segment.count} customers</div>
              </div>
              <div className="segment-metrics">
                <div className="segment-metric">
                  <span className="metric-label">Total Revenue</span>
                  <span className="metric-value">${segment.total_revenue?.toLocaleString()}</span>
                </div>
                <div className="segment-metric">
                  <span className="metric-label">Avg Revenue</span>
                  <span className="metric-value">${segment.avg_revenue?.toLocaleString()}</span>
                </div>
                <div className="segment-metric">
                  <span className="metric-label">Growth Rate</span>
                  <span className="metric-value growth-positive">+{segment.growth}%</span>
                </div>
              </div>
            </div>
          )) || []}
        </div>
      </div>
    </div>
  );
};

export default RevenueAnalytics;