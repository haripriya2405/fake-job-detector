import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [guestScanCount, setGuestScanCount] = useState(() => {
    const saved = localStorage.getItem('sentinel_guest_scans_count');
    return saved ? parseInt(saved, 10) : 0;
  });

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getMe();
          setUser(userData);
        }
      } catch (err) {
        console.error('Failed to restore session', err);
        authService.logout();
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const incrementGuestScan = () => {
    setGuestScanCount((prev) => {
      const next = prev + 1;
      localStorage.setItem('sentinel_guest_scans_count', next.toString());
      return next;
    });
  };

  const login = async (email, password) => {
    const { user: loggedInUser } = await authService.login(email, password);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const register = async (fullName, email, password) => {
    const { user: registeredUser } = await authService.register(fullName, email, password);
    setUser(registeredUser);
    return registeredUser;
  };

  const loginWithGoogle = async (idToken) => {
    const { user: loggedInUser } = await authService.loginWithGoogle(idToken);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const hasUsedGuestScan = !user && guestScanCount >= 1;

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        loginWithGoogle,
        logout,
        isAuthenticated: !!user,
        guestScanCount,
        hasUsedGuestScan,
        incrementGuestScan,
      }}
    >
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
