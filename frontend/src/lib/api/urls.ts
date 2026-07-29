/**
 * URL API — mirrors POST /urls, GET /urls/{code}, DELETE /urls/{code}.
 */
import { api } from "@/lib/api/client";
import type { URLCreateRequest, URLCreateResponse, URLMetaResponse } from "@/types";

export const urlApi = {
  create: (body: URLCreateRequest) =>
    api.post<URLCreateResponse>("/urls", body).then((r) => r.data),

  getMeta: (shortCode: string) =>
    api.get<URLMetaResponse>(`/urls/${shortCode}`).then((r) => r.data),

  delete: (shortCode: string) => api.delete(`/urls/${shortCode}`),
};
