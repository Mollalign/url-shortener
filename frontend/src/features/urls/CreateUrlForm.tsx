"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { createUrlSchema, type CreateUrlFormValues } from "@/lib/validators";
import { useCreateUrl } from "@/features/urls/hooks";
import { getErrorMessage } from "@/lib/api/client";
import { toast } from "sonner";
import { inputCn } from "@/features/auth/LoginForm";

export function CreateUrlForm() {
  const { mutate, isPending, isError, error, reset } = useCreateUrl();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset: resetForm,
  } = useForm<CreateUrlFormValues>({ resolver: zodResolver(createUrlSchema) });

  const onSubmit = (data: CreateUrlFormValues) => {
    mutate(
      {
        long_url: data.long_url,
        custom_alias: data.custom_alias || undefined,
        expiration_date: data.expiration_date
          ? new Date(data.expiration_date).toISOString()
          : undefined,
      },
      {
        onSuccess: (res) => {
          toast.success("Link created", { description: res.short_url });
          resetForm();
          reset();
        },
      }
    );
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <h2 className="mb-4 text-sm font-semibold text-foreground">
        Shorten a URL
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {isError && (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3.5 py-2.5 text-sm text-destructive">
            {getErrorMessage(error)}
          </div>
        )}

        {/* Destination URL — full width */}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-foreground">
            Destination URL
          </label>
          <input
            type="url"
            placeholder="https://example.com/very/long/path"
            className={inputCn(!!errors.long_url)}
            {...register("long_url")}
          />
          {errors.long_url && (
            <p className="text-xs text-destructive">{errors.long_url.message}</p>
          )}
        </div>

        {/* Optional row */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground">
              Custom alias
              <span className="ml-1 text-xs font-normal text-muted-foreground">
                (optional)
              </span>
            </label>
            <input
              type="text"
              placeholder="my-link"
              className={inputCn(!!errors.custom_alias)}
              {...register("custom_alias")}
            />
            {errors.custom_alias && (
              <p className="text-xs text-destructive">
                {errors.custom_alias.message}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground">
              Expiry date
              <span className="ml-1 text-xs font-normal text-muted-foreground">
                (optional)
              </span>
            </label>
            <input
              type="datetime-local"
              className={inputCn(!!errors.expiration_date)}
              {...register("expiration_date")}
            />
            {errors.expiration_date && (
              <p className="text-xs text-destructive">
                {errors.expiration_date.message}
              </p>
            )}
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending}
            className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Create link
          </button>
        </div>
      </form>
    </div>
  );
}
