"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { loginSchema, type LoginFormValues } from "@/lib/validators";
import { useLogin } from "@/features/auth/hooks";
import { useAuthStore } from "@/store";
import { getErrorMessage } from "@/lib/api/client";

export function LoginForm() {
  const login = useLogin();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuthStore();
  const redirectTarget = searchParams.get("redirect") || "/dashboard";

  const [showPassword, setShowPassword] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      router.replace(redirectTarget);
    }
  }, [isAuthenticated, router, redirectTarget]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  return (
    <div className="w-full max-w-sm">
      {/* Back to Home link */}
      <div className="mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Home
        </Link>
      </div>

      {/* Header */}
      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
          <svg
            className="h-5 w-5 text-primary-foreground"
            fill="none"
            stroke="currentColor"
            strokeWidth={2.2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
            />
          </svg>
        </div>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">
          Sign in to Snip
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Welcome back
        </p>
      </div>

      {/* Form */}
      <form
        onSubmit={handleSubmit((d) =>
          login.mutate(d, {
            onSuccess: () => {
              router.push(redirectTarget);
            },
          })
        )}
        className="space-y-4"
        noValidate
      >
        {/* API error */}
        {login.isError && (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3.5 py-2.5 text-sm text-destructive">
            {getErrorMessage(login.error)}
          </div>
        )}

        <Field label="Email" error={errors.email?.message}>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            className={inputCn(!!errors.email)}
            {...register("email")}
          />
        </Field>

        <Field label="Password" error={errors.password?.message}>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••"
              className={`${inputCn(!!errors.password)} pr-10`}
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
        </Field>

        <button
          type="submit"
          disabled={login.isPending}
          className="mt-1 flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {login.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          Sign in
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        No account?{" "}
        <Link
          href={`/register${redirectTarget !== "/dashboard" ? `?redirect=${encodeURIComponent(redirectTarget)}` : ""}`}
          className="font-medium text-foreground underline-offset-4 hover:underline"
        >
          Create one
        </Link>
      </p>
    </div>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium text-foreground">{label}</label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

export function inputCn(hasError = false) {
  return [
    "w-full rounded-md border bg-muted/30 px-3 py-2 text-sm text-foreground",
    "placeholder:text-muted-foreground/60",
    "transition-colors",
    "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background focus:border-transparent",
    hasError ? "border-destructive/70" : "border-border",
  ].join(" ");
}
