// Beta authentication - uses environment variables for credentials
// NOTE: This is temporary until proper Supabase Auth is implemented

const AUTH_KEY = 'omi_edge_auth';
const AUTH_EMAIL_KEY = 'omi_edge_email';

export interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
}

// Demo accounts that bypass Tier 2 restrictions (from env var)
// Format: comma-separated emails in DEMO_ACCOUNTS env var
function getDemoAccounts(): string[] {
  const envAccounts = process.env.NEXT_PUBLIC_DEMO_ACCOUNTS || '';
  return envAccounts.split(',').map(e => e.trim().toLowerCase()).filter(Boolean);
}

// Beta accounts loaded from environment variable
// Format: BETA_ACCOUNTS="email1:password1,email2:password2"
function getBetaAccounts(): Record<string, string> {
  const envAccounts = process.env.BETA_ACCOUNTS || '';
  const accounts: Record<string, string> = {};

  envAccounts.split(',').forEach(pair => {
    const [email, password] = pair.split(':').map(s => s.trim());
    if (email && password) {
      accounts[email.toLowerCase()] = password;
    }
  });

  return accounts;
}

export function getAuthState(): AuthState {
  if (typeof window === 'undefined') {
    return { isAuthenticated: false, email: null };
  }

  const auth = localStorage.getItem(AUTH_KEY);
  const email = localStorage.getItem(AUTH_EMAIL_KEY);

  return {
    isAuthenticated: auth === 'true',
    email: email || null,
  };
}

export function login(email: string, password: string): { success: boolean; error?: string } {
  const betaAccounts = getBetaAccounts();
  const normalizedEmail = email.toLowerCase().trim();

  // Check if email exists in beta accounts
  const validPassword = betaAccounts[normalizedEmail];

  if (!validPassword) {
    return { success: false, error: 'Email not registered for beta access' };
  }

  if (validPassword !== password) {
    return { success: false, error: 'Invalid password' };
  }

  // Store auth state
  localStorage.setItem(AUTH_KEY, 'true');
  localStorage.setItem(AUTH_EMAIL_KEY, normalizedEmail);

  return { success: true };
}

export function logout(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(AUTH_EMAIL_KEY);
}

export function isDemoAccount(email: string | null): boolean {
  if (!email) return false;
  const demoAccounts = getDemoAccounts();
  return demoAccounts.includes(email.toLowerCase());
}

// For components that import DEMO_ACCOUNTS directly
export const DEMO_ACCOUNTS: string[] = [];
