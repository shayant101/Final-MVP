import React from 'react';
import { Rocket, Smartphone, TrendingUp } from 'lucide-react';
import './ScoreBreakdown.css';

const ScoreBreakdown = ({ websiteData, onClose }) => {
  if (!websiteData) return null;

  const { score, grade, issues, recommendations, validation_data } = websiteData;

  // Calculate component scores
  const getComponentScore = (name, points, maxPoints) => ({
    name,
    points,
    maxPoints,
    percentage: Math.round((points / maxPoints) * 100)
  });

  const components = [
    getComponentScore('Website Accessibility', validation_data?.accessible ? 30 : 0, 30),
    getComponentScore('SSL Security', validation_data?.has_ssl ? 15 : 0, 15),
    getComponentScore('Loading Speed', validation_data?.response_time <= 2 ? 15 : validation_data?.response_time <= 4 ? 10 : 5, 15),
    getComponentScore('Basic Setup', validation_data?.accessible ? 5 : 0, 5),
    getComponentScore('Online Ordering', getOrderingScore(recommendations, issues), 25)
  ];

  function getOrderingScore(recommendations, issues) {
    const hasOrderingIssue = issues?.some(issue => issue.toLowerCase().includes('order'));
    const hasOrderingRec = recommendations?.some(rec => rec.toLowerCase().includes('order'));
    
    if (hasOrderingIssue || hasOrderingRec) {
      return 0; // No online ordering detected
    }
    return 15; // Has online ordering (medium confidence gets 10, high gets 15)
  }

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return '#10B981'; // Green
    if (percentage >= 60) return '#F59E0B'; // Yellow
    if (percentage >= 40) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A': '#10B981',
      'B': '#3B82F6', 
      'C': '#F59E0B',
      'D': '#F97316',
      'F': '#EF4444'
    };
    return colors[grade] || '#6B7280';
  };

  return (
    <div className="score-breakdown-overlay">
      <div className="score-breakdown-modal">
        <div className="score-breakdown-header">
          <h2>Website Score Breakdown</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="score-breakdown-content">
          {/* Overall Score Circle */}
          <div className="overall-score-section">
            <div className="score-circle-large">
              <svg width="120" height="120" viewBox="0 0 120 120" style={{ position: 'absolute', top: 0, left: 0 }}>
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="8"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke={getScoreColor(score)}
                  strokeWidth="8"
                  strokeDasharray={`${(score / 100) * 314.16} 314.16`}
                  strokeDashoffset="0"
                  transform="rotate(-90 60 60)"
                  className="score-progress"
                  strokeLinecap="round"
                />
              </svg>
              <div className="score-text-large">
                <div className="score-number">{score}</div>
                <div className="score-total">/100</div>
                <div className="score-grade" style={{ color: getGradeColor(grade) }}>
                  Grade {grade}
                </div>
              </div>
            </div>
            <div className="score-summary">
              <h3>Overall Performance</h3>
              <p>Your website scored {score} out of 100 points across key digital presence factors.</p>
            </div>
          </div>

          {/* Component Breakdown */}
          <div className="components-section">
            <h3>Score Components</h3>
            <div className="components-grid">
              {components.map((component, index) => (
                <div key={index} className="component-card">
                  <div className="component-header">
                    <span className="component-name">{component.name}</span>
                    <span className="component-score">
                      {component.points}/{component.maxPoints}
                    </span>
                  </div>
                  <div className="component-bar">
                    <div 
                      className="component-progress"
                      style={{ 
                        width: `${component.percentage}%`,
                        backgroundColor: getScoreColor(component.percentage)
                      }}
                    />
                  </div>
                  <div className="component-percentage">
                    {component.percentage}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="metrics-section">
            <h3>Technical Metrics</h3>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon"><Rocket size={24} /></div>
                <div className="metric-content">
                  <div className="metric-label">Loading Speed</div>
                  <div className="metric-value">
                    {validation_data?.response_time ? `${validation_data.response_time}s` : 'N/A'}
                  </div>
                  <div className="metric-status">
                    {validation_data?.response_time <= 2 ? 'Excellent' : 
                     validation_data?.response_time <= 4 ? 'Good' : 'Needs Improvement'}
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🔒</div>
                <div className="metric-content">
                  <div className="metric-label">Security</div>
                  <div className="metric-value">
                    {validation_data?.has_ssl ? 'HTTPS' : 'HTTP'}
                  </div>
                  <div className="metric-status">
                    {validation_data?.has_ssl ? 'Secure' : 'Not Secure'}
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><Smartphone size={24} /></div>
                <div className="metric-content">
                  <div className="metric-label">Accessibility</div>
                  <div className="metric-value">
                    {validation_data?.accessible ? 'Online' : 'Offline'}
                  </div>
                  <div className="metric-status">
                    {validation_data?.accessible ? 'Available' : 'Unavailable'}
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🛒</div>
                <div className="metric-content">
                  <div className="metric-label">Online Ordering</div>
                  <div className="metric-value">
                    {getOrderingScore(recommendations, issues) > 0 ? 'Detected' : 'Missing'}
                  </div>
                  <div className="metric-status">
                    {getOrderingScore(recommendations, issues) > 0 ? 'Available' : 'Not Found'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Issues and Recommendations */}
          <div className="insights-section">
            <div className="issues-column">
              <h3>🚨 Issues Found</h3>
              {issues && issues.length > 0 ? (
                <ul className="issues-list">
                  {issues.map((issue, index) => (
                    <li key={index} className="issue-item">
                      <span className="issue-icon">⚠️</span>
                      {issue}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-issues">No critical issues detected!</p>
              )}
            </div>

            <div className="recommendations-column">
              <h3>💡 Recommendations</h3>
              {recommendations && recommendations.length > 0 ? (
                <ul className="recommendations-list">
                  {recommendations.slice(0, 5).map((rec, index) => (
                    <li key={index} className="recommendation-item">
                      <span className="rec-icon">✨</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-recommendations">Great job! No immediate recommendations.</p>
              )}
            </div>
          </div>

          {/* Impact Projection */}
          <div className="impact-section">
            <h3><TrendingUp className="inline mr-2" size={18} />Improvement Impact</h3>
            <div className="impact-cards">
              <div className="impact-card">
                <div className="impact-title">Potential Score Increase</div>
                <div className="impact-value">+{100 - score} points</div>
                <div className="impact-description">
                  By addressing the recommendations above
                </div>
              </div>
              <div className="impact-card">
                <div className="impact-title">Revenue Impact</div>
                <div className="impact-value">$500-2000/month</div>
                <div className="impact-description">
                  Estimated increase from better digital presence
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreBreakdown;