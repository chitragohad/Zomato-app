import type { Recommendation } from "./types";

export function budgetLabelToTier(label: string): "low" | "medium" | "high" {
  const n = label.toLowerCase();
  if (n === "mid") return "medium";
  return n as "low" | "medium" | "high";
}

export function ratingLabelToValue(label: string): number {
  const map: Record<string, number> = {
    Any: 0,
    "3.0+": 3,
    "4.0+": 4,
    "4.5+": 4.5,
  };
  return map[label] ?? 0;
}

export function formatLocationLine(rec: Recommendation, city: string): string {
  if (rec.location_detail && city) {
    return `${rec.location_detail}, ${city}`;
  }
  if (rec.location_detail) return rec.location_detail;
  const addr = rec.address?.trim();
  if (!addr) return "Location not available";
  const parts = addr.split(",").map((p) => p.trim()).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[parts.length - 2]}, ${parts[parts.length - 1]}`;
  }
  return addr.slice(0, 80);
}

export function splitCuisineTags(cuisine: string, max = 4): string[] {
  const tags = cuisine
    .split(/[,/]/)
    .map((t) => t.trim())
    .filter(Boolean);
  return tags.length ? tags.slice(0, max) : cuisine ? [cuisine] : [];
}

export function formatRating(rating: number | null): string {
  if (rating == null) return "—";
  return rating.toFixed(1);
}
