"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store";
import { useMyUrls } from "@/features/auth/hooks";
import { CreateUrlForm } from "@/features/urls/CreateUrlForm";
import { UrlTable } from "@/features/urls/UrlTable";
import { DashboardNav } from "@/components/DashboardNav";
import { Link2, MousePointerClick, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();
  const { data: urls = [], isLoading } = useMyUrls();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login?redirect=/dashboard");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  const totalClicks = urls.reduce((sum, u) => sum + u.clicks, 0);
  const activeUrls = urls.filter(
    (u) => !u.expires_at || new Date(u.expires_at) > new Date()
  );

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav />

      <main className="mx-auto max-w-5xl px-6 py-10">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Welcome back, {user?.username}
          </p>
        </div>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard
            icon={Link2}
            label="Total links"
            value={isLoading ? null : urls.length}
          />
          <StatCard
            icon={MousePointerClick}
            label="Total clicks"
            value={isLoading ? null : totalClicks}
          />
          <StatCard
            icon={TrendingUp}
            label="Active links"
            value={isLoading ? null : activeUrls.length}
          />
        </div>

        {/* Create form */}
        <div className="mb-6">
          <CreateUrlForm />
        </div>

        {/* URL list */}
        <UrlTable urls={urls} isLoading={isLoading} />
      </main>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: number | null;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-muted-foreground/60" />
      </div>
      {value === null ? (
        <div className="skeleton h-7 w-16 rounded" />
      ) : (
        <p className="text-2xl font-semibold tabular-nums text-foreground">
          {value.toLocaleString()}
        </p>
      )}
    </div>
  );
}
