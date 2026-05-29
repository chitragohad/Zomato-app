"use client";

interface SegmentedControlProps<T extends string> {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
}

export function SegmentedControl<T extends string>({
  label,
  options,
  value,
  onChange,
}: SegmentedControlProps<T>) {
  return (
    <div className="rounded-lg bg-surface-container p-4">
      <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-on-surface-variant">
        {label}
      </span>
      <div
        className="flex gap-1 rounded-lg bg-surface-container-low p-1"
        role="group"
        aria-label={label}
      >
        {options.map((opt) => {
          const selected = opt === value;
          return (
            <button
              key={opt}
              type="button"
              onClick={() => onChange(opt)}
              aria-pressed={selected}
              className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                selected
                  ? "bg-primary text-on-primary shadow-sm"
                  : "bg-surface-container-lowest text-on-surface hover:bg-white"
              }`}
            >
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
