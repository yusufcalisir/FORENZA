export default function DatabaseLoading() {
  return (
    <div className="w-full space-y-6 animate-pulse">
      {/* Header Skeleton */}
      <div className="h-20 w-full rounded-2xl bg-tactical-surface/70 border border-tactical-border/60 p-6 flex justify-between items-center">
        <div className="space-y-2">
          <div className="h-5 w-64 rounded bg-zinc-800" />
          <div className="h-3 w-80 rounded bg-zinc-800/60" />
        </div>
      </div>

      {/* Stats Strip Skeleton */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-20 rounded-xl bg-tactical-surface/50 border border-tactical-border/40 p-3 space-y-2">
            <div className="h-2.5 w-16 rounded bg-zinc-800/60" />
            <div className="h-5 w-12 rounded bg-zinc-800" />
          </div>
        ))}
      </div>

      {/* Table & Filter Skeleton */}
      <div className="rounded-2xl bg-tactical-surface/40 border border-tactical-border/60 p-4 space-y-3">
        <div className="h-10 w-full rounded-xl bg-black/40" />
        {[1, 2, 3, 4, 5, 6].map((row) => (
          <div key={row} className="h-12 w-full rounded-lg bg-zinc-800/30" />
        ))}
      </div>
    </div>
  );
}
