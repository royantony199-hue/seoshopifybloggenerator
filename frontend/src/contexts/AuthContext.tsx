import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { secureStorage } from '../utils/secureStorage';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  tenant_id: number;
  tenant_name: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

const initialState: AuthState = {
  user: null,
  token: null,
  loading: true,
  error: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false,
        error: null,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: null,
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

interface AuthContextType extends AuthState {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

// Auto-login credentials
const AUTO_LOGIN_EMAIL = 'newuser@test.com';
const AUTO_LOGIN_PASSWORD = 'Password123';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const performLogin = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  };

  // Auto-login on app start
  useEffect(() => {
    const autoLogin = async () => {
      // First check if we already have valid credentials stored
      const token = secureStorage.getAuthToken();
      const user = secureStorage.getUserData();

      if (token && user) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });

          if (response.ok) {
            const userData = await response.json();
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: { user: userData, token }
            });
            return;
          }
        } catch (error) {
          // Token invalid, will auto-login below
        }
      }

      // Auto-login with default credentials
      try {
        const data = await performLogin(AUTO_LOGIN_EMAIL, AUTO_LOGIN_PASSWORD);
        secureStorage.setAuthToken(data.access_token);
        secureStorage.setUserData(data.user);
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: data.user, token: data.access_token },
        });
      } catch (error) {
        console.error('Auto-login failed, continuing without auth');
        // Still allow app to load even if auto-login fails
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    autoLogin();
  }, []);

  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const data = await performLogin(email, password);
      secureStorage.setAuthToken(data.access_token);
      secureStorage.setUserData(data.user);
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: data.user, token: data.access_token },
      });
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error instanceof Error ? error.message : 'Login failed',
      });
      throw error;
    }
  };

  const register = async (userData: any) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      secureStorage.setAuthToken(data.access_token);
      secureStorage.setUserData(data.user);
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: data.user, token: data.access_token },
      });
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error instanceof Error ? error.message : 'Registration failed',
      });
      throw error;
    }
  };

  const logout = () => {
    secureStorage.clearAuthData();
    dispatch({ type: 'LOGOUT' });
  };

  const value: AuthContextType = {
    ...state,
    isAuthenticated: true, // Always authenticated
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
