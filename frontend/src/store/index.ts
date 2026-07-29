/**
 * Zustand store — UI state only.
 *
 * Rules:
 *  - Server state (users, URLs) lives in TanStack Query, NOT here.
 *  - This store manages: auth token persistence, theme, sidebar.
 */
"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;
  isAuthenticated: boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) => {
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", token);
        }
        set({ token, user, isAuthenticated: true });
      },
      clearAuth: () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
        }
        set({ token: null, user: null, isAuthenticated: false });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);

// Rehydrate isAuthenticated after persist loads
useAuthStore.subscribe((state) => {
  if (state.token && !state.isAuthenticated) {
    useAuthStore.setState({ isAuthenticated: true });
  }
});

// ── UI Store ──────────────────────────────────────────────────────────────────

interface UIState {
  theme: "dark" | "light";
  sidebarOpen: boolean;
  toggleTheme: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: "dark",
      sidebarOpen: true,
      toggleTheme: () =>
        set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
    }),
    { name: "ui-storage", partialize: (s) => ({ theme: s.theme }) }
  )
);
