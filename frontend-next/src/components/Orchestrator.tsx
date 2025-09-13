import React, { useState, useEffect } from 'react';
import './Orchestrator.css';
import { checklistAPI, dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { 
  ChevronDown, 
  ChevronUp, 
  Target, 
  TrendingUp, 
  Award, 
  Clock,
  CheckCircle,
  AlertCircle,
  DollarSign,
  Zap,
  Play
} from 'lucide-react';

interface OrchestratorProps {
  viewMode?: string;
}

const Orchestrator: React.FC<OrchestratorProps> = ({ viewMode: externalViewMode }) => {
  const { user } = useAuth();
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<any>({});
  const [updatingItems, setUpdatingItems] = useState<any>({});
  const [restaurantId, setRestaurantId] = useState<string | null>(null);
  const viewMode = externalViewMode || 'overview';
  const [activeTab, setActiveTab] = useState('foundation');

  // Get restaurant ID from auth context
  useEffect(() => {
    const getRestaurantData = async () => {
      try {
        if (user?.role === 'restaurant') {
          setRestaurantId(user.user_id);
        } else if (user?.impersonating_restaurant_id) {
          setRestaurantId(user.impersonating_restaurant_id);
        } else {
          const dashboardData = await dashboardAPI.getRestaurantDashboard();
          setRestaurantId(dashboardData.restaurant.restaurant_id);
        }
      } catch (err) {
        console.error('Error getting restaurant data:', err);
        setError('Failed to get restaurant information');
      }
    };

    if (user) {
      getRestaurantData();
    }
  }, [user]);

  // Load checklist data when restaurant ID is available
  useEffect(() => {
    if (restaurantId) {
      loadChecklistData();
    }
  }, [restaurantId]);

  const loadChecklistData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [categoriesResponse, progressResponse] = await Promise.all([
        checklistAPI.getCategoriesWithItems(null, restaurantId ? restaurantId : null),
        checklistAPI.getProgress(restaurantId)
      ]);

      if (categoriesResponse.success) {
        setCategories(categoriesResponse.categories);
      }

      if (progressResponse.success) {
        setProgress(progressResponse.progress);
      }
    } catch (err) {
      console.error('Error loading checklist data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateItemStatus = async (itemId: string, newStatus: string) => {
    try {
      setUpdatingItems((prev: any) => ({ ...prev, [itemId]: true }));

      const result = await checklistAPI.updateStatus(restaurantId, itemId, newStatus);
      
      if (!result.success) {
        throw new Error('Backend update failed');
      }
      
      // Update local state
      setCategories(prevCategories => {
        return prevCategories.map(category => ({
          ...category,
          items: category.items.map(item =>
            item.item_id === itemId
              ? { ...item, status: newStatus }
              : item
          )
        }));
      });
      
      // Reload progress data
      const progressResponse = await checklistAPI.getProgress(restaurantId);
      if (progressResponse.success) {
        setProgress(progressResponse.progress);
      }
      
    } catch (err) {
      console.error('Error updating item status:', err);
      setError(err.message);
      await loadChecklistData();
    } finally {
      setUpdatingItems((prev: any) => ({ ...prev, [itemId]: false }));
    }
  };

  const handleCheckboxChange = (itemId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    updateItemStatus(itemId, newStatus);
  };

  const getOverallProgress = () => {
    const foundationalProgress = progress.foundational || {};
    const ongoingProgress = progress.ongoing || {};
    
    return {
      foundational: {
        completed: foundationalProgress.completedItems || 0,
        total: foundationalProgress.totalItems || 0,
        percentage: foundationalProgress.completionPercentage || 0,
        criticalCompleted: foundationalProgress.completedCriticalItems || 0,
        criticalTotal: foundationalProgress.criticalItems || 0,
        criticalPercentage: foundationalProgress.criticalCompletionPercentage || 0
      },
      ongoing: {
        completed: ongoingProgress.completedItems || 0,
        total: ongoingProgress.totalItems || 0,
        percentage: ongoingProgress.completionPercentage || 0
      }
    };
  };

  const calculateOverallScore = () => {
    const overallProgress = getOverallProgress();
    
    const foundationalWeight = 0.7;
    const ongoingWeight = 0.3;
    const criticalBonus = 0.1;
    
    const foundationalBaseScore = (overallProgress.foundational.completed / Math.max(overallProgress.foundational.total, 1)) * 100;
    const criticalScore = (overallProgress.foundational.criticalCompleted / Math.max(overallProgress.foundational.criticalTotal, 1)) * 100;
    const foundationalScore = (foundationalBaseScore * (1 - criticalBonus)) + (criticalScore * criticalBonus);
    
    const ongoingScore = (overallProgress.ongoing.completed / Math.max(overallProgress.ongoing.total, 1)) * 100;
    
    const totalScore = (foundationalScore * foundationalWeight) + (ongoingScore * ongoingWeight);
    
    return Math.round(Math.min(totalScore, 100));
  };

  const calculateRevenueImpact = () => {
    if (!categories.length) {
      return {
        weeklyPotential: 0,
        completedValue: 0,
        totalPotential: 0,
        completionPercentage: 0
      };
    }

    const revenueImpacts = {
      'google_business_optimization': 450,
      'google_reviews_management': 320,
      'social_media_posting': 280,
      'social_media_advertising': 680,
      'online_ordering_setup': 890,
      'menu_optimization': 340,
      'upselling_strategies': 520,
      'email_campaigns': 380,
      'promotional_campaigns': 450,
      'loyalty_program': 420,
      'rewards_system': 290,
      'facebook_advertising': 720,
      'google_ads': 650,
      'promotional_offers': 380,
      'customer_feedback': 180,
      'review_management': 220,
    };

    let totalPotential = 0;
    let completedRevenue = 0;

    categories.forEach(category => {
      category.items.forEach(item => {
        const itemKey = getRevenueCategory(item.title, item.description);
        const impact = revenueImpacts[itemKey] || 150; // Default impact
        
        totalPotential += impact;
        
        if (item.status === 'completed') {
          completedRevenue += impact;
        }
      });
    });

    const remainingPotential = totalPotential - completedRevenue;
    
    return {
      weeklyPotential: Math.round(remainingPotential),
      completedValue: Math.round(completedRevenue),
      totalPotential: Math.round(totalPotential),
      completionPercentage: totalPotential > 0 ? Math.round((completedRevenue / totalPotential) * 100) : 0
    };
  };

  const getRevenueCategory = (title: string, description: string) => {
    const text = (title + ' ' + description).toLowerCase();
    
    if (text.includes('google business') || text.includes('gbp')) return 'google_business_optimization';
    if (text.includes('review') && text.includes('google')) return 'google_reviews_management';
    if (text.includes('social media') && text.includes('post')) return 'social_media_posting';
    if (text.includes('facebook') && text.includes('ad')) return 'facebook_advertising';
    if (text.includes('google') && text.includes('ad')) return 'google_ads';
    if (text.includes('online ordering') || text.includes('delivery')) return 'online_ordering_setup';
    if (text.includes('menu') && (text.includes('optim') || text.includes('updat'))) return 'menu_optimization';
    if (text.includes('upsell') || text.includes('cross-sell')) return 'upselling_strategies';
    if (text.includes('email') && text.includes('campaign')) return 'email_campaigns';
    if (text.includes('promotion') || text.includes('offer')) return 'promotional_campaigns';
    if (text.includes('loyalty') || text.includes('reward')) return 'loyalty_program';
    if (text.includes('social media') && text.includes('ad')) return 'social_media_advertising';
    if (text.includes('feedback') || text.includes('survey')) return 'customer_feedback';
    if (text.includes('review') && !text.includes('google')) return 'review_management';
    
    return 'google_business_optimization';
  };

  const getNextAction = () => {
    const overallProgress = getOverallProgress();
    const criticalItems = [];
    const pendingItems = [];

    categories.forEach(category => {
      category.items.forEach(item => {
        if (item.status !== 'completed') {
          if (item.is_critical === 1) {
            criticalItems.push(item);
          } else {
            pendingItems.push(item);
          }
        }
      });
    });

    if (criticalItems.length > 0) {
      return {
        type: 'critical',
        item: criticalItems[0],
        message: `Complete critical task: ${criticalItems[0].title}`,
        impact: 'High revenue impact'
      };
    }

    if (pendingItems.length > 0) {
      return {
        type: 'normal',
        item: pendingItems[0],
        message: `Next recommended task: ${pendingItems[0].title}`,
        impact: 'Steady progress'
      };
    }

    return {
      type: 'complete',
      message: 'All tasks completed! Great work!',
      impact: 'Optimization mode'
    };
  };

  const getHealthStatus = () => {
    const score = calculateOverallScore();
    if (score >= 80) return { status: '🟢', label: 'Excellent', color: '#10b981' };
    if (score >= 60) return { status: '🟡', label: 'Good', color: '#f59e0b' };
    return { status: '🔴', label: 'Needs Work', color: '#ef4444' };
  };

  if (loading) {
    return (
      <div className="orchestrator">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading Command Center...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="orchestrator">
        <div className="error-state">
          <h3>⚠️ Error Loading Data</h3>
          <p>{error}</p>
          <button onClick={loadChecklistData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const overallProgress = getOverallProgress();
  const revenueData = calculateRevenueImpact();
  const nextAction = getNextAction();
  const healthStatus = getHealthStatus();
  const foundationalCategories = categories.filter(cat => cat.type === 'foundational');
  const ongoingCategories = categories.filter(cat => cat.type === 'ongoing');

  return (
    <div className="orchestrator">
      {/* Enhanced Dashboard Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="dashboard-title">Marketing Command Center</h1>
            <p className="dashboard-subtitle">Track progress, optimize performance, drive revenue</p>
          </div>
          <div className="header-right">
            <div className="view-controls">
              <button 
                className={`view-toggle ${viewMode === 'overview' ? 'active' : ''}`}
                onClick={() => window.location.hash = 'overview'}
              >
                📊 Dashboard
              </button>
              <button 
                className={`view-toggle ${viewMode !== 'overview' ? 'active' : ''}`}
                onClick={() => window.location.hash = 'details'}
              >
                📋 Details
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Conditional View Rendering */}
      {viewMode === 'overview' ? (
        <>
        {/* Key Metrics Overview Bar */}
        <div className="metrics-overview">
          <div className="metric-card">
            <div className="metric-icon">🎯</div>
            <div className="metric-content">
              <div className="metric-value">{calculateOverallScore()}</div>
              <div className="metric-label">Overall Score</div>
              <div className="metric-trend">+{Math.round(calculateOverallScore() * 0.1)} this week</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">💰</div>
            <div className="metric-content">
              <div className="metric-value">${revenueData.completedValue}</div>
              <div className="metric-label">Revenue Unlocked</div>
              <div className="metric-trend">${revenueData.weeklyPotential} potential</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">⚡</div>
            <div className="metric-content">
              <div className="metric-value">{overallProgress.foundational.criticalCompleted}/{overallProgress.foundational.criticalTotal}</div>
              <div className="metric-label">Critical Tasks</div>
              <div className="metric-trend">{overallProgress.foundational.criticalPercentage}% complete</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <div className="metric-value">{overallProgress.foundational.completed + overallProgress.ongoing.completed}</div>
              <div className="metric-label">Tasks Complete</div>
              <div className="metric-trend">{overallProgress.foundational.total + overallProgress.ongoing.total} total</div>
            </div>
          </div>
        </div>

        {/* Enhanced Three-Panel Layout */}
        <div className="command-center-grid">
        
        {/* Left Panel - Score Zone */}
        <div className="score-zone panel card">
          <div className="panel-header">
            <h3>Performance Overview</h3>
            <span className="panel-subtitle">Track your marketing progress</span>
          </div>
          
          <div className="score-hero">
            <div className="score-container">
              <div className="circular-score">
                <svg width="160" height="160" viewBox="0 0 160 160">
                  {/* Background circle */}
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke="rgba(102, 126, 234, 0.08)"
                    strokeWidth="5"
                  />
                  {/* Progress circle */}
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke="url(#scoreGradient)"
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 70}`}
                    strokeDashoffset={`${2 * Math.PI * 70 * (1 - calculateOverallScore() / 100)}`}
                    transform="rotate(-90 80 80)"
                    className="progress-circle"
                  />
                  {/* Gradient definitions */}
                  <defs>
                    <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="50%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                      <feMerge> 
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                </svg>
                <div className="score-content">
                  <div className="score-number">{calculateOverallScore()}</div>
                  <div className="score-label">Marketing Score</div>
                </div>
              </div>
              <div className="health-status">
                <div className="status-badge" style={{ backgroundColor: `${healthStatus.color}15`, borderColor: healthStatus.color }}>
                  <span className="status-indicator" style={{ color: healthStatus.color }}>
                    {healthStatus.status}
                  </span>
                  <span className="status-label">{healthStatus.label}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="revenue-summary">
            <div className="revenue-item">
              <DollarSign size={16} />
              <div className="revenue-details">
                <span className="revenue-amount">${revenueData.completedValue}</span>
                <span className="revenue-label">Unlocked</span>
              </div>
            </div>
            <div className="revenue-item">
              <TrendingUp size={16} />
              <div className="revenue-details">
                <span className="revenue-amount">${revenueData.weeklyPotential}</span>
                <span className="revenue-label">Potential</span>
              </div>
            </div>
          </div>

          <div className="kpi-pills">
            <div className="kpi-pill">
              <span className="kpi-label text-secondary">Foundation</span>
              <span className="kpi-value text-primary">{overallProgress.foundational.percentage}%</span>
            </div>
            <div className="kpi-pill">
              <span className="kpi-label text-secondary">Critical</span>
              <span className="kpi-value text-primary">{overallProgress.foundational.criticalCompleted}/{overallProgress.foundational.criticalTotal}</span>
            </div>
            <div className="kpi-pill">
              <span className="kpi-label text-secondary">Ongoing</span>
              <span className="kpi-value text-primary">{overallProgress.ongoing.percentage}%</span>
            </div>
          </div>

          <div className="achievement-row">
            <div className={`achievement ${overallProgress.foundational.completed > 0 ? 'earned' : 'locked'}`}>
              <Award size={14} />
            </div>
            <div className={`achievement ${overallProgress.foundational.criticalCompleted >= 3 ? 'earned' : 'locked'}`}>
              <Zap size={14} />
            </div>
            <div className={`achievement ${calculateOverallScore() >= 80 ? 'earned' : 'locked'}`}>
              <Target size={14} />
            </div>
          </div>
        </div>

        {/* Center Panel - Action Zone */}
        <div className="action-zone panel card">
          <div className="panel-header">
            <h3>Action Center</h3>
            <span className="panel-subtitle">Complete tasks to boost your score</span>
          </div>
          
          <div className="next-action-card">
            <div className="action-header">
              <div className="action-icon">
                {nextAction.type === 'critical' ? <AlertCircle size={20} /> : <Play size={20} />}
              </div>
              <div className="action-content">
                <h3>Next Action</h3>
                <p>{nextAction.message}</p>
                <span className="action-impact">{nextAction.impact}</span>
              </div>
            </div>
            {nextAction.item && (
              <button 
                className="start-action-btn"
                onClick={() => handleCheckboxChange(nextAction.item.item_id, nextAction.item.status)}
                disabled={updatingItems[nextAction.item.item_id]}
              >
                {updatingItems[nextAction.item.item_id] ? 'Updating...' : 'Mark Complete'}
              </button>
            )}
          </div>

          <div className="quick-wins">
            <h4>Quick Wins</h4>
            <div className="quick-win-list">
              {categories.slice(0, 2).map(category => {
                const pendingItems = category.items.filter(item => item.status !== 'completed').slice(0, 2);
                return pendingItems.map(item => (
                  <div key={item.item_id} className="quick-win-item">
                    <input
                      type="checkbox"
                      checked={item.status === 'completed'}
                      onChange={() => handleCheckboxChange(item.item_id, item.status)}
                      disabled={updatingItems[item.item_id]}
                    />
                    <span className="quick-win-title">{item.title}</span>
                    {item.is_critical === 1 && <Zap size={12} className="critical-icon" />}
                  </div>
                ));
              })}
            </div>
          </div>

          <div className="smart-insights">
            <h4>Smart Insights</h4>
            <div className="insight-card">
              <div className="insight-icon">💡</div>
              <p>Complete Google Business Profile to unlock ${revenueData.weeklyPotential > 400 ? '450' : '200'}/week</p>
            </div>
          </div>

          <div className="recent-activity">
            <h4>Recent Activity</h4>
            <div className="activity-list">
              {categories.slice(0, 1).map(category => {
                const completedItems = category.items.filter(item => item.status === 'completed').slice(0, 3);
                return completedItems.map(item => (
                  <div key={item.item_id} className="activity-item">
                    <CheckCircle size={14} />
                    <span>{item.title}</span>
                    <span className="activity-time">Recently</span>
                  </div>
                ));
              })}
            </div>
          </div>
        </div>

        {/* Right Panel - Progress Zone */}
        <div className="progress-zone panel card">
          <div className="panel-header">
            <h3>Progress Tracker</h3>
            <span className="panel-subtitle">Monitor category completion rates</span>
          </div>
          
          <div className="category-progress">
            <div className="progress-header">
              <h4>Category Progress</h4>
            </div>
            <div className="progress-bars">
              {foundationalCategories.slice(0, 4).map(category => {
                const categoryProgress = Math.round((category.items.filter(item => item.status === 'completed').length / category.items.length) * 100);
                return (
                  <div key={category.category_id} className="progress-bar-item">
                    <div className="progress-info">
                      <span className="progress-name">{category.name}</span>
                      <span className="progress-percentage">{categoryProgress}%</span>
                    </div>
                    <div className="progress-bar-track">
                      <div 
                        className="progress-bar-fill"
                        style={{ width: `${categoryProgress}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="critical-alerts">
            <h4>Critical Items</h4>
            <div className="alert-list">
              {categories.slice(0, 1).map(category => {
                const criticalItems = category.items.filter(item => item.is_critical === 1 && item.status !== 'completed').slice(0, 3);
                return criticalItems.map(item => (
                  <div key={item.item_id} className="alert-item">
                    <AlertCircle size={14} />
                    <span>{item.title}</span>
                    <button 
                      className="alert-action"
                      onClick={() => handleCheckboxChange(item.item_id, item.status)}
                      disabled={updatingItems[item.item_id]}
                    >
                      Complete
                    </button>
                  </div>
                ));
              })}
            </div>
          </div>

          <div className="timeline-view">
            <h4>This Week</h4>
            <div className="timeline-items">
              <div className="timeline-item">
                <Clock size={14} />
                <span>Update Google Business hours</span>
              </div>
              <div className="timeline-item">
                <Clock size={14} />
                <span>Post social media content</span>
              </div>
              <div className="timeline-item">
                <Clock size={14} />
                <span>Review customer feedback</span>
              </div>
            </div>
          </div>

          <div className="progress-trend">
            <h4>Progress Trend</h4>
            <div className="trend-chart">
              <div className="trend-line">
                <span className="trend-point"></span>
                <span className="trend-point"></span>
                <span className="trend-point active"></span>
                <span className="trend-point"></span>
                <span className="trend-point"></span>
              </div>
              <div className="trend-labels">
                <span>Mon</span>
                <span>Tue</span>
                <span>Wed</span>
                <span>Thu</span>
                <span>Fri</span>
              </div>
            </div>
          </div>
        </div>
        </div>
        </>
      ) : (
        /* Details View */
        <div className="details-view">
          <div className="details-header">
            <div className="details-tabs">
              <button 
                className={`details-tab ${activeTab === 'foundation' ? 'active' : ''}`}
                onClick={() => setActiveTab('foundation')}
              >
                Foundation ({foundationalCategories.length})
              </button>
              <button 
                className={`details-tab ${activeTab === 'ongoing' ? 'active' : ''}`}
                onClick={() => setActiveTab('ongoing')}
              >
                Ongoing ({ongoingCategories.length})
              </button>
              <button 
                className={`details-tab ${activeTab === 'completed' ? 'active' : ''}`}
                onClick={() => setActiveTab('completed')}
              >
                Completed
              </button>
            </div>
          </div>

          <div className="details-content">
            {activeTab === 'foundation' && (
              <div className="detailed-checklist">
                {foundationalCategories.map(category => (
                  <div key={category.category_id} className="detailed-category">
                    <div className="category-header">
                      <h3 className="category-title">{category.icon} {category.name}</h3>
                      <div className="category-progress">
                        <span className="progress-fraction">
                          {category.items.filter(item => item.status === 'completed').length}/{category.items.length}
                        </span>
                        <div className="category-progress-bar">
                          <div 
                            className="category-progress-fill"
                            style={{ 
                              width: `${Math.round((category.items.filter(item => item.status === 'completed').length / category.items.length) * 100)}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="detailed-items">
                      {category.items.map(item => (
                        <div key={item.item_id} className={`detailed-item ${item.status === 'completed' ? 'completed' : ''}`}>
                          <div className="item-checkbox">
                            <input
                              type="checkbox"
                              checked={item.status === 'completed'}
                              onChange={() => handleCheckboxChange(item.item_id, item.status)}
                              disabled={updatingItems[item.item_id]}
                            />
                          </div>
                          <div className="item-content">
                            <div className="item-header">
                              <h4 className="item-title">
                                {item.title}
                                {item.is_critical === 1 && <Zap size={14} className="critical-badge" />}
                              </h4>
                              <div className="item-badges">
                                {item.is_critical === 1 && (
                                  <span className="badge critical">Critical</span>
                                )}
                                <span className={`badge status ${item.status}`}>
                                  {item.status === 'completed' ? 'Complete' : 'Pending'}
                                </span>
                              </div>
                            </div>
                            {item.description && (
                              <p className="item-description">{item.description}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'ongoing' && (
              <div className="detailed-checklist">
                {ongoingCategories.map(category => (
                  <div key={category.category_id} className="detailed-category">
                    <div className="category-header">
                      <h3 className="category-title">{category.icon} {category.name}</h3>
                      <div className="category-progress">
                        <span className="progress-fraction">
                          {category.items.filter(item => item.status === 'completed').length}/{category.items.length}
                        </span>
                        <div className="category-progress-bar">
                          <div 
                            className="category-progress-fill"
                            style={{ 
                              width: `${Math.round((category.items.filter(item => item.status === 'completed').length / category.items.length) * 100)}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="detailed-items">
                      {category.items.map(item => (
                        <div key={item.item_id} className={`detailed-item ${item.status === 'completed' ? 'completed' : ''}`}>
                          <div className="item-checkbox">
                            <input
                              type="checkbox"
                              checked={item.status === 'completed'}
                              onChange={() => handleCheckboxChange(item.item_id, item.status)}
                              disabled={updatingItems[item.item_id]}
                            />
                          </div>
                          <div className="item-content">
                            <div className="item-header">
                              <h4 className="item-title">{item.title}</h4>
                              <div className="item-badges">
                                <span className={`badge status ${item.status}`}>
                                  {item.status === 'completed' ? 'Complete' : 'Pending'}
                                </span>
                              </div>
                            </div>
                            {item.description && (
                              <p className="item-description">{item.description}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'completed' && (
              <div className="detailed-checklist">
                {categories.map(category => {
                  const completedItems = category.items.filter(item => item.status === 'completed');
                  if (completedItems.length === 0) return null;
                  
                  return (
                    <div key={category.category_id} className="detailed-category">
                      <div className="category-header">
                        <h3 className="category-title">{category.icon} {category.name}</h3>
                        <div className="category-progress">
                          <span className="progress-fraction">{completedItems.length} completed</span>
                        </div>
                      </div>
                      <div className="detailed-items">
                        {completedItems.map(item => (
                          <div key={item.item_id} className="detailed-item completed">
                            <div className="item-checkbox">
                              <CheckCircle size={20} className="completed-icon" />
                            </div>
                            <div className="item-content">
                              <div className="item-header">
                                <h4 className="item-title">{item.title}</h4>
                                <div className="item-badges">
                                  <span className="badge status completed">Complete</span>
                                </div>
                              </div>
                              {item.description && (
                                <p className="item-description">{item.description}</p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default Orchestrator;