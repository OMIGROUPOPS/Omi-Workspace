"use client";

import { useState } from "react";
import { signInWithEmail } from "@/lib/supabaseAuth";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    const { error } = await signInWithEmail({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    window.location.href = "/internal";
  };

  return (
    <div className="hecate-login">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap');

        .hecate-login {
          min-height: 100vh;
          background: #0c0a09;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
          position: relative;
          font-family: 'Cormorant Garamond', Georgia, serif;
        }

        .hecate-login::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('/internal-backdrop.jpg') center center / cover no-repeat;
          opacity: 0.4;
          pointer-events: none;
        }

        .hecate-login::after {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: radial-gradient(ellipse at 50% 50%, rgba(12, 10, 9, 0.5) 0%, rgba(12, 10, 9, 0.9) 70%);
          pointer-events: none;
        }

        .hecate-login-inner {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 400px;
        }

        .hecate-login-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .hecate-login-logo {
          width: 64px;
          height: 64px;
          border-radius: 50%;
          overflow: hidden;
          margin: 0 auto 1.5rem;
        }

        .hecate-login-logo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .hecate-login-title {
          font-family: 'Cinzel', serif;
          font-size: 1.5rem;
          font-weight: 500;
          letter-spacing: 0.15em;
          color: #e7e0d5;
          margin: 0 0 0.4rem;
        }

        .hecate-login-subtitle {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.95rem;
          font-style: italic;
          color: rgba(181, 155, 99, 0.45);
          letter-spacing: 0.05em;
          margin: 0;
        }

        .hecate-login-card {
          background: rgba(18, 15, 13, 0.8);
          border: 1px solid rgba(181, 155, 99, 0.12);
          border-radius: 2px;
          padding: 2.5rem 2rem;
          position: relative;
        }

        .hecate-login-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 60px;
          height: 1px;
          background: rgba(181, 155, 99, 0.3);
        }

        .hecate-login-error {
          margin-bottom: 1.5rem;
          padding: 0.8rem 1rem;
          background: rgba(180, 60, 60, 0.1);
          border: 1px solid rgba(180, 60, 60, 0.2);
          border-radius: 2px;
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.9rem;
          color: #c47070;
        }

        .hecate-login-field {
          margin-bottom: 1.5rem;
        }

        .hecate-login-label {
          display: block;
          font-family: 'Cinzel', serif;
          font-size: 0.65rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.5);
          margin-bottom: 0.6rem;
        }

        .hecate-login-input {
          width: 100%;
          padding: 0.8rem 1rem;
          background: rgba(12, 10, 9, 0.8);
          border: 1px solid rgba(181, 155, 99, 0.15);
          border-radius: 2px;
          color: #e7e0d5;
          font-family: 'Cormorant Garamond', serif;
          font-size: 1rem;
          letter-spacing: 0.02em;
          outline: none;
          transition: border-color 0.3s ease;
          box-sizing: border-box;
        }

        .hecate-login-input::placeholder {
          color: rgba(181, 155, 99, 0.2);
        }

        .hecate-login-input:focus {
          border-color: rgba(181, 155, 99, 0.4);
        }

        .hecate-login-button {
          width: 100%;
          padding: 0.8rem;
          background: transparent;
          border: 1px solid rgba(181, 155, 99, 0.3);
          border-radius: 2px;
          color: #b59b63;
          font-family: 'Cinzel', serif;
          font-size: 0.75rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-top: 0.5rem;
        }

        .hecate-login-button:hover {
          background: rgba(181, 155, 99, 0.08);
          border-color: rgba(181, 155, 99, 0.5);
        }

        .hecate-login-button:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .hecate-login-signup {
          text-align: center;
          margin-top: 1.5rem;
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.9rem;
          color: rgba(181, 155, 99, 0.3);
        }

        .hecate-login-signup a {
          color: rgba(181, 155, 99, 0.6);
          text-decoration: none;
          transition: color 0.3s ease;
        }

        .hecate-login-signup a:hover {
          color: #b59b63;
        }

        .hecate-login-footer {
          text-align: center;
          margin-top: 2rem;
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.8rem;
          color: rgba(181, 155, 99, 0.2);
          letter-spacing: 0.1em;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .hecate-login-inner {
          animation: fadeIn 0.8s ease-out;
        }
      `}</style>

      <div className="hecate-login-inner">
        {/* Header */}
        <div className="hecate-login-header">
          <div className="hecate-login-logo">
            <img src="/hecate-logo.png" alt="OMI" />
          </div>
          <h1 className="hecate-login-title">Internal Access</h1>
          <p className="hecate-login-subtitle">OMI Group Operations</p>
        </div>

        {/* Login Card */}
        <div className="hecate-login-card">
          {error && (
            <div className="hecate-login-error">{error}</div>
          )}

          <div className="hecate-login-field">
            <label className="hecate-login-label">Email</label>
            <input
              type="email"
              className="hecate-login-input"
              placeholder="operator@omigroup.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            />
          </div>

          <div className="hecate-login-field">
            <label className="hecate-login-label">Password</label>
            <input
              type="password"
              className="hecate-login-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="hecate-login-button"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>

          <p className="hecate-login-signup">
            No account?{" "}
            <Link href="/signup">Request access</Link>
          </p>
        </div>

        {/* Footer */}
        <p className="hecate-login-footer">
          OMI Group &copy; {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );
}
