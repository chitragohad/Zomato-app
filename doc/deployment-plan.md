# Deployment Plan: Railway (Backend) + Vercel (Frontend)

Deploy the **DineAI** stack as two services:

| Platform | Service | Repo path | Public URL |
|----------|---------|-----------|------------|
| **Railway** | FastAPI API (`uvicorn`) | Project root | `https://<api>.up.railway.app` |
| **Vercel** | Next.js 14 UI | `frontend/` | `https://<app>.vercel.app` |

Streamlit (`src/ui/app.py`) is **not** included in this plan. Use the Next.js app on Vercel as the production UI.

---

## Architecture

```
┌─────────────────────┐         HTTPS          ┌──────────────────────────┐
│  Vercel             │  POST /api/recommendations│  Railway                 │
│  Next.js (frontend) │ ────────────────────────► │  FastAPI + Parquet cache │
│  NEXT_PUBLIC_API_URL│  GET  /api/metadata/*   │  Groq LLM (env key)      │
└─────────────────────┘                           └──────────────────────────┘
```

**Request flow:** Browser → Vercel (static/SSR) → Railway API → filter → Groq → JSON response.

---

## Prerequisites

1. **GitHub repo** with this project pushed (Railway and Vercel connect via GitHub).
2. **Groq API key** — [console.groq.com/keys](https://console.groq.com/keys).
3. **Restaurant data** — processed cache at `data/restaurants.parquet` (~6 MB). Required for the API to start.
4. Accounts: [Railway](https://railway.app), [Vercel](https://vercel.com).

---

## Phase 0: Prepare the repository

### 0.1 Include the Parquet cache (recommended)

`data/restaurants.parquet` is gitignored locally. For cloud deploy, pick **one** option:

| Option | Pros | Cons |
|--------|------|------|
| **A. Commit parquet** (~6 MB) | Fast cold start, simple | Slightly larger repo |
| **B. Railway Volume** | No repo bloat | Manual upload once |
| **C. Ingest on deploy** | No committed data | Slow build (HF download), may timeout |

**Recommended: Option A** for coursework/demo.

```bash
# One-time: allow parquet in git (or use Git LFS)
git add -f data/restaurants.parquet
git commit -m "Add restaurant cache for production deploy"
git push
```

If you skip this, run ingest during Railway build (see §2.4).

### 0.2 Deployment config files (included in repo)

| File | Purpose |
|------|---------|
| `Procfile` | Railway/Heroku-style start command |
| `railway.toml` | Build (pip + optional ingest), health check, start |
| `runtime.txt` | Python 3.11 |
| `frontend/vercel.json` | Vercel Next.js settings |

### 0.3 Production CORS (implemented)

`src/config.py` reads `CORS_ORIGINS` (comma-separated). `src/api/main.py` applies it via `CORSMiddleware`.

Set on Railway:

```env
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

For local dev, default is `http://localhost:3000,http://127.0.0.1:3000`. Use `CORS_ORIGINS=*` for demos only.

---

## Phase 1: Deploy backend on Railway

### 1.1 Create project

1. Railway → **New Project** → **Deploy from GitHub repo**.
2. Select this repository.
3. **Root directory:** `/` (repository root, not `frontend/`).

### 1.2 Service settings

| Setting | Value |
|---------|--------|
| **Start command** | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
| **Health check** | `/health` |
| **Region** | Closest to users (e.g. `asia-southeast1` if available) |

Railway sets `$PORT` automatically.

### 1.3 Environment variables (Railway)

| Variable | Required | Example |
|----------|----------|---------|
| `LLM_PROVIDER` | Yes | `groq` |
| `LLM_API_KEY` | Yes | `gsk_...` |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` |
| `GROQ_BASE_URL` | No | `https://api.groq.com/openai/v1` |
| `DATA_CACHE_PATH` | No | `data/restaurants.parquet` |
| `HF_DATASET_ID` | No | `ManikaSaini/zomato-restaurant-recommendation` |
| `MAX_CANDIDATES` | No | `30` |
| `TOP_K_RESULTS` | No | `5` |
| `CORS_ORIGINS` | Recommended | `https://your-app.vercel.app` |

Mark `LLM_API_KEY` as **secret**.

### 1.4 Build: ensure data exists

**If parquet is in the repo:** deploy as-is; verify logs show restaurant count on `/health`.

**If parquet is NOT in the repo**, add a **custom build command** in Railway:

```bash
pip install -r requirements.txt && \
python -m src.data.loader --ingest || test -f data/restaurants.parquet
```

Note: first-time HF ingest can take several minutes and needs network; prefer committing the 6 MB parquet.

### 1.5 Public networking

1. Railway service → **Settings** → **Networking** → **Generate domain**.
2. Copy URL, e.g. `https://zomato-api-production.up.railway.app`.
3. Verify:

```bash
curl https://<your-railway-domain>/health
```

Expected:

```json
{
  "status": "ok",
  "restaurants_loaded": 51717,
  "llm_provider": "groq",
  "llm_available": true
}
```

### 1.6 Resource sizing

| Tier | RAM | Notes |
|------|-----|--------|
| Hobby | 512 MB–1 GB | Enough for pandas + parquet (~6 MB) |
| Build | — | Allow 2–5 min if running ingest |

Enable **restart on failure**; API loads parquet at startup via `@lru_cache` on `get_service()`.

---

## Phase 2: Deploy frontend on Vercel

### 2.1 Import project

1. Vercel → **Add New** → **Project** → import same GitHub repo.
2. **Root Directory:** `frontend` (critical).
3. **Framework Preset:** Next.js (auto-detected).

### 2.2 Build settings

| Setting | Value |
|---------|--------|
| **Build command** | `npm run build` (default) |
| **Output** | `.next` (default) |
| **Install command** | `npm install` |
| **Node.js** | 18.x or 20.x |

### 2.3 Environment variables (Vercel)

| Variable | Required | Value |
|----------|----------|--------|
| `NEXT_PUBLIC_API_URL` | Yes | `https://<your-railway-domain>` (no trailing slash) |

Set for **Production**, **Preview**, and **Development** as needed.

> `NEXT_PUBLIC_*` is baked in at build time. After changing it, **redeploy** the frontend.

### 2.4 Deploy

1. Click **Deploy**.
2. Open `https://<project>.vercel.app`.
3. Confirm sidebar loads cities/cuisines (metadata from Railway).
4. Click **Get Recommendations** and verify results + AI summary.

### 2.5 Optional: `vercel.json` in `frontend/`

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install"
}
```

Usually not required; Vercel detects Next.js automatically.

---

## Phase 3: Connect frontend ↔ backend

1. Railway URL → Vercel `NEXT_PUBLIC_API_URL`.
2. Railway `CORS_ORIGINS` → include Vercel production + preview URLs.
3. Redeploy **both** after env changes (Vercel especially, for `NEXT_PUBLIC_*`).

**Smoke test checklist:**

- [ ] `GET <railway>/health` → `status: ok`
- [ ] `GET <railway>/api/metadata/cities` → JSON list
- [ ] Vercel app loads without “Cannot reach API” banner
- [ ] Recommendations for **Bangalore** return cards
- [ ] **Delhi** / **Mumbai** return results (dataset has few rows; may be 1–2 picks)

---

## Phase 4: Custom domains (optional)

| Service | Example |
|---------|---------|
| Vercel | `dineai.yourdomain.com` |
| Railway | `api.yourdomain.com` |

Update `NEXT_PUBLIC_API_URL` and `CORS_ORIGINS` to match.

---

## Environment variable reference (full)

### Railway (backend)

```env
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxxxxxxx
LLM_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
LLM_TEMPERATURE=0.3
LLM_TIMEOUT=60
LLM_MAX_RETRIES=1
DATA_CACHE_PATH=data/restaurants.parquet
HF_DATASET_ID=ManikaSaini/zomato-restaurant-recommendation
MAX_CANDIDATES=30
TOP_K_RESULTS=5
CORS_ORIGINS=https://your-app.vercel.app
```

### Vercel (frontend)

```env
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
```

---

## CI/CD (optional)

| Event | Railway | Vercel |
|-------|---------|--------|
| Push to `main` | Auto-deploy API | Auto-deploy production |
| Pull request | Preview env (optional) | Preview deployment |

**PR previews:** Set Vercel preview `NEXT_PUBLIC_API_URL` to a staging Railway service or the same production API.

---

## Security checklist

- [ ] Never commit `.env` (only `.env.example`).
- [ ] Store `LLM_API_KEY` only in Railway secrets.
- [ ] Restrict `CORS_ORIGINS` in production.
- [ ] Rotate Groq key if exposed.
- [ ] Railway service is public; no admin endpoints without auth (current API is read-only + recommend).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| Vercel “Cannot reach API” | Wrong `NEXT_PUBLIC_API_URL` or API down | Fix env; redeploy Vercel |
| CORS error in browser | Origin not allowed | Add Vercel URL to `CORS_ORIGINS`; redeploy Railway |
| `/health` → `degraded` / file error | Missing parquet | Commit `data/restaurants.parquet` or run ingest on Railway |
| 503 on recommend | Data not loaded | Check Railway logs; verify `DATA_CACHE_PATH` |
| LLM fallback banner | Missing/invalid `LLM_API_KEY` | Set Groq key on Railway |
| Delhi/Mumbai empty | Dataset is ~97% Bangalore | Expected; relax budget or use Bangalore for demos |
| Vercel build fails | Wrong root directory | Set root to `frontend/` |
| Railway build timeout | HF ingest on build | Commit parquet instead |

---

## Cost estimate (hobby / demo)

| Platform | Typical |
|----------|---------|
| Railway | $5/mo credit on hobby; API idle scales to zero on some plans |
| Vercel | Free tier sufficient for Next.js hobby |
| Groq | Free tier with rate limits |

---

## Deployment order (summary)

```text
1. Commit data/restaurants.parquet (or plan ingest)
2. Add Procfile / railway.toml (optional)
3. Deploy Railway → set env vars → get public URL
4. curl /health on Railway
5. Deploy Vercel (frontend/) → set NEXT_PUBLIC_API_URL
6. Set CORS_ORIGINS on Railway → redeploy API
7. Redeploy Vercel → end-to-end test
```

---

## What not to deploy on these platforms

| Component | Platform | Reason |
|-----------|----------|--------|
| Streamlit UI | Railway (separate service) | Possible but separate process; not in this plan |
| Hugging Face ingest | Vercel | No Python/long-running jobs on Vercel |
| Parquet / pandas | Vercel | Serverless size/time limits |

---

## Related docs

- [`README.md`](../README.md) — local run commands
- [`architecture.md`](../architecture.md) — system design
- [`.env.example`](../.env.example) — backend env template
- [`frontend/.env.local.example`](../frontend/.env.local.example) — frontend env template
