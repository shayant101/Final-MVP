'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';

interface User {
  id: string;
  email: string;
  role: 'admin' | 'restaurant';
  restaurant_name?: string;
  impersonating_restaurant_id?: string | null;
  impersonating_restaurant?: {
    id: string;
    name: string;
  } | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<any>;
  register: (userData: any) => Promise<any>;
  logout: () => void;
  impersonate: (restaurantId: string) => Promise<any>;
  endImpersonation: () => Promise<any>;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isRestaurant: boolean;
  isImpersonating: boolean;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);

  // Initialize token from localStorage after component mounts
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('token');
      setToken(savedToken);
    }
  }, []);

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

  const login = async (email: string, password: string) => {
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

  const register = async (userData: any) => {
    try {
      const response = await authAPI.register(userData);
      const { token: newToken, user: newUser } = response;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(newUser);
      
      // Redirect to welcome page after successful registration
      window.location.href = '/welcome';
      
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

  const impersonate = async (restaurantId: string) => {
    try {
      const response = await authAPI.impersonate(restaurantId);
      const { token: newToken, impersonating_restaurant } = response;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      
      // Update user with impersonation info
      setUser(prev => prev ? ({
        ...prev,
        impersonating_restaurant_id: restaurantId,
        impersonating_restaurant
      }) : null);
      
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
      setUser(prev => prev ? ({
        ...prev,
        impersonating_restaurant_id: null,
        impersonating_restaurant: null
      }) : null);
      
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