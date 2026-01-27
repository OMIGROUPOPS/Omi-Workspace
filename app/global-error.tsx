'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body style={{ backgroundColor: '#0a0a0a', color: '#e4e4e7', fontFamily: 'system-ui, sans-serif' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Something went wrong</h2>
          <p style={{ fontSize: '0.875rem', color: '#71717a', marginBottom: '1rem' }}>{error.message}</p>
          <button
            onClick={reset}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem', backgroundColor: '#27272a', border: '1px solid #3f3f46', borderRadius: '0.5rem', color: '#e4e4e7', cursor: 'pointer' }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
