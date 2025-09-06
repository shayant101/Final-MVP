'use client';

import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import RestaurantDashboard from './RestaurantDashboard';
import AdminDashboard from './AdminDashboard';
import GetNewCustomers from './GetNewCustomers';
import BringBackRegulars from './BringBackRegulars';
import MarketingFoundations from './MarketingFoundations';
import LoadingScreen from './LoadingScreen';

const MainDashboard = () => {
  const { user, isAdmin, isImpersonating, endImpersonation, logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleTabChange = async (newTab: string) => {
    if (newTab === activeTab) return;
    
    setIsTransitioning(true);
    
    // Simulate loading time for tab transition
    await new Promise(resolve => setTimeout(resolve, 800));
    
    setActiveTab(newTab);
    setIsTransitioning(false);
  };

  const handleLogout = () => {
    logout();
  };

  const handleBackToDashboard = () => {
    handleTabChange('dashboard');
  };

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        // If admin is impersonating, show restaurant dashboard
        // If admin is not impersonating, show admin dashboard
        // If restaurant user, show restaurant dashboard
        return (isAdmin && !isImpersonating) ? (
          <AdminDashboard />
        ) : (
          <RestaurantDashboard setActiveTab={handleTabChange} />
        );
      case 'get-new-customers':
        return <GetNewCustomers onBackToDashboard={handleBackToDashboard} />;
      case 'bring-back-regulars':
        return <BringBackRegulars onBackToDashboard={handleBackToDashboard} />;
      case 'marketing-foundations':
        return <MarketingFoundations />;
      default:
        return (isAdmin && !isImpersonating) ? (
          <AdminDashboard />
        ) : (
          <RestaurantDashboard setActiveTab={handleTabChange} />
        );
    }
  };

  const handleEndImpersonation = async () => {
    try {
      await endImpersonation();
      // Reset to dashboard tab after ending impersonation
      setActiveTab('dashboard');
    } catch (error) {
      console.error('Failed to end impersonation:', error);
    }
  };

  if (isTransitioning) {
    return <LoadingScreen />;
  }

  return (
    <div className="App">
      {/* Impersonation Banner */}
      {isImpersonating && (
        <div className="impersonation-banner" style={{
          backgroundColor: '#ff6b35',
          color: 'white',
          padding: '10px 20px',
          textAlign: 'center',
          fontWeight: 'bold',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>🎭 IMPERSONATING: {user?.impersonating_restaurant?.name || 'Restaurant'}</span>
          <button
            onClick={handleEndImpersonation}
            style={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: '1px solid white',
              color: 'white',
              padding: '5px 15px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            End Impersonation
          </button>
        </div>
      )}

      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            {(activeTab === 'marketing-foundations' ||
              activeTab === 'get-new-customers' ||
              activeTab === 'bring-back-regulars') && (
              <button
                className="back-to-dashboard-button"
                onClick={handleBackToDashboard}
                aria-label="Back to Dashboard"
              >
                ← Back to Dashboard
              </button>
            )}
          </div>
          <div className="header-text">
            <h1 className="app-title">Uplit</h1>
            <p className="app-subtitle">
              {isImpersonating
                ? `Impersonating: ${user?.impersonating_restaurant?.name || 'Restaurant'}`
                : isAdmin
                ? 'Platform Administration'
                : 'AI-Powered Restaurant Marketing Platform'
              }
            </p>
          </div>
          <div className="header-actions">
            <button
              className="dark-mode-toggle"
              onClick={toggleTheme}
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? '☀️' : '🌙'}
            </button>
            <button
              className="logout-button"
              onClick={handleLogout}
              aria-label="Logout"
            >
              🚪 Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation bar removed as requested */}

      <main className="app-main">
        {renderActiveComponent()}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Uplit - Helping restaurants grow one customer at a time</p>
      </footer>
    </div>
  );
};

export default MainDashboard;