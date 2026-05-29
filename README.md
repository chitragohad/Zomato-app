# Zomato AI Restaurant Recommendation System

AI-powered restaurant recommendations using the Zomato Hugging Face dataset and an LLM.

## Documentation

- [`context.md`](context.md) — Product requirements
- [`architecture.md`](architecture.md) — Technical design
- [`implementation-plan.md`](implementation-plan.md) — Phase-wise roadmap
- [`edge-cases.md`](edge-cases.md) — Edge case handling
- [`doc/data-schema.md`](doc/data-schema.md) — Dataset column mapping

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Phase 1: Data Ingestion

Download, preprocess, and cache the dataset (~574 MB first run):

```bash
python -m src.data.loader --ingest
```

Force re-download:

```bash
python -m src.data.loader --ingest --force
```

Cache location: `data/restaurants.parquet` (gitignored).

### Verify ingestion

```bash
python -c "
from src.data.repository import RestaurantRepository
repo = RestaurantRepository()
print('Restaurants:', repo.get_restaurant_count())
print('Cities:', repo.get_cities()[:10])
print('Cuisines (sample):', repo.get_cuisines()[:10])
"
```

## Quick Start (Streamlit UI)

```bash
# 1. Setup (once)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Groq API key

# 2. Ingest data (once)
python -m src.data.loader --ingest

# 3. Launch app
streamlit run src/ui/app.py
```

Opens a browser with the recommendation UI — sidebar for preferences, main panel for AI-ranked results.

## Next.js Frontend (DineAI — Stitch design)

Production-style UI matching `stitch_dineai_restaurant_recommender/` — sidebar filters, AI summary card, horizontal restaurant cards.

**Prerequisites:** Node.js 18+, backend running on port 8000.

```bash
# Terminal 1 — API
source .venv/bin/activate
uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — Next.js (from project root)
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open **http://localhost:3000**

| URL | Service |
|-----|---------|
| http://localhost:3000 | Next.js UI |
| http://127.0.0.1:8000/docs | FastAPI |

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API is not on `http://127.0.0.1:8000`.

## Phase 5: Streamlit UI

```bash
streamlit run src/ui/app.py
```

Features: location/cuisine dropdowns, budget & rating filters, Groq-powered explanations, fallback mode, error handling.

## Phase 4: End-to-end recommendations (Groq)

Configure Groq in `.env`:

```bash
LLM_PROVIDER=groq
LLM_API_KEY=gsk_...                    # https://console.groq.com/keys
LLM_MODEL=llama-3.3-70b-versatile
```

Run the full pipeline (filter → Groq → ranked results):

```bash
python -m src.main --location Bangalore --budget medium --cuisine Italian --min-rating 4.0 --top-k 5
```

Without API key (rule-based fallback):

```bash
python -m src.main --location Bangalore --cuisine Italian --min-rating 4.0 --fallback
```

## Phase 3: LLM engine (used by Phase 4)

```bash
python scripts/test_llm.py --fallback
python scripts/test_llm.py --location Bangalore --cuisine Italian --min-rating 4.0
```

## Phase 2: Filtering

Filter restaurants by user preferences before the LLM call:

```bash
python -c "
from src.data.repository import RestaurantRepository
from src.domain.filter import FilterService
from src.models.preferences import UserPreferences
from src.models.restaurant import BudgetTier

repo = RestaurantRepository()
service = FilterService(repo)
prefs = UserPreferences(
    location='Bangalore',
    budget=BudgetTier.MEDIUM,
    cuisine='Italian',
    min_rating=4.0,
)
results = service.filter(prefs)
print(f'Found {len(results)} candidates')
for r in results[:3]:
    print(f'  - {r.name} ({r.rating}) {r.cuisines}')
"
```

## Deployment (Railway + Vercel)

Production deploy: **FastAPI on Railway**, **Next.js on Vercel**.

See **[`doc/deployment-plan.md`](doc/deployment-plan.md)** for step-by-step instructions.

Quick checklist:

1. Commit `data/restaurants.parquet` (or let Railway build ingest run once).
2. Deploy repo root to **Railway** — set `LLM_API_KEY`, `CORS_ORIGINS`.
3. Deploy `frontend/` to **Vercel** — set `NEXT_PUBLIC_API_URL` to your Railway URL.

Config files: `Procfile`, `railway.toml`, `runtime.txt`, `frontend/vercel.json`.

## Tests

```bash
pytest tests/ -v
```

## Project structure

```
src/
├── config.py
├── data/
│   ├── loader.py          # HF download + CLI ingest
│   ├── preprocessor.py    # Normalize to canonical schema
│   └── repository.py      # Load Parquet cache
├── main.py                # CLI entry (Phase 4)
├── services/
│   └── recommendation.py  # RecommendationService orchestration
├── ai/
│   ├── prompt.py          # PromptBuilder
│   ├── client.py          # GroqClient (default), Ollama
│   ├── parser.py          # JSON response parser
│   ├── fallback.py        # Rule-based ranker
│   └── engine.py          # RecommendationEngine
├── domain/
│   ├── budget.py          # Budget tier + BudgetMapper
│   ├── filter.py          # FilterService pipeline
│   ├── serialize.py       # Candidate JSON for LLM
│   └── exceptions.py      # EmptyFilterResultError, etc.
├── ui/
│   ├── app.py             # Streamlit UI (Phase 5)
│   └── helpers.py         # Form helpers
└── models/
    ├── restaurant.py
    ├── preferences.py     # UserPreferences
    └── recommendation.py  # RecommendationResponse
```
