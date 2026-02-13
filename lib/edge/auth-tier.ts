// Server-safe tier access checking - no browser APIs
// This module can be imported by both server and client components

// Tier 2 accounts - hardcoded accounts that bypass Live In-Game paywall
export const TIER2_ACCOUNTS: string[] = [
  'omigroup.ops@outlook.com',
  'deankardamis@gmail.com',
  'sneary1996@gmail.com',
  'harleyburke12@yahoo.com',
  'jack.vaughn@klgates.com',
];

// Check if an email has Tier 2 access
export function isTier2Account(email: string | null | undefined): boolean {
  if (!email) return false;
  return TIER2_ACCOUNTS.map(e => e.toLowerCase()).includes(email.toLowerCase());
}
