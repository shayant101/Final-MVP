import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainDashboard from './components/MainDashboard';
import Login from './components/Login';
import LandingPage from './components/LandingPage';
import AIFeatures from './components/AIFeatures';
import AIAssistant from './components/AIAssistant';
import WebsiteBuilder from './components/WebsiteBuilder/WebsiteBuilder';
import WebsitePreview from './components/WebsiteBuilder/WebsitePreview';
import WebsiteEditor from './components/WebsiteBuilder/WebsiteEditor';
import TemplateGallery from './components/WebsiteBuilder/TemplateGallery';
import TemplateCustomizer from './components/WebsiteBuilder/TemplateCustomizer';
import LoadingScreen from './components/LoadingScreen';
import './App.css';

const AppContent = () => {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingScreen message="Initializing your restaurant's AI-powered marketing platform..." />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <MainDashboard />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-features"
          element={
            <ProtectedRoute>
              <AIFeatures />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/website-builder"
          element={
            <ProtectedRoute>
              <WebsiteBuilder />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/website-builder/preview/:id"
          element={
            <ProtectedRoute>
              <WebsitePreview />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/website-builder/edit/:id"
          element={
            <ProtectedRoute>
              <WebsiteEditor />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/website-builder/templates"
          element={
            <ProtectedRoute>
              <TemplateGallery />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/website-builder/templates/:templateId/customize"
          element={
            <ProtectedRoute>
              <TemplateCustomizer />
              <AIAssistant />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
