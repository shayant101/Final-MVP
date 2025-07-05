# Enhanced Admin Dashboard Architecture for AI Feature Oversight and Analytics

## Executive Summary

This document outlines the comprehensive architectural plan for enhancing the existing admin dashboard to provide real-time monitoring and analytics for all AI features. The architecture leverages the existing MongoDB database, FastAPI backend, and React frontend while adding new analytics collections and real-time capabilities.

## Current State Analysis

### Existing Infrastructure
- **Frontend**: React with [`AdminDashboard.js`](client/src/components/AdminDashboard.js) providing basic restaurant management
- **Backend**: FastAPI with comprehensive AI services:
  - [`ai_image_enhancement.py`](backendv2/app/services/ai_image_enhancement.py) - Image processing with OpenAI integration
  - [`ai_content_engine.py`](backendv2/app/services/ai_content_engine.py) - Multi-channel content generation
  - [`openai_service.py`](backendv2/app/services/openai_service.py) - OpenAI API integration
  - [`campaign_service.py`](backendv2/app/services/campaign_service.py) - Campaign management
- **Database**: MongoDB with existing collections for restaurants, campaigns, users
- **API**: Well-structured endpoints in [`ai_features.py`](backendv2/app/routes/ai_features.py)

### Data Collection Opportunities
From analyzing the existing services, we can collect:
- Image enhancement requests and processing times
- Content generation usage by type and platform
- OpenAI API calls and response times
- Campaign creation and performance metrics
- Error rates and failure patterns

## Design Requirements Implementation

### 1. Real-time AI Usage Analytics Dashboard
- **Hybrid Approach**: Real-time for critical metrics, periodic for detailed analytics
- Track image enhancement requests per restaurant
- Monitor content generation usage (types, platforms)
- Simple platform-wide OpenAI cost tracking
- Success/failure rates for AI operations
- Performance metrics (response times, error rates)

### 2. AI Content Moderation System
- **Post-publication monitoring** with retroactive flagging capability
- Automated content analysis and flagging
- Bulk approval/rejection workflows
- Quality scoring system
- Admin review interface for flagged content

### 3. AI Model Management Interface
- OpenAI API key management
- Rate limiting controls per restaurant
- Feature toggles (enable/disable AI features)
- Model performance monitoring

## Technical Architecture

### 1. Database Schema for Analytics Tracking

```javascript
// ai_usage_analytics collection
{
  analytics_id: "uuid",
  restaurant_id: "restaurant_123",
  feature_type: "image_enhancement", // image_enhancement, content_generation, marketing_assistant
  operation_type: "enhance_image", // specific operation
  timestamp: ISODate(),
  processing_time_ms: 1250,
  tokens_used: 150,
  estimated_cost: 0.003,
  status: "success", // success, error, timeout
  metadata: {
    image_size: "2MB",
    enhancement_options: {...},
    error_details: null
  },
  created_at: ISODate()
}

// ai_content_moderation collection
{
  moderation_id: "uuid",
  restaurant_id: "restaurant_123",
  content_type: "social_media_caption", // social_media_caption, menu_description, etc.
  content_id: "content_456",
  status: "flagged", // approved, flagged, pending_review
  content_data: {
    original_content: "Generated content text...",
    content_metadata: {...}
  },
  flags: ["inappropriate_content", "quality_issue"],
  reviewed_by: "admin_user_id",
  flagged_at: ISODate(),
  reviewed_at: ISODate()
}

// ai_performance_metrics collection (aggregated daily)
{
  metric_id: "uuid",
  feature_type: "image_enhancement",
  metric_date: ISODate("2025-01-15"),
  total_requests: 245,
  successful_requests: 238,
  failed_requests: 7,
  avg_processing_time: 1180,
  total_cost: 0.73,
  hourly_breakdown: {
    "00": {requests: 5, cost: 0.015},
    "01": {requests: 3, cost: 0.009},
    // ... 24 hours
  }
}

// ai_feature_toggles collection
{
  toggle_id: "uuid",
  restaurant_id: "restaurant_123",
  feature_name: "image_enhancement", // image_enhancement, content_generation, etc.
  enabled: true,
  rate_limits: {
    daily_limit: 100,
    hourly_limit: 10
  },
  updated_at: ISODate(),
  updated_by: "admin_user_id"
}
```

### 2. Enhanced Component Architecture

```
Enhanced AdminDashboard
├── AI Analytics Overview
│   ├── Real-time Metrics Widget (WebSocket)
│   ├── Usage Analytics Charts (Chart.js/Recharts)
│   ├── Cost Monitoring
│   └── Performance Dashboard
├── Content Moderation Panel
│   ├── Content Review Queue
│   ├── Flagged Content List
│   └── Bulk Actions Panel
├── Feature Management
│   ├── Feature Toggle Controls
│   ├── Rate Limiting Settings
│   └── API Key Management
└── Restaurant Management (Enhanced)
    ├── AI Usage per Restaurant
    └── Feature Status Overview
```

### 3. Real-time Data Flow

```
Restaurant → AI Service → MongoDB (Log Analytics) → WebSocket → Admin Dashboard
                      ↓
                 Real-time Event Emission
                      ↓
              Admin Dashboard Update
```

## Detailed Implementation Plan

### Phase 1: Analytics Infrastructure (Week 1-2)

#### 1.1 Database Collections Setup
Create new MongoDB collections with proper indexing:

```javascript
// Indexes for performance
db.ai_usage_analytics.createIndex({ "restaurant_id": 1, "timestamp": -1 })
db.ai_usage_analytics.createIndex({ "feature_type": 1, "timestamp": -1 })
db.ai_usage_analytics.createIndex({ "status": 1, "timestamp": -1 })

db.ai_content_moderation.createIndex({ "status": 1, "flagged_at": -1 })
db.ai_content_moderation.createIndex({ "restaurant_id": 1, "status": 1 })

db.ai_performance_metrics.createIndex({ "feature_type": 1, "metric_date": -1 })
db.ai_feature_toggles.createIndex({ "restaurant_id": 1, "feature_name": 1 })
```

#### 1.2 Analytics Service Layer
Create `backendv2/app/services/analytics_service.py`:

```python
class AIAnalyticsService:
    def __init__(self):
        self.db = None
    
    async def get_db(self):
        if not self.db:
            self.db = get_database()
        return self.db

    async def log_ai_usage(self, restaurant_id: str, feature_type: str, 
                          operation_type: str, processing_time: int, 
                          tokens_used: int, status: str, metadata: dict):
        """Log AI feature usage for analytics"""
        db = await self.get_db()
        
        analytics_doc = {
            "analytics_id": str(uuid.uuid4()),
            "restaurant_id": restaurant_id,
            "feature_type": feature_type,
            "operation_type": operation_type,
            "timestamp": datetime.now(),
            "processing_time_ms": processing_time,
            "tokens_used": tokens_used,
            "estimated_cost": self._calculate_cost(tokens_used, feature_type),
            "status": status,
            "metadata": metadata,
            "created_at": datetime.now()
        }
        
        await db.ai_usage_analytics.insert_one(analytics_doc)
        
        # Emit real-time event for critical metrics
        if feature_type in ["image_enhancement", "content_generation"]:
            await websocket_manager.broadcast_ai_metrics({
                "type": feature_type,
                "status": status,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            })
        
    async def get_real_time_metrics(self) -> dict:
        """Get current real-time metrics for admin dashboard"""
        db = await self.get_db()
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's metrics
        pipeline = [
            {"$match": {"timestamp": {"$gte": today_start}}},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "successful_requests": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                "failed_requests": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                "avg_processing_time": {"$avg": "$processing_time_ms"},
                "total_cost": {"$sum": "$estimated_cost"}
            }}
        ]
        
        result = await db.ai_usage_analytics.aggregate(pipeline).to_list(1)
        metrics = result[0] if result else {}
        
        return {
            "today_requests": metrics.get("total_requests", 0),
            "success_rate": round((metrics.get("successful_requests", 0) / max(metrics.get("total_requests", 1), 1)) * 100, 2),
            "avg_response_time": round(metrics.get("avg_processing_time", 0)),
            "daily_cost": round(metrics.get("total_cost", 0), 4),
            "active_requests": await self._get_active_requests_count(),
            "last_updated": now.isoformat()
        }
        
    async def get_usage_analytics(self, date_range: tuple, 
                                 feature_type: str = None) -> dict:
        """Get detailed usage analytics with filtering"""
        db = await self.get_db()
        start_date, end_date = date_range
        
        match_filter = {"timestamp": {"$gte": start_date, "$lte": end_date}}
        if feature_type:
            match_filter["feature_type"] = feature_type
        
        # Usage over time
        usage_pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "feature_type": "$feature_type"
                },
                "requests": {"$sum": 1},
                "cost": {"$sum": "$estimated_cost"}
            }},
            {"$sort": {"_id.date": 1}}
        ]
        
        # Feature breakdown
        feature_pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": "$feature_type",
                "requests": {"$sum": 1},
                "cost": {"$sum": "$estimated_cost"},
                "avg_processing_time": {"$avg": "$processing_time_ms"}
            }}
        ]
        
        # Error analysis
        error_pipeline = [
            {"$match": {**match_filter, "status": "error"}},
            {"$group": {
                "_id": "$feature_type",
                "error_count": {"$sum": 1},
                "error_types": {"$push": "$metadata.error_details"}
            }}
        ]
        
        usage_data = await db.ai_usage_analytics.aggregate(usage_pipeline).to_list(None)
        feature_data = await db.ai_usage_analytics.aggregate(feature_pipeline).to_list(None)
        error_data = await db.ai_usage_analytics.aggregate(error_pipeline).to_list(None)
        
        return {
            "usage_over_time": usage_data,
            "feature_breakdown": feature_data,
            "error_analysis": error_data,
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()}
        }
        
    async def calculate_daily_aggregates(self, date: datetime):
        """Calculate and store daily performance metrics"""
        db = await self.get_db()
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Get feature types
        feature_types = await db.ai_usage_analytics.distinct("feature_type", {
            "timestamp": {"$gte": day_start, "$lt": day_end}
        })
        
        for feature_type in feature_types:
            # Calculate daily metrics for each feature
            pipeline = [
                {"$match": {
                    "feature_type": feature_type,
                    "timestamp": {"$gte": day_start, "$lt": day_end}
                }},
                {"$group": {
                    "_id": {"$hour": "$timestamp"},
                    "requests": {"$sum": 1},
                    "successful": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "failed": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                    "avg_processing_time": {"$avg": "$processing_time_ms"},
                    "cost": {"$sum": "$estimated_cost"}
                }}
            ]
            
            hourly_data = await db.ai_usage_analytics.aggregate(pipeline).to_list(None)
            
            # Create hourly breakdown
            hourly_breakdown = {}
            total_requests = 0
            total_successful = 0
            total_failed = 0
            total_cost = 0
            
            for hour_data in hourly_data:
                hour = str(hour_data["_id"]).zfill(2)
                hourly_breakdown[hour] = {
                    "requests": hour_data["requests"],
                    "cost": round(hour_data["cost"], 4)
                }
                total_requests += hour_data["requests"]
                total_successful += hour_data["successful"]
                total_failed += hour_data["failed"]
                total_cost += hour_data["cost"]
            
            # Store daily aggregate
            metric_doc = {
                "metric_id": str(uuid.uuid4()),
                "feature_type": feature_type,
                "metric_date": day_start,
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "failed_requests": total_failed,
                "avg_processing_time": round(sum(h.get("avg_processing_time", 0) for h in hourly_data) / len(hourly_data) if hourly_data else 0),
                "total_cost": round(total_cost, 4),
                "hourly_breakdown": hourly_breakdown,
                "created_at": datetime.now()
            }
            
            # Upsert daily metric
            await db.ai_performance_metrics.replace_one(
                {"feature_type": feature_type, "metric_date": day_start},
                metric_doc,
                upsert=True
            )
    
    def _calculate_cost(self, tokens_used: int, feature_type: str) -> float:
        """Calculate estimated cost based on tokens and feature type"""
        # Simple cost calculation - adjust based on actual OpenAI pricing
        cost_per_token = {
            "image_enhancement": 0.0,  # No tokens for image enhancement
            "content_generation": 0.00002,  # ~$0.02 per 1K tokens
            "marketing_assistant": 0.00002
        }
        
        return tokens_used * cost_per_token.get(feature_type, 0.00002)
    
    async def _get_active_requests_count(self) -> int:
        """Get count of currently active AI requests"""
        # This would track in-progress requests in a separate collection or cache
        # For now, return 0 as placeholder
        return 0

# Create service instance
analytics_service = AIAnalyticsService()
```

#### 1.3 WebSocket Integration
Create `backendv2/app/websocket_manager.py`:

```python
from fastapi import WebSocket
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_ai_metrics(self, metrics: dict):
        """Broadcast real-time AI metrics to admin dashboards"""
        if not self.active_connections:
            return
        
        message = {
            "type": "ai_metrics_update",
            "data": metrics
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def notify_content_flagged(self, content_data: dict):
        """Notify admins of flagged content"""
        message = {
            "type": "content_flagged",
            "data": content_data
        }
        
        await self._broadcast_to_admins(message)
    
    async def _broadcast_to_admins(self, message: dict):
        """Broadcast message to admin connections only"""
        # For now, broadcast to all connections
        # In production, you'd filter by admin role
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending admin WebSocket message: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

# Create global instance
websocket_manager = WebSocketManager()
```

### Phase 2: Enhanced Admin Dashboard Frontend (Week 3-4)

#### 2.1 Enhanced AdminDashboard Component Structure

```jsx
// Enhanced AdminDashboard.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI } from '../services/api';
import AIAnalyticsOverview from './admin/AIAnalyticsOverview';
import ContentModerationPanel from './admin/ContentModerationPanel';
import FeatureManagementPanel from './admin/FeatureManagementPanel';
import CostMonitoringPanel from './admin/CostMonitoringPanel';
import RealTimeMetricsBar from './admin/RealTimeMetricsBar';
import AdminNavigation from './admin/AdminNavigation';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [restaurants, setRestaurants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('ai-overview');
  const [realTimeMetrics, setRealTimeMetrics] = useState({});
  const [wsConnection, setWsConnection] = useState(null);
  const { impersonate } = useAuth();

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://localhost:8000/ws/admin`);
      
      ws.onopen = () => {
        console.log('Admin WebSocket connected');
        setWsConnection(ws);
      };
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'ai_metrics_update') {
          setRealTimeMetrics(prev => ({
            ...prev,
            ...message.data
          }));
        }
      };
      
      ws.onclose = () => {
        console.log('Admin WebSocket disconnected');
        setWsConnection(null);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();

    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, []);

  // Fetch initial data
  useEffect(() => {
    fetchDashboardData();
    if (activeView === 'restaurants') {
      fetchRestaurants();
    }
  }, [activeView]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getAdminDashboard();
      setDashboardData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRestaurants = async () => {
    try {
      const data = await dashboardAPI.getAllRestaurants(searchTerm);
      setRestaurants(data.restaurants);
    } catch (error) {
      setError('Failed to fetch restaurants');
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants();
  };

  const handleImpersonate = async (restaurantId) => {
    try {
      await impersonate(restaurantId);
      window.location.reload();
    } catch (error) {
      setError('Failed to start impersonation');
    }
  };

  const views = {
    'ai-overview': <AIAnalyticsOverview />,
    'content-moderation': <ContentModerationPanel />,
    'feature-management': <FeatureManagementPanel />,
    'cost-monitoring': <CostMonitoringPanel />,
    'restaurants': (
      <div className="restaurants-content">
        <div className="restaurants-header">
          <h2>Manage All Restaurants</h2>
          <form onSubmit={handleSearchSubmit} className="search-form">
            <input
              type="text"
              placeholder="Search restaurants by name..."
              value={searchTerm}
              onChange={handleSearch}
              className="search-input"
            />
            <button type="submit" className="search-button">Search</button>
          </form>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="restaurants-table-container">
          <table className="restaurants-table">
            <thead>
              <tr>
                <th>Restaurant Name</th>
                <th>Owner Email</th>
                <th>Signup Date</th>
                <th>AI Usage</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {restaurants.map(restaurant => (
                <tr key={restaurant.restaurant_id}>
                  <td>
                    <div className="restaurant-info">
                      <div className="restaurant-name">{restaurant.name}</div>
                      {restaurant.address && (
                        <div className="restaurant-address">{restaurant.address}</div>
                      )}
                    </div>
                  </td>
                  <td>{restaurant.email}</td>
                  <td>{new Date(restaurant.signup_date).toLocaleDateString()}</td>
                  <td>
                    <div className="ai-usage-summary">
                      <span className="usage-badge">🤖 {restaurant.ai_requests || 0}</span>
                    </div>
                  </td>
                  <td>
                    <button
                      className="impersonate-button"
                      onClick={() => handleImpersonate(restaurant.restaurant_id)}
                    >
                      🎭 Impersonate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {restaurants.length === 0 && !loading && (
            <div className="no-restaurants">
              <p>No restaurants found</p>
              {searchTerm && (
                <p>Try adjusting your search terms</p>
              )}
            </div>
          )}
        </div>
      </div>
    )
  };

  if (loading && !dashboardData) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="admin-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="enhanced-admin-dashboard">
      <div className="admin-header">
        <h1>AI Platform Administration</h1>
        <p>Monitor and manage AI features across all restaurants</p>
      </div>

      <AdminNavigation activeView={activeView} setActiveView={setActiveView} />
      <RealTimeMetricsBar metrics={realTimeMetrics} />
      
      <div className="admin-content">
        {views[activeView]}
      </div>
    </div>
  );
};

export default AdminDashboard;
```

#### 2.2 AI Analytics Overview Component

```jsx
// components/admin/AIAnalyticsOverview.js
import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { adminAnalyticsAPI } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const AIAnalyticsOverview = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [realTimeData, setRealTimeData] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7d');

  useEffect(() => {
    fetchAnalyticsData();
    fetchRealTimeMetrics();
    fetchRecentActivities();
  }, [dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      const data = await adminAnalyticsAPI.getUsageAnalytics(dateRange);
      setAnalyticsData(data);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    }
  };

  const fetchRealTimeMetrics = async () => {
    try {
      const data = await adminAnalyticsAPI.getRealTimeMetrics();
      setRealTimeData(data);
    } catch (error) {
      console.error('Failed to fetch real-time metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentActivities = async () => {
    try {
      const data = await adminAnalyticsAPI.getRecentActivities();
      setRecentActivities(data.activities || []);
    } catch (error) {
      console.error('Failed to fetch recent activities:', error);
    }
  };

  const MetricCard = ({ title, value, trend, icon, status = 'normal' }) => (
    <div className={`metric-card ${status}`}>
      <div className="metric-header">
        <span className="metric-icon">{icon}</span>
        <span className="metric-title">{title}</span>
      </div>
      <div className="metric-value">{value}</div>
      {trend && (
        <div className={`metric-trend ${trend > 0 ? 'positive' : 'negative'}`}>
          {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  );

  const UsageChart = ({ data }) => {
    if (!data || !data.usage_over_time) return <div>No usage data available</div>;

    const chartData = {
      labels: data.usage_over_time.map(item => item._id.date),
      datasets: [
        {
          label: 'AI Requests',
          data: data.usage_over_time.map(item => item.requests),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }
      ]
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'AI Usage Over Time'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    };

    return <Line data={chartData} options={options} />;
  };

  const FeatureBreakdownChart = ({ data }) => {
    if (!data || !data.feature_breakdown) return <div>No feature data available</div>;

    const chartData = {
      labels: data.feature_breakdown.map(item => item._id.replace('_', ' ').toUpperCase()),
      datasets: [
        {
          label: 'Requests',
          data: data.feature_breakdown.map(item => item.requests),
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
          ]
        }
      ]
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
        },
        title: {
          display: true,
          text: 'Feature Usage Breakdown'
        }
      }
    };

    return <Doughnut data={chartData} options={options} />;
  };

  const ErrorRateChart = ({ data }) => {
    if (!data || !data.error_analysis) return <div>No error data available</div>;

    const chartData = {
      labels: data.error_analysis.map(item => item._id.replace('_', ' ').toUpperCase()),
      datasets: [
        {
          label: 'Error Count',
          data: data.error_analysis.map(item => item.error_count),
          backgroundColor: 'rgba(255, 99, 132, 0.8)',
          borderColor: 'rgba(