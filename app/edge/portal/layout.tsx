'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getAuthState, logout } from '@/lib/edge/auth';

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
        label: 'Exchange Markets',
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
    <a href="/edge/portal/sports" className="flex items-center gap-2.5 cursor-pointer">
      <div className="w-7 h-7 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded flex items-center justify-center flex-shrink-0">
        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-bold text-zinc-100 leading-tight tracking-tight">
          OMI <span className="text-emerald-400">EDGE</span>
        </span>
        <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest leading-tight">Terminal</span>
      </div>
    </a>
  );
}

function Sidebar({ isOpen, onClose, onLogout, userEmail }: { isOpen: boolean; onClose: () => void; onLogout: () => void; userEmail: string | null }) {
  const pathname = usePathname();
  const userTier = 2; // Allow access to Tier 2 features (Live Markets, ARB Trading)

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm" onClick={onClose} />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-52 bg-[#0a0a0a] border-r border-zinc-800/80
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto flex flex-col
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-14 px-3 flex items-center border-b border-zinc-800/80 flex-shrink-0">
          <Logo />
          <button onClick={onClose} className="ml-auto lg:hidden p-1.5 text-zinc-400 hover:text-zinc-100">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 overflow-y-auto">
          {NAV_SECTIONS.map((section, sIdx) => (
            <div key={section.label} className={sIdx > 0 ? 'mt-4' : ''}>
              <div className="px-2.5 mb-1.5">
                <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">{section.label}</span>
              </div>
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive = pathname.startsWith(item.href);
                  const isLocked = item.tier && item.tier > userTier;

                  return (
                    <a
                      key={item.key}
                      href={isLocked ? '/edge/pricing' : item.href}
                      className={`
                        flex items-center gap-2 px-2.5 py-1.5 rounded-md transition-all text-[13px]
                        ${isActive
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 border border-transparent'
                        }
                        ${isLocked ? 'opacity-50' : ''}
                      `}
                    >
                      {item.icon}
                      <span className="font-medium flex-1 truncate">{item.label}</span>
                      {isLocked && (
                        <span className="text-[8px] font-mono bg-zinc-800 text-zinc-500 px-1 py-0.5 rounded flex-shrink-0 tracking-wider">PRO</span>
                      )}
                      {isActive && (
                        <div className="w-1 h-1 rounded-full bg-emerald-400 flex-shrink-0" />
                      )}
                    </a>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Status Footer */}
        <div className="p-2 border-t border-zinc-800/80 flex-shrink-0 space-y-2">
          {/* User Info */}
          {userEmail && (
            <div className="bg-zinc-900/50 rounded-md p-2.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-emerald-500/20 rounded flex items-center justify-center flex-shrink-0">
                  <span className="text-[9px] font-mono font-bold text-emerald-400">
                    {userEmail.slice(0, 2).toUpperCase()}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] text-zinc-400 truncate">{userEmail}</p>
                  <p className="text-[8px] font-mono text-zinc-600 uppercase">Beta Access</p>
                </div>
              </div>
            </div>
          )}

          {/* System Status */}
          <div className="bg-zinc-900/50 rounded-md p-2.5">
            <div className="flex items-center gap-1.5 mb-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
              <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">System Online</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <div className="bg-zinc-800/40 rounded px-1.5 py-1">
                <span className="text-[8px] font-mono text-zinc-600 block">TIER</span>
                <span className="text-[10px] font-mono text-emerald-400 font-semibold">{userTier}</span>
              </div>
              <div className="bg-zinc-800/40 rounded px-1.5 py-1">
                <span className="text-[8px] font-mono text-zinc-600 block">API</span>
                <span className="text-[10px] font-mono text-emerald-400 font-semibold">OK</span>
              </div>
            </div>
          </div>

          {/* Upgrade */}
          <Link
            href="/edge/pricing"
            className="block w-full text-center text-[10px] font-mono font-medium text-zinc-400 bg-zinc-900/50 hover:bg-zinc-800 border border-zinc-800 rounded-md py-1.5 transition-colors uppercase tracking-wider"
          >
            Upgrade Plan
          </Link>

          {/* Logout */}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-1.5 text-[10px] font-mono font-medium text-zinc-500 hover:text-red-400 bg-zinc-900/50 hover:bg-red-500/10 border border-zinc-800 hover:border-red-500/20 rounded-md py-1.5 transition-colors uppercase tracking-wider"
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
    <header className="h-14 bg-gradient-to-r from-[#0a0a0a] to-[#0c0c0c] border-b border-zinc-800/60 px-4 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} className="lg:hidden p-2 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50 rounded-lg transition-all">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div className="flex items-center gap-3">
          <div className="w-1 h-5 bg-emerald-500 rounded-full" />
          <span className="text-sm font-semibold text-zinc-100">{getPageTitle()}</span>
        </div>

        {/* Breadcrumb for game pages */}
        {pathname.includes('/sports/game/') && (
          <div className="hidden sm:flex items-center gap-2 text-xs">
            <span className="text-zinc-600">/</span>
            <Link href="/edge/portal/sports" className="text-zinc-500 hover:text-emerald-400 transition-colors">
              Markets
            </Link>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Live Clock - Bloomberg style */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-zinc-900/60 rounded-lg border border-zinc-800/60">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-mono text-zinc-400" suppressHydrationWarning>
            {currentTime ? currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : '--:--:--'}
          </span>
          <span className="text-[10px] font-mono text-zinc-600">ET</span>
        </div>

        <div className="w-px h-6 bg-zinc-800" />

        {/* Notification */}
        <button className="p-2 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50 rounded-lg relative transition-all">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full border-2 border-[#0a0a0a]" />
        </button>

        {/* User */}
        <button className="flex items-center gap-2 px-2 py-1.5 hover:bg-zinc-800/50 rounded-lg transition-all">
          <div className="w-7 h-7 bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30 rounded-lg flex items-center justify-center">
            <span className="text-[10px] font-mono font-bold text-emerald-400">OG</span>
          </div>
          <svg className="w-3 h-3 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
          <span className="text-xs font-mono text-zinc-600 uppercase tracking-wider">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-100 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} onLogout={handleLogout} userEmail={userEmail} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
