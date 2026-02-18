'use client';

export default function SportsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <div className="w-16 h-16 rounded-2xl bg-white border border-red-200 flex items-center justify-center mb-4">
        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-800 mb-2">Failed to Load Sports Data</h3>
      <p className="text-sm text-gray-500 text-center max-w-md mb-1">
        {error.message || 'An unexpected error occurred while loading the sports dashboard.'}
      </p>
      {error.digest && (
        <p className="text-xs font-mono text-gray-400 mt-1">Digest: {error.digest}</p>
      )}
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        Retry
      </button>
    </div>
  );
}
