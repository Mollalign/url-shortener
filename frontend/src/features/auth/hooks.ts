"use client";

/**
 * TanStack Query hooks — auth feature.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/store";
import type { LoginRequest, RegisterRequest, UpdateProfileRequest } from "@/types";

export const QUERY_KEYS = {
  me: ["me"] as const,
  myUrls: (skip: number, limit: number) => ["my-urls", skip, limit] as const,
};

/** Fetch current user — only runs when authenticated. */
export function useMe() {
  const { isAuthenticated } = useAuthStore();
  return useQuery({
    queryKey: QUERY_KEYS.me,
    queryFn: authApi.getMe,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });
}

/** Register mutation — sets auth state on success. */
export function useRegister() {
  const { setAuth } = useAuthStore();
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (res) => {
      setAuth(res.access_token, res.user);
      qc.setQueryData(QUERY_KEYS.me, res.user);
      router.push("/dashboard");
    },
  });
}

/** Login mutation — sets auth state on success. */
export function useLogin() {
  const { setAuth } = useAuthStore();
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (res) => {
      setAuth(res.access_token, res.user);
      qc.setQueryData(QUERY_KEYS.me, res.user);
      router.push("/dashboard");
    },
  });
}

/** Logout — clears local state and navigates to /login. */
export function useLogout() {
  const { clearAuth } = useAuthStore();
  const qc = useQueryClient();
  const router = useRouter();

  return () => {
    clearAuth();
    qc.clear();
    router.push("/login");
  };
}

/** Update username / password. */
export function useUpdateProfile() {
  const qc = useQueryClient();
  const { user, setAuth, token } = useAuthStore();

  return useMutation({
    mutationFn: (data: UpdateProfileRequest) => authApi.updateMe(data),
    onSuccess: (updated) => {
      qc.setQueryData(QUERY_KEYS.me, updated);
      // Keep token, update user in store
      if (token) setAuth(token, updated);
    },
  });
}

/** List authenticated user's URLs (paginated). */
export function useMyUrls(skip = 0, limit = 50) {
  const { isAuthenticated } = useAuthStore();
  return useQuery({
    queryKey: QUERY_KEYS.myUrls(skip, limit),
    queryFn: () => authApi.getMyUrls({ skip, limit }),
    enabled: isAuthenticated,
    staleTime: 30_000,
  });
}

/** Delete account. */
export function useDeleteAccount() {
  const { clearAuth } = useAuthStore();
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: authApi.deleteAccount,
    onSuccess: () => {
      clearAuth();
      qc.clear();
      router.push("/");
    },
  });
}
