"""Ingest: run the lead pipeline and write data/snapshot.json (consumed by the app/DB).

Used by the monthly GitHub Action and the FastAPI startup seed. Pure-python (no fastapi).
"""
from __future__ import annotations
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nri_leadgen.pipeline import run  # noqa: E402

SNAPSHOT = os.path.join(ROOT, "data", "snapshot.json")
DEFAULT_CONFIG = {
    "min_liquid_usd_m": 30,
    "sources": {
        "seed_csv": {"enabled": True, "path": os.path.join(ROOT, "data", "seed_leads.csv")},
        "ipo_ma": {"enabled": True, "path": os.path.join(ROOT, "data", "events.csv")},
        "sec_edgar": {"enabled": bool(os.getenv("SEC_USER_AGENT")),
                      "user_agent": os.getenv("SEC_USER_AGENT", ""),
                      "use_watchlist": True,
                      "watchlist_csv": os.path.join(ROOT, "data", "watchlist.csv"),
                      "max_per_query": 8},
    },
}


def build_snapshot(config=None, out=SNAPSHOT):
    leads = run(config or DEFAULT_CONFIG)
    rows = [l.to_dict() for l in leads]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(rows)} leads -> {out}")
    return rows


if __name__ == "__main__":
    build_snapshot()
