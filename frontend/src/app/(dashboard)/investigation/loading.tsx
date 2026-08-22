export default function InvestigationLoading() {
  return (
    <div className="w-full space-y-6 animate-pulse">
      {/* Header Skeleton */}
      <div className="h-20 w-full rounded-2xl bg-tactical-surface/70 border border-tactical-border/60 p-6 flex justify-between items-center">
        <div className="space-y-2">
          <div className="h-5 w-72 rounded bg-zinc-800" />
          <div className="h-3 w-96 rounded bg-zinc-800/60" />
        </div>
      </div>

      {/* Hero Vault Search Skeleton */}
      <div className="h-80 w-full rounded-2xl bg-tactical-surface/50 border border-tactical-border/60 p-8 flex flex-col items-center justify-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-zinc-800" />
        <div className="h-5 w-64 rounded bg-zinc-800" />
        <div className="h-3.5 w-96 rounded bg-zinc-800/60" />
        <div className="h-10 w-48 rounded-xl bg-zinc-800 mt-4" />
      </div>

      {/* Graph Area Skeleton */}
      <div className="h-96 w-full rounded-2xl bg-black/40 border border-tactical-border/40" />
    </div>
  );
}
