"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Link2, Settings, LogOut, Home, LayoutDashboard } from "lucide-react";
import { useLogout } from "@/features/auth/hooks";
import { useAuthStore } from "@/store";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function DashboardNav() {
  const logout = useLogout();
  const { user } = useAuthStore();
  const pathname = usePathname();
  const router = useRouter();

  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
        {/* Logo and Nav Links */}
        <div className="flex items-center gap-6">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 font-semibold text-foreground"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary">
              <Link2 className="h-3.5 w-3.5 text-primary-foreground" />
            </div>
            <span className="text-sm tracking-tight">Snip</span>
          </Link>

          <nav className="hidden sm:flex items-center gap-1">
            <Link
              href="/dashboard"
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                pathname === "/dashboard"
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              }`}
            >
              <LayoutDashboard className="h-3.5 w-3.5" />
              Dashboard
            </Link>
            <Link
              href="/profile"
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                pathname === "/profile"
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              }`}
            >
              <Settings className="h-3.5 w-3.5" />
              Settings
            </Link>
          </nav>
        </div>

        {/* User menu and theme toggle */}
        <div className="flex items-center gap-2">
          <ThemeToggle />

          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground outline-none">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground uppercase">
                {user?.username?.[0] ?? "U"}
              </div>
              <span className="hidden sm:inline">{user?.username}</span>
            </DropdownMenuTrigger>

            <DropdownMenuContent
              side="bottom"
              align="end"
              className="w-52 border-border bg-popover text-popover-foreground"
            >
              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  {user?.email}
                </DropdownMenuLabel>
              </DropdownMenuGroup>

              <DropdownMenuSeparator />

              <DropdownMenuItem
                className="cursor-pointer gap-2 px-2 py-1.5 text-sm"
                onClick={() => router.push("/dashboard")}
              >
                <LayoutDashboard className="h-3.5 w-3.5 text-muted-foreground" />
                Dashboard
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer gap-2 px-2 py-1.5 text-sm"
                onClick={() => router.push("/profile")}
              >
                <Settings className="h-3.5 w-3.5 text-muted-foreground" />
                Settings
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer gap-2 px-2 py-1.5 text-sm"
                onClick={() => router.push("/")}
              >
                <Home className="h-3.5 w-3.5 text-muted-foreground" />
                Back to Home
              </DropdownMenuItem>

              <DropdownMenuSeparator />

              <DropdownMenuItem
                onClick={logout}
                className="cursor-pointer gap-2 px-2 py-1.5 text-sm text-destructive focus:text-destructive"
              >
                <LogOut className="h-3.5 w-3.5" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
