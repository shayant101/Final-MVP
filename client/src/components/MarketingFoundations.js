import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MarketingFoundations.css';

// Create API instance directly
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Temporary checklistAPI implementation until import issue is resolved
const checklistAPI = {
  getCategoriesWithItems: async (type = null, restaurantId = null) => {
    try {
      const params = {};
      if (type) params.type = type;
      if (restaurantId) params.restaurantId = restaurantId;
      
      const response = await api.get('/checklist/categories-with-items', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch categories with items');
    }
  },
  
  getProgress: async (restaurantId, type = null) => {
    try {
      const params = type ? { type } : {};
      const response = await api.get(`/checklist/progress/${restaurantId}`, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch progress');
    }
  },
  
  updateStatus: async (restaurantId, itemId, status, notes = null) => {
    try {
      const response = await api.put(`/checklist/status/${restaurantId}/${itemId}`, {
        status,
        notes
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update status');
    }
  }
};

const MarketingFoundations = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [progress, setProgress] = useState({});
  const [updatingItems, setUpdatingItems] = useState({});

  // Mock restaurant ID - in a real app, this would come from auth context
  const restaurantId = 1;

  useEffect(() => {
    loadChecklistData();
  }, []);

  const loadChecklistData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load categories with items and status
      console.log('🔧 Loading data for restaurantId:', restaurantId);
      const [categoriesResponse, progressResponse] = await Promise.all([
        checklistAPI.getCategoriesWithItems(null, restaurantId), // Include restaurantId to get status
        checklistAPI.getProgress(restaurantId)
      ]);

      if (categoriesResponse.success) {
        console.log('🔧 Categories loaded:', categoriesResponse.categories.length);
        console.log('🔧 Sample item statuses:', categoriesResponse.categories[0]?.items?.slice(0, 3).map(item => ({ id: item.item_id, status: item.status })));
        setCategories(categoriesResponse.categories);
        
        // Auto-expand foundational categories
        const initialExpanded = {};
        categoriesResponse.categories.forEach(category => {
          if (category.type === 'foundational') {
            initialExpanded[category.category_id] = true;
          }
        });
        setExpandedCategories(initialExpanded);
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

  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };

  const updateItemStatus = async (itemId, newStatus) => {
    try {
      console.log('🔧 Updating item status:', { restaurantId, itemId, newStatus });
      setUpdatingItems(prev => ({ ...prev, [itemId]: true }));

      const result = await checklistAPI.updateStatus(restaurantId, itemId, newStatus);
      console.log('🔧 Update result:', result);
      
      // Store current scroll position
      const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
      
      // Update local state immediately for better UX
      setCategories(prevCategories =>
        prevCategories.map(category => ({
          ...category,
          items: category.items.map(item =>
            item.item_id === itemId
              ? { ...item, status: newStatus }
              : item
          )
        }))
      );
      
      // Reload progress data only (not full data to avoid scroll reset)
      const progressResponse = await checklistAPI.getProgress(restaurantId);
      if (progressResponse.success) {
        setProgress(progressResponse.progress);
      }
      
      // Restore scroll position after state update
      setTimeout(() => {
        window.scrollTo(0, scrollPosition);
      }, 0);
      
    } catch (err) {
      console.error('❌ Error updating item status:', err);
      setError(err.message);
      // On error, reload full data to ensure consistency
      await loadChecklistData();
    } finally {
      setUpdatingItems(prev => ({ ...prev, [itemId]: false }));
    }
  };

  const handleCheckboxChange = (itemId, currentStatus) => {
    console.log('🔧 Checkbox clicked:', { itemId, currentStatus });
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    console.log('🔧 New status will be:', newStatus);
    updateItemStatus(itemId, newStatus);
  };

  const getCategoryProgress = (category) => {
    const totalItems = category.items.length;
    const completedItems = category.items.filter(item => item.status === 'completed').length;
    const percentage = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
    
    return {
      completed: completedItems,
      total: totalItems,
      percentage
    };
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
    
    // Weighted scoring algorithm:
    // Foundational items are worth 70% of total score (more important)
    // Ongoing items are worth 30% of total score
    // Critical items within foundational get extra weight
    
    const foundationalWeight = 0.7;
    const ongoingWeight = 0.3;
    const criticalBonus = 0.1; // Extra 10% weight for critical items
    
    // Calculate foundational score
    const foundationalBaseScore = (overallProgress.foundational.completed / Math.max(overallProgress.foundational.total, 1)) * 100;
    const criticalScore = (overallProgress.foundational.criticalCompleted / Math.max(overallProgress.foundational.criticalTotal, 1)) * 100;
    const foundationalScore = (foundationalBaseScore * (1 - criticalBonus)) + (criticalScore * criticalBonus);
    
    // Calculate ongoing score
    const ongoingScore = (overallProgress.ongoing.completed / Math.max(overallProgress.ongoing.total, 1)) * 100;
    
    // Calculate weighted total
    const totalScore = (foundationalScore * foundationalWeight) + (ongoingScore * ongoingWeight);
    
    return Math.round(Math.min(totalScore, 100));
  };


  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Great';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    if (score >= 40) return 'Needs Work';
    return 'Getting Started';
  };

  // Calculate potential weekly revenue based on completed revenue-generating activities
  const calculateRevenueImpact = () => {
    if (!categories.length) return 0;

    // Revenue impact values for different activity types (weekly potential)
    const revenueImpacts = {
      // Google Business Profile activities
      'google_business_optimization': 450, // Better local visibility
      'google_reviews_management': 320, // Trust and conversion
      
      // Social Media activities
      'social_media_posting': 280, // Brand awareness and engagement
      'social_media_advertising': 680, // Direct advertising ROI
      
      // Online Ordering & Upselling
      'online_ordering_setup': 890, // Direct sales channel
      'menu_optimization': 340, // Higher average order value
      'upselling_strategies': 520, // Increased order value
      
      // Email Marketing
      'email_campaigns': 380, // Customer retention
      'promotional_campaigns': 450, // Direct sales impact
      
      // Loyalty & Rewards
      'loyalty_program': 420, // Customer retention value
      'rewards_system': 290, // Repeat business
      
      // Advertising
      'facebook_advertising': 720, // Paid advertising ROI
      'google_ads': 650, // Search advertising
      'promotional_offers': 380, // Sales promotions
      
      // Customer retention
      'customer_feedback': 180, // Improved service = retention
      'review_management': 220, // Reputation = more customers
    };

    let totalPotential = 0;
    let completedRevenue = 0;

    // Calculate based on completed items
    categories.forEach(category => {
      category.items.forEach(item => {
        // Map item titles/descriptions to revenue impact categories
        const itemKey = getRevenueCategory(item.title, item.description);
        const impact = revenueImpacts[itemKey] || 0;
        
        totalPotential += impact;
        
        if (item.status === 'completed') {
          completedRevenue += impact;
        }
      });
    });

    // Calculate remaining potential (what they could earn by completing remaining tasks)
    const remainingPotential = totalPotential - completedRevenue;
    
    return {
      weeklyPotential: Math.round(remainingPotential),
      completedValue: Math.round(completedRevenue),
      totalPotential: Math.round(totalPotential),
      completionPercentage: totalPotential > 0 ? Math.round((completedRevenue / totalPotential) * 100) : 0
    };
  };

  // Map checklist items to revenue categories
  const getRevenueCategory = (title, description) => {
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
    
    // Default for foundational items
    return 'google_business_optimization';
  };

  const renderStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '🔄';
      case 'not_applicable':
        return '➖';
      default:
        return '⭕';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-in-progress';
      case 'not_applicable':
        return 'status-not-applicable';
      default:
        return 'status-pending';
    }
  };

  if (loading) {
    return (
      <div className="marketing-foundations">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading Momentum Orchestrator...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="marketing-foundations">
        <div className="error-state">
          <h3>⚠️ Error Loading Checklist</h3>
          <p>{error}</p>
          <button onClick={loadChecklistData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const overallProgress = getOverallProgress();
  const foundationalCategories = categories.filter(cat => cat.type === 'foundational');
  const ongoingCategories = categories.filter(cat => cat.type === 'ongoing');

  return (
    <div className="marketing-foundations">
      <div className="section-header">
        <h2>🎯 Momentum Orchestrator</h2>
        <p>Your comprehensive restaurant marketing success system</p>
      </div>

      <div className="modern-dashboard">
        {/* Hero Analytics Section */}
        <div className="hero-analytics">
          <div className="main-score-container">
            <div className="score-visualization">
              <svg className="score-ring" width="200" height="200" viewBox="0 0 200 200">
                <defs>
                  <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#667eea" />
                    <stop offset="50%" stopColor="#764ba2" />
                    <stop offset="100%" stopColor="#f093fb" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                
                {/* Background circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="85"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="12"
                  opacity="0.3"
                />
                
                {/* Progress circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="85"
                  fill="none"
                  stroke="url(#scoreGradient)"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${(calculateOverallScore() / 100) * 534.07} 534.07`}
                  transform="rotate(-90 100 100)"
                  filter="url(#glow)"
                  className="score-progress-ring"
                />
                
                {/* Center content */}
                <text x="100" y="90" textAnchor="middle" className="score-number-svg">
                  {calculateOverallScore()}
                </text>
                <text x="100" y="115" textAnchor="middle" className="score-label-svg">
                  Marketing Score
                </text>
              </svg>
            </div>
            
            <div className="score-details">
              <h3 className="score-status-modern">
                {getScoreLabel(calculateOverallScore())}
              </h3>
              <p className="score-description-modern">
                {calculateOverallScore() === 0 && "🚀 Ready to launch your marketing journey!"}
                {calculateOverallScore() > 0 && calculateOverallScore() < 30 && "🌟 Great start! Building momentum..."}
                {calculateOverallScore() >= 30 && calculateOverallScore() < 60 && "🔥 Making solid progress!"}
                {calculateOverallScore() >= 60 && calculateOverallScore() < 80 && "💪 Strong foundation established!"}
                {calculateOverallScore() >= 80 && "🏆 Marketing excellence achieved!"}
              </p>
              
              <div className="achievement-indicator">
                <div className="achievement-dots">
                  <div className={`dot ${calculateOverallScore() >= 20 ? 'active' : ''}`}></div>
                  <div className={`dot ${calculateOverallScore() >= 40 ? 'active' : ''}`}></div>
                  <div className={`dot ${calculateOverallScore() >= 60 ? 'active' : ''}`}></div>
                  <div className={`dot ${calculateOverallScore() >= 80 ? 'active' : ''}`}></div>
                  <div className={`dot ${calculateOverallScore() >= 100 ? 'active' : ''}`}></div>
                </div>
                <span className="achievement-text">Progress Milestones</span>
              </div>
            </div>
          </div>
        </div>

        {/* Visual Progress Cards */}
        <div className="progress-cards-modern">
          <div className="progress-card-modern foundational">
            <div className="card-header-modern">
              <div className="card-icon-modern">🏗️</div>
              <div className="card-info">
                <h4>Foundation</h4>
                <span className="card-subtitle">Essential Setup</span>
              </div>
              <div className="card-percentage">
                {Math.round(overallProgress.foundational.percentage)}%
              </div>
            </div>
            
            <div className="progress-visual">
              <div className="progress-bar-modern">
                <div
                  className="progress-fill-animated foundational"
                  style={{
                    width: `${overallProgress.foundational.percentage}%`,
                    animationDelay: '0.2s'
                  }}
                ></div>
              </div>
              <div className="progress-numbers">
                <span className="completed-number">{overallProgress.foundational.completed}</span>
                <span className="divider">/</span>
                <span className="total-number">{overallProgress.foundational.total}</span>
                <span className="completed-label">tasks done</span>
              </div>
            </div>
          </div>

          <div className="progress-card-modern critical">
            <div className="card-header-modern">
              <div className="card-icon-modern">⚡</div>
              <div className="card-info">
                <h4>Critical</h4>
                <span className="card-subtitle">High Priority</span>
              </div>
              <div className="card-percentage">
                {Math.round(overallProgress.foundational.criticalPercentage)}%
              </div>
            </div>
            
            <div className="progress-visual">
              <div className="progress-bar-modern">
                <div
                  className="progress-fill-animated critical"
                  style={{
                    width: `${overallProgress.foundational.criticalPercentage}%`,
                    animationDelay: '0.4s'
                  }}
                ></div>
              </div>
              <div className="progress-numbers">
                <span className="completed-number">{overallProgress.foundational.criticalCompleted}</span>
                <span className="divider">/</span>
                <span className="total-number">{overallProgress.foundational.criticalTotal}</span>
                <span className="completed-label">critical done</span>
              </div>
            </div>
          </div>

          <div className="progress-card-modern ongoing">
            <div className="card-header-modern">
              <div className="card-icon-modern">🔄</div>
              <div className="card-info">
                <h4>Ongoing</h4>
                <span className="card-subtitle">Maintenance</span>
              </div>
              <div className="card-percentage">
                {Math.round(overallProgress.ongoing.percentage)}%
              </div>
            </div>
            
            <div className="progress-visual">
              <div className="progress-bar-modern">
                <div
                  className="progress-fill-animated ongoing"
                  style={{
                    width: `${overallProgress.ongoing.percentage}%`,
                    animationDelay: '0.6s'
                  }}
                ></div>
              </div>
              <div className="progress-numbers">
                <span className="completed-number">{overallProgress.ongoing.completed}</span>
                <span className="divider">/</span>
                <span className="total-number">{overallProgress.ongoing.total}</span>
                <span className="completed-label">ongoing done</span>
              </div>
            </div>
          </div>

          <div className="progress-card-modern revenue">
            <div className="card-header-modern">
              <div className="card-icon-modern">💰</div>
              <div className="card-info">
                <h4>Revenue Potential</h4>
                <span className="card-subtitle">Weekly Opportunity</span>
              </div>
              <div className="card-percentage">
                ${calculateRevenueImpact().weeklyPotential}
              </div>
            </div>
            
            <div className="progress-visual">
              <div className="progress-bar-modern">
                <div
                  className="progress-fill-animated revenue"
                  style={{
                    width: `${calculateRevenueImpact().completionPercentage}%`,
                    animationDelay: '0.8s'
                  }}
                ></div>
              </div>
              <div className="progress-numbers">
                <span className="completed-number">${calculateRevenueImpact().completedValue}</span>
                <span className="divider">/</span>
                <span className="total-number">${calculateRevenueImpact().totalPotential}</span>
                <span className="completed-label">revenue unlocked</span>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Recommendations */}
        <div className="smart-recommendations">
          <div className="recommendation-card">
            <div className="recommendation-icon">🎯</div>
            <div className="recommendation-content">
              <h4>Next Smart Action</h4>
              <p>
                {calculateRevenueImpact().weeklyPotential > 1000
                  ? `Complete more tasks to unlock $${calculateRevenueImpact().weeklyPotential} in weekly revenue potential!`
                  : overallProgress.foundational.criticalCompleted < overallProgress.foundational.criticalTotal
                  ? "Focus on critical items first - they have the biggest impact on your marketing success"
                  : overallProgress.foundational.completed < overallProgress.foundational.total
                  ? "Complete your foundation setup to unlock advanced marketing strategies"
                  : "Great foundation! Time to optimize with ongoing operations"
                }
              </p>
            </div>
            <div className="recommendation-action">
              <button className="action-button">
                {overallProgress.foundational.criticalCompleted < overallProgress.foundational.criticalTotal
                  ? "View Critical"
                  : "Continue Setup"
                }
              </button>
            </div>
          </div>
        </div>

        {/* Achievement Badges */}
        <div className="achievement-showcase">
          <h4 className="achievement-title">🏆 Your Achievements</h4>
          <div className="badges-grid">
            <div className={`badge ${overallProgress.foundational.completed > 0 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">🌟</div>
              <span>First Steps</span>
            </div>
            <div className={`badge ${overallProgress.foundational.criticalCompleted >= 3 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">⚡</div>
              <span>Critical Focus</span>
            </div>
            <div className={`badge ${overallProgress.foundational.percentage >= 50 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">🔥</div>
              <span>Halfway Hero</span>
            </div>
            <div className={`badge ${calculateOverallScore() >= 80 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">👑</div>
              <span>Marketing Pro</span>
            </div>
          </div>
        </div>
      </div>

      <div className="category-section">
        <h3 className="section-title">🏗️ Foundational Setup (Complete These First)</h3>
        <p className="section-description">
          Essential marketing foundations that every restaurant needs. Complete these to establish your digital presence.
        </p>
        
        {foundationalCategories.map((category) => {
          const categoryProgress = getCategoryProgress(category);
          const isExpanded = expandedCategories[category.category_id];
          
          return (
            <div key={category.category_id} className="category-container foundational">
              <div 
                className="category-header"
                onClick={() => toggleCategory(category.category_id)}
              >
                <div className="category-info">
                  <h4 className="category-title">
                    {category.icon} {category.name}
                  </h4>
                  <p className="category-description">{category.description}</p>
                </div>
                <div className="category-progress">
                  <span className="progress-text">
                    {categoryProgress.completed}/{categoryProgress.total} ({categoryProgress.percentage}%)
                  </span>
                  <div className="mini-progress-bar">
                    <div 
                      className="mini-progress-fill"
                      style={{ width: `${categoryProgress.percentage}%` }}
                    ></div>
                  </div>
                  <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                    ▼
                  </span>
                </div>
              </div>

              {isExpanded && (
                <div className="category-items">
                  {category.items.map((item) => (
                    <div key={item.item_id} className={`checklist-item ${getStatusClass(item.status)}`}>
                      <div className="checkbox-container">
                        <input
                          type="checkbox"
                          id={`item-${item.item_id}`}
                          checked={item.status === 'completed'}
                          onChange={(e) => {
                            console.log('🔧 Checkbox input onChange fired:', { itemId: item.item_id, checked: e.target.checked, currentStatus: item.status });
                            handleCheckboxChange(item.item_id, item.status);
                          }}
                          onClick={(e) => {
                            console.log('🔧 Checkbox input onClick fired:', { itemId: item.item_id, currentStatus: item.status });
                          }}
                          disabled={updatingItems[item.item_id]}
                          className="foundation-checkbox"
                        />
                        <label
                          htmlFor={`item-${item.item_id}`}
                          className="checkbox-label"
                          onClick={(e) => {
                            console.log('🔧 Checkbox label onClick fired:', { itemId: item.item_id, currentStatus: item.status });
                          }}
                        >
                          <span className="checkmark"></span>
                        </label>
                      </div>
                      
                      <div className="item-content">
                        <div className="item-header">
                          <h5 className="item-title">
                            {item.is_critical === 1 && <span className="critical-badge">CRITICAL</span>}
                            {item.title}
                            <span className="status-icon">{renderStatusIcon(item.status)}</span>
                          </h5>
                        </div>
                        
                        <p className="item-description">{item.description}</p>
                        
                        {item.external_link && (
                          <a 
                            href={item.external_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="external-link"
                          >
                            {item.link_text || 'Learn More'} →
                          </a>
                        )}

                        {item.notes && (
                          <div className="item-notes">
                            <small><strong>Notes:</strong> {item.notes}</small>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="category-section">
        <h3 className="section-title">🔄 Ongoing Operations (Maintain & Optimize)</h3>
        <p className="section-description">
          Continuous marketing activities to maintain momentum and drive growth. Focus on these after completing foundations.
        </p>
        
        {ongoingCategories.map((category) => {
          const categoryProgress = getCategoryProgress(category);
          const isExpanded = expandedCategories[category.category_id];
          
          return (
            <div key={category.category_id} className="category-container ongoing">
              <div 
                className="category-header"
                onClick={() => toggleCategory(category.category_id)}
              >
                <div className="category-info">
                  <h4 className="category-title">
                    {category.icon} {category.name}
                  </h4>
                  <p className="category-description">{category.description}</p>
                </div>
                <div className="category-progress">
                  <span className="progress-text">
                    {categoryProgress.completed}/{categoryProgress.total} ({categoryProgress.percentage}%)
                  </span>
                  <div className="mini-progress-bar">
                    <div 
                      className="mini-progress-fill"
                      style={{ width: `${categoryProgress.percentage}%` }}
                    ></div>
                  </div>
                  <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                    ▼
                  </span>
                </div>
              </div>

              {isExpanded && (
                <div className="category-items">
                  {category.items.map((item) => (
                    <div key={item.item_id} className={`checklist-item ${getStatusClass(item.status)}`}>
                      <div className="checkbox-container">
                        <input
                          type="checkbox"
                          id={`item-${item.item_id}`}
                          checked={item.status === 'completed'}
                          onChange={(e) => {
                            console.log('🔧 Checkbox input onChange fired:', { itemId: item.item_id, checked: e.target.checked, currentStatus: item.status });
                            handleCheckboxChange(item.item_id, item.status);
                          }}
                          onClick={(e) => {
                            console.log('🔧 Checkbox input onClick fired:', { itemId: item.item_id, currentStatus: item.status });
                          }}
                          disabled={updatingItems[item.item_id]}
                          className="foundation-checkbox"
                        />
                        <label
                          htmlFor={`item-${item.item_id}`}
                          className="checkbox-label"
                          onClick={(e) => {
                            console.log('🔧 Checkbox label onClick fired:', { itemId: item.item_id, currentStatus: item.status });
                          }}
                        >
                          <span className="checkmark"></span>
                        </label>
                      </div>
                      
                      <div className="item-content">
                        <div className="item-header">
                          <h5 className="item-title">
                            {item.is_critical === 1 && <span className="critical-badge">CRITICAL</span>}
                            {item.title}
                            <span className="status-icon">{renderStatusIcon(item.status)}</span>
                          </h5>
                        </div>
                        
                        <p className="item-description">{item.description}</p>
                        
                        {item.external_link && (
                          <a 
                            href={item.external_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="external-link"
                          >
                            {item.link_text || 'Learn More'} →
                          </a>
                        )}

                        {item.notes && (
                          <div className="item-notes">
                            <small><strong>Notes:</strong> {item.notes}</small>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {overallProgress.foundational.percentage === 100 && (
        <div className="celebration-message">
          <h3>🎉 Foundational Setup Complete!</h3>
          <p>
            Excellent work! You've completed all essential marketing foundations. 
            Your restaurant is now ready to focus on ongoing growth and optimization.
          </p>
        </div>
      )}

      <div className="info-section">
        <div className="info-box">
          <h3>💡 About the Momentum Orchestrator</h3>
          <p>
            This comprehensive system guides you through every aspect of restaurant marketing success. 
            Start with foundational items to establish your digital presence, then maintain momentum 
            with ongoing operational tasks.
          </p>
          <p>
            <strong>Critical items</strong> are marked with badges and should be prioritized. 
            Your progress is automatically saved and tracked across all categories.
          </p>
        </div>

        <div className="next-steps-box">
          <h3>🚀 Recommended Next Steps</h3>
          <ul>
            <li>Complete all <strong>CRITICAL</strong> foundational items first</li>
            <li>Focus on one category at a time for better results</li>
            <li>Use other Momentum tools to implement these strategies</li>
            <li>Review and update your progress regularly</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MarketingFoundations;