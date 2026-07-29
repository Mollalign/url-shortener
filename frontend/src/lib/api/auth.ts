/**
 * Auth API — mirrors POST /auth/register, POST /auth/login exactly.
 */
import { api } from "@/lib/api/client";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UpdateProfileRequest,
  URLMetaResponse,
  User,
} from "@/types";

export const authApi = {
  register: (body: RegisterRequest) =>
    api.post<TokenResponse>("/auth/register", body).then((r) => r.data),

  login: (body: LoginRequest) =>
    api.post<TokenResponse>("/auth/login", body).then((r) => r.data),

  getMe: () => api.get<User>("/users/me").then((r) => r.data),

  updateMe: (body: UpdateProfileRequest) =>
    api.patch<User>("/users/me", body).then((r) => r.data),

  /** GET /users/me/urls — supports skip & limit query params */
  getMyUrls: (params?: { skip?: number; limit?: number }) =>
    api
      .get<URLMetaResponse[]>("/users/me/urls", { params })
      .then((r) => r.data),

  deleteAccount: () => api.delete("/users/me"),
};
