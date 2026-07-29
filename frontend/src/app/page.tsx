"use client";

import Link from "next/link";
import { ArrowRight, Link2, MousePointerClick, Timer, LayoutDashboard } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuthStore } from "@/store";
import { useEffect, useState } from "react";

export default function HomePage() {
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* ── Nav ───────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold text-foreground">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary">
              <Link2 className="h-3.5 w-3.5 text-primary-foreground" />
            </div>
            <span className="text-sm tracking-tight">Snip</span>
          </Link>

          <nav className="flex items-center gap-2">
            <ThemeToggle />

            {mounted && isAuthenticated ? (
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
              >
                <LayoutDashboard className="h-3.5 w-3.5" />
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
                >
                  Get started
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <main className="flex flex-1 flex-col items-center justify-center px-6 pb-32 pt-24 text-center">
        {/* Badge */}
        <div className="mb-8 inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
          Production-ready URL shortener
        </div>

        <h1 className="mb-4 max-w-2xl text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
          Short links that{" "}
          <span className="text-primary">work beautifully</span>
        </h1>

        <p className="mb-10 max-w-md text-base leading-relaxed text-muted-foreground">
          Create compact links in seconds. Track every click. Set expiry dates.
          No noise, just links.
        </p>

        <div className="flex flex-col items-center gap-3 sm:flex-row">
          {mounted && isAuthenticated ? (
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          ) : (
            <>
              <Link
                href="/register"
                className="group inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
              >
                Start for free
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center rounded-md border border-border px-5 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:border-border/80 hover:bg-muted hover:text-foreground"
              >
                Sign in
              </Link>
            </>
          )}
        </div>

        {/* ── Features ──────────────────────────────────────────────── */}
        <div className="mt-24 grid w-full max-w-3xl gap-4 text-left sm:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-xl border border-border bg-card p-5 transition-colors hover:border-border/80 hover:bg-card/80"
            >
              <div className="mb-3 inline-flex rounded-md border border-border p-2 text-muted-foreground">
                <f.icon className="h-4 w-4" />
              </div>
              <h3 className="mb-1 text-sm font-semibold text-foreground">
                {f.title}
              </h3>
              <p className="text-xs leading-relaxed text-muted-foreground">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </main>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer className="border-t border-border/50 px-6 py-6">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} Snip
          </p>
          <p className="text-xs text-muted-foreground">
            Built with Next.js · FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: Link2,
    title: "Custom aliases",
    description: "Pick a memorable slug instead of a random code.",
  },
  {
    icon: MousePointerClick,
    title: "Click analytics",
    description: "Track how many times each link was visited in real time.",
  },
  {
    icon: Timer,
    title: "Expiry dates",
    description: "Links that self-expire so stale content doesn't linger.",
  },
];
