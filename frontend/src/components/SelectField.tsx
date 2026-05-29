interface SelectFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: readonly string[];
}

function ChevronDown() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export function SelectField({
  id,
  label,
  value,
  onChange,
  options,
}: SelectFieldProps) {
  const safeValue = options.includes(value) ? value : (options[0] ?? "");

  return (
    <div className="rounded-lg bg-surface-container p-4">
      <label
        htmlFor={id}
        className="mb-2 block text-xs font-semibold uppercase tracking-wider text-on-surface-variant"
      >
        {label}
      </label>
      <div className="relative isolate">
        <select
          id={id}
          value={safeValue}
          onChange={(e) => onChange(e.target.value)}
          className="select-input relative z-0 w-full rounded-lg border border-outline-variant bg-white py-2.5 pl-3 pr-11 text-sm leading-normal text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
        <span
          className="pointer-events-none absolute inset-y-0 right-0 z-10 flex w-11 shrink-0 items-center justify-center text-on-surface-variant"
          aria-hidden
        >
          <ChevronDown />
        </span>
      </div>
    </div>
  );
}
