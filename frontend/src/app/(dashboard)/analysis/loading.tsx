export default function AnalysisLoading() {
  return (
    <div className="w-full space-y-6 animate-pulse">
      {/* Header Banner Skeleton */}
      <div className="h-24 w-full rounded-2xl bg-tactical-surface/70 border border-tactical-border/60 p-6 flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-6 w-64 rounded bg-zinc-800" />
          <div className="h-3.5 w-96 rounded bg-zinc-800/60" />
        </div>
        <div className="h-10 w-36 rounded-xl bg-zinc-800 hidden md:block" />
      </div>

      {/* 7 Pillars Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {[1, 2, 3, 4, 5, 6, 7].map((pillar) => (
          <div
            key={pillar}
            className="rounded-2xl bg-tactical-surface/50 border border-tactical-border/50 p-5 space-y-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-zinc-800" />
              <div className="space-y-1.5 flex-1">
                <div className="h-4 w-3/4 rounded bg-zinc-800" />
                <div className="h-3 w-1/2 rounded bg-zinc-800/60" />
              </div>
            </div>
            <div className="h-16 rounded-xl bg-black/40" />
            <div className="flex justify-between items-center pt-2">
              <div className="h-3 w-20 rounded bg-zinc-800/50" />
              <div className="h-7 w-24 rounded-lg bg-zinc-800" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
