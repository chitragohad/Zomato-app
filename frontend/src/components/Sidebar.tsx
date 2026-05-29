"use client";

import type { FilterState } from "@/lib/types";
import { SegmentedControl } from "./SegmentedControl";
import { SelectField } from "./SelectField";

const BUDGET_OPTIONS = ["Low", "Mid", "High"] as const;
const RATING_OPTIONS = ["Any", "3.0+", "4.0+", "4.5+"] as const;

interface SidebarProps {
  filters: FilterState;
  cities: string[];
  cuisines: string[];
  loading: boolean;
  onFilterChange: <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => void;
  onSubmit: () => void;
}

export function Sidebar({
  filters,
  cities,
  cuisines,
  loading,
  onFilterChange,
  onSubmit,
}: SidebarProps) {
  const cuisineOptions = ["Any", ...cuisines] as const;

  return (
    <aside className="sticky top-0 flex h-full max-h-dvh w-[350px] shrink-0 flex-col overflow-hidden border-r border-outline-variant bg-surface-container-low">
      <header className="shrink-0 border-b border-outline-variant px-6 py-5">
        <h1 className="font-display text-2xl font-bold text-primary">DineAI</h1>
        <p className="mt-1 text-xs text-on-surface-variant">
          51K+ restaurants · AI-powered picks
        </p>
      </header>

      <div className="sidebar-filters min-h-0 flex-1 space-y-3 overflow-y-auto overflow-x-hidden px-6 py-5 scrollbar-none">
        <SelectField
          id="location"
          label="Location"
          value={filters.location}
          onChange={(v) => onFilterChange("location", v)}
          options={cities}
        />

        <SegmentedControl
          label="Budget"
          options={BUDGET_OPTIONS}
          value={filters.budget}
          onChange={(v) => onFilterChange("budget", v)}
        />

        <SelectField
          id="cuisine"
          label="Cuisine"
          value={filters.cuisine}
          onChange={(v) => onFilterChange("cuisine", v)}
          options={cuisineOptions}
        />

        <SegmentedControl
          label="Minimum Rating"
          options={RATING_OPTIONS}
          value={filters.minRating}
          onChange={(v) => onFilterChange("minRating", v)}
        />

        <div className="rounded-lg bg-surface-container p-4">
          <label
            htmlFor="additional"
            className="mb-2 block text-xs font-semibold uppercase tracking-wider text-on-surface-variant"
          >
            Additional preferences
          </label>
          <textarea
            id="additional"
            rows={3}
            placeholder="e.g. family-friendly, quick service, rooftop"
            value={filters.additional}
            onChange={(e) => onFilterChange("additional", e.target.value)}
            className="w-full resize-none rounded-lg border border-outline-variant bg-white px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div className="rounded-lg bg-surface-container p-4">
          <label
            htmlFor="topK"
            className="mb-2 block text-xs font-semibold uppercase tracking-wider text-on-surface-variant"
          >
            Recommendations count
          </label>
          <div className="flex items-center gap-3">
            <input
              id="topK"
              type="range"
              min={1}
              max={10}
              value={filters.topK}
              onChange={(e) => onFilterChange("topK", Number(e.target.value))}
              className="h-2 flex-1 cursor-pointer accent-primary"
            />
            <span className="min-w-[1.5rem] text-center text-sm font-semibold text-on-surface">
              {filters.topK}
            </span>
          </div>
        </div>
      </div>

      <footer className="shrink-0 border-t border-outline-variant bg-surface-container-low p-6">
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading}
          className="w-full rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-on-primary shadow-sm transition-colors hover:bg-primary-container disabled:opacity-70"
        >
          {loading ? "Finding spots…" : "Get Recommendations"}
        </button>
      </footer>
    </aside>
  );
}
