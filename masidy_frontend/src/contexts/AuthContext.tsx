'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getStoredTokens = (): AuthTokens | null => {
    if (typeof window === 'undefined') return null;
    const tokens = localStorage.getItem('auth_tokens');
    return tokens ? JSON.parse(tokens) : null;
  };

  const setStoredTokens = (tokens: AuthTokens | null) => {
    if (typeof window === 'undefined') return;
    if (tokens) {
      localStorage.setItem('auth_tokens', JSON.stringify(tokens));
    } else {
      localStorage.removeItem('auth_tokens');
    }
  };

  const fetchUser = useCallback(async (accessToken: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      return false;
    }
  }, []);

  const refreshToken = useCallback(async () => {
    const tokens = getStoredTokens();
    if (!tokens?.refresh_token) {
      setUser(null);
      setStoredTokens(null);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      });

      if (response.ok) {
        const newTokens = await response.json();
        setStoredTokens(newTokens);
        await fetchUser(newTokens.access_token);
      } else {
        setUser(null);
        setStoredTokens(null);
      }
    } catch (error) {
      console.error('Failed to refresh token:', error);
      setUser(null);
      setStoredTokens(null);
    }
  }, [fetchUser]);

  useEffect(() => {
    const initAuth = async () => {
      const tokens = getStoredTokens();
      if (tokens?.access_token) {
        const success = await fetchUser(tokens.access_token);
        if (!success) {
          await refreshToken();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [fetchUser, refreshToken]);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/login/json`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const tokens: AuthTokens = await response.json();
    setStoredTokens(tokens);
    await fetchUser(tokens.access_token);
  };

  const signup = async (email: string, password: string, name: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    // Auto login after signup
    await login(email, password);
  };

  const logout = () => {
    setUser(null);
    setStoredTokens(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
