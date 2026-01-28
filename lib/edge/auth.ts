// Simple localStorage-based auth for beta access
// This is a temporary solution until proper auth is implemented

const AUTH_KEY = 'omi_edge_auth';
const AUTH_EMAIL_KEY = 'omi_edge_email';

export interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
}

// Demo accounts that bypass Tier 2 restrictions
// Add investor and demo emails here
export const DEMO_ACCOUNTS: string[] = [
  // 'your-email@example.com',
  // 'dean@investor.com',
];

// Valid beta accounts (email + password pairs)
// In production, this would be a database lookup
export const BETA_ACCOUNTS: Record<string, string> = {
  'omigroup.ops@outlook.com': 'Druids08',
};

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
  // Check if email exists in beta accounts
  const validPassword = BETA_ACCOUNTS[email.toLowerCase()];

  if (!validPassword) {
    return { success: false, error: 'Email not registered for beta access' };
  }

  if (validPassword !== password) {
    return { success: false, error: 'Invalid password' };
  }

  // Store auth state
  localStorage.setItem(AUTH_KEY, 'true');
  localStorage.setItem(AUTH_EMAIL_KEY, email.toLowerCase());

  return { success: true };
}

export function logout(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem(AUTH_EMAIL_KEY);
}

export function isDemoAccount(email: string | null): boolean {
  if (!email) return false;
  return DEMO_ACCOUNTS.includes(email.toLowerCase());
}
