import type { Recommendation } from "@/lib/types";
import {
  formatRating,
  formatLocationLine,
  splitCuisineTags,
} from "@/lib/utils";

interface RestaurantCardProps {
  rec: Recommendation;
  city: string;
}

export function RestaurantCard({ rec, city }: RestaurantCardProps) {
  const location = formatLocationLine(rec, city);
  const tags = splitCuisineTags(rec.cuisine);
  const ratingText = formatRating(rec.rating);

  return (
    <article className="overflow-hidden rounded-card border border-surface-container bg-white p-6 shadow-card">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="rounded-md bg-primary px-2.5 py-1 text-sm font-bold text-on-primary">
          #{rec.rank}
        </span>
        {ratingText !== "—" && (
          <span className="rounded-md bg-surface-container px-2.5 py-1 text-sm font-bold text-on-surface">
            {ratingText} / 5
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-on-surface">{rec.name}</h3>
          <p className="mt-1 text-sm text-on-surface-variant">{location}</p>
        </div>
        <span className="shrink-0 rounded-full bg-surface-container px-3 py-1 text-base font-semibold text-on-surface">
          {rec.estimated_cost}
        </span>
      </div>

      {tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-outline-variant bg-surface px-3 py-1 text-sm font-medium text-on-surface-variant"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="mt-4 rounded-lg border-l-4 border-primary bg-surface-container-low p-4">
        <p className="text-[15px] leading-relaxed text-on-surface-variant">
          <strong className="font-semibold text-on-surface">AI Match:</strong>{" "}
          {rec.explanation}
        </p>
      </div>
    </article>
  );
}
