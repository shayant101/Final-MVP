'use client';

import React from 'react';
import AIAnalytics from '../../../components/AIAnalytics';
import '../../../components/AdminDashboard.css';

const AdminAnalyticsPage = () => {
  return (
    <div className="admin-dashboard">
      <div className="admin-main-content">
        <div className="main-header">
          <div className="header-title">
            <h1>AI Analytics</h1>
            <p>AI performance metrics and analytics</p>
          </div>
        </div>
        
        <div className="content-area">
          <div className="analytics-content">
            <AIAnalytics />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyticsPage;