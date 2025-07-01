import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainDashboard from './components/MainDashboard';
import Login from './components/Login';
import LandingPage from './components/LandingPage';
import AIFeatures from './components/AIFeatures';
import AIAssistant from './components/AIAssistant';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
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
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
