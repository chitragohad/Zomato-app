"use client";

import { useCallback, useEffect, useState } from "react";
import { getCities, getCuisines, getRecommendations } from "@/lib/api";
import type { FilterState, RecommendationResponse } from "@/lib/types";
import { budgetLabelToTier, ratingLabelToValue } from "@/lib/utils";
import { AISummaryCard } from "./AISummaryCard";
import { RestaurantCard } from "./RestaurantCard";
import { Sidebar } from "./Sidebar";
import { WelcomeState } from "./WelcomeState";

const DEFAULT_FILTERS: FilterState = {
  location: "Bangalore",
  budget: "High",
  cuisine: "Any",
  minRating: "Any",
  additional: "",
  topK: 5,
  forceFallback: false,
};

export function HomePage() {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [cities, setCities] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [metaError, setMetaError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMeta() {
      try {
        const [cityList, cuisineList] = await Promise.all([
          getCities(),
          getCuisines(),
        ]);
        setCities(cityList);
        setCuisines(cuisineList);
        setFilters((f) => ({
          ...f,
          location: cityList.includes("Bangalore")
            ? "Bangalore"
            : cityList[0] ?? f.location,
          cuisine:
            f.cuisine === "Any" || cuisineList.includes(f.cuisine)
              ? f.cuisine
              : "Any",
        }));
      } catch (e) {
        setMetaError(
          e instanceof Error
            ? e.message
            : "Cannot reach API. Start backend: uvicorn src.api.main:app --port 8000"
        );
      }
    }
    loadMeta();
  }, []);

  const onFilterChange = useCallback(
    <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
      setError(null);
      setResponse(null);
      setHasSearched(false);
    },
    []
  );

  const onSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const result = await getRecommendations(
        {
          location: filters.location,
          budget: budgetLabelToTier(filters.budget),
          cuisine: filters.cuisine === "Any" ? null : filters.cuisine,
          min_rating: ratingLabelToValue(filters.minRating),
          additional_preferences: filters.additional.trim() || null,
        },
        { topK: filters.topK, forceFallback: filters.forceFallback }
      );
      setResponse(result);
    } catch (e) {
      setResponse(null);
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  return (
    <div className="flex h-dvh max-h-dvh min-h-0 overflow-hidden">
      <Sidebar
        filters={filters}
        cities={cities.length ? cities : [filters.location]}
        cuisines={cuisines}
        loading={loading}
        onFilterChange={onFilterChange}
        onSubmit={onSubmit}
      />

      <main className="min-h-0 min-w-0 flex-1 overflow-y-auto overscroll-y-contain bg-surface">
        <div className="px-8 py-8 lg:px-16">
          <div className="mx-auto max-w-5xl pb-12">
            {metaError && (
              <div
                role="alert"
                className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
              >
                {metaError}
              </div>
            )}

            {loading && (
              <AISummaryCard summary="Finding your perfect spots — filtering candidates and ranking with AI…" />
            )}

            {!loading && error && (
              <div
                role="alert"
                className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900"
              >
                {error}
              </div>
            )}

            {!loading && response?.used_fallback && (
              <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                Showing <strong>rule-based rankings</strong> (Groq unavailable).
                Add <code className="text-xs">LLM_API_KEY</code> in{" "}
                <code className="text-xs">.env</code> for AI explanations.
              </div>
            )}

            {!loading && response?.summary && (
              <div className="mb-8">
                <AISummaryCard summary={response.summary} />
              </div>
            )}

            {!loading && response && response.recommendations.length > 0 && (
              <>
                <h2 className="mb-6 text-[1.75rem] font-bold tracking-tight text-on-surface">
                  Top picks ({response.recommendations.length} restaurant
                  {response.recommendations.length !== 1 ? "s" : ""})
                </h2>
                <div className="space-y-6 pb-12">
                  {response.recommendations.map((rec) => (
                    <RestaurantCard
                      key={`${rec.restaurant_id}-${rec.rank}`}
                      rec={rec}
                      city={filters.location}
                    />
                  ))}
                </div>
              </>
            )}

            {!loading && !hasSearched && !metaError && <WelcomeState />}

            {!loading &&
              hasSearched &&
              !error &&
              response &&
              response.recommendations.length === 0 && (
                <p className="text-on-surface-variant">
                  No recommendations returned. Try relaxing your filters.
                </p>
              )}
          </div>
        </div>
      </main>
    </div>
  );
}
