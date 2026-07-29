"use client";

import { Copy, ExternalLink, MousePointerClick, Trash2 } from "lucide-react";
import { toast } from "sonner";
import type { URLMetaResponse } from "@/types";
import { useDeleteUrl } from "@/features/urls/hooks";
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

interface UrlTableProps {
  urls: URLMetaResponse[];
  isLoading: boolean;
}

export function UrlTable({ urls, isLoading }: UrlTableProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-border bg-card">
        <div className="border-b border-border px-6 py-4">
          <div className="skeleton h-4 w-24 rounded" />
        </div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-6 py-4">
            <div className="flex-1 space-y-2">
              <div className="skeleton h-3.5 w-40 rounded" />
              <div className="skeleton h-3 w-64 rounded" />
            </div>
            <div className="skeleton h-3 w-12 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (urls.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-card px-6 py-16 text-center">
        <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full border border-border">
          <MousePointerClick className="h-5 w-5 text-muted-foreground" />
        </div>
        <p className="text-sm font-medium text-foreground">No links yet</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Create your first short link above.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card">
      {/* Table header */}
      <div className="grid grid-cols-[1fr_auto_auto] items-center border-b border-border px-6 py-3">
        <span className="text-xs font-medium text-muted-foreground">Link</span>
        <span className="mr-12 text-xs font-medium text-muted-foreground">Clicks</span>
        <span className="text-xs font-medium text-muted-foreground">Actions</span>
      </div>

      <div className="divide-y divide-border">
        {urls.map((url) => (
          <UrlRow key={url.short_url} url={url} />
        ))}
      </div>
    </div>
  );
}

function UrlRow({ url }: { url: URLMetaResponse }) {
  const deleteMutation = useDeleteUrl();
  const shortCode = url.short_url.split("/").pop() ?? "";
  const isExpired =
    url.expires_at ? new Date(url.expires_at) < new Date() : false;

  const copy = async () => {
    await navigator.clipboard.writeText(url.short_url);
    toast.success("Copied to clipboard");
  };

  const handleDelete = () => {
    deleteMutation.mutate(shortCode, {
      onSuccess: () => toast.success("Link deleted"),
    });
  };

  return (
    <div className="group grid grid-cols-[1fr_auto_auto] items-center gap-4 px-6 py-4 transition-colors hover:bg-muted/30">
      {/* Link info */}
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <a
            href={url.short_url}
            target="_blank"
            rel="noopener noreferrer"
            className="truncate font-mono text-sm font-medium text-foreground hover:text-primary transition-colors"
          >
            {url.short_url}
          </a>
          {isExpired && (
            <span className="shrink-0 rounded border border-border px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
              Expired
            </span>
          )}
        </div>
        <p className="mt-0.5 truncate text-xs text-muted-foreground">
          {url.long_url}
        </p>
        <p className="mt-0.5 text-[11px] text-muted-foreground/60">
          {new Date(url.created_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
          {url.expires_at &&
            ` · expires ${new Date(url.expires_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            })}`}
        </p>
      </div>

      {/* Click count */}
      <div className="mr-4 flex items-center gap-1.5 tabular-nums text-sm text-foreground">
        <MousePointerClick className="h-3.5 w-3.5 text-muted-foreground/60" />
        {url.clicks.toLocaleString()}
      </div>

      {/* Actions — visible on hover */}
      <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <button
          onClick={copy}
          aria-label="Copy link"
          className="rounded p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <Copy className="h-3.5 w-3.5" />
        </button>

        <a
          href={url.long_url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Visit destination"
          className="rounded p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <ExternalLink className="h-3.5 w-3.5" />
        </a>

        <AlertDialog>
          <AlertDialogTrigger
            aria-label="Delete link"
            className="rounded p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </AlertDialogTrigger>

          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete this link?</AlertDialogTitle>
              <AlertDialogDescription>
                <span className="font-mono text-foreground">{url.short_url}</span>{" "}
                will stop redirecting immediately. This cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
