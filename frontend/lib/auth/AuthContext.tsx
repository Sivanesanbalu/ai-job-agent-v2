"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { User, Profile, Preferences, ApplicationProfile } from "@/types";
import { api } from "@/lib/api/client";

interface AuthContextType {
  user: User | null;
  profile: Profile | null;
  preferences: Preferences | null;
  applicationProfile: ApplicationProfile | null;
  creditsRemaining: number;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (
    email: string,
    pass: string,
    firstName?: string,
    lastName?: string
  ) => Promise<void>;
  logout: () => void;
  refreshUserData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [applicationProfile, setApplicationProfile] =
    useState<ApplicationProfile | null>(null);
  const [creditsRemaining, setCreditsRemaining] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  const refreshUserData = async () => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const data = await api.auth.getMe();
      setUser({
        id: data.id,
        email: data.email,
        is_admin: data.is_admin,
        first_name: data.profile?.first_name,
        last_name: data.profile?.last_name,
      });
      setProfile(data.profile);
      setPreferences(data.preferences);
      setApplicationProfile(data.application_profile);
      setCreditsRemaining(data.credits_remaining || 0);
    } catch (err) {
      console.error("Failed to load user info:", err);
      localStorage.removeItem("auth_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUserData();
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await api.auth.login({ email, password: pass });
    localStorage.setItem("auth_token", res.access_token);
    await refreshUserData();
  };

  const register = async (
    email: string,
    pass: string,
    firstName?: string,
    lastName?: string
  ) => {
    const res = await api.auth.register({
      email,
      password: pass,
      first_name: firstName,
      last_name: lastName,
    });
    localStorage.setItem("auth_token", res.access_token);
    await refreshUserData();
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setUser(null);
    setProfile(null);
    setPreferences(null);
    setApplicationProfile(null);
    setCreditsRemaining(0);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        preferences,
        applicationProfile,
        creditsRemaining,
        loading,
        login,
        register,
        logout,
        refreshUserData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
