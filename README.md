# NRI / OCI UHNW Lead Intelligence — deployable app

A self-updating web app that surfaces **non-obvious, newly-liquid** Indian-origin (NRI/OCI)
and resident-India UHNW prospects for **wealth & asset management**, ranks them by
**liquidity-event signal**, and gives each a **detailed profile** (sector, region, photo slot,
news clippings, good-to-knows, funds & affiliations, contact pathway).

- **Backend:** FastAPI + SQLAlchemy (SQLite by default, Postgres via `DATABASE_URL`)
- **UI:** server-rendered pages — a filterable directory (by sector / region / country) + rich
  profile pages
- **Data engine:** the `nri_leadgen` pipeline (SEC EDGAR + IPO/M&A events + curated seed)
- **Refresh:** a weekly GitHub Action rebuilds the data and commits it
- **Enrichment:** news + contact pathways auto-fill from your API keys (Serper / Apollo)

> ⚠️ Read [`COMPLIANCE.md`](COMPLIANCE.md). Public/licensed data only; **no personal contact
> details are fabricated** — contact fields are pathways (IR/company/LinkedIn) until enriched
> from a provider you're licensed to use. Verify identity, origin/residency & holdings before outreach.

## Run locally

```bash
pip install -r requirements.txt
python build_dataset.py          # build the exclusive seed + watchlist
python -m app.ingest             # pipeline -> data/snapshot.json
uvicorn app.main:app --reload    # http://127.0.0.1:8000
```

No-server preview (renders the real templates to static HTML):

```bash
python build_preview.py && open site_preview/index.html
```

## Endpoints

| Path | What |
|---|---|
| `GET /` | Filterable directory (sector / region / country / search) |
| `GET /p/{slug}` | Full profile page |
| `GET /api/leads` | JSON, same filters (`?sector=&region=&country=&q=`) |
| `GET /api/leads/{slug}` | Single profile JSON |
| `GET /api/facets` | Counts by sector/region/country |
| `POST /admin/refresh?token=…` | Re-seed DB + enrich (token = `ADMIN_TOKEN`) |
| `GET /healthz` | Liveness |

## Deploy from GitHub

1. Push this folder to a GitHub repo.
2. Deploy the container anywhere that builds a `Dockerfile` (Render, Railway, Fly.io, Azure
   Container Apps). Start command is already set; it listens on `$PORT`.
3. Set env vars (see `.env.example`): `SEC_USER_AGENT`, optional `SERPER_API_KEY` /
   `APOLLO_API_KEY`, `ADMIN_TOKEN`, and `DATABASE_URL` for Postgres.
4. Local container: `docker compose up --build` → http://localhost:8000

### Weekly auto-refresh
`.github/workflows/refresh.yml` runs at 06:00 UTC every Monday (and on demand). It
rebuilds the dataset, runs the pipeline, enriches profiles (if keys are set as repo **secrets**:
`SEC_USER_AGENT`, `SERPER_API_KEY`, `APOLLO_API_KEY`), and commits the refreshed
`data/*.json|csv`. With ephemeral SQLite the app reseeds from the new snapshot on redeploy; for
persistent Postgres, set repo secret `DEPLOY_REFRESH_URL` to `https://your-app/admin/refresh?token=…`
and the Action will ping it.

## How profiles are filled

| Field | Source |
|---|---|
| Sector / region / country | Derived from the pipeline (sector inferred from industry) |
| Liquidity signal, score, stake | Pipeline (event-driven scoring) |
| Funds & affiliations, good-to-knows, photo, LinkedIn | `data/profile_extras.json` (curated; you edit) |
| News clippings | Curated, or auto via `SERPER_API_KEY` each refresh |
| Contact pathway | Pathway by default; business contact via `APOLLO_API_KEY` |

## Structure

```
app/            FastAPI runtime (main, database, models_db, crud, profiles, ingest, enrich)
  templates/    base / index / profile (Jinja2)   static/  style.css
nri_leadgen/    lead pipeline (sources, scoring, dedup) — see CLAUDE.md
data/           seed_leads.csv, watchlist.csv, events.csv, profile_extras.json, snapshot.json
build_dataset.py / build_preview.py
Dockerfile / docker-compose.yml / Procfile / .github/workflows/refresh.yml / .env.example
```

## Accuracy & disclaimer
`Est. Liquid Wealth` is a **modelled** prioritisation figure, not verified; some origins are
tagged "(verify)". Confirm everything before outreach. See `COMPLIANCE.md`.


## One-click deploy (Render)
This repo includes `render.yaml`. In Render: **New → Blueprint → select this repo**. It provisions
the web service, a 1 GB persistent disk for the SQLite DB, a random `ADMIN_TOKEN`, and prompts you
for `SEC_USER_AGENT` / `SERPER_API_KEY` / `APOLLO_API_KEY`. Health check is `/healthz`.

## Auto-filled appearances
When `SERPER_API_KEY` is set, the weekly refresh runs an events-feed enricher (`app/enrich.py`)
that searches public listings and fills each profile's **Movement history** and **Upcoming visits**
(past vs. future split by year). Auto entries are tagged "auto · verify" with a source link and limited
to publicly announced events.
