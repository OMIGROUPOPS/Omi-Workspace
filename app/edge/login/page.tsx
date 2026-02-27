'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login } from '@/lib/edge/auth';

export default function EdgeLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate a small delay for UX
    await new Promise(resolve => setTimeout(resolve, 500));

    const result = login(email, password);

    if (result.success) {
      router.push('/edge/portal/sports');
    } else {
      setError(result.error || 'Login failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="terminal-login">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap');

        .terminal-login {
          min-height: 100vh;
          background:
            radial-gradient(ellipse at 50% 60%, rgba(8, 6, 4, 0.15) 0%, rgba(8, 6, 4, 0.75) 55%, rgba(8, 6, 4, 0.92) 100%),
            url('/terminal-backdrop.jpg') center center / cover no-repeat;
          background-color: #080604;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
          position: relative;
          font-family: 'Cormorant Garamond', Georgia, serif;
          overflow: hidden;
        }

        /* Subtle warm grain overlay */
        .terminal-login::before {
          content: '';
          position: absolute;
          inset: 0;
          background: 
            linear-gradient(180deg, rgba(8,6,4,0.4) 0%, transparent 30%, transparent 70%, rgba(8,6,4,0.6) 100%);
          pointer-events: none;
          z-index: 0;
        }

        .terminal-login-inner {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 400px;
          animation: terminalFadeIn 1s ease-out;
        }

        .terminal-login-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .terminal-login-logo {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          overflow: hidden;
          margin: 0 auto 1.5rem;
          border: 1px solid rgba(181, 155, 99, 0.2);
          box-shadow: 0 0 30px rgba(181, 155, 99, 0.08);
        }

        .terminal-login-logo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .terminal-login-title {
          font-family: 'Cinzel', serif;
          font-size: 1.6rem;
          font-weight: 500;
          letter-spacing: 0.18em;
          color: #e7e0d5;
          margin: 0 0 0.5rem;
          text-shadow: 0 2px 20px rgba(0,0,0,0.5);
        }

        .terminal-login-subtitle {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.9rem;
          font-style: italic;
          color: rgba(181, 155, 99, 0.4);
          letter-spacing: 0.08em;
          margin: 0 0 1.5rem;
        }

        .terminal-login-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 6px 16px;
          background: rgba(181, 155, 99, 0.06);
          border: 1px solid rgba(181, 155, 99, 0.15);
          border-radius: 2px;
        }

        .terminal-login-badge-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #b59b63;
          animation: terminalPulse 2.5s ease-in-out infinite;
        }

        .terminal-login-badge-text {
          font-family: 'Cinzel', serif;
          font-size: 0.6rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.6);
        }

        .terminal-login-card {
          background: rgba(14, 12, 10, 0.82);
          border: 1px solid rgba(181, 155, 99, 0.1);
          border-radius: 2px;
          padding: 2.5rem 2rem;
          position: relative;
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          box-shadow: 
            0 20px 60px rgba(0,0,0,0.5),
            inset 0 1px 0 rgba(181, 155, 99, 0.05);
        }

        .terminal-login-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 60px;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(181, 155, 99, 0.35), transparent);
        }

        .terminal-login-welcome {
          text-align: center;
          margin-bottom: 2rem;
        }

        .terminal-login-welcome h2 {
          font-family: 'Cinzel', serif;
          font-size: 1.1rem;
          font-weight: 500;
          letter-spacing: 0.1em;
          color: #e7e0d5;
          margin: 0 0 0.3rem;
        }

        .terminal-login-welcome p {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.88rem;
          color: rgba(181, 155, 99, 0.35);
          margin: 0;
          letter-spacing: 0.03em;
        }

        .terminal-login-field {
          margin-bottom: 1.5rem;
        }

        .terminal-login-label {
          display: block;
          font-family: 'Cinzel', serif;
          font-size: 0.6rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.45);
          margin-bottom: 0.6rem;
        }

        .terminal-login-input {
          width: 100%;
          padding: 0.8rem 1rem;
          background: rgba(8, 6, 4, 0.7);
          border: 1px solid rgba(181, 155, 99, 0.12);
          border-radius: 2px;
          color: #e7e0d5;
          font-family: 'Cormorant Garamond', serif;
          font-size: 1rem;
          letter-spacing: 0.02em;
          outline: none;
          transition: border-color 0.3s ease, box-shadow 0.3s ease;
          box-sizing: border-box;
        }

        .terminal-login-input::placeholder {
          color: rgba(181, 155, 99, 0.18);
        }

        .terminal-login-input:focus {
          border-color: rgba(181, 155, 99, 0.35);
          box-shadow: 0 0 12px rgba(181, 155, 99, 0.05);
        }

        .terminal-login-error {
          margin-bottom: 1.5rem;
          padding: 0.8rem 1rem;
          background: rgba(180, 60, 60, 0.1);
          border: 1px solid rgba(180, 60, 60, 0.2);
          border-radius: 2px;
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.9rem;
          color: #c47070;
          text-align: center;
        }

        .terminal-login-button {
          width: 100%;
          padding: 0.85rem;
          background: transparent;
          border: 1px solid rgba(181, 155, 99, 0.25);
          border-radius: 2px;
          color: #b59b63;
          font-family: 'Cinzel', serif;
          font-size: 0.72rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-top: 0.5rem;
          position: relative;
          overflow: hidden;
        }

        .terminal-login-button::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, transparent, rgba(181, 155, 99, 0.04), transparent);
          transform: translateX(-100%);
          transition: transform 0.6s ease;
        }

        .terminal-login-button:hover::before {
          transform: translateX(100%);
        }

        .terminal-login-button:hover {
          background: rgba(181, 155, 99, 0.06);
          border-color: rgba(181, 155, 99, 0.45);
          box-shadow: 0 0 20px rgba(181, 155, 99, 0.06);
        }

        .terminal-login-button:disabled {
          opacity: 0.35;
          cursor: not-allowed;
        }

        .terminal-login-button:disabled:hover::before {
          transform: translateX(-100%);
        }

        .terminal-login-divider {
          position: relative;
          margin: 1.8rem 0;
          text-align: center;
        }

        .terminal-login-divider::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 1px;
          background: rgba(181, 155, 99, 0.08);
        }

        .terminal-login-divider span {
          position: relative;
          z-index: 1;
          padding: 0 1rem;
          background: rgba(14, 12, 10, 0.95);
          font-family: 'Cinzel', serif;
          font-size: 0.55rem;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.25);
        }

        .terminal-login-beta {
          text-align: center;
        }

        .terminal-login-beta p {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.85rem;
          color: rgba(181, 155, 99, 0.25);
          margin: 0 0 0.8rem;
        }

        .terminal-login-beta a {
          font-family: 'Cinzel', serif;
          font-size: 0.6rem;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.4);
          text-decoration: none;
          transition: color 0.3s ease;
        }

        .terminal-login-beta a:hover {
          color: #b59b63;
        }

        .terminal-login-footer {
          text-align: center;
          margin-top: 2rem;
        }

        .terminal-login-footer a {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.8rem;
          color: rgba(181, 155, 99, 0.2);
          letter-spacing: 0.08em;
          text-decoration: none;
          transition: color 0.3s ease;
        }

        .terminal-login-footer a:hover {
          color: rgba(181, 155, 99, 0.5);
        }

        @keyframes terminalFadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes terminalPulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }

        /* Responsive */
        @media (max-width: 480px) {
          .terminal-login-card {
            padding: 2rem 1.5rem;
          }
          .terminal-login-title {
            font-size: 1.35rem;
          }
        }
      `}</style>

      <div className="terminal-login-inner">
        {/* Header */}
        <div className="terminal-login-header">
          <div className="terminal-login-logo">
            <img src="/hecate-logo.png" alt="OMI" />
          </div>
          <h1 className="terminal-login-title">OMI Terminal</h1>
          <p className="terminal-login-subtitle">Predictive Market Intelligence</p>
          <div className="terminal-login-badge">
            <div className="terminal-login-badge-dot" />
            <span className="terminal-login-badge-text">Early Access</span>
          </div>
        </div>

        {/* Login Card */}
        <div className="terminal-login-card">
          <div className="terminal-login-welcome">
            <h2>Welcome Back</h2>
            <p>Sign in to access your terminal</p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Error */}
            {error && (
              <div className="terminal-login-error">{error}</div>
            )}

            {/* Email */}
            <div className="terminal-login-field">
              <label className="terminal-login-label">Email Address</label>
              <input
                type="email"
                className="terminal-login-input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            {/* Password */}
            <div className="terminal-login-field">
              <label className="terminal-login-label">Password</label>
              <input
                type="password"
                className="terminal-login-input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="terminal-login-button"
            >
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          {/* Divider */}
          <div className="terminal-login-divider">
            <span>Private Beta</span>
          </div>

          {/* Beta Info */}
          <div className="terminal-login-beta">
            <p>OMI Terminal is currently in private beta.</p>
            <Link href="/">
              Request Access &rarr;
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="terminal-login-footer">
          <Link href="/">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
