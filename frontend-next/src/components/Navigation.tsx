import React from 'react';
import './Navigation.css';

const Navigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    {
      id: 'get-new-customers',
      label: 'Get New Customers',
      icon: '🎯',
      description: 'Launch Facebook ads to attract new diners'
    },
    {
      id: 'bring-back-regulars',
      label: 'Bring Back Regulars',
      icon: '📱',
      description: 'Send SMS campaigns to lapsed customers'
    },
    {
      id: 'marketing-foundations',
      label: 'Momentum Orchestrator',
      icon: '📋',
      description: 'Essential marketing setup checklist'
    }
  ];

  return (
    <nav className="navigation">
      <div className="nav-container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <div className="nav-tab-icon">{tab.icon}</div>
            <div className="nav-tab-content">
              <h3 className="nav-tab-label">{tab.label}</h3>
              <p className="nav-tab-description">{tab.description}</p>
            </div>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default Navigation;