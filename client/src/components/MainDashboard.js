import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import RestaurantDashboard from './RestaurantDashboard';
import AdminDashboard from './AdminDashboard';
import GetNewCustomers from './GetNewCustomers';
import BringBackRegulars from './BringBackRegulars';
import MarketingFoundations from './MarketingFoundations';
import Navigation from './Navigation';

const MainDashboard = () => {
  const { user, isAdmin, isRestaurant, logout } = useAuth();
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

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        return isAdmin ? (
          <AdminDashboard />
        ) : (
          <RestaurantDashboard setActiveTab={setActiveTab} />
        );
      case 'get-new-customers':
        return <GetNewCustomers />;
      case 'bring-back-regulars':
        return <BringBackRegulars />;
      case 'marketing-foundations':
        return <MarketingFoundations />;
      default:
        return isAdmin ? (
          <AdminDashboard />
        ) : (
          <RestaurantDashboard setActiveTab={setActiveTab} />
        );
    }
  };

  return (
    <div className={`App ${isDarkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1 className="app-title">Momentum Growth Starter</h1>
            <p className="app-subtitle">
              {isAdmin 
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

      {/* Only show navigation for restaurant users or when not on dashboard */}
      {(isRestaurant && activeTab !== 'dashboard') && (
        <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      )}

      <main className="app-main">
        {renderActiveComponent()}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Momentum Growth Starter - Helping restaurants grow one customer at a time</p>
      </footer>
    </div>
  );
};

export default MainDashboard;