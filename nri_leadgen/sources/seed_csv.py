"""Seed source: curated, signal-tagged non-obvious prospects from data/seed_leads.csv.
Works fully offline -- the baseline that always runs."""
from __future__ import annotations
import csv, os
from typing import Iterable
from .base import Source
from ..models import Lead

DEFAULT_PATH = os.path.join("data", "seed_leads.csv")


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def _i(v, d=3):
    try:
        return int(v) if v not in (None, "") else d
    except ValueError:
        return d


class SeedCSVSource(Source):
    name = "seed_csv"

    def fetch(self) -> Iterable[Lead]:
        path = self.config.get("path", DEFAULT_PATH)
        if not os.path.exists(path):
            return []
        leads = []
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                leads.append(Lead(
                    name=r["name"], role=r.get("role", ""), company=r.get("company", ""),
                    diaspora_category=r.get("diaspora_category", ""),
                    city=r.get("city", ""), country=r.get("country", ""),
                    region=r.get("region", ""), industry=r.get("industry", ""),
                    exchange_ticker=r.get("exchange_ticker", ""),
                    event_type=r.get("event_type", ""), event_date=r.get("event_date", ""),
                    event_value_usd_m=_f(r.get("event_value_usd_m")),
                    stake_pct=_f(r.get("stake_pct")),
                    est_liquid_wealth_usd_m=_f(r.get("est_liquid_wealth_usd_m")),
                    liquidity_signal=r.get("liquidity_signal", ""),
                    public_source=r.get("public_source", "seed"),
                    source_url=r.get("source_url", ""),
                    addressability=_i(r.get("addressability")),
                    diaspora_fit=_i(r.get("diaspora_fit")),
                    geo_fit=_i(r.get("geo_fit")),
                ))
        return leads
