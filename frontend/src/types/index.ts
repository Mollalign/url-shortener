// ─────────────────────────────────────────────────────────────────────────────
// Backend-derived TypeScript types.
// Generated from FastAPI Pydantic schemas — keep in sync with backend.
// ─────────────────────────────────────────────────────────────────────────────

// ── Auth / User ───────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string; // ISO 8601
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

// Requests
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UpdateProfileRequest {
  username?: string;
  password?: string;
}

// ── URLs ─────────────────────────────────────────────────────────────────────

export interface URLCreateRequest {
  long_url: string;
  custom_alias?: string | null;
  expiration_date?: string | null; // ISO 8601 UTC
}

export interface URLCreateResponse {
  short_url: string;
  alias: string;
  expires_at: string | null;
}

export interface URLMetaResponse {
  short_url: string;
  long_url: string;
  created_at: string;
  expires_at: string | null;
  clicks: number;
}

// ── Errors ────────────────────────────────────────────────────────────────────

export interface ErrorResponse {
  error: string;
  message: string;
}

/**
 * FastAPI returns validation errors as { detail: ValidationError[] }
 * for 422 responses.
 */
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface APIError {
  status: number;
  detail?: string | ValidationError[];
  error?: string;
  message?: string;
}

// ── Health ────────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: "ok" | "degraded";
  environment: string;
  version: string;
  db: boolean;
  redis: boolean;
}
