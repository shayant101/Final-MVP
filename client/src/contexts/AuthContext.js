import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      authAPI.getCurrentUser()
        .then(response => {
          setUser(response.user);
        })
        .catch(() => {
          // Token is invalid, remove it
          localStorage.removeItem('token');
          setToken(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { token: newToken, user: userData } = response;
      
      if (!newToken || !userData) {
        throw new Error('Invalid response from server');
      }
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(userData);
      
      // Redirect to main dashboard after successful login
      window.location.href = '/dashboard';
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { token: newToken, user: newUser } = response;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(newUser);
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const impersonate = async (restaurantId) => {
    try {
      const response = await authAPI.impersonate(restaurantId);
      const { token: newToken, impersonating_restaurant } = response;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      
      // Update user with impersonation info
      setUser(prev => ({
        ...prev,
        impersonating_restaurant_id: restaurantId,
        impersonating_restaurant
      }));
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const endImpersonation = async () => {
    try {
      const response = await authAPI.endImpersonation();
      const { token: newToken } = response;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      
      // Remove impersonation info from user
      setUser(prev => ({
        ...prev,
        impersonating_restaurant_id: null,
        impersonating_restaurant: null
      }));
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    impersonate,
    endImpersonation,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isRestaurant: user?.role === 'restaurant',
    isImpersonating: !!user?.impersonating_restaurant_id
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};