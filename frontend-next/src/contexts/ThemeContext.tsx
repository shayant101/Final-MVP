'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ThemeContextType {
  theme: string;
  toggleTheme: () => void;
  setLightTheme: () => void;
  setDarkTheme: () => void;
  isDark: boolean;
  isLight: boolean;
}

interface ThemeProviderProps {
  children: ReactNode;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState('dark');

  // Initialize theme from localStorage after component mounts
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
        setTheme(savedTheme);
      }
    }
  }, []);

  // Apply theme to document on mount and when theme changes
  useEffect(() => {
    // Set data-theme attribute on document element for CSS
    document.documentElement.setAttribute('data-theme', theme);
    
    // Also set dark-mode class on body for backward compatibility
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  const setLightTheme = () => {
    setTheme('light');
  };

  const setDarkTheme = () => {
    setTheme('dark');
  };

  const value = {
    theme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;