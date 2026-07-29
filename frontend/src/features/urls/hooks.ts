"use client";

/**
 * TanStack Query hooks — URL feature.
 */
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { urlApi } from "@/lib/api/urls";
import { QUERY_KEYS } from "@/features/auth/hooks";
import type { URLCreateRequest } from "@/types";

/** Create a short URL. Works anonymously or authenticated (JWT auto-attached). */
export function useCreateUrl() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (data: URLCreateRequest) => urlApi.create(data),
    onSuccess: () => {
      // Invalidate user's URL list so dashboard refreshes
      qc.invalidateQueries({ queryKey: ["my-urls"] });
    },
  });
}

/** Delete a short URL by alias / short_code. */
export function useDeleteUrl() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (shortCode: string) => urlApi.delete(shortCode),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.myUrls(0, 50) });
      qc.invalidateQueries({ queryKey: ["my-urls"] });
    },
  });
}
