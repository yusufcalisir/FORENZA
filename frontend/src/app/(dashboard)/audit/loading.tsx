export default function AuditLoading() {
  return (
    <div className="w-full space-y-6 animate-pulse">
      {/* Header Skeleton */}
      <div className="h-20 w-full rounded-2xl bg-tactical-surface/70 border border-tactical-border/60 p-6 flex justify-between items-center">
        <div className="space-y-2">
          <div className="h-5 w-56 rounded bg-zinc-800" />
          <div className="h-3 w-80 rounded bg-zinc-800/60" />
        </div>
        <div className="h-8 w-44 rounded-lg bg-zinc-800 hidden sm:block" />
      </div>

      {/* Metrics Row Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 rounded-xl bg-tactical-surface/50 border border-tactical-border/50 p-4 space-y-2">
            <div className="h-3 w-24 rounded bg-zinc-800/60" />
            <div className="h-6 w-16 rounded bg-zinc-800" />
          </div>
        ))}
      </div>

      {/* Table Skeleton */}
      <div className="rounded-2xl bg-tactical-surface/40 border border-tactical-border/60 p-4 space-y-3">
        <div className="h-8 w-full rounded-lg bg-black/40" />
        {[1, 2, 3, 4, 5, 6, 7].map((row) => (
          <div key={row} className="h-12 w-full rounded-lg bg-zinc-800/30" />
        ))}
      </div>
    </div>
  );
}
