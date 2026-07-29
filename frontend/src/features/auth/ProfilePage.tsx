"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2, Trash2 } from "lucide-react";
import { updateProfileSchema, type UpdateProfileFormValues } from "@/lib/validators";
import { useDeleteAccount, useUpdateProfile } from "@/features/auth/hooks";
import { useAuthStore } from "@/store";
import { getErrorMessage } from "@/lib/api/client";
import { toast } from "sonner";
import { DashboardNav } from "@/components/DashboardNav";
import { inputCn } from "@/features/auth/LoginForm";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export function ProfilePage() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();

  const updateProfile = useUpdateProfile();
  const deleteAccount = useDeleteAccount();

  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login?redirect=/profile");
    }
  }, [isAuthenticated, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<UpdateProfileFormValues>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: { username: "", password: "" },
  });

  const onSubmit = (data: UpdateProfileFormValues) => {
    const payload: { username?: string; password?: string } = {};
    if (data.username) payload.username = data.username;
    if (data.password) payload.password = data.password;

    updateProfile.mutate(payload, {
      onSuccess: () => {
        toast.success("Profile updated");
        reset();
      },
    });
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav />

      <main className="mx-auto max-w-2xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Settings
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your account preferences and security
          </p>
        </div>

        {/* Account Info */}
        <div className="mb-6 rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-semibold text-foreground">
            Account Details
          </h2>
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between border-b border-border/50 pb-2.5">
              <dt className="text-muted-foreground">Email</dt>
              <dd className="font-medium text-foreground">{user?.email}</dd>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-2.5">
              <dt className="text-muted-foreground">Username</dt>
              <dd className="font-mono text-xs text-foreground">@{user?.username}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Member since</dt>
              <dd className="text-foreground">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })
                  : "—"}
              </dd>
            </div>
          </dl>
        </div>

        {/* Update Form */}
        <div className="mb-6 rounded-xl border border-border bg-card p-6">
          <h2 className="mb-1 text-sm font-semibold text-foreground">
            Update Credentials
          </h2>
          <p className="mb-4 text-xs text-muted-foreground">
            Leave any field empty if you do not wish to change it.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {updateProfile.isError && (
              <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3.5 py-2.5 text-sm text-destructive">
                {getErrorMessage(updateProfile.error)}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground">
                New username
              </label>
              <input
                type="text"
                placeholder={user?.username}
                className={inputCn(!!errors.username)}
                {...register("username")}
              />
              {errors.username && (
                <p className="text-xs text-destructive">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground">
                New password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
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
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={updateProfile.isPending}
                className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {updateProfile.isPending && (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                )}
                Save changes
              </button>
            </div>
          </form>
        </div>

        {/* Danger Zone */}
        <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
          <h2 className="mb-1 text-sm font-semibold text-destructive">
            Danger Zone
          </h2>
          <p className="mb-4 text-xs text-muted-foreground">
            Deactivating your account will disable login immediately. Existing short links will continue redirecting.
          </p>

          <AlertDialog>
            <AlertDialogTrigger className="inline-flex items-center gap-2 rounded-md bg-destructive px-3.5 py-2 text-xs font-medium text-destructive-foreground transition-opacity hover:opacity-90">
              <Trash2 className="h-3.5 w-3.5" />
              Deactivate account
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  Your account will be deactivated and you will be signed out immediately.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => deleteAccount.mutate()}
                  disabled={deleteAccount.isPending}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Yes, deactivate
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </main>
    </div>
  );
}
