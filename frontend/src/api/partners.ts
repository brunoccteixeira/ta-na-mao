/**
 * Partners API client
 */

const API_BASE = '/api/v1/partners';

export interface Partner {
  id: string;
  name: string;
  slug: string;
  type: string;
  logoUrl: string | null;
  ctaText: string;
  ctaUrl: string;
  description: string;
  benefits: string[];
  color: string | null;
  targetPrograms: string[] | null;
}

export async function fetchPartners(): Promise<Partner[]> {
  try {
    const res = await fetch(API_BASE);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function trackConversion(
  partnerSlug: string,
  event: 'impression' | 'click' | 'redirect',
  source: string,
): Promise<void> {
  try {
    const sessionId = getOrCreateSessionId();
    await fetch(`${API_BASE}/conversions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        partner_slug: partnerSlug,
        session_id: sessionId,
        event,
        source,
      }),
    });
  } catch {
    // Silently fail - tracking should never break the user experience
  }
}

function getOrCreateSessionId(): string {
  const key = 'tnm-session-id';
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}
