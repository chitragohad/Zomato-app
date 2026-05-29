"""DineAI UI components — text-only HTML for Streamlit (no icons or images)."""

from __future__ import annotations

import html

from src.models.recommendation import Recommendation
from src.ui.theme import (
    ON_PRIMARY,
    ON_SURFACE,
    ON_SURFACE_VARIANT,
    OUTLINE_VARIANT,
    PRIMARY,
    PRIMARY_FIXED,
    SECONDARY_CONTAINER,
    SURFACE,
    SURFACE_CONTAINER,
    SURFACE_CONTAINER_LOW,
    SURFACE_CONTAINER_LOWEST,
)

def escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_sidebar_brand() -> str:
    return (
        f'<div style="padding:0 0 1rem 0;border-bottom:1px solid {OUTLINE_VARIANT};margin-bottom:1rem;">'
        f'<p style="margin:0;font-size:1.375rem;font-weight:700;color:{PRIMARY};line-height:1.2;">DineAI</p>'
        f'<p style="margin:0.35rem 0 0 0;font-size:0.8rem;color:{ON_SURFACE_VARIANT};">'
        f"51K+ restaurants · AI-powered picks</p></div>"
    )


def render_ai_summary(summary: str) -> str:
    text = escape(summary)
    return (
        f'<div style="background:linear-gradient(135deg,{PRIMARY_FIXED}55 0%,{SURFACE_CONTAINER_LOWEST} 70%);'
        f"border:1px solid {SECONDARY_CONTAINER};border-radius:12px;padding:1.25rem 1.5rem;"
        f'margin-bottom:1.5rem;box-shadow:0 1px 3px rgba(26,26,46,0.06);">'
        f'<p style="margin:0 0 0.5rem 0;font-size:1.125rem;font-weight:600;color:{ON_SURFACE};">'
        f"Curated by AI</p>"
        f'<p style="margin:0;font-size:0.9375rem;line-height:1.55;color:{ON_SURFACE_VARIANT};">'
        f"{text}</p></div>"
    )


def render_results_heading(count: int) -> str:
    noun = "restaurants" if count != 1 else "restaurant"
    return (
        f'<p class="dineai-results" style="margin:0 0 1.25rem 0;font-size:1.75rem;font-weight:700;'
        f'color:{ON_SURFACE};letter-spacing:-0.02em;">Top picks ({count} {noun})</p>'
    )


def _cuisine_chips_html(cuisine: str, max_tags: int = 4) -> str:
    tags = [t.strip() for t in cuisine.replace("/", ",").split(",") if t.strip()][:max_tags]
    if not tags and cuisine:
        tags = [cuisine.strip()]
    chips = []
    for tag in tags:
        chips.append(
            f'<span style="display:inline-block;padding:0.25rem 0.75rem;margin-right:0.5rem;'
            f"border-radius:9999px;border:1px solid {OUTLINE_VARIANT};background:{SURFACE};"
            f'color:{ON_SURFACE_VARIANT};font-size:0.875rem;font-weight:500;">{escape(tag)}</span>'
        )
    return "".join(chips)


def render_recommendation_card(rec: Recommendation, location_line: str) -> str:
    name = escape(rec.name or "Unknown restaurant")
    location = escape(location_line)
    explanation = escape(rec.explanation)
    rating = escape(f"{rec.rating:.1f}" if rec.rating is not None else "")
    cost = escape(rec.estimated_cost)
    chips = _cuisine_chips_html(rec.cuisine or "")

    rating_badge = ""
    if rating:
        rating_badge = (
            f'<span style="border-radius:6px;background:{SURFACE_CONTAINER};padding:0.25rem 0.65rem;'
            f'font-size:0.875rem;font-weight:700;color:{ON_SURFACE};">{rating} / 5</span>'
        )

    return (
        f'<article style="background:{SURFACE_CONTAINER_LOWEST};border:1px solid {SURFACE_CONTAINER};'
        f"border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;"
        f'box-shadow:0 4px 12px rgba(26,26,46,0.05);">'
        f'<div style="margin-bottom:0.75rem;display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">'
        f'<span style="background:{PRIMARY};color:{ON_PRIMARY};font-weight:700;font-size:0.875rem;'
        f'padding:0.25rem 0.65rem;border-radius:6px;">#{rec.rank}</span>{rating_badge}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">'
        f'<div><p style="margin:0 0 0.25rem 0;font-size:1.125rem;font-weight:600;color:{ON_SURFACE};">'
        f"{name}</p>"
        f'<p style="margin:0;font-size:0.9375rem;color:{ON_SURFACE_VARIANT};">{location}</p></div>'
        f'<span style="flex-shrink:0;font-size:1rem;font-weight:600;color:{ON_SURFACE};'
        f"background:{SURFACE_CONTAINER};padding:0.35rem 0.85rem;border-radius:9999px;"
        f'white-space:nowrap;">{cost}</span></div>'
        f'<div style="margin:0.75rem 0;">{chips}</div>'
        f'<div style="background:{SURFACE_CONTAINER_LOW};border-radius:8px;padding:1rem;'
        f'border-left:4px solid {PRIMARY};">'
        f'<p style="margin:0;font-size:0.9375rem;line-height:1.55;color:{ON_SURFACE_VARIANT};">'
        f'<strong style="color:{ON_SURFACE};font-weight:600;">AI Match:</strong> {explanation}</p>'
        f"</div></article>"
    )


def render_welcome() -> str:
    return (
        f'<div style="text-align:center;padding:3rem 2rem;background:{SURFACE_CONTAINER_LOWEST};'
        f"border:1px dashed {OUTLINE_VARIANT};border-radius:12px;margin-top:1rem;\">"
        f'<p style="margin:0 0 0.5rem 0;font-size:1.5rem;font-weight:700;color:{ON_SURFACE};">'
        f"Tell us what you&apos;re craving</p>"
        f'<p style="margin:0 auto;max-width:28rem;font-size:0.9375rem;line-height:1.55;'
        f'color:{ON_SURFACE_VARIANT};">Set your preferences in the sidebar, then tap '
        f"<strong style=\"color:{ON_SURFACE};\">Get Recommendations</strong> for "
        f"AI-ranked restaurants with personalized explanations.</p></div>"
    )


def render_fallback_banner() -> str:
    return (
        '<div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;'
        'padding:0.75rem 1rem;margin-bottom:1rem;color:#92400e;font-size:0.9rem;">'
        "Showing <strong>rule-based rankings</strong> (Groq unavailable). "
        "Add <code>LLM_API_KEY</code> in <code>.env</code> for AI explanations.</div>"
    )
