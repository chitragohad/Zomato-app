# DineAI Frontend (Next.js)

React/Next.js UI for the restaurant recommendation API, based on the Stitch design in `../stitch_dineai_restaurant_recommender/`.

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Plus Jakarta Sans + Playfair Display (logo)

## Run

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Backend must be running: `uvicorn src.api.main:app --port 8000` (from repo root).

## Structure

```
src/
  app/           layout, page, globals
  components/    Sidebar, RestaurantCard, AISummaryCard, …
  lib/           api.ts, types.ts, utils.ts
```
