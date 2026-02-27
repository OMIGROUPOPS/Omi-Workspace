import Link from "next/link";

export default function InternalHubPage() {
  return (
    <div className="hecate-hub">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap');

        .hecate-hub {
          min-height: 100vh;
          background:
            radial-gradient(ellipse at 50% 40%, rgba(12, 10, 9, 0.35) 0%, rgba(12, 10, 9, 0.88) 65%),
            url('/internal-hub-backdrop.jpg') center center / cover no-repeat;
          background-color: #0c0a09;
          font-family: 'Cormorant Garamond', Georgia, serif;
          color: #e7e0d5;
          position: relative;
          padding: 2rem;
        }

        .hecate-hub-header {
          max-width: 1000px;
          margin: 0 auto 3rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .hecate-hub-header-left {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .hecate-hub-logo {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          overflow: hidden;
          flex-shrink: 0;
        }

        .hecate-hub-logo img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .hecate-hub-title {
          font-family: 'Cinzel', serif;
          font-size: 1.1rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          color: #b59b63;
          text-transform: uppercase;
          margin: 0;
        }

        .hecate-hub-subtitle {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.85rem;
          font-style: italic;
          color: rgba(181, 155, 99, 0.4);
          margin: 0.2rem 0 0;
          letter-spacing: 0.05em;
        }

        .hecate-hub-back {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.85rem;
          color: rgba(181, 155, 99, 0.35);
          text-decoration: none;
          letter-spacing: 0.1em;
          transition: color 0.3s ease;
        }

        .hecate-hub-back:hover {
          color: rgba(181, 155, 99, 0.7);
        }

        /* Divider */
        .hecate-hub-divider {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1.5rem;
          max-width: 300px;
          margin: 0 auto 2.5rem;
        }

        .hecate-hub-divider-line {
          flex: 1;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(181, 155, 99, 0.3), transparent);
        }

        .hecate-hub-divider-diamond {
          width: 6px;
          height: 6px;
          border: 1px solid rgba(181, 155, 99, 0.4);
          transform: rotate(45deg);
          flex-shrink: 0;
        }

        .hecate-hub-section-label {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .hecate-hub-section-label h2 {
          font-family: 'Cinzel', serif;
          font-size: 1rem;
          font-weight: 500;
          letter-spacing: 0.25em;
          color: rgba(181, 155, 99, 0.45);
          text-transform: uppercase;
          margin: 0;
        }

        /* Cards */
        .hecate-hub-cards {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
          max-width: 1000px;
          margin: 0 auto;
        }

        @media (max-width: 768px) {
          .hecate-hub-cards {
            grid-template-columns: 1fr;
            max-width: 400px;
          }
        }

        .hecate-hub-card {
          background: rgba(12, 10, 9, 0.7);
          border: 1px solid rgba(181, 155, 99, 0.12);
          border-radius: 2px;
          padding: 2rem 1.75rem;
          text-align: left;
          transition: all 0.4s ease;
          position: relative;
          backdrop-filter: blur(8px);
        }

        .hecate-hub-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 40px;
          height: 1px;
          background: rgba(181, 155, 99, 0.3);
          transition: width 0.4s ease;
        }

        .hecate-hub-card:hover {
          border-color: rgba(181, 155, 99, 0.25);
          background: rgba(18, 15, 13, 0.85);
        }

        .hecate-hub-card:hover::before {
          width: 80px;
        }

        .hecate-hub-card-label {
          font-family: 'Cinzel', serif;
          font-size: 0.65rem;
          font-weight: 500;
          letter-spacing: 0.3em;
          color: rgba(181, 155, 99, 0.3);
          text-transform: uppercase;
          margin-bottom: 1.25rem;
        }

        .hecate-hub-card-title {
          font-family: 'Cinzel', serif;
          font-size: 1.3rem;
          font-weight: 600;
          letter-spacing: 0.06em;
          color: #e7e0d5;
          margin: 0 0 0.35rem;
        }

        .hecate-hub-card-desc {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.95rem;
          font-style: italic;
          color: rgba(181, 155, 99, 0.55);
          margin: 0 0 1.75rem;
          letter-spacing: 0.02em;
        }

        .hecate-hub-card-link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-family: 'Cinzel', serif;
          font-size: 0.7rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #b59b63;
          text-decoration: none;
          padding: 0.6rem 0;
          border-bottom: 1px solid rgba(181, 155, 99, 0.2);
          transition: all 0.3s ease;
        }

        .hecate-hub-card-link:hover {
          border-bottom-color: rgba(181, 155, 99, 0.6);
          color: #d4bc7c;
        }

        .hecate-hub-card-link svg {
          width: 14px;
          height: 14px;
          transition: transform 0.3s ease;
        }

        .hecate-hub-card-link:hover svg {
          transform: translateX(3px);
        }

        /* Animations */
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .hecate-hub-card {
          animation: fadeInUp 0.7s ease-out backwards;
        }

        .hecate-hub-card:nth-child(1) { animation-delay: 0.15s; }
        .hecate-hub-card:nth-child(2) { animation-delay: 0.3s; }
        .hecate-hub-card:nth-child(3) { animation-delay: 0.45s; }
      `}</style>

      {/* Header */}
      <header className="hecate-hub-header">
        <div className="hecate-hub-header-left">
          <div className="hecate-hub-logo">
            <img src="/hecate-logo.png" alt="OMI" />
          </div>
          <div>
            <h1 className="hecate-hub-title">OMI Internal</h1>
            <p className="hecate-hub-subtitle">Operator Dashboard</p>
          </div>
        </div>
        <Link href="/" className="hecate-hub-back">
          Home
        </Link>
      </header>

      {/* Divider */}
      <div className="hecate-hub-divider">
        <div className="hecate-hub-divider-line" />
        <div className="hecate-hub-divider-diamond" />
        <div className="hecate-hub-divider-line" />
      </div>

      {/* Section Label */}
      <div className="hecate-hub-section-label">
        <h2>Operations</h2>
      </div>

      {/* Cards */}
      <div className="hecate-hub-cards">
        {/* Solutions Internal */}
        <div className="hecate-hub-card">
          <div className="hecate-hub-card-label">Automation</div>
          <h3 className="hecate-hub-card-title">Solutions</h3>
          <p className="hecate-hub-card-desc">Client Management</p>
          <Link href="/dashboard" className="hecate-hub-card-link">
            Enter
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>

        {/* Edge Internal */}
        <div className="hecate-hub-card">
          <div className="hecate-hub-card-label">Intelligence</div>
          <h3 className="hecate-hub-card-title">Edge</h3>
          <p className="hecate-hub-card-desc">Performance & Grading</p>
          <Link href="/internal/edge" className="hecate-hub-card-link">
            Enter
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>

        {/* Trading Internal */}
        <div className="hecate-hub-card">
          <div className="hecate-hub-card-label">Quantitative</div>
          <h3 className="hecate-hub-card-title">Trading</h3>
          <p className="hecate-hub-card-desc">Arb Scanner & Execution</p>
          <Link href="/internal/trading" className="hecate-hub-card-link">
            Enter
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
