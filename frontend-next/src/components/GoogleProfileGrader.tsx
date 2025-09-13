import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Star, 
  MapPin, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp,
  ExternalLink,
  Clock,
  Target,
  Award,
  Users
} from 'lucide-react';
import './GoogleProfileGrader.css';

interface ScoreBreakdown {
  business_name: { score: number; max: number; weight: string };
  reviews_ratings: { score: number; max: number; weight: string };
  categories: { score: number; max: number; weight: string };
  accessibility: { score: number; max: number; weight: string };
  verification: { score: number; max: number; weight: string };
}

interface ScrapedData {
  business_name?: string;
  rating?: number;
  review_count?: number;
  categories?: string[];
  profile_url?: string;
}

interface GoogleProfileResult {
  overall_score: number;
  grade: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  score_breakdown?: ScoreBreakdown;
  issues: string[];
  recommendations: string[];
  strengths?: string[];
  scraped_data?: ScrapedData;
  analysis_method: string;
  grader_version: string;
  openai_analysis?: any; // Raw OpenAI response data
}

interface GoogleProfileGraderProps {
  restaurantName?: string;
  googleBusinessUrl?: string;
  onGradeComplete?: (result: GoogleProfileResult) => void;
}

const GoogleProfileGrader: React.FC<GoogleProfileGraderProps> = ({
  restaurantName = '',
  googleBusinessUrl = '',
  onGradeComplete
}) => {
  const [formData, setFormData] = useState({
    restaurant_name: restaurantName,
    google_business_url: googleBusinessUrl
  });
  const [result, setResult] = useState<GoogleProfileResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [graderMode, setGraderMode] = useState('classic');

  useEffect(() => {
    setFormData({
      restaurant_name: restaurantName,
      google_business_url: googleBusinessUrl
    });
  }, [restaurantName, googleBusinessUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/google-profile/grade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...formData, mode: graderMode })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: GoogleProfileResult = await response.json();
      setResult(data);
      onGradeComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return '#22c55e';
      case 'B': return '#84cc16';
      case 'C': return '#eab308';
      case 'D': return '#f97316';
      case 'F': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'LOW': return '#22c55e';
      case 'MEDIUM': return '#eab308';
      case 'HIGH': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const ScoreBreakdownItem: React.FC<{ 
    label: string; 
    score: number; 
    max: number; 
    weight: string 
  }> = ({ label, score, max, weight }) => {
    const percentage = (score / max) * 100;
    return (
      <div className="score-breakdown-item">
        <div className="score-breakdown-header">
          <span className="score-breakdown-label">{label}</span>
          <span className="score-breakdown-weight">{weight}</span>
        </div>
        <div className="score-breakdown-bar">
          <div 
            className="score-breakdown-fill" 
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="score-breakdown-score">
          {score}/{max} points
        </div>
      </div>
    );
  };

  return (
    <div className="google-profile-grader">
      <div className="grader-header">
        <div className="header-icon">
          <MapPin className="icon" />
        </div>
        <div className="header-content">
          <h2>Google Business Profile Grader</h2>
          <p>Get a detailed analysis of your Google Business Profile performance</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grader-form">
        <div className="form-group">
          <label htmlFor="restaurant_name">Restaurant Name</label>
          <input
            type="text"
            id="restaurant_name"
            value={formData.restaurant_name}
            onChange={(e) => setFormData({ ...formData, restaurant_name: e.target.value })}
            placeholder="Enter your restaurant name"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="google_business_url">Google Business Profile URL</label>
          <input
            type="url"
            id="google_business_url"
            value={formData.google_business_url}
            onChange={(e) => setFormData({ ...formData, google_business_url: e.target.value })}
            placeholder="https://maps.google.com/..."
            required
          />
          <small className="form-help">
            Copy the URL from your Google Maps business listing
          </small>
        </div>
        
        <div className="form-group">
          <label htmlFor="grader_mode">Grader Mode</label>
          <select
            id="grader_mode"
            value={graderMode}
            onChange={(e) => setGraderMode(e.target.value)}
          >
            <option value="classic">Classic</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>

        <button
          type="submit"
          className="grade-button"
          disabled={loading}
        >
          {loading ? (
            <>
              <Clock className="icon animate-spin" />
              Analyzing Profile...
            </>
          ) : (
            <>
              <Search className="icon" />
              Grade My Profile
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <AlertCircle className="icon" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="grader-results">
          <div className="result-header">
            <div className="overall-score">
              <div 
                className="score-circle"
                style={{ borderColor: getGradeColor(result.grade) }}
              >
                <span className="score-number">{result.overall_score}</span>
                <span className="score-grade" style={{ color: getGradeColor(result.grade) }}>
                  {result.grade}
                </span>
              </div>
              <div className="score-info">
                <h3>Overall Score</h3>
                <span 
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(result.priority) }}
                >
                  {result.priority} Priority
                </span>
              </div>
            </div>

            {result.scraped_data && (
              <div className="profile-summary">
                <h4>Profile Information</h4>
                <div className="profile-details">
                  {result.scraped_data.business_name && (
                    <div className="detail-item">
                      <Award className="icon" />
                      <span>{result.scraped_data.business_name}</span>
                    </div>
                  )}
                  {result.scraped_data.rating && (
                    <div className="detail-item">
                      <Star className="icon" />
                      <span>{result.scraped_data.rating}/5 stars</span>
                    </div>
                  )}
                  {result.scraped_data.review_count && (
                    <div className="detail-item">
                      <Users className="icon" />
                      <span>{result.scraped_data.review_count} reviews</span>
                    </div>
                  )}
                  {result.scraped_data.profile_url && (
                    <a 
                      href={result.scraped_data.profile_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="profile-link"
                    >
                      <ExternalLink className="icon" />
                      View Profile
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>

          {result.strengths && result.strengths.length > 0 && (
            <div className="strengths-section">
              <h4>
                <CheckCircle2 className="icon" />
                Profile Strengths
              </h4>
              <ul className="strengths-list">
                {result.strengths.map((strength, index) => (
                  <li key={index} className="strength-item">
                    <CheckCircle2 className="icon" />
                    {strength}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.issues.length > 0 && (
            <div className="issues-section">
              <h4>
                <AlertCircle className="icon" />
                Issues Found
              </h4>
              <ul className="issues-list">
                {result.issues.map((issue, index) => (
                  <li key={index} className="issue-item">
                    <AlertCircle className="icon" />
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="recommendations-section">
            <h4>
              <TrendingUp className="icon" />
              Recommendations
            </h4>
            <ul className="recommendations-list">
              {result.recommendations.map((rec, index) => (
                <li key={index} className="recommendation-item">
                  <Target className="icon" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>

          {result.score_breakdown && (
            <div className="score-breakdown">
              <div className="breakdown-header">
                <h4>Detailed Score Breakdown</h4>
                <button 
                  className="toggle-details"
                  onClick={() => setShowDetails(!showDetails)}
                >
                  {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
              </div>
              
              {showDetails && (
                <div className="breakdown-details">
                  <ScoreBreakdownItem
                    label="Business Name"
                    score={result.score_breakdown.business_name.score}
                    max={result.score_breakdown.business_name.max}
                    weight={result.score_breakdown.business_name.weight}
                  />
                  <ScoreBreakdownItem
                    label="Reviews & Ratings"
                    score={result.score_breakdown.reviews_ratings.score}
                    max={result.score_breakdown.reviews_ratings.max}
                    weight={result.score_breakdown.reviews_ratings.weight}
                  />
                  <ScoreBreakdownItem
                    label="Categories"
                    score={result.score_breakdown.categories.score}
                    max={result.score_breakdown.categories.max}
                    weight={result.score_breakdown.categories.weight}
                  />
                  <ScoreBreakdownItem
                    label="Accessibility"
                    score={result.score_breakdown.accessibility.score}
                    max={result.score_breakdown.accessibility.max}
                    weight={result.score_breakdown.accessibility.weight}
                  />
                  <ScoreBreakdownItem
                    label="Verification"
                    score={result.score_breakdown.verification.score}
                    max={result.score_breakdown.verification.max}
                    weight={result.score_breakdown.verification.weight}
                  />
                </div>
              )}
            </div>
          )}

          {result.analysis_method === 'openai_enhanced' && result.openai_analysis && (
            <div className="raw-output-section">
              <div className="raw-output-header">
                <h4>
                  <ExternalLink className="icon" />
                  Raw OpenAI Analysis
                </h4>
                <button 
                  className="toggle-details"
                  onClick={() => setShowDetails(!showDetails)}
                >
                  {showDetails ? 'Hide Raw Output' : 'Show Raw Output'}
                </button>
              </div>
              
              {showDetails && (
                <div className="raw-output-content">
                  <textarea
                    className="raw-output-textarea"
                    value={JSON.stringify(result.openai_analysis, null, 2)}
                    readOnly
                    rows={20}
                    placeholder="Raw OpenAI analysis data will appear here..."
                  />
                  <div className="raw-output-actions">
                    <button
                      className="copy-button"
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(result.openai_analysis, null, 2));
                        // You could add a toast notification here
                      }}
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="result-footer">
            <small>
              Analysis completed using {result.analysis_method} • Grader v{result.grader_version}
            </small>
          </div>
        </div>
      )}
    </div>
  );
};

export default GoogleProfileGrader;