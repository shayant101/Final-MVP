'use client';

import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { 
  BarChart3, 
  Target, 
  MessageCircle, 
  Globe, 
  FolderOpen, 
  Layout, 
  TrendingUp, 
  Code2, 
  Brain, 
  BarChart2, 
  Menu, 
  PenTool, 
  LineChart, 
  Bot, 
  BookOpen,
  Sun,
  Moon,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Eye,
  Edit,
  Trash2,
  Zap,
  Rocket,
  DollarSign,
  Award,
  Flame,
  Star,
  ChefHat,
  BarChart,
  Smartphone,
  MapPin
} from 'lucide-react';
import WebsiteBuilder from './WebsiteBuilder/WebsiteBuilder';
import TemplateGallery from './WebsiteBuilder/TemplateGallery';
import WebsiteEditor from './WebsiteBuilder/WebsiteEditor';
import MyWebsites from './WebsiteBuilder/MyWebsites';
import WebsiteAnalytics from './WebsiteBuilder/WebsiteAnalytics';
import CustomCodeEditor from './WebsiteBuilder/CustomCodeEditor';
import AIFeatures from './AIFeatures';
import AIFeaturesLanding from './AIFeaturesLanding';
import AIAnalytics from './AIAnalytics';
import AIAssistant from './AIAssistant';
import Orchestrator from './Orchestrator';
import GoogleProfileGrader from './GoogleProfileGrader';
// import GetNewCustomers from './GetNewCustomers';
// import BringBackRegulars from './BringBackRegulars';
// import MarketingFoundations from './MarketingFoundations';
import './RestaurantDashboard.css';

interface RestaurantDashboardProps {
  setActiveTab: (tab: string) => void;
}

interface DashboardData {
  restaurant: {
    name: string;
    email: string;
    status: string;
  };
  performanceSnapshot: {
    period: string;
    newCustomersAcquired: number;
    customersReengaged: number;
  };
  activeCampaigns: Array<{
    campaign_id: string;
    name: string;
    campaign_type: string;
    status: string;
  }>;
  momentumMetrics?: {
    marketingScore: number;
    weeklyRevenuePotential: number;
    completedRevenue: number;
    totalPotential: number;
    foundationalProgress?: {
      percentage: number;
    };
    ongoingProgress?: {
      percentage: number;
    };
  };
}

const RestaurantDashboard: React.FC<RestaurantDashboardProps> = ({ setActiveTab }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('overview');
  const [orchestratorViewMode, setOrchestratorViewMode] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();

  useEffect(() => {
    fetchDashboardData();
    // Check URL parameters for initial view
    const urlParams = new URLSearchParams(window.location.search);
    const viewParam = urlParams.get('view');
    if (viewParam) {
      setActiveView(viewParam);
    }
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getRestaurantDashboard();
      setDashboardData(data);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };


  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  const { restaurant, performanceSnapshot, activeCampaigns } = dashboardData!;

  return (
    <div className="restaurant-dashboard">
      {/* Left Sidebar Navigation */}
      <div className={`restaurant-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-title">
            {!sidebarCollapsed && (
              <>
                <h2>{restaurant.name}</h2>
                <p>Growth Command Center</p>
              </>
            )}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={toggleSidebar}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
{sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        <nav className="sidebar-nav">
          {/* Dashboard Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">Dashboard</div>}
            <button
              className={`nav-item ${activeView === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveView('overview')}
              title="Dashboard Overview"
            >
              <span className="nav-icon"><BarChart3 size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Dashboard Overview</span>}
            </button>
          </div>

          {/* Marketing Tools Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">Marketing Tools</div>}
            <button
              className={`nav-item ${activeView === 'get-new-customers' ? 'active' : ''}`}
              onClick={() => setActiveView('get-new-customers')}
              title="Get New Customers"
            >
              <span className="nav-icon"><Target size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Get New Customers</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'bring-back-regulars' ? 'active' : ''}`}
              onClick={() => setActiveView('bring-back-regulars')}
              title="Bring Back Regulars"
            >
              <span className="nav-icon"><MessageCircle size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Bring Back Regulars</span>}
            </button>
            <button
              className={`nav-item ${activeView === 'website-builder' ? 'active' : ''}`}
              onClick={() => setActiveView('website-builder')}
              title="Website Builder"
            >
              <span className="nav-icon"><Globe size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Website Builder</span>}
            </button>
            {!sidebarCollapsed && (activeView === 'website-builder' || activeView === 'templates' || activeView === 'edit' || activeView === 'my-websites' || activeView === 'website-analytics' || activeView === 'code-editor') && (
              <div className="nav-sub-items">
                <button
                  className={`nav-sub-item ${activeView === 'my-websites' ? 'active' : ''}`}
                  onClick={() => setActiveView('my-websites')}
                  title="My Websites"
                >
                  <span className="nav-sub-icon"><FolderOpen size={16} /></span>
                  <span className="nav-sub-label">My Websites</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'templates' ? 'active' : ''}`}
                  onClick={() => setActiveView('templates')}
                  title="Template Gallery"
                >
                  <span className="nav-sub-icon"><Layout size={16} /></span>
                  <span className="nav-sub-label">Template Gallery</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'website-analytics' ? 'active' : ''}`}
                  onClick={() => setActiveView('website-analytics')}
                  title="Website Analytics"
                >
                  <span className="nav-sub-icon"><TrendingUp size={16} /></span>
                  <span className="nav-sub-label">Website Analytics</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'code-editor' ? 'active' : ''}`}
                  onClick={() => setActiveView('code-editor')}
                  title="Custom Code Editor"
                >
                  <span className="nav-sub-icon"><Code2 size={16} /></span>
                  <span className="nav-sub-label">Custom Code Editor</span>
                </button>
              </div>
            )}
            <button
              className={`nav-item ${activeView === 'orchestrator' ? 'active' : ''}`}
              onClick={() => setActiveView('orchestrator')}
              title="Orchestrator"
            >
              <span className="nav-icon"><BookOpen size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Orchestrator</span>}
            </button>
          </div>

          {/* AI Features Section */}
          <div className="nav-section">
            {!sidebarCollapsed && <div className="nav-section-title">AI Features</div>}
            <button
              className={`nav-item ${activeView === 'ai-features' ? 'active' : ''}`}
              onClick={() => setActiveView('ai-features')}
              title="AI Features"
            >
              <span className="nav-icon"><Brain size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">AI Features</span>}
            </button>
            {!sidebarCollapsed && (activeView === 'ai-features' || activeView === 'digital-presence-grader' || activeView === 'google-profile-grader' || activeView === 'menu-optimizer' || activeView === 'content-creator' || activeView === 'ai-analytics' || activeView === 'ai-assistant') && (
              <div className="nav-sub-items">
                <button
                  className={`nav-sub-item ${activeView === 'digital-presence-grader' || activeView === 'google-profile-grader' ? 'active' : ''}`}
                  onClick={() => setActiveView('digital-presence-grader')}
                  title="Digital Presence Grader"
                >
                  <span className="nav-sub-icon"><BarChart2 size={16} /></span>
                  <span className="nav-sub-label">Digital Presence Grader</span>
                </button>
                {(activeView === 'digital-presence-grader' || activeView === 'google-profile-grader') && (
                  <div className="nav-sub-sub-items">
                    <button
                      className={`nav-sub-sub-item ${activeView === 'google-profile-grader' ? 'active' : ''}`}
                      onClick={() => setActiveView('google-profile-grader')}
                      title="Google Profile Grader"
                    >
                      <span className="nav-sub-sub-icon"><MapPin size={14} /></span>
                      <span className="nav-sub-sub-label">Google Profile</span>
                    </button>
                  </div>
                )}
                <button
                  className={`nav-sub-item ${activeView === 'menu-optimizer' ? 'active' : ''}`}
                  onClick={() => setActiveView('menu-optimizer')}
                  title="Smart Menu Optimizer"
                >
                  <span className="nav-sub-icon"><Menu size={16} /></span>
                  <span className="nav-sub-label">Smart Menu Optimizer</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'content-creator' ? 'active' : ''}`}
                  onClick={() => setActiveView('content-creator')}
                  title="Content Creator"
                >
                  <span className="nav-sub-icon"><PenTool size={16} /></span>
                  <span className="nav-sub-label">Content Creator</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'ai-analytics' ? 'active' : ''}`}
                  onClick={() => setActiveView('ai-analytics')}
                  title="AI Analytics"
                >
                  <span className="nav-sub-icon"><LineChart size={16} /></span>
                  <span className="nav-sub-label">AI Analytics</span>
                </button>
                <button
                  className={`nav-sub-item ${activeView === 'ai-assistant' ? 'active' : ''}`}
                  onClick={() => setActiveView('ai-assistant')}
                  title="AI Assistant"
                >
                  <span className="nav-sub-icon"><Bot size={16} /></span>
                  <span className="nav-sub-label">AI Assistant</span>
                </button>
              </div>
            )}
          </div>

          {/* Account Section */}
          <div className="nav-section logout-section">
            <button
              className="nav-item theme-toggle"
              onClick={toggleTheme}
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              <span className="nav-icon">{isDark ? <Sun size={18} /> : <Moon size={18} />}</span>
              {!sidebarCollapsed && <span className="nav-label">{isDark ? 'Light Mode' : 'Dark Mode'}</span>}
            </button>
            <button
              className="nav-item logout-button"
              onClick={handleLogout}
              title="Logout"
            >
              <span className="nav-icon"><LogOut size={18} /></span>
              {!sidebarCollapsed && <span className="nav-label">Logout</span>}
            </button>
          </div>
        </nav>
      </div>

      {/* Main Content Area */}
      <div className={`restaurant-main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Header */}
        <div className="main-header">
          <div className="header-title">
            <h1>
              {activeView === 'overview' && 'Your Growth Command Center'}
              {activeView === 'get-new-customers' && 'Get New Customers'}
              {activeView === 'bring-back-regulars' && 'Bring Back Regulars'}
              {activeView === 'website-builder' && 'Website Builder'}
              {activeView === 'my-websites' && 'My Websites'}
              {activeView === 'templates' && 'Template Gallery'}
              {activeView === 'website-analytics' && 'Website Analytics'}
              {activeView === 'code-editor' && 'Custom Code Editor'}
              {activeView === 'orchestrator' && 'Marketing Command Center'}
              {activeView === 'edit' && 'Website Editor'}
              {activeView === 'ai-features' && 'AI Features'}
              {activeView === 'digital-presence-grader' && 'Digital Presence Grader'}
              {activeView === 'google-profile-grader' && 'Google Profile Grader'}
              {activeView === 'menu-optimizer' && 'Smart Menu Optimizer'}
              {activeView === 'content-creator' && 'Content Creator'}
              {activeView === 'ai-analytics' && 'AI Analytics'}
              {activeView === 'ai-assistant' && 'AI Assistant'}
            </h1>
            <p>
              {activeView === 'overview' && `Welcome back to ${restaurant.name}!`}
              {activeView === 'get-new-customers' && 'Launch Facebook ads to attract new customers'}
              {activeView === 'bring-back-regulars' && 'Send SMS campaigns to re-engage customers'}
              {activeView === 'website-builder' && 'Create stunning AI-powered restaurant websites'}
              {activeView === 'my-websites' && 'Manage and view all your created websites'}
              {activeView === 'templates' && 'Choose from professionally designed restaurant templates'}
              {activeView === 'website-analytics' && 'Track your website performance and visitor insights'}
              {activeView === 'code-editor' && 'Advanced HTML, CSS, and JavaScript editing capabilities'}
              {activeView === 'orchestrator' && 'Your marketing command center with at-a-glance insights and actionable next steps'}
              {activeView === 'edit' && 'Edit your website content and design'}
              {activeView === 'ai-features' && 'Unlock AI-powered growth tools'}
              {activeView === 'digital-presence-grader' && 'Analyze and grade your restaurant\'s digital presence'}
              {activeView === 'google-profile-grader' && 'Analyze and grade your Google Business Profile'}
              {activeView === 'menu-optimizer' && 'Optimize menu performance and pricing strategies'}
              {activeView === 'content-creator' && 'AI-powered image enhancement and content generation'}
              {activeView === 'ai-analytics' && 'Track AI feature usage and performance insights'}
              {activeView === 'ai-assistant' && 'Chat with your AI marketing assistant'}
            </p>
          </div>
          
          {/* Header Actions - Only show for orchestrator view */}
          {activeView === 'orchestrator' && (
            <div className="header-actions">
              <div className="view-toggle-group">
                <button 
                  className={`header-toggle-btn ${orchestratorViewMode === 'overview' ? 'active' : ''}`}
                  onClick={() => setOrchestratorViewMode('overview')}
                >
                  Overview
                </button>
                <button 
                  className={`header-toggle-btn ${orchestratorViewMode === 'details' ? 'active' : ''}`}
                  onClick={() => setOrchestratorViewMode('details')}
                >
                  Details
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="content-area">
          {activeView === 'overview' && (
            <div className="overview-content">
              <div className="dashboard-grid">
                {/* Analytics */}
                <div className="dashboard-card performance-card">
                  <div className="card-header">
                    <h3><BarChart className="inline mr-2" size={18} />Analytics</h3>
                    <span className="period">{performanceSnapshot.period}</span>
                  </div>
                  <div className="performance-metrics">
                    <div className="metric">
                      <div className="metric-value">{performanceSnapshot.newCustomersAcquired}</div>
                      <div className="metric-label">New Customers Acquired</div>
                    </div>
                    <div className="metric">
                      <div className="metric-value">{performanceSnapshot.customersReengaged}</div>
                      <div className="metric-label">Customers Re-engaged</div>
                    </div>
                  </div>
                  
                  {/* Compact Performance Insights */}
                  <div className="performance-insights-compact">
                    <div className="compact-stats">
                      <div className="compact-stat">
                        <span className="compact-value">${Math.round((performanceSnapshot.newCustomersAcquired * 45) + (performanceSnapshot.customersReengaged * 32))}</span>
                        <span className="compact-label">Revenue Generated</span>
                      </div>
                      <div className="compact-stat">
                        <span className="compact-value">{performanceSnapshot.newCustomersAcquired + performanceSnapshot.customersReengaged}</span>
                        <span className="compact-label">Total Customers</span>
                      </div>
                      <div className="compact-stat">
                        <span className="compact-value">{Math.round(((performanceSnapshot.newCustomersAcquired + performanceSnapshot.customersReengaged) / 25) * 100)}%</span>
                        <span className="compact-label">Growth Rate</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Campaigns */}
                <div className="dashboard-card campaigns-card">
                  <div className="card-header">
                    <h3><Rocket className="inline mr-2" size={18} />Campaigns</h3>
                    <button
                      className="view-all-button"
                      onClick={() => setActiveView('get-new-customers')}
                    >
                      View All
                    </button>
                  </div>
                  <div className="campaigns-list">
                    {activeCampaigns.length > 0 ? (
                      activeCampaigns.map(campaign => (
                        <div key={campaign.campaign_id} className="campaign-item">
                          <div className="campaign-info">
                            <div className="campaign-name">{campaign.name}</div>
                            <div className="campaign-type">
                              {campaign.campaign_type === 'ad' ? <><Smartphone className="inline mr-1" size={14} />Facebook Ad</> : <><MessageCircle className="inline mr-1" size={14} />SMS Campaign</>}
                            </div>
                          </div>
                          <div className="campaign-status">
                            <span className={`status-badge ${campaign.status}`}>
                              {campaign.status}
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="growth-potential-visual">
                        <div className="visual-header">
                          <p>Your progress vs campaign potential</p>
                        </div>
                        <div className="line-chart">
                          <div className="chart-container">
                            <svg className="line-graph" viewBox="0 0 280 100" preserveAspectRatio="xMidYMid meet">
                              {/* Grid lines */}
                              <defs>
                                <pattern id="grid" width="56" height="20" patternUnits="userSpaceOnUse">
                                  <path d="M 56 0 L 0 0 0 20" fill="none" stroke="rgba(1, 90, 246, 0.1)" strokeWidth="0.5"/>
                                </pattern>
                              </defs>
                              <rect width="280" height="100" fill="url(#grid)" />
                              
                              {/* Current progress line (solid) */}
                              <polyline
                                fill="none"
                                stroke="var(--color-brand-blue)"
                                strokeWidth="2"
                                points="20,80 76,70 132,75 188,65 244,60"
                                className="progress-line"
                              />
                              
                              {/* Campaign potential line (dotted) */}
                              <polyline
                                fill="none"
                                stroke="rgba(34, 197, 94, 0.8)"
                                strokeWidth="2"
                                strokeDasharray="4,3"
                                points="20,80 76,60 132,45 188,30 244,20"
                                className="potential-line"
                              />
                              
                              {/* Data points for current progress */}
                              <circle cx="20" cy="80" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="76" cy="70" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="132" cy="75" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="188" cy="65" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              <circle cx="244" cy="60" r="3" fill="var(--color-brand-blue)" className="data-point" />
                              
                              {/* Data points for potential */}
                              <circle cx="244" cy="20" r="3" fill="rgba(34, 197, 94, 0.8)" className="potential-point" />
                            </svg>
                            <div className="chart-labels">
                              <span>Jan</span>
                              <span>Feb</span>
                              <span>Mar</span>
                              <span>Apr</span>
                              <span>May</span>
                            </div>
                            <div className="chart-legend">
                              <div className="legend-item">
                                <div className="legend-line solid"></div>
                                <span>Current Progress</span>
                              </div>
                              <div className="legend-item">
                                <div className="legend-line dotted"></div>
                                <span>With Campaigns</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="growth-stats">
                          <div className="stat-visual">
                            <span className="stat-number">7%</span>
                            <span className="stat-text">Current Growth</span>
                          </div>
                          <div className="stat-visual">
                            <span className="stat-number">29%</span>
                            <span className="stat-text">Potential Growth</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* AI Marketing Features */}
                <div className="dashboard-card ai-marketing-card">
                  {/* Shine layers for enhanced glassmorphism */}
                  <div className="shine-layer-1"></div>
                  <div className="shine-layer-2"></div>
                  <div className="edge-highlight"></div>
                  
                  <div className="card-header">
                    <h3><Brain className="inline mr-2" size={18} />AI Marketing</h3>
                    <span className="period">Powered by AI</span>
                  </div>
                  <div className="ai-marketing-content">
                    <div className="ai-marketing-icon">
                      <div className="ai-brain-animation"><Brain size={24} /></div>
                    </div>
                    <div className="ai-marketing-text">
                      <h4>Unlock AI-Powered Growth</h4>
                      <p>Discover intelligent tools to optimize your menu, grade your digital presence, and generate compelling marketing content.</p>
                    </div>
                    <button
                      className="ai-marketing-cta"
                      onClick={() => window.location.href = '/ai-features'}
                    >
                      Explore AI Features
                      <span className="cta-arrow">→</span>
                    </button>
                  </div>
                </div>

                {/* Quick Links */}
                <div className="dashboard-card quick-links-card">
                  <div className="card-header">
                    <h3><Zap className="inline mr-2" size={18} />Quick Actions</h3>
                  </div>
                  <div className="quick-links">
                    <button
                      className="quick-link-button primary"
                      onClick={() => setActiveView('get-new-customers')}
                    >
                      <span className="button-icon"><Target size={18} /></span>
                      Launch New Ad
                    </button>
                    <button
                      className="quick-link-button secondary"
                      onClick={() => setActiveView('bring-back-regulars')}
                    >
                      <span className="button-icon"><MessageCircle size={18} /></span>
                      Send SMS Campaign
                    </button>
                    <button
                      className="quick-link-button website-builder"
                      onClick={() => setActiveView('website-builder')}
                    >
                      <span className="button-icon"><Globe size={18} /></span>
                      Build Website
                    </button>
                    <button
                      className="quick-link-button tertiary"
                      onClick={() => setActiveView('marketing-foundations')}
                    >
                      <span className="button-icon"><BookOpen size={18} /></span>
                      Review Marketing Foundations
                    </button>
                  </div>
                </div>

                {/* Marketing Score Card */}
                <div className="dashboard-card marketing-score-card">
                  <div className="card-header">
                    <h3><Target className="inline mr-2" size={18} />Marketing Score</h3>
                    <span className="period">Health Check</span>
                  </div>
                  <div className="marketing-score-content">
                    <div className="score-circle">
                      <svg className="score-ring" width="100" height="100" viewBox="0 0 100 100">
                        <defs>
                          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#1E40AF" />
                            <stop offset="100%" stopColor="#3B82F6" />
                          </linearGradient>
                        </defs>
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#E5E7EB"
                          strokeWidth="8"
                          opacity="0.3"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="url(#scoreGradient)"
                          strokeWidth="8"
                          strokeLinecap="round"
                          strokeDasharray={`${((dashboardData?.momentumMetrics?.marketingScore || 0) / 100) * 251.33} 251.33`}
                          transform="rotate(-90 50 50)"
                          className="score-progress-ring"
                        />
                      </svg>
                      <div className="score-content">
                        <div className="score-value">{dashboardData?.momentumMetrics?.marketingScore || 0}</div>
                        <div className="score-label">Score</div>
                      </div>
                    </div>
                    <div className="score-status">
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 80 && <><Award className="inline mr-1" size={16} />Excellent</>}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 60 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 80 && <><TrendingUp className="inline mr-1" size={16} />Strong</>}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 40 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 60 && <><Flame className="inline mr-1" size={16} />Growing</>}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) >= 20 && (dashboardData?.momentumMetrics?.marketingScore || 0) < 40 && <><Star className="inline mr-1" size={16} />Building</>}
                      {(dashboardData?.momentumMetrics?.marketingScore || 0) < 20 && <><Rocket className="inline mr-1" size={16} />Starting</>}
                    </div>
                    <div className="progress-bars">
                      <div className="progress-item">
                        <div className="progress-info">
                          <span className="progress-name">Foundation</span>
                          <span className="progress-percent">{dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0}%</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill foundation"
                            style={{ width: `${dashboardData?.momentumMetrics?.foundationalProgress?.percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="progress-item">
                        <div className="progress-info">
                          <span className="progress-name">Ongoing</span>
                          <span className="progress-percent">{dashboardData?.momentumMetrics?.ongoingProgress?.percentage || 0}%</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill ongoing"
                            style={{ width: `${dashboardData?.momentumMetrics?.ongoingProgress?.percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Revenue Potential Card */}
                <div className="dashboard-card revenue-potential-card">
                  <div className="card-header">
                    <h3><DollarSign className="inline mr-2" size={18} />Revenue</h3>
                    <span className="period">Weekly Opportunity</span>
                  </div>
                  <div className="revenue-potential-content">
                    <div className="revenue-header">
                      <div className="revenue-icon"><DollarSign size={24} /></div>
                      <div className="revenue-trend">
                        {(dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0) > 0 ? <TrendingUp size={20} /> : <BarChart size={20} />}
                      </div>
                    </div>
                    <div className="revenue-value">${dashboardData?.momentumMetrics?.weeklyRevenuePotential || 0}</div>
                    <div className="revenue-label">Weekly Revenue Potential</div>
                    <div className="revenue-bar">
                      <div
                        className="revenue-fill"
                        style={{
                          width: `${Math.min(((dashboardData?.momentumMetrics?.completedRevenue || 0) / Math.max((dashboardData?.momentumMetrics?.totalPotential || 1), 1)) * 100, 100)}%`
                        }}
                      ></div>
                    </div>
                    <div className="revenue-description">
                      ${dashboardData?.momentumMetrics?.completedRevenue || 0} unlocked of ${dashboardData?.momentumMetrics?.totalPotential || 0} total
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Get New Customers Tab */}
          {activeView === 'get-new-customers' && (
            <div className="get-new-customers-content">
              <div className="placeholder-content">
                <h2><Target className="inline mr-2" size={24} />Get New Customers</h2>
                <p>Launch Facebook ads to attract new customers to your restaurant.</p>
                <button className="btn-primary" onClick={() => window.location.href = '/get-new-customers'}>
                  Go to Get New Customers
                </button>
              </div>
            </div>
          )}

          {/* Bring Back Regulars Tab */}
          {activeView === 'bring-back-regulars' && (
            <div className="bring-back-regulars-content">
              <div className="placeholder-content">
                <h2><MessageCircle className="inline mr-2" size={24} />Bring Back Regulars</h2>
                <p>Send SMS campaigns to re-engage your past customers.</p>
                <button className="btn-primary" onClick={() => window.location.href = '/bring-back-regulars'}>
                  Go to Bring Back Regulars
                </button>
              </div>
            </div>
          )}

          {/* Website Builder Tab */}
          {activeView === 'website-builder' && (
            <div className="website-builder-content">
              <WebsiteBuilder />
            </div>
          )}

          {/* Template Gallery Tab */}
          {activeView === 'templates' && (
            <div className="templates-content">
              <TemplateGallery />
            </div>
          )}

          {/* Website Editor Tab */}
          {activeView === 'edit' && (
            <div className="website-editor-content">
              <WebsiteEditor id={new URLSearchParams(window.location.search).get('id') || ''} />
            </div>
          )}

          {/* AI Features Tab */}
          {activeView === 'ai-features' && (
            <div className="ai-features-content">
              <AIFeaturesLanding />
            </div>
          )}

          {/* Digital Presence Grader Tab */}
          {activeView === 'digital-presence-grader' && (
            <div className="digital-presence-grader-content">
              <AIFeatures />
            </div>
          )}

          {/* Google Profile Grader Tab */}
          {activeView === 'google-profile-grader' && (
            <div className="google-profile-grader-content">
              <GoogleProfileGrader 
                restaurantName={dashboardData?.restaurant?.name || ''}
                googleBusinessUrl={dashboardData?.restaurant?.google_business_url || ''}
              />
            </div>
          )}

          {/* Menu Optimizer Tab */}
          {activeView === 'menu-optimizer' && (
            <div className="menu-optimizer-content">
              <AIFeatures />
            </div>
          )}

          {/* Content Creator Tab */}
          {activeView === 'content-creator' && (
            <div className="content-creator-content">
              <AIFeatures />
            </div>
          )}

          {/* AI Analytics Tab */}
          {activeView === 'ai-analytics' && (
            <div className="ai-analytics-content">
              <AIAnalytics />
            </div>
          )}

          {/* AI Assistant Tab */}
          {activeView === 'ai-assistant' && (
            <div className="ai-assistant-content">
              <div className="ai-assistant-main">
                <h2><Bot className="inline mr-2" size={24} />AI Assistant</h2>
                <p>Your personal AI marketing assistant is always available to help with questions, suggestions, and guidance.</p>
                <div className="assistant-placeholder">
                  <AIAssistant />
                  <div className="assistant-info">
                    <h3>How to use your AI Assistant:</h3>
                    <ul>
                      <li>Click the floating AI button to start a conversation</li>
                      <li>Ask about marketing strategies, campaign optimization, or general business questions</li>
                      <li>Get personalized recommendations based on your restaurant's data</li>
                      <li>Receive step-by-step guidance for complex tasks</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* My Websites Tab */}
          {activeView === 'my-websites' && (
            <div className="my-websites-content">
              <MyWebsites />
            </div>
          )}

          {/* Website Analytics Tab */}
          {activeView === 'website-analytics' && (
            <div className="website-analytics-content">
              <WebsiteAnalytics />
            </div>
          )}

          {/* Custom Code Editor Tab */}
          {activeView === 'code-editor' && (
            <div className="code-editor-content">
              <CustomCodeEditor />
            </div>
          )}

          {/* Orchestrator Tab */}
          {activeView === 'orchestrator' && (
            <Orchestrator viewMode={orchestratorViewMode} />
          )}

        </div>
      </div>
    </div>
  );
};

export default RestaurantDashboard;