'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Smartphone, 
  Monitor, 
  ExternalLink 
} from 'lucide-react';
import './WebsiteBuilder.css'; // Reuse existing styles

interface AnalyticsData {
  totalVisitors: number;
  pageViews: number;
  bounceRate: number;
  avgSessionDuration: string;
  topPages: Array<{ page: string; views: number }>;
  deviceBreakdown: Array<{ device: string; percentage: number }>;
  trafficSources: Array<{ source: string; percentage: number }>;
}

const WebsiteAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');

  useEffect(() => {
    // TODO: Implement API call to fetch analytics data
    // For now, use placeholder data
    const placeholderData: AnalyticsData = {
      totalVisitors: 1247,
      pageViews: 3891,
      bounceRate: 34.2,
      avgSessionDuration: '2m 45s',
      topPages: [
        { page: 'Home', views: 1543 },
        { page: 'Menu', views: 892 },
        { page: 'About', views: 567 },
        { page: 'Contact', views: 445 },
        { page: 'Gallery', views: 321 }
      ],
      deviceBreakdown: [
        { device: 'Desktop', percentage: 52 },
        { device: 'Mobile', percentage: 38 },
        { device: 'Tablet', percentage: 10 }
      ],
      trafficSources: [
        { source: 'Direct', percentage: 35 },
        { source: 'Search', percentage: 28 },
        { source: 'Social', percentage: 22 },
        { source: 'Referral', percentage: 15 }
      ]
    };
    
    setTimeout(() => {
      setAnalyticsData(placeholderData);
      setLoading(false);
    }, 1000);
  }, [selectedPeriod]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading analytics data...</p>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="empty-state">
        <div className="empty-icon"><BarChart size={48} /></div>
        <h3>No analytics data available</h3>
        <p>Publish your website to start tracking analytics</p>
      </div>
    );
  }

  return (
    <div className="website-analytics">
      {/* Period Selector */}
      <div className="analytics-controls">
        <div className="period-selector">
          {['24h', '7d', '30d', '90d'].map(period => (
            <button
              key={period}
              className={`period-btn ${selectedPeriod === period ? 'active' : ''}`}
              onClick={() => setSelectedPeriod(period)}
            >
              {period === '24h' ? 'Last 24 Hours' :
               period === '7d' ? 'Last 7 Days' :
               period === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="analytics-grid">
        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>{analyticsData.totalVisitors.toLocaleString()}</h3>
            <p>Total Visitors</p>
            <span className="metric-change positive">+12.3% vs previous period</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📄</div>
          <div className="metric-content">
            <h3>{analyticsData.pageViews.toLocaleString()}</h3>
            <p>Page Views</p>
            <span className="metric-change positive">+8.7% vs previous period</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <h3>{analyticsData.avgSessionDuration}</h3>
            <p>Avg. Session Duration</p>
            <span className="metric-change positive">+5.2% vs previous period</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📉</div>
          <div className="metric-content">
            <h3>{analyticsData.bounceRate}%</h3>
            <p>Bounce Rate</p>
            <span className="metric-change negative">-2.1% vs previous period</span>
          </div>
        </div>
      </div>

      {/* Charts and Details */}
      <div className="analytics-details">
        {/* Top Pages */}
        <div className="analytics-section">
          <h3><BarChart className="inline mr-2" size={18} />Top Pages</h3>
          <div className="top-pages-list">
            {analyticsData.topPages.map((page, index) => (
              <div key={index} className="page-item">
                <div className="page-info">
                  <span className="page-name">{page.page}</span>
                  <span className="page-views">{page.views.toLocaleString()} views</span>
                </div>
                <div className="page-bar">
                  <div 
                    className="page-bar-fill" 
                    style={{ width: `${(page.views / analyticsData.topPages[0].views) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device Breakdown */}
        <div className="analytics-section">
          <h3><Smartphone className="inline mr-2" size={18} />Device Breakdown</h3>
          <div className="device-breakdown">
            {analyticsData.deviceBreakdown.map((device, index) => (
              <div key={index} className="device-item">
                <div className="device-info">
                  <span className="device-icon">
                    {device.device === 'Desktop' ? '🖥️' :
                     device.device === 'Mobile' ? <Smartphone size={16} /> : <Monitor size={16} />}
                  </span>
                  <span className="device-name">{device.device}</span>
                </div>
                <span className="device-percentage">{device.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Traffic Sources */}
        <div className="analytics-section">
          <h3>🚦 Traffic Sources</h3>
          <div className="traffic-sources">
            {analyticsData.trafficSources.map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-info">
                  <span className="source-icon">
                    {source.source === 'Direct' ? '🔗' :
                     source.source === 'Search' ? '🔍' :
                     source.source === 'Social' ? <Smartphone size={16} /> : <ExternalLink size={16} />}
                  </span>
                  <span className="source-name">{source.source}</span>
                </div>
                <span className="source-percentage">{source.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebsiteAnalytics;