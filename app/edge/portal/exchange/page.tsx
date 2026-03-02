"use client";

import { useState, useEffect } from "react";
import Terminal from "@/components/terminal/Terminal";

export default function ExchangePage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = sessionStorage.getItem("omni-exchange-auth");
    if (stored === "true") setAuthenticated(true);
  }, []);

  if (!mounted) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === "omni2026") {
      setAuthenticated(true);
      sessionStorage.setItem("omni-exchange-auth", "true");
    } else {
      setError(true);
      setPassword("");
      setTimeout(() => setError(false), 2000);
    }
  };

  if (!authenticated) {
    return (
      <div
        style={{
          height: "calc(100vh - 56px)",
          background: "#0a0a0a",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "24px",
            width: "320px",
          }}
        >
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "32px",
                fontWeight: 700,
                color: "#FF6600",
                letterSpacing: "0.15em",
                marginBottom: "8px",
              }}
            >
              OMNI
            </div>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "10px",
                color: "rgba(255,102,0,0.4)",
                textTransform: "uppercase",
                letterSpacing: "0.3em",
              }}
            >
              Exchange Terminal
            </div>
          </div>

          <div
            style={{
              width: "100%",
              height: "1px",
              background:
                "linear-gradient(90deg, transparent, rgba(255,102,0,0.2), transparent)",
            }}
          />

          <div style={{ width: "100%" }}>
            <label
              style={{
                display: "block",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "9px",
                color: "#666",
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                marginBottom: "8px",
              }}
            >
              Access Code
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoFocus
              placeholder="Enter access code"
              style={{
                width: "100%",
                background: "#111",
                border: error ? "1px solid #FF3366" : "1px solid #222",
                borderRadius: "4px",
                padding: "12px 16px",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "14px",
                color: "#e0e0e0",
                outline: "none",
                transition: "border-color 0.2s",
                boxSizing: "border-box",
              }}
              onFocus={(e) => {
                if (!error) e.currentTarget.style.borderColor = "rgba(255,102,0,0.5)";
              }}
              onBlur={(e) => {
                if (!error) e.currentTarget.style.borderColor = "#222";
              }}
            />
            {error && (
              <div
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: "10px",
                  color: "#FF3366",
                  marginTop: "8px",
                }}
              >
                Invalid access code
              </div>
            )}
          </div>

          <button
            type="submit"
            style={{
              width: "100%",
              background: "#FF6600",
              color: "#000",
              border: "none",
              borderRadius: "4px",
              padding: "12px",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "12px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              cursor: "pointer",
              transition: "opacity 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = "0.85";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "1";
            }}
          >
            Authenticate
          </button>

          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "8px",
              color: "#333",
              textTransform: "uppercase",
              letterSpacing: "0.2em",
            }}
          >
            Restricted Access
          </div>
        </form>
      </div>
    );
  }

  return (
    <div style={{ height: "calc(100vh - 56px)", overflow: "hidden" }}>
      <Terminal />
    </div>
  );
}
