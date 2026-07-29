/**
 * Axios client — single instance for all API requests.
 *
 * Responsibilities:
 *  - Sets baseURL from NEXT_PUBLIC_API_URL
 *  - Attaches JWT Bearer token from localStorage on every request
 *  - Normalises error shapes (FastAPI 422 vs HTTPException vs network)
 *  - Returns 401 → clears token (no refresh — backend issues one-time JWTs)
 */
import axios, { AxiosError, type AxiosResponse } from "axios";
import type { APIError, ValidationError } from "@/types";
import { useAuthStore } from "@/store";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

// ── Request interceptor — attach JWT ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ── Response interceptor — normalise errors ───────────────────────────────────
api.interceptors.response.use(
  (res: AxiosResponse) => res,
  (error: AxiosError) => {
    const status = error.response?.status ?? 0;
    const data = error.response?.data as Record<string, unknown> | undefined;

    // 401 → wipe stored token and auth store so UI redirects to login
    if (status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      useAuthStore.getState().clearAuth();
    }

    // Build a normalised APIError
    const apiError: APIError = { status };

    if (data) {
      // FastAPI HTTPException → { detail: string }
      if (typeof data.detail === "string") {
        apiError.detail = data.detail;
      }
      // FastAPI 422 validation → { detail: ValidationError[] }
      if (Array.isArray(data.detail)) {
        apiError.detail = data.detail as ValidationError[];
      }
      // Our custom error envelope → { error, message }
      if (typeof data.error === "string") apiError.error = data.error;
      if (typeof data.message === "string") apiError.message = data.message;
    }

    if (!error.response) {
      // Network / timeout
      apiError.message = "Network error — please check your connection.";
    }

    return Promise.reject(apiError);
  }
);

/** Returns a human-readable message from any API error. */
export function getErrorMessage(err: unknown): string {
  const e = err as APIError;
  if (!e) return "An unexpected error occurred.";

  // 422 validation error — show the first violation
  if (Array.isArray(e.detail)) {
    const first = (e.detail as ValidationError[])[0];
    return first?.msg ?? "Validation error.";
  }

  return (
    (typeof e.detail === "string" ? e.detail : null) ??
    e.message ??
    "An unexpected error occurred."
  );
}

/** Returns field-level errors from a 422 response keyed by field name. */
export function getFieldErrors(
  err: unknown
): Record<string, string> {
  const e = err as APIError;
  if (!Array.isArray(e?.detail)) return {};

  const result: Record<string, string> = {};
  for (const ve of e.detail as ValidationError[]) {
    const field = ve.loc[ve.loc.length - 1];
    if (typeof field === "string") {
      result[field] = ve.msg;
    }
  }
  return result;
}
