import type {
  HealthResponse,
  RecommendationResponse,
  UserPreferences,
} from "./types";

/** Railway / production backend URL (set in Vercel env at build time). */
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";

/**
 * Browser on Vercel uses same-origin `/api-proxy` (see next.config.mjs rewrites).
 * Local dev and SSR use the direct backend URL.
 */
export const API_BASE =
  typeof window !== "undefined" && BACKEND_URL
    ? "/api-proxy"
    : BACKEND_URL || "http://127.0.0.1:8000";

function networkErrorMessage(): string {
  if (!BACKEND_URL) {
    return (
      "Cannot reach API. Set NEXT_PUBLIC_API_URL in Vercel to your Railway HTTPS URL " +
      "(e.g. https://your-app.up.railway.app) and redeploy."
    );
  }
  return (
    `Cannot reach API at ${BACKEND_URL}. Confirm Railway is running, ` +
    "NEXT_PUBLIC_API_URL matches your Railway domain, and redeploy Vercel after env changes."
  );
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(networkErrorMessage());
    }
    throw err;
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail ?? body);
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchJson(`${API_BASE}/health`);
}

export async function getCities(): Promise<string[]> {
  const data = await fetchJson<{ cities: string[] }>(
    `${API_BASE}/api/metadata/cities`
  );
  return data.cities;
}

export async function getCuisines(): Promise<string[]> {
  const data = await fetchJson<{ cuisines: string[] }>(
    `${API_BASE}/api/metadata/cuisines`
  );
  return data.cuisines;
}

export async function getRecommendations(
  preferences: UserPreferences,
  options?: { topK?: number; forceFallback?: boolean }
): Promise<RecommendationResponse> {
  const params = new URLSearchParams();
  if (options?.topK != null) params.set("top_k", String(options.topK));
  if (options?.forceFallback) params.set("force_fallback", "true");
  const qs = params.toString();
  const url = `${API_BASE}/api/recommendations${qs ? `?${qs}` : ""}`;
  return fetchJson(url, {
    method: "POST",
    body: JSON.stringify(preferences),
  });
}
