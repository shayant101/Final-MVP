import React, { useState, useEffect } from 'react';
import './MarketingFoundations.css';
import { checklistAPI, dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const MarketingFoundations = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [progress, setProgress] = useState({});
  const [updatingItems, setUpdatingItems] = useState({});
  const [restaurantId, setRestaurantId] = useState(null);

  // Get restaurant ID from auth context
  useEffect(() => {
    const getRestaurantData = async () => {
      try {
        if (user?.role === 'restaurant') {
          // For restaurant users, user_id IS the restaurant_id
          setRestaurantId(user.user_id);
        } else if (user?.impersonating_restaurant_id) {
          // For admin users impersonating a restaurant
          setRestaurantId(user.impersonating_restaurant_id);
        } else {
          // Fallback: get restaurant ID from dashboard API
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
  }, [restaurantId]); // eslint-disable-line react-hooks/exhaustive-deps

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


  // Removed getScoreLabel as it's no longer needed in the new design

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
    <div className="momentum-growth-starter">

      {/* Header Section - Marketing Score */}
      <div className="main-header-section">
        <div className="score-display">
          <div className="circular-progress-container">
            <svg className="circular-progress" width="200" height="200" viewBox="0 0 200 200">
              {/* Background circle */}
              <circle
                cx="100"
                cy="100"
                r="95"
                fill="none"
                stroke="rgba(96, 165, 250, 0.1)"
                strokeWidth="4"
                className="progress-bg"
              />
              {/* Progress circle */}
              <circle
                cx="100"
                cy="100"
                r="95"
                fill="none"
                stroke="url(#progressGradient)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 95}`}
                strokeDashoffset={`${2 * Math.PI * 95 * (1 - calculateOverallScore() / 100)}`}
                className="progress-circle"
                transform="rotate(-90 100 100)"
              />
              {/* Gradient definition */}
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#60a5fa" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              {/* Score text */}
              <text x="100" y="95" textAnchor="middle" className="score-number-circular">
                {calculateOverallScore()}
              </text>
              <text x="100" y="115" textAnchor="middle" className="score-label-circular">
                MARKETING SCORE
              </text>
            </svg>
          </div>
        </div>
      </div>

      {/* Progress Overview Section */}
      <div className="section-container">
        <div className="section-header-simple">
          <h2>📊 Progress Overview</h2>
        </div>
        
        <div className="unified-progress-grid">
          <div className="unified-card foundational">
            <div className="card-content">
              <div className="card-title">🏗️ Foundation</div>
              <div className="card-stats">
                <span className="big-number">{overallProgress.foundational.completed}</span>
                <span className="small-text">/ {overallProgress.foundational.total} tasks</span>
              </div>
              <div className="progress-bar-simple">
                <div className="progress-fill-simple foundational" style={{ width: `${overallProgress.foundational.percentage}%` }}></div>
              </div>
            </div>
          </div>

          <div className="unified-card critical">
            <div className="card-content">
              <div className="card-title">⚡ Critical</div>
              <div className="card-stats">
                <span className="big-number">{overallProgress.foundational.criticalCompleted}</span>
                <span className="small-text">/ {overallProgress.foundational.criticalTotal} priority</span>
              </div>
              <div className="progress-bar-simple">
                <div className="progress-fill-simple critical" style={{ width: `${overallProgress.foundational.criticalPercentage}%` }}></div>
              </div>
            </div>
          </div>

          <div className="unified-card ongoing">
            <div className="card-content">
              <div className="card-title">🔄 Ongoing</div>
              <div className="card-stats">
                <span className="big-number">{overallProgress.ongoing.completed}</span>
                <span className="small-text">/ {overallProgress.ongoing.total} ongoing</span>
              </div>
              <div className="progress-bar-simple">
                <div className="progress-fill-simple ongoing" style={{ width: `${overallProgress.ongoing.percentage}%` }}></div>
              </div>
            </div>
          </div>

          <div className="unified-card revenue">
            <div className="card-content">
              <div className="card-title">💰 Revenue</div>
              <div className="card-stats">
                <span className="big-number">${calculateRevenueImpact().completedValue}</span>
                <span className="small-text">/ ${calculateRevenueImpact().totalPotential} unlocked</span>
              </div>
              <div className="progress-bar-simple">
                <div className="progress-fill-simple revenue" style={{ width: `${calculateRevenueImpact().completionPercentage}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Next Action Section */}
      <div className="section-container">
        <div className="section-header-simple">
          <h2>🎯 Next Action</h2>
        </div>
        
        <div className="action-card-simple">
          <div className="action-content-simple">
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
            <button className="action-button-simple">
              {overallProgress.foundational.criticalCompleted < overallProgress.foundational.criticalTotal
                ? "View Critical Tasks"
                : "Continue Setup"
              }
            </button>
          </div>
        </div>
      </div>

      {/* Achievements Section */}
      <div className="section-container">
        <div className="section-header-simple">
          <h2>🏆 Achievements</h2>
        </div>
        
        <div className="achievements-grid-simple">
          <div className={`achievement-badge ${overallProgress.foundational.completed > 0 ? 'earned' : 'locked'}`}>
            <div className="badge-icon-simple">🌟</div>
            <span>First Steps</span>
          </div>
          <div className={`achievement-badge ${overallProgress.foundational.criticalCompleted >= 3 ? 'earned' : 'locked'}`}>
            <div className="badge-icon-simple">⚡</div>
            <span>Critical Focus</span>
          </div>
          <div className={`achievement-badge ${overallProgress.foundational.percentage >= 50 ? 'earned' : 'locked'}`}>
            <div className="badge-icon-simple">🔥</div>
            <span>Halfway Hero</span>
          </div>
          <div className={`achievement-badge ${calculateOverallScore() >= 80 ? 'earned' : 'locked'}`}>
            <div className="badge-icon-simple">👑</div>
            <span>Marketing Pro</span>
          </div>
        </div>
      </div>

      {/* Foundational Setup Checklist */}
      <div className="checklist-section">
        <div className="section-header glass-card">
          <h3 className="section-title">🏗️ Foundational Setup</h3>
          <p className="section-description">
            Complete these first - Essential marketing foundations that every restaurant needs.
          </p>
        </div>
        
        {foundationalCategories.map((category) => {
          const categoryProgress = getCategoryProgress(category);
          const isExpanded = expandedCategories[category.category_id];
          
          return (
            <div key={category.category_id} className="category-card glass-card">
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
                    <div key={item.item_id} className={`checklist-item glass-card ${getStatusClass(item.status)}`}>
                      <div className="checkbox-container">
                        <input
                          type="checkbox"
                          id={`item-${item.item_id}`}
                          checked={item.status === 'completed'}
                          onChange={() => handleCheckboxChange(item.item_id, item.status)}
                          disabled={updatingItems[item.item_id]}
                          className="custom-checkbox"
                        />
                        <label htmlFor={`item-${item.item_id}`} className="checkbox-label">
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

      {/* Ongoing Operations Checklist */}
      <div className="checklist-section">
        <div className="section-header glass-card">
          <h3 className="section-title">⚙️ Ongoing Operations</h3>
          <p className="section-description">
            Continuous marketing activities to maintain momentum and drive growth.
          </p>
        </div>
        
        {ongoingCategories.map((category) => {
          const categoryProgress = getCategoryProgress(category);
          const isExpanded = expandedCategories[category.category_id];
          
          return (
            <div key={category.category_id} className="category-card glass-card">
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
                    <div key={item.item_id} className={`checklist-item glass-card ${getStatusClass(item.status)}`}>
                      <div className="checkbox-container">
                        <input
                          type="checkbox"
                          id={`item-${item.item_id}`}
                          checked={item.status === 'completed'}
                          onChange={() => handleCheckboxChange(item.item_id, item.status)}
                          disabled={updatingItems[item.item_id]}
                          className="custom-checkbox"
                        />
                        <label htmlFor={`item-${item.item_id}`} className="checkbox-label">
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

      {/* Celebration Message */}
      {overallProgress.foundational.percentage === 100 && (
        <div className="celebration-card glass-card">
          <h3>🎉 Foundational Setup Complete!</h3>
          <p>
            Excellent work! You've completed all essential marketing foundations.
            Your restaurant is now ready to focus on ongoing growth and optimization.
          </p>
        </div>
      )}
    </div>
  );
};

export default MarketingFoundations;