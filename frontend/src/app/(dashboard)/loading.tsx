export default function DashboardLoading() {
  return (
    <div className="w-full space-y-4 animate-pulse p-2 sm:p-4">
      {/* Header Skeleton */}
      <div className="h-20 w-full rounded-2xl bg-tactical-surface/60 border border-tactical-border/60 flex items-center justify-between px-6">
        <div className="space-y-2">
          <div className="h-5 w-48 rounded-md bg-zinc-800" />
          <div className="h-3 w-72 rounded-md bg-zinc-800/60" />
        </div>
        <div className="h-9 w-32 rounded-xl bg-zinc-800/80 hidden sm:block" />
      </div>

      {/* Content Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="h-44 rounded-2xl bg-tactical-surface/40 border border-tactical-border/40 p-5 space-y-3"
          >
            <div className="h-4 w-1/3 rounded bg-zinc-800" />
            <div className="h-3 w-3/4 rounded bg-zinc-800/60" />
            <div className="h-16 w-full rounded-xl bg-black/40 mt-4" />
          </div>
        ))}
      </div>
    </div>
  );
}
