# CLAUDE.md — project guide for Claude Code

## What this is
A SIGNAL-DRIVEN lead generator for wealth/asset management targeting non-obvious, newly-liquid
Indian-origin (NRI/OCI) and resident-India founders/execs/ESOP holders. It scores LIQUIDITY
EVENTS (IPO, lock-up expiry, acquisition, funding, insider sale), not rich-list rank.

## Run
```bash
pip install -r requirements.txt
python build_dataset.py                         # rebuild data/ (exclusive seed + watchlist)
python -m nri_leadgen.cli --top 15              # offline
python -m nri_leadgen.cli --config config.yaml  # live sources
```

## Architecture
- `nri_leadgen/models.py` — `Lead` dataclass; event fields (event_type/date/value, stake_pct,
  est_liquid_wealth_usd_m) + `months_since()`. `EVENT_WEIGHTS` ranks event types.
- `nri_leadgen/scoring.py` — recency + magnitude + addressability + diaspora + geo → 0–100.
  Tune `WEIGHTS` here. Recency uses event_date vs today (so it drifts; re-run to refresh).
- `nri_leadgen/sources/` — subclass `base.Source`, implement `available()` + `fetch()`.
  MUST NOT raise: catch, print `[name] skipped`, return `[]`. Register in `__init__.py:REGISTRY`.
  - `sec_edgar.py` is the core engine: watchlist → EDGAR full-text → insiders, form→event map.
  - `ipo_ma.py` reads `data/events.csv` (maintain it; lock-up expiries are gold).
- `dedup.py` merges same-person records (keeps larger est wealth + more recent event).
- `pipeline.py` collect → qualify → dedupe → score → sort. `cli.py`/`export.py` = entry + writers.

## Conventions
- Stdlib `urllib` for network (no heavy deps). Money in **$ millions**.
- Analyst inputs `addressability`/`diaspora_fit`/`geo_fit` are 1–5; geo auto-fills from region.

## ENVIRONMENT NOTE
In this build session the file-tool→bash mount truncated large files; source files were
authored directly via the shell. On a normal machine this isn't a concern — edit normally.

## Good next tasks
- Parse Form 4 XML (transaction code S, share count × price) for exact realised $ per insider.
- Add 13D/13G large-stake source and an NSE/BSE promoter-holding source for India tickers.
- Auto-detect lock-up expiries ~6 months after each watchlist IPO date.
- Streamlit/HTML dashboard over output/leads.csv; unit tests for scoring.py & dedup.py.

## Guardrails
Respect COMPLIANCE.md. Public/licensed data only; no scraping in breach of terms; no MNPI.
Identify & score only — never auto-contact or move money.
