import React, { useState, useEffect } from 'react';
import './App.css';
import Navigation from './components/Navigation';
import GetNewCustomers from './components/GetNewCustomers';
import BringBackRegulars from './components/BringBackRegulars';
import MarketingFoundations from './components/MarketingFoundations';

function App() {
  const [activeTab, setActiveTab] = useState('get-new-customers');
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Load dark mode preference from localStorage on component mount
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode) {
      setIsDarkMode(JSON.parse(savedDarkMode));
    }
  }, []);

  // Update localStorage and apply dark mode class when isDarkMode changes
  useEffect(() => {
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

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'get-new-customers':
        return <GetNewCustomers />;
      case 'bring-back-regulars':
        return <BringBackRegulars />;
      case 'marketing-foundations':
        return <MarketingFoundations />;
      default:
        return <GetNewCustomers />;
    }
  };

  return (
    <div className={`App ${isDarkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1 className="app-title">Momentum Growth Starter</h1>
            <p className="app-subtitle">Launch your restaurant's marketing campaigns in minutes</p>
          </div>
          <button
            className="dark-mode-toggle"
            onClick={toggleDarkMode}
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="app-main">
        {renderActiveComponent()}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Momentum Growth Starter - Helping restaurants grow one customer at a time</p>
      </footer>
    </div>
  );
}

export default App;
