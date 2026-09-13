import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, AuthState } from '../types';
import { api } from '../services/api';

interface AuthContextType extends AuthState {
  login: (token: string, user: User) => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('trizen_auth_token'),
    isAuthenticated: false,
    isLoading: true,
  });

  const login = (token: string, user: User) => {
    localStorage.setItem('trizen_auth_token', token);
    setState({
      user,
      token,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  const logout = () => {
    localStorage.removeItem('trizen_auth_token');
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('trizen_auth_token');
    if (!token) {
      setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const res = await api.get('/auth/me');
      setState({
        user: res.data,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      localStorage.removeItem('trizen_auth_token');
      setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
