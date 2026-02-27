import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="hecate-landing">
      {/* Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=Cinzel:wght@400;500;600;700&display=swap');

        .hecate-landing {
          min-height: 100vh;
          background: #0c0a09;
          color: #e7e0d5;
          font-family: 'Cormorant Garamond', Georgia, serif;
          position: relative;
          overflow-x: hidden;
        }

        /* Subtle parchment texture overlay */
        .hecate-landing::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: 
            radial-gradient(ellipse at 20% 50%, rgba(139, 109, 63, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 50%, rgba(139, 109, 63, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 0%, rgba(139, 109, 63, 0.08) 0%, transparent 40%);
          pointer-events: none;
          z-index: 0;
        }

        /* Noise texture */
        .hecate-landing::after {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          opacity: 0.03;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
          pointer-events: none;
          z-index: 0;
        }

        .hecate-content {
          position: relative;
          z-index: 1;
        }

        /* ── HEADER ── */
        .hecate-header {
          padding: 1.5rem 2rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(139, 109, 63, 0.15);
        }

        .hecate-header-left {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .hecate-logo-mark {
          width: 40px;
          height: 40px;
          border: 1.5px solid rgba(181, 155, 99, 0.5);
          border-radius: 2px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Cinzel', serif;
          font-weight: 600;
          font-size: 0.65rem;
          letter-spacing: 0.15em;
          color: #b59b63;
        }

        .hecate-logo-text {
          font-family: 'Cinzel', serif;
          font-size: 1.1rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          color: #b59b63;
          text-transform: uppercase;
        }

        .hecate-internal-link {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.85rem;
          color: rgba(181, 155, 99, 0.4);
          text-decoration: none;
          letter-spacing: 0.1em;
          transition: color 0.3s ease;
        }

        .hecate-internal-link:hover {
          color: rgba(181, 155, 99, 0.7);
        }

        /* ── HERO ── */
        .hecate-hero {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 3rem 2rem 2rem;
          text-align: center;
        }

        .hecate-ornament-top {
          width: 120px;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(181, 155, 99, 0.4), transparent);
          margin-bottom: 2rem;
        }

        .hecate-hero-title {
          font-family: 'Cinzel', serif;
          font-size: clamp(2.5rem, 5vw, 4rem);
          font-weight: 700;
          letter-spacing: 0.15em;
          color: #e7e0d5;
          margin: 0 0 0.5rem;
          text-transform: uppercase;
        }

        .hecate-hero-subtitle {
          font-family: 'Cormorant Garamond', serif;
          font-size: clamp(1rem, 2vw, 1.25rem);
          font-weight: 300;
          font-style: italic;
          color: rgba(181, 155, 99, 0.6);
          letter-spacing: 0.05em;
          margin: 0 0 2.5rem;
        }

        /* ── HECATE IMAGE ── */
        .hecate-image-container {
          position: relative;
          width: clamp(220px, 30vw, 320px);
          margin: 0 auto 1rem;
        }

        .hecate-image-container::before {
          content: '';
          position: absolute;
          top: -12px;
          left: -12px;
          right: -12px;
          bottom: -12px;
          border: 1px solid rgba(181, 155, 99, 0.15);
          border-radius: 2px;
        }

        .hecate-image-container::after {
          content: '';
          position: absolute;
          top: -6px;
          left: -6px;
          right: -6px;
          bottom: -6px;
          border: 1px solid rgba(181, 155, 99, 0.08);
          border-radius: 2px;
        }

        .hecate-image {
          width: 100%;
          display: block;
          filter: sepia(0.15) contrast(1.1) brightness(0.85);
          mix-blend-mode: lighten;
          opacity: 0.9;
          border-radius: 2px;
        }

        .hecate-image-caption {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.8rem;
          font-style: italic;
          color: rgba(181, 155, 99, 0.35);
          margin-top: 1.5rem;
          letter-spacing: 0.05em;
        }

        /* ── DIVIDER ── */
        .hecate-divider {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1.5rem;
          margin: 3rem auto;
          max-width: 400px;
          padding: 0 2rem;
        }

        .hecate-divider-line {
          flex: 1;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(181, 155, 99, 0.3), transparent);
        }

        .hecate-divider-diamond {
          width: 8px;
          height: 8px;
          border: 1px solid rgba(181, 155, 99, 0.4);
          transform: rotate(45deg);
          flex-shrink: 0;
        }

        /* ── THREE FACES HEADING ── */
        .hecate-faces-heading {
          text-align: center;
          margin-bottom: 3rem;
          padding: 0 2rem;
        }

        .hecate-faces-heading h2 {
          font-family: 'Cinzel', serif;
          font-size: clamp(1.1rem, 2vw, 1.4rem);
          font-weight: 500;
          letter-spacing: 0.25em;
          color: rgba(181, 155, 99, 0.5);
          text-transform: uppercase;
          margin: 0;
        }

        /* ── DIVISION CARDS ── */
        .hecate-cards {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1.5rem;
          max-width: 1100px;
          margin: 0 auto;
          padding: 0 2rem 4rem;
        }

        @media (max-width: 768px) {
          .hecate-cards {
            grid-template-columns: 1fr;
            max-width: 450px;
          }
        }

        .hecate-card {
          background: rgba(12, 10, 9, 0.6);
          border: 1px solid rgba(181, 155, 99, 0.12);
          border-radius: 2px;
          padding: 2.5rem 2rem;
          text-align: left;
          transition: all 0.4s ease;
          position: relative;
        }

        .hecate-card::before {
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

        .hecate-card:hover {
          border-color: rgba(181, 155, 99, 0.25);
          background: rgba(18, 15, 13, 0.8);
        }

        .hecate-card:hover::before {
          width: 80px;
        }

        .hecate-card-numeral {
          font-family: 'Cinzel', serif;
          font-size: 0.7rem;
          font-weight: 600;
          letter-spacing: 0.3em;
          color: rgba(181, 155, 99, 0.3);
          margin-bottom: 1.5rem;
          text-transform: uppercase;
        }

        .hecate-card-title {
          font-family: 'Cinzel', serif;
          font-size: 1.4rem;
          font-weight: 600;
          letter-spacing: 0.08em;
          color: #e7e0d5;
          margin: 0 0 0.4rem;
        }

        .hecate-card-slogan {
          font-family: 'Cormorant Garamond', serif;
          font-size: 1rem;
          font-weight: 400;
          font-style: italic;
          color: rgba(181, 155, 99, 0.6);
          margin: 0 0 2rem;
          letter-spacing: 0.02em;
        }

        .hecate-card-description {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.95rem;
          line-height: 1.7;
          color: rgba(231, 224, 213, 0.45);
          margin: 0 0 2rem;
        }

        .hecate-card-link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-family: 'Cinzel', serif;
          font-size: 0.75rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: #b59b63;
          text-decoration: none;
          padding: 0.7rem 0;
          border-bottom: 1px solid rgba(181, 155, 99, 0.2);
          transition: all 0.3s ease;
        }

        .hecate-card-link:hover {
          border-bottom-color: rgba(181, 155, 99, 0.6);
          color: #d4bc7c;
        }

        .hecate-card-link svg {
          width: 14px;
          height: 14px;
          transition: transform 0.3s ease;
        }

        .hecate-card-link:hover svg {
          transform: translateX(3px);
        }

        /* ── LOCKED CARD (OMI Trading) ── */
        .hecate-card-locked {
          opacity: 0.5;
          cursor: default;
        }

        .hecate-card-locked:hover {
          border-color: rgba(181, 155, 99, 0.12);
          background: rgba(12, 10, 9, 0.6);
        }

        .hecate-card-locked:hover::before {
          width: 40px;
        }

        .hecate-locked-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          font-family: 'Cinzel', serif;
          font-size: 0.65rem;
          font-weight: 500;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: rgba(181, 155, 99, 0.35);
          padding: 0.5rem 0;
          border-bottom: 1px solid rgba(181, 155, 99, 0.08);
        }

        .hecate-locked-badge svg {
          width: 12px;
          height: 12px;
        }

        /* ── FOOTER ── */
        .hecate-footer {
          border-top: 1px solid rgba(181, 155, 99, 0.1);
          padding: 2rem;
          text-align: center;
        }

        .hecate-footer-text {
          font-family: 'Cormorant Garamond', serif;
          font-size: 0.8rem;
          color: rgba(181, 155, 99, 0.25);
          letter-spacing: 0.15em;
          margin: 0;
        }

        /* ── ANIMATIONS ── */
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .hecate-hero {
          animation: fadeIn 1.2s ease-out;
        }

        .hecate-card {
          animation: fadeInUp 0.8s ease-out backwards;
        }

        .hecate-card:nth-child(1) { animation-delay: 0.2s; }
        .hecate-card:nth-child(2) { animation-delay: 0.4s; }
        .hecate-card:nth-child(3) { animation-delay: 0.6s; }
      `}</style>

      <div className="hecate-content">
        {/* Header */}
        <header className="hecate-header">
          <div className="hecate-header-left">
            <div className="hecate-logo-mark">OMI</div>
            <span className="hecate-logo-text">OMI Group</span>
          </div>
          <Link href="/internal" className="hecate-internal-link">
            Internal Login
          </Link>
        </header>

        {/* Hero */}
        <section className="hecate-hero">
          <div className="hecate-ornament-top" />

          <h1 className="hecate-hero-title">OMI Group</h1>
          <p className="hecate-hero-subtitle">Goddess of the Crossroads</p>

          <div className="hecate-image-container">
            <img
              src="/hecate.jpg"
              alt="Hecate — Triple-faced goddess, symbol of OMI"
              className="hecate-image"
            />
          </div>
          <p className="hecate-image-caption">
            Three faces. Three paths. One dominion.
          </p>
        </section>

        {/* Divider */}
        <div className="hecate-divider">
          <div className="hecate-divider-line" />
          <div className="hecate-divider-diamond" />
          <div className="hecate-divider-line" />
        </div>

        {/* Three Faces Section Header */}
        <div className="hecate-faces-heading">
          <h2>The Three Faces</h2>
        </div>

        {/* Division Cards */}
        <div className="hecate-cards">
          {/* OMI Solutions — The Key (knowledge, unlocking) */}
          <div className="hecate-card">
            <div className="hecate-card-numeral">I — The Key</div>
            <h3 className="hecate-card-title">OMI Solutions</h3>
            <p className="hecate-card-slogan">Adaptive Enterprise Systems</p>
            <p className="hecate-card-description">
              Client-based automation, engineered to transform and scale your operations.
            </p>
            <Link href="/client/login" className="hecate-card-link">
              Client Portal
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>

          {/* OMI Edge (Terminal) — The Torch (illumination, foresight) */}
          <div className="hecate-card">
            <div className="hecate-card-numeral">II — The Torch</div>
            <h3 className="hecate-card-title">OMI Edge</h3>
            <p className="hecate-card-slogan">Predictive Market Intelligence</p>
            <p className="hecate-card-description">
              See what others cannot. Data-driven foresight across every market.
            </p>
            <Link href="/edge/portal/sports" className="hecate-card-link">
              OMI Edge
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>

          {/* OMI Trading — The Serpent (power, hidden knowledge) — LOCKED */}
          <div className="hecate-card hecate-card-locked">
            <div className="hecate-card-numeral">III — The Serpent</div>
            <h3 className="hecate-card-title">OMI Trading</h3>
            <p className="hecate-card-slogan">Automated Arbitrage Trading</p>
            <p className="hecate-card-description">
              Proprietary. Internal use only.
            </p>
            <div className="hecate-locked-badge">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Restricted Access
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="hecate-footer">
          <p className="hecate-footer-text">
            OMI Group &copy; {new Date().getFullYear()}
          </p>
        </footer>
      </div>
    </div>
  );
}
