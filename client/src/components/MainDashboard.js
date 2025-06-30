import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import RestaurantDashboard from './RestaurantDashboard';
import AdminDashboard from './AdminDashboard';
import GetNewCustomers from './GetNewCustomers';
import BringBackRegulars from './BringBackRegulars';
import MarketingFoundations from './MarketingFoundations';

const MainDashboard = () => {
  const { user, isAdmin, isImpersonating, endImpersonation, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  // Update localStorage and apply dark mode class when isDarkMode changes
  React.useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleLogout = () => {
    logout();
  };

  const handleBackToDashboard = () => {
    setActiveTab('dashboard');
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
          <RestaurantDashboard setActiveTab={setActiveTab} />
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
          <RestaurantDashboard setActiveTab={setActiveTab} />
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

  return (
    <div className={`App ${isDarkMode ? 'dark-mode' : ''}`}>
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
                : `Welcome back, ${user?.restaurant?.name || user?.email}!`
              }
            </p>
          </div>
          <div className="header-actions">
            <button
              className="dark-mode-toggle"
              onClick={toggleDarkMode}
              aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDarkMode ? '☀️' : '🌙'}
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