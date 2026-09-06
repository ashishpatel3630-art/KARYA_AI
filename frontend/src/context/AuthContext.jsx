import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { getCurrentUser, loginUser, logoutUser, registerUser } from "../services/auth";
import { clearStoredTokens, getStoredAccessToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const checkAuth = async () => {
    const token = getStoredAccessToken();

    if (!token) {
      setUser(null);
      setAuthReady(true);
      return;
    }

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
      clearStoredTokens();
    } finally {
      setAuthReady(true);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email, password) => {
    setIsAuthenticating(true);
    try {
      const payload = await loginUser(email, password);
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return { payload, currentUser };
    } finally {
      setIsAuthenticating(false);
    }
  };

  const signUp = async (registration) => {
    setIsAuthenticating(true);
    try {
      const payload = await registerUser(registration);
      return payload;
    } finally {
      setIsAuthenticating(false);
    }
  };

  const signOut = async () => {
    try {
      await logoutUser();
    } finally {
      setUser(null);
      setAuthReady(true);
    }
  };

  const value = useMemo(
    () => ({
      user,
      role: user?.role || null,
      permissions: user?.permissions || [],
      authReady,
      isAuthenticated: Boolean(user),
      isAuthenticating,
      login,
      signUp,
      signOut,
      refreshAuth: checkAuth,
    }),
    [user, authReady, isAuthenticating],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
