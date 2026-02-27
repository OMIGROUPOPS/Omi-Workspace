'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getAuthState, logout } from '@/lib/edge/auth';
import { isTier2Account } from '@/lib/edge/auth-tier';

interface NavItem {
  key: string;
  label: string;
  href: string;
  icon: React.ReactNode;
  tier?: number;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    label: 'Tier 1',
    items: [
      {
        key: 'sports',
        label: 'Game Markets',
        href: '/edge/portal/sports',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" strokeWidth="1.5" />
            <path strokeLinecap="round" strokeWidth="1.5" d="M12 2c-2.5 3-4 6.5-4 10s1.5 7 4 10M12 2c2.5 3 4 6.5 4 10s-1.5 7-4 10M2 12h20" />
          </svg>
        ),
      },
      {
        key: 'props',
        label: 'Player Props',
        href: '/edge/portal/props',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ),
      },
      {
        key: 'fantasy',
        label: 'Fantasy',
        href: '/edge/portal/fantasy',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        ),
      },
    ],
  },
  {
    label: 'Tier 2',
    items: [
      {
        key: 'live',
        label: 'Live Markets',
        href: '/edge/portal/live',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
          </svg>
        ),
        tier: 2,
      },
      {
        key: 'exchanges',
        label: 'Live Edge Tracker',
        href: '/edge/portal/exchanges',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
          </svg>
        ),
        tier: 2,
      },
      {
        key: 'trading',
        label: 'ARB Trading',
        href: '/edge/portal/trading',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        ),
        tier: 2,
      },
    ],
  },
  {
    label: 'System',
    items: [
      {
        key: 'settings',
        label: 'Settings',
        href: '/edge/portal/settings',
        icon: (
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        ),
      },
    ],
  },
];

function Logo() {
  return (
    <a href="/edge/portal/sports" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
      <img
        src="/hecate-logo.png"
        alt="OMI"
        style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'cover' }}
      />
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{
          fontFamily: "'Cinzel', serif",
          fontSize: '12px',
          fontWeight: 600,
          letterSpacing: '0.12em',
          color: '#e7e0d5',
          lineHeight: 1.2,
        }}>
          OMI <span style={{ color: '#b59b63' }}>TERMINAL</span>
        </span>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '8px',
          color: 'rgba(181,155,99,0.35)',
          textTransform: 'uppercase' as const,
          letterSpacing: '0.2em',
          lineHeight: 1.2,
        }}>
          Analytics
        </span>
      </div>
    </a>
  );
}

function Sidebar({ isOpen, onClose, onLogout, userEmail }: { isOpen: boolean; onClose: () => void; onLogout: () => void; userEmail: string | null }) {
  const pathname = usePathname();
  const userTier = isTier2Account(userEmail) ? 2 : 1;
  console.log('[Layout] userEmail:', userEmail, '| userTier:', userTier);

  return (
    <>
      {isOpen && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 40, backdropFilter: 'blur(4px)' }}
          className="lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-52
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto flex flex-col
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        style={{
          background: '#0d0d0d',
          borderRight: '1px solid #1a1a1a',
        }}
      >
        {/* Logo */}
        <div style={{
          height: '56px',
          padding: '0 12px',
          display: 'flex',
          alignItems: 'center',
          borderBottom: '1px solid #1a1a1a',
          flexShrink: 0,
        }}>
          <Logo />
          <button
            onClick={onClose}
            className="ml-auto lg:hidden"
            style={{ padding: '6px', color: 'rgba(181,155,99,0.4)' }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '8px', overflowY: 'auto' }}>
          {NAV_SECTIONS.map((section, sIdx) => (
            <div key={section.label} style={{ marginTop: sIdx > 0 ? '16px' : '0' }}>
              <div style={{ padding: '0 10px', marginBottom: '6px' }}>
                <span style={{
                  fontFamily: "'Cinzel', serif",
                  fontSize: '9px',
                  fontWeight: 500,
                  color: 'rgba(181,155,99,0.3)',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.2em',
                }}>
                  {section.label}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                {section.items.map((item) => {
                  const isActive = pathname.startsWith(item.href);
                  const isLocked = item.tier && item.tier > userTier;

                  return (
                    <a
                      key={item.key}
                      href={isLocked ? '/edge/pricing' : item.href}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '7px 10px',
                        borderRadius: '3px',
                        fontSize: '13px',
                        fontFamily: "'Cormorant Garamond', Georgia, serif",
                        fontWeight: 500,
                        textDecoration: 'none',
                        transition: 'all 0.2s ease',
                        color: isActive ? '#e7e0d5' : 'rgba(181,155,99,0.45)',
                        background: isActive ? 'rgba(181,155,99,0.08)' : 'transparent',
                        borderLeft: isActive ? '2px solid #b59b63' : '2px solid transparent',
                        opacity: isLocked ? 0.35 : 1,
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) {
                          e.currentTarget.style.color = '#e7e0d5';
                          e.currentTarget.style.background = 'rgba(181,155,99,0.04)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) {
                          e.currentTarget.style.color = 'rgba(181,155,99,0.45)';
                          e.currentTarget.style.background = 'transparent';
                        }
                      }}
                    >
                      {item.icon}
                      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.label}</span>
                      {isLocked && (
                        <span style={{
                          fontFamily: "'JetBrains Mono', monospace",
                          fontSize: '7px',
                          background: 'rgba(181,155,99,0.08)',
                          color: 'rgba(181,155,99,0.35)',
                          padding: '2px 5px',
                          borderRadius: '2px',
                          letterSpacing: '0.15em',
                          border: '1px solid rgba(181,155,99,0.1)',
                          flexShrink: 0,
                        }}>
                          PRO
                        </span>
                      )}
                      {isActive && (
                        <div style={{
                          width: '4px',
                          height: '4px',
                          borderRadius: '50%',
                          background: '#b59b63',
                          boxShadow: '0 0 6px rgba(181,155,99,0.4)',
                          flexShrink: 0,
                        }} />
                      )}
                    </a>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Status Footer */}
        <div style={{
          padding: '8px',
          borderTop: '1px solid #1a1a1a',
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}>
          {/* User Info */}
          {userEmail && (
            <div style={{
              background: 'rgba(181,155,99,0.04)',
              border: '1px solid rgba(181,155,99,0.08)',
              borderRadius: '3px',
              padding: '10px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  background: 'rgba(181,155,99,0.1)',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <span style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '8px',
                    fontWeight: 700,
                    color: '#b59b63',
                  }}>
                    {userEmail.slice(0, 2).toUpperCase()}
                  </span>
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <p style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '9px',
                    color: 'rgba(181,155,99,0.5)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    margin: 0,
                  }}>
                    {userEmail}
                  </p>
                  <p style={{
                    fontFamily: "'Cinzel', serif",
                    fontSize: '7px',
                    color: 'rgba(181,155,99,0.25)',
                    textTransform: 'uppercase' as const,
                    letterSpacing: '0.15em',
                    margin: 0,
                  }}>
                    Beta Access
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* System Status */}
          <div style={{
            background: 'rgba(181,155,99,0.04)',
            border: '1px solid rgba(181,155,99,0.08)',
            borderRadius: '3px',
            padding: '10px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <div style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#22c55e',
                boxShadow: '0 0 6px rgba(34,197,94,0.4)',
              }} />
              <span style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '8px',
                color: 'rgba(181,155,99,0.4)',
                textTransform: 'uppercase' as const,
                letterSpacing: '0.15em',
              }}>
                System Online
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
              <div style={{
                background: 'rgba(0,0,0,0.3)',
                borderRadius: '2px',
                padding: '4px 6px',
                border: '1px solid rgba(181,155,99,0.06)',
              }}>
                <span style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '7px',
                  color: 'rgba(181,155,99,0.25)',
                  display: 'block',
                }}>TIER</span>
                <span style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '10px',
                  color: '#b59b63',
                  fontWeight: 600,
                }}>{userTier}</span>
              </div>
              <div style={{
                background: 'rgba(0,0,0,0.3)',
                borderRadius: '2px',
                padding: '4px 6px',
                border: '1px solid rgba(181,155,99,0.06)',
              }}>
                <span style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '7px',
                  color: 'rgba(181,155,99,0.25)',
                  display: 'block',
                }}>API</span>
                <span style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '10px',
                  color: '#22c55e',
                  fontWeight: 600,
                }}>OK</span>
              </div>
            </div>
          </div>

          {/* Upgrade */}
          <Link
            href="/edge/pricing"
            style={{
              display: 'block',
              width: '100%',
              textAlign: 'center',
              fontFamily: "'Cinzel', serif",
              fontSize: '9px',
              fontWeight: 500,
              color: '#b59b63',
              background: 'transparent',
              border: '1px solid rgba(181,155,99,0.15)',
              borderRadius: '2px',
              padding: '7px 0',
              textTransform: 'uppercase' as const,
              letterSpacing: '0.18em',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(181,155,99,0.06)';
              e.currentTarget.style.borderColor = 'rgba(181,155,99,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'rgba(181,155,99,0.15)';
            }}
          >
            Upgrade Plan
          </Link>

          {/* Logout */}
          <button
            onClick={onLogout}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontFamily: "'Cinzel', serif",
              fontSize: '9px',
              fontWeight: 500,
              color: 'rgba(181,155,99,0.3)',
              background: 'transparent',
              border: '1px solid rgba(181,155,99,0.08)',
              borderRadius: '2px',
              padding: '7px 0',
              textTransform: 'uppercase' as const,
              letterSpacing: '0.18em',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#c47070';
              e.currentTarget.style.borderColor = 'rgba(196,112,112,0.25)';
              e.currentTarget.style.background = 'rgba(196,112,112,0.04)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'rgba(181,155,99,0.3)';
              e.currentTarget.style.borderColor = 'rgba(181,155,99,0.08)';
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </aside>
    </>
  );
}

function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const pathname = usePathname();
  const [currentTime, setCurrentTime] = useState<Date | null>(null);

  useEffect(() => {
    setCurrentTime(new Date());
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getPageTitle = () => {
    if (pathname.includes('/sports/game/')) return 'Game Analysis';
    if (pathname.includes('/sports/')) return 'Sports Markets';
    if (pathname.includes('/exchanges')) return 'Prediction Exchanges';
    if (pathname.includes('/results')) return 'Results';
    if (pathname.includes('/events')) return 'Events';
    return 'Sports Markets';
  };

  return (
    <header style={{
      height: '56px',
      background: '#0d0d0d',
      borderBottom: '1px solid #1a1a1a',
      padding: '0 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 30,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onMenuClick}
          className="lg:hidden"
          style={{
            padding: '8px',
            color: 'rgba(181,155,99,0.4)',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '4px',
          }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '3px',
            height: '18px',
            background: 'linear-gradient(180deg, #b59b63, rgba(181,155,99,0.3))',
            borderRadius: '2px',
          }} />
          <span style={{
            fontFamily: "'Cinzel', serif",
            fontSize: '13px',
            fontWeight: 500,
            color: '#e7e0d5',
            letterSpacing: '0.08em',
          }}>
            {getPageTitle()}
          </span>
        </div>

        {pathname.includes('/sports/game/') && (
          <div className="hidden sm:flex" style={{ alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <span style={{ color: 'rgba(181,155,99,0.2)' }}>/</span>
            <Link
              href="/edge/portal/sports"
              style={{
                color: 'rgba(181,155,99,0.4)',
                textDecoration: 'none',
                fontFamily: "'Cormorant Garamond', serif",
                transition: 'color 0.2s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = '#b59b63'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(181,155,99,0.4)'; }}
            >
              Markets
            </Link>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Live Clock */}
        <div className="hidden sm:flex" style={{
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          background: 'rgba(181,155,99,0.04)',
          borderRadius: '3px',
          border: '1px solid rgba(181,155,99,0.08)',
        }}>
          <div style={{
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 6px rgba(34,197,94,0.4)',
            animation: 'omiClockPulse 2s ease-in-out infinite',
          }} />
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '11px',
            color: 'rgba(181,155,99,0.6)',
          }} suppressHydrationWarning>
            {currentTime ? currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : '--:--:--'}
          </span>
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '9px',
            color: 'rgba(181,155,99,0.25)',
          }}>ET</span>
        </div>

        <div style={{ width: '1px', height: '24px', background: 'rgba(181,155,99,0.08)' }} />

        {/* Notification */}
        <button
          style={{
            padding: '8px',
            color: 'rgba(181,155,99,0.35)',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '4px',
            position: 'relative',
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = '#b59b63'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(181,155,99,0.35)'; }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span style={{
            position: 'absolute',
            top: '4px',
            right: '4px',
            width: '6px',
            height: '6px',
            background: '#b59b63',
            borderRadius: '50%',
            border: '1.5px solid #0d0d0d',
          }} />
        </button>

        {/* User Avatar */}
        <button
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 8px',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '4px',
            transition: 'background 0.2s',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(181,155,99,0.04)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
        >
          <div style={{
            width: '28px',
            height: '28px',
            background: 'rgba(181,155,99,0.08)',
            border: '1px solid rgba(181,155,99,0.15)',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <span style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '9px',
              fontWeight: 700,
              color: '#b59b63',
            }}>OG</span>
          </div>
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: 'rgba(181,155,99,0.25)' }}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </header>
  );
}

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const router = useRouter();

  // Check auth on mount
  useEffect(() => {
    const authState = getAuthState();
    console.log('[Layout] authState:', { isAuthenticated: authState.isAuthenticated, email: authState.email });
    if (!authState.isAuthenticated) {
      router.replace('/edge/login');
    } else {
      setUserEmail(authState.email);
      setIsLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    logout();
    router.replace('/edge/login');
  };

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#0a0a0a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            border: '2px solid rgba(181,155,99,0.15)',
            borderTop: '2px solid #b59b63',
            borderRadius: '50%',
            animation: 'omiSpin 1s linear infinite',
          }} />
          <span style={{
            fontFamily: "'Cinzel', serif",
            fontSize: '10px',
            color: 'rgba(181,155,99,0.3)',
            textTransform: 'uppercase',
            letterSpacing: '0.2em',
          }}>Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Nuclear CSS reset — kill all Tailwind light-mode leaks */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        .omi-terminal-shell,
        .omi-terminal-shell *,
        .omi-terminal-shell *::before,
        .omi-terminal-shell *::after {
          border-color: #1a1a1a !important;
        }

        .omi-terminal-shell .bg-white,
        .omi-terminal-shell .bg-gray-50,
        .omi-terminal-shell .bg-gray-100 {
          background-color: #0d0d0d !important;
        }

        .omi-terminal-shell .border-gray-200,
        .omi-terminal-shell .border-\\[\\#e2e4e8\\] {
          border-color: #1a1a1a !important;
        }

        @keyframes omiSpin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes omiClockPulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>

      <div
        className="omi-terminal-shell"
        style={{
          minHeight: '100vh',
          background: '#0a0a0a',
          color: '#e7e0d5',
          display: 'flex',
        }}
      >
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} onLogout={handleLogout} userEmail={userEmail} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <Header onMenuClick={() => setSidebarOpen(true)} />
          <main style={{ flex: 1, overflowY: 'auto', background: '#0a0a0a' }}>{children}</main>
        </div>
      </div>
    </>
  );
}
