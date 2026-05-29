# Google Stitch Design Prompt — Zomato AI Restaurant Recommender

Copy everything below the line into Google Stitch.

---

## Product brief

Design a **modern, polished web UI** for an **AI-powered restaurant recommendation app** inspired by Zomato (India food discovery). The app helps users in Indian cities find restaurants that match their preferences. It combines **structured filtering** on a real dataset (~51K restaurants) with **Groq LLM** rankings and personalized explanations.

**Audience:** Urban diners in India (Bangalore, Delhi, Mumbai, etc.) exploring where to eat tonight.

**Tone:** Trustworthy, appetizing, smart — not a generic admin dashboard. Feel like a premium consumer product (Zomato / Swiggy / Dineout quality), with subtle AI flair.

**Platform:** Desktop-first web app (1280px+), responsive down to tablet (768px). Sidebar + main content layout.

---

## Core user flow

1. User lands on home → sees hero + preference panel.
2. User sets: **location**, **budget** (low / medium / high), **cuisine**, **minimum rating** (0–5), **additional notes** (free text, e.g. “family-friendly, rooftop”), **number of results** (1–10).
3. User taps **“Get Recommendations”** → loading state (3–30 seconds).
4. Results appear: optional **AI summary paragraph**, then **ranked restaurant cards** (#1 best → #N).
5. Edge states: no matches, API key missing (fallback mode), network/LLM error.

---

## Information architecture

### Screen: Home / Recommend (single primary screen)

**Layout:** Two-column.

| Zone | Width | Content |
|------|-------|---------|
| **Left sidebar** | ~320–380px fixed | Preference form (sticky on scroll) |
| **Main panel** | Fluid | Empty state, loading, summary, result cards |

**Header (full width above columns):**
- App name: **“Zomato AI Restaurant Recommender”** (or shorter: **“DineAI”** if you prefer a product name)
- Subtitle: “Personalized picks from 51K+ restaurants · Powered by AI”
- Optional: small status pill — “Groq LLM ready” (green) or “Rule-based mode” (amber)

---

## Sidebar — preference controls

Design a clean, scannable form with clear labels and helper text.

| Control | Type | Options / range | Notes |
|---------|------|-----------------|-------|
| **Location** | Searchable dropdown | Cities from dataset (Bangalore, Delhi, Mumbai, …) | Primary filter; show map-pin icon |
| **Budget** | Segmented control (3 pills) | Low · Medium · High | INR context: low ≤₹500, medium ₹501–1500, high >₹1500 for two |
| **Cuisine** | Dropdown | “Any” + cuisine list (Italian, Chinese, Asian, North Indian, …) | Optional filter |
| **Minimum rating** | Slider | 0.0 – 5.0, step 0.5 | Show live value (e.g. “4.0+”) |
| **Additional preferences** | Textarea | Placeholder: “family-friendly, quick service, rooftop” | 2–3 lines; soft constraints for AI |
| **Number of recommendations** | Slider or stepper | 1 – 10, default 5 | |
| **Advanced** (collapsed) | Checkbox | “Force rule-based (skip AI)” | Dev/demo only; muted styling |
| **Primary CTA** | Full-width button | **“Get Recommendations”** | Brand red; disabled while loading |

**Sidebar footer:** Link “How it works” → 3-step explainer: Filter → AI ranks → You dine.

---

## Main panel — states

### A. Empty / welcome state (before search)

- Illustration or food photography mood (subtle, not stock-cluttered).
- Headline: “Tell us what you’re craving”
- Short copy: “We’ll filter thousands of restaurants, then AI picks the best matches for you.”
- Show 2–3 example chips: “Bangalore · High budget · Asian” (tap to pre-fill — optional).

### B. Loading state

- Skeleton cards (3–5) OR centered spinner with copy: “Finding your perfect spots…”
- Subtext: “Filtering candidates and ranking with AI”
- Do not block sidebar; show progress indicator on CTA.

### C. Results state

**Optional AI summary block** (top of results):
- Light tinted panel, quote-style or “insight” card.
- 2–4 sentences summarizing the set (e.g. “These Asian spots in Bangalore match your high budget…”).

**Section title:** “Top picks” with count badge (e.g. “5 restaurants”).

**Restaurant result cards** — vertical stack, generous spacing. Each card MUST include:

| Element | Priority | Design notes |
|---------|----------|--------------|
| **Rank badge** | High | `#1`, `#2` … pill on brand red `#E23744` (Zomato red) |
| **Restaurant name** | Required | Large, bold, dark `#1A1A2E` — must be highly readable |
| **Full address** | Required | Pin icon + full address line, gray `#374151`, wraps on long text |
| **Meta row** | Required | Cuisine · star rating (visual stars + numeric) · cost “₹1,400 for two” |
| **AI explanation** | Required | Separated section (top border or subtle background); 2–3 sentences why it fits user prefs |
| **Optional** | Nice-to-have | “Matches your budget” chip, cuisine tags, save/bookmark icon |

**Card styling:**
- White or very light warm background (`#FFFFFF` → `#FFF8F8` subtle gradient).
- Soft border `#E8D4D4`, 12px radius, light shadow.
- **Critical:** All text must remain readable on light cards in both light AND dark app themes (no white-on-white headings).

**Rules:**
- **No duplicate restaurant names** in the list.
- Cards are equal width; #1 card can have slightly stronger emphasis (border or glow).

### D. Error / empty results

| Case | Message pattern |
|------|-----------------|
| No matches | Friendly empty state: “No restaurants match — try lowering minimum rating or choosing ‘Any’ cuisine.” |
| LLM fallback | Info banner (blue/amber): “Showing rule-based rankings — add API key for AI explanations.” |
| Missing data | Setup instructions, not raw error |

---

## Design system

### Brand & color

- **Primary:** Zomato-inspired red `#E23744` (CTAs, rank badges, accents).
- **Background:** App shell — dark charcoal `#1A1A2E` or warm off-white `#FAFAFA` (pick one direction and commit; current app leans dark shell + light cards).
- **Text on cards:** Name `#1A1A2E`, address `#374151`, body `#1F2937`, muted meta `#4B5563`.
- **Success / AI ready:** `#10B981` · **Warning / fallback:** `#F59E0B` · **Error:** `#EF4444`.
- **Indian context:** Use ₹ for currency; star ratings out of 5.

### Typography

- **Display / restaurant names:** Strong sans (e.g. Inter, Plus Jakarta Sans, or similar) — 20–22px semibold.
- **UI labels:** 13–14px medium.
- **Explanations:** 15px regular, comfortable line-height 1.55.
- Avoid overly playful fonts; prioritize legibility for long addresses.

### Iconography

- Location pin, star rating, rupee/cost, sparkles or wand for “AI explanation” section.
- Cuisine could use small tags/chips.

### Accessibility (WCAG AA)

- Name on white: contrast ≥ 7:1.
- Address on white: ≥ 4.5:1.
- Focus states on all interactive controls.
- Touch targets ≥ 44px on mobile breakpoints.

---

## Component inventory (for Stitch)

Generate high-fidelity mocks for:

1. **App shell** — header + sidebar + main
2. **Preference sidebar** — all controls + primary CTA
3. **Welcome / empty state**
4. **Loading state** — skeleton or spinner
5. **Results with summary** — 3 full restaurant cards (#1–#3) with realistic Indian copy:
   - Example: “Flechazo”, Whitefield Bangalore, Asian/Mediterranean, 4.9★, ₹1400 for two
   - Example: “Asia Kitchen By Mainland China”, Koramangala, 4.9★, ₹1500 for two
6. **Info banner** — fallback mode
7. **No results empty state**
8. **Mobile / tablet** — collapsed sidebar → bottom sheet or drawer for preferences

---

## Sample content (use in mocks)

**User preferences shown in sidebar:**
- Location: Bangalore  
- Budget: High  
- Cuisine: Asian  
- Minimum rating: 0.0  
- Additional: (empty)  
- Recommendations: 5  

**Sample AI summary:**
> “Based on your preference for Asian cuisine and a high budget in Bangalore, here are top-rated venues with strong reviews and premium dining experiences.”

**Sample explanation (on card):**
> “Flechazo offers Asian and Mediterranean dishes with a 4.9 rating, fitting your high budget and Asian cuisine preference in Whitefield, Bangalore.”

---

## Technical context (for implementers)

- Current implementation: **Streamlit** (`src/ui/app.py`) with HTML cards; target is a **visual redesign** that can be implemented in Streamlit custom CSS or migrated to **React + FastAPI**.
- Backend: FastAPI on port 8000; frontend Streamlit on 8501.
- API returns JSON: `{ summary, recommendations: [{ rank, name, address, cuisine, rating, estimated_cost, explanation }] }`.
- Do not design login/auth — single-session discovery tool.

---

## What to avoid

- Generic Bootstrap admin templates
- Dense data tables instead of cards
- Tiny illegible address text
- Repeating the same restaurant name twice in results
- Clashing red-on-red text
- Overly futuristic “AI slop” gradients; keep food-first warmth

---

## Deliverables requested from Stitch

1. **Desktop mockup** — full home/results screen with sidebar filled and 3 result cards visible  
2. **Component sheet** — buttons, inputs, cards, badges, banners  
3. **Color & type tokens** — exportable spec  
4. **Mobile adaptation** — one key breakpoint  
5. **Dark mode variant** (optional) — ensuring result cards stay light with dark text  

**Design goal:** Transform the current basic Streamlit UI into a **production-quality, Zomato-adjacent food discovery experience** that highlights AI-powered explanations as the differentiator.
