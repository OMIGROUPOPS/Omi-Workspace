import type { EdgeStatus } from '@/types/edge';

interface EdgeBadgeProps {
  status: EdgeStatus;
  confidence?: number;
  size?: 'sm' | 'md';
}

const statusStyles: Record<EdgeStatus, string> = {
  pass: 'bg-zinc-800 text-zinc-500 border-zinc-700',
  watch: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  edge: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  strong_edge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  rare: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
};

const statusLabels: Record<EdgeStatus, string> = {
  pass: 'Pass',
  watch: 'Watch',
  edge: 'Edge',
  strong_edge: 'Strong',
  rare: 'Rare',
};

export function EdgeBadge({ status, confidence, size = 'sm' }: EdgeBadgeProps) {
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${sizeClasses} ${statusStyles[status]}`}
    >
      {status === 'rare' && <span className="text-purple-400">★</span>}
      {statusLabels[status]}
      {confidence !== undefined && (
        <span className="font-mono opacity-80">{confidence.toFixed(0)}%</span>
      )}
    </span>
  );
}