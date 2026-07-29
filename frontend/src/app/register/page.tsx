import type { Metadata } from "next";
import { Suspense } from "react";
import { RegisterForm } from "@/features/auth/RegisterForm";

export const metadata: Metadata = { title: "Register — Snip" };

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      <Suspense fallback={<div className="h-64 w-80 skeleton rounded-xl" />}>
        <RegisterForm />
      </Suspense>
    </main>
  );
}
