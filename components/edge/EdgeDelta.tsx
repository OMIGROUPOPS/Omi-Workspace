import { formatEdgeDelta } from '@/lib/edge/utils/odds-math';

interface EdgeDeltaProps {
  delta: number;
  size?: 'sm' | 'md' | 'lg';
}

export function EdgeDelta({ delta, size = 'md' }: EdgeDeltaProps) {
  const isPositive = delta > 0;
  const isSignificant = Math.abs(delta) >= 0.03;
  const isStrong = Math.abs(delta) >= 0.06;

  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-1',
    lg: 'text-base px-3 py-1.5 font-medium',
  };

  const colorClasses = isPositive
    ? isStrong
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
      : isSignificant
      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
      : 'bg-zinc-800 text-zinc-400 border-zinc-700'
    : isStrong
    ? 'bg-red-500/20 text-red-400 border-red-500/30'
    : isSignificant
    ? 'bg-red-500/10 text-red-300 border-red-500/20'
    : 'bg-zinc-800 text-zinc-400 border-zinc-700';

  return (
    <span
      className={`inline-flex items-center font-mono rounded border ${sizeClasses[size]} ${colorClasses}`}
    >
      {formatEdgeDelta(delta)}
    </span>
  );
}