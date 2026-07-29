import type { Metadata } from "next";
import { Suspense } from "react";
import { LoginForm } from "@/features/auth/LoginForm";

export const metadata: Metadata = { title: "Login — Snip" };

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      <Suspense fallback={<div className="h-64 w-80 skeleton rounded-xl" />}>
        <LoginForm />
      </Suspense>
    </main>
  );
}
