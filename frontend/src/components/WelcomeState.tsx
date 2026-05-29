export function WelcomeState() {
  return (
    <div className="mx-auto mt-16 max-w-lg rounded-card border border-dashed border-outline-variant bg-white px-8 py-12 text-center">
      <h2 className="text-2xl font-bold text-on-surface">
        Tell us what you&apos;re craving
      </h2>
      <p className="mt-3 text-[15px] leading-relaxed text-on-surface-variant">
        Set your preferences in the sidebar, then tap{" "}
        <strong className="text-on-surface">Get Recommendations</strong> for
        AI-ranked restaurants with personalized explanations.
      </p>
    </div>
  );
}
