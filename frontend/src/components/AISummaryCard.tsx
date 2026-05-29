interface AISummaryCardProps {
  summary: string;
}

export function AISummaryCard({ summary }: AISummaryCardProps) {
  return (
    <div className="rounded-xl border border-[#e2e0fc] bg-gradient-to-br from-primary-fixed/30 to-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-on-surface">Curated by AI</h2>
      <p className="mt-2 max-w-3xl text-[15px] leading-relaxed text-on-surface-variant">
        {summary}
      </p>
    </div>
  );
}
