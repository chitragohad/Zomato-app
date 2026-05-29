import type {
  HealthResponse,
  RecommendationResponse,
  UserPreferences,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
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

export { API_BASE };
