import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { adminAnalyticsAPI } from '../services/api';
import './AIAnalytics.css';

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

const AIAnalytics = () => {
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  const [usageAnalytics, setUsageAnalytics] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(7);
  const [selectedFeature, setSelectedFeature] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyticsData();
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchRealTimeMetrics, 30000);
    return () => clearInterval(interval);
  }, [selectedPeriod, selectedFeature]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchRealTimeMetrics(),
        fetchUsageAnalytics()
      ]);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealTimeMetrics = async () => {
    try {
      const response = await adminAnalyticsAPI.getRealTimeMetrics();
      setRealTimeMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch real-time metrics:', error);
    }
  };

  const fetchUsageAnalytics = async () => {
    try {
      const featureType = selectedFeature === 'all' ? null : selectedFeature;
      const response = await adminAnalyticsAPI.getUsageAnalytics(selectedPeriod, featureType);
      setUsageAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch usage analytics:', error);
    }
  };

  const getUsageChartData = () => {
    if (!usageAnalytics?.usage_over_time) return null;

    const dates = [...new Set(usageAnalytics.usage_over_time.map(item => item._id.date))].sort();
    const features = [...new Set(usageAnalytics.usage_over_time.map(item => item._id.feature_type))];

    const datasets = features.map((feature, index) => {
      const colors = [
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)'
      ];

      const data = dates.map(date => {
        const item = usageAnalytics.usage_over_time.find(
          d => d._id.date === date && d._id.feature_type === feature
        );
        return item ? item.requests : 0;
      });

      return {
        label: feature.replace('_', ' ').toUpperCase(),
        data,
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length],
        tension: 0.4,
      };
    });

    return {
      labels: dates,
      datasets,
    };
  };

  const getFeatureBreakdownData = () => {
    if (!usageAnalytics?.feature_breakdown) return null;

    const colors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(16, 185, 129, 0.8)',
      'rgba(245, 158, 11, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(139, 92, 246, 0.8)'
    ];

    return {
      labels: usageAnalytics.feature_breakdown.map(item => 
        item._id.replace('_', ' ').toUpperCase()
      ),
      datasets: [{
        data: usageAnalytics.feature_breakdown.map(item => item.requests),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff',
      }],
    };
  };

  const getCostTrendData = () => {
    if (!usageAnalytics?.usage_over_time) return null;

    const dates = [...new Set(usageAnalytics.usage_over_time.map(item => item._id.date))].sort();
    const costData = dates.map(date => {
      const dayTotal = usageAnalytics.usage_over_time
        .filter(item => item._id.date === date)
        .reduce((sum, item) => sum + (item.cost || 0), 0);
      return dayTotal;
    });

    return {
      labels: dates,
      datasets: [{
        label: 'Daily Cost ($)',
        data: costData,
        borderColor: 'rgba(245, 158, 11, 1)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.4,
      }],
    };
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
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  };

  if (loading && !realTimeMetrics) {
    return (
      <div className="ai-analytics-loading">
        <div className="loading-spinner"></div>
        <p>Loading AI analytics...</p>
      </div>
    );
  }

  if (error && !realTimeMetrics) {
    return (
      <div className="ai-analytics-error">
        <h3>Error Loading Analytics</h3>
        <p>{error}</p>
        <button onClick={fetchAnalyticsData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="ai-analytics">
      {/* Real-time Metrics Bar */}
      {realTimeMetrics && (
        <div className="real-time-metrics">
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.today_requests}</div>
            <div className="metric-label">Today's Requests</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.success_rate}%</div>
            <div className="metric-label">Success Rate</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.avg_response_time}ms</div>
            <div className="metric-label">Avg Response Time</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">${realTimeMetrics.daily_cost}</div>
            <div className="metric-label">Daily Cost</div>
          </div>
          <div className="metric-item">
            <div className="metric-value">{realTimeMetrics.active_requests}</div>
            <div className="metric-label">Active Requests</div>
          </div>
          <div className="metric-item last-updated">
            <div className="metric-label">
              Last Updated: {new Date(realTimeMetrics.last_updated).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="analytics-controls">
        <div className="control-group">
          <label>Time Period:</label>
          <select 
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(parseInt(e.target.value))}
          >
            <option value={1}>Last 24 Hours</option>
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
        </div>
        <div className="control-group">
          <label>Feature Filter:</label>
          <select 
            value={selectedFeature} 
            onChange={(e) => setSelectedFeature(e.target.value)}
          >
            <option value="all">All Features</option>
            <option value="image_enhancement">Image Enhancement</option>
            <option value="content_generation">Content Generation</option>
            <option value="marketing_assistant">Marketing Assistant</option>
            <option value="menu_optimizer">Menu Optimizer</option>
            <option value="digital_grader">Digital Grader</option>
          </select>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Usage Over Time */}
        <div className="chart-container large">
          <div className="chart-header">
            <h3>📈 Usage Over Time</h3>
            <span className="chart-subtitle">Requests per day by feature</span>
          </div>
          <div className="chart-content">
            {getUsageChartData() ? (
              <Line data={getUsageChartData()} options={chartOptions} />
            ) : (
              <div className="no-data">No usage data available</div>
            )}
          </div>
        </div>

        {/* Feature Breakdown */}
        <div className="chart-container">
          <div className="chart-header">
            <h3>🎯 Feature Usage Breakdown</h3>
            <span className="chart-subtitle">Distribution by feature type</span>
          </div>
          <div className="chart-content">
            {getFeatureBreakdownData() ? (
              <Doughnut data={getFeatureBreakdownData()} options={doughnutOptions} />
            ) : (
              <div className="no-data">No feature data available</div>
            )}
          </div>
        </div>

        {/* Cost Trend */}
        <div className="chart-container">
          <div className="chart-header">
            <h3>💰 Cost Trend</h3>
            <span className="chart-subtitle">Daily OpenAI API costs</span>
          </div>
          <div className="chart-content">
            {getCostTrendData() ? (
              <Line data={getCostTrendData()} options={chartOptions} />
            ) : (
              <div className="no-data">No cost data available</div>
            )}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="chart-container">
          <div className="chart-header">
            <h3>⚡ Performance Metrics</h3>
            <span className="chart-subtitle">Average processing time by feature</span>
          </div>
          <div className="chart-content">
            {usageAnalytics?.feature_breakdown ? (
              <Bar 
                data={{
                  labels: usageAnalytics.feature_breakdown.map(item => 
                    item._id.replace('_', ' ').toUpperCase()
                  ),
                  datasets: [{
                    label: 'Avg Processing Time (ms)',
                    data: usageAnalytics.feature_breakdown.map(item => 
                      Math.round(item.avg_processing_time || 0)
                    ),
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 1,
                  }],
                }}
                options={chartOptions}
              />
            ) : (
              <div className="no-data">No performance data available</div>
            )}
          </div>
        </div>
      </div>

      {/* Summary Statistics */}
      {usageAnalytics && (
        <div className="analytics-summary">
          <h3>📊 Summary Statistics</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <div className="summary-label">Total Requests</div>
              <div className="summary-value">
                {usageAnalytics.feature_breakdown.reduce((sum, item) => sum + item.requests, 0)}
              </div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Total Cost</div>
              <div className="summary-value">
                ${usageAnalytics.feature_breakdown.reduce((sum, item) => sum + (item.cost || 0), 0).toFixed(4)}
              </div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Most Used Feature</div>
              <div className="summary-value">
                {usageAnalytics.feature_breakdown.length > 0 
                  ? usageAnalytics.feature_breakdown
                      .sort((a, b) => b.requests - a.requests)[0]._id
                      .replace('_', ' ').toUpperCase()
                  : 'N/A'
                }
              </div>
            </div>
            <div className="summary-item">
              <div className="summary-label">Error Rate</div>
              <div className="summary-value">
                {usageAnalytics.error_analysis.length > 0 
                  ? `${((usageAnalytics.error_analysis.reduce((sum, item) => sum + item.error_count, 0) / 
                       usageAnalytics.feature_breakdown.reduce((sum, item) => sum + item.requests, 1)) * 100).toFixed(2)}%`
                  : '0%'
                }
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalytics;