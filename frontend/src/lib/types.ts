export type BudgetTier = "low" | "medium" | "high";

export interface UserPreferences {
  location: string;
  budget: BudgetTier;
  cuisine?: string | null;
  min_rating: number;
  additional_preferences?: string | null;
}

export interface Recommendation {
  rank: number;
  restaurant_id: string;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: string;
  explanation: string;
  location_detail?: string | null;
  address: string;
}

export interface RecommendationResponse {
  summary: string | null;
  recommendations: Recommendation[];
  used_fallback: boolean;
}

export interface HealthResponse {
  status: string;
  restaurants_loaded?: number;
  llm_provider?: string;
  llm_available?: boolean;
  cache_path?: string;
  error?: string;
}

export interface FilterState {
  location: string;
  budget: "Low" | "Mid" | "High";
  cuisine: string;
  minRating: "Any" | "3.0+" | "4.0+" | "4.5+";
  additional: string;
  topK: number;
  forceFallback: boolean;
}
