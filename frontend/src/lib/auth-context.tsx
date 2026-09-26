"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { authAPI } from "./api";

interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  patient_id?: string;
  doctor_id?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => void;
  isPatient: boolean;
  isDoctor: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async (savedToken: string) => {
    try {
      const me = await authAPI.getMe(savedToken);
      setUser({
        id: me.id,
        email: me.email,
        name: me.full_name,
        role: me.role,
        patient_id: me.patient_id,
        doctor_id: me.doctor_id,
      });
      setToken(savedToken);
    } catch {
      localStorage.removeItem("token");
      setUser(null);
      setToken(null);
    }
  }, []);

  useEffect(() => {
    let active = true;
    const initAuth = async () => {
      const savedToken = localStorage.getItem("token");
      if (savedToken) {
        await loadUser(savedToken);
      }
      if (active) setLoading(false);
    };
    initAuth();
    return () => { active = false; };
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    const res = await authAPI.login({ email, password });
    localStorage.setItem("token", res.access_token);
    setToken(res.access_token);
    await loadUser(res.access_token);
  };

  const register = async (name: string, email: string, password: string, phone?: string) => {
    await authAPI.register({ name, email, password, phone, role: "patient" });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isPatient: user?.role === "patient",
        isDoctor: user?.role === "doctor",
        isAdmin: user?.role === "admin",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
