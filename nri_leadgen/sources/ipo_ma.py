"""IPO / M&A liquidity-event source.

Ingests a maintained events file (data/events.csv): recent IPOs, acquisitions, big funding
rounds and IPO lock-up expiry dates for Indian-origin founders. Lock-up expiry ~6 months
post-IPO is when restricted shares become sellable -- a prime timing signal.
No file -> skipped.
"""
from __future__ import annotations
import csv, os
from typing import Iterable
from .base import Source
from ..models import Lead

DEFAULT_PATH = os.path.join("data", "events.csv")


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


class IPOMASource(Source):
    name = "ipo_ma"

    def available(self) -> bool:
        return os.path.exists(self.config.get("path", DEFAULT_PATH))

    def fetch(self) -> Iterable[Lead]:
        path = self.config.get("path", DEFAULT_PATH)
        if not os.path.exists(path):
            return []
        leads = []
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                nm = (r.get("name") or "").strip()
                if not nm or nm.upper().startswith("TEMPLATE"):
                    continue
                leads.append(Lead(
                    name=r.get("name", ""), role=r.get("role", ""), company=r.get("company", ""),
                    diaspora_category=r.get("diaspora_category", ""),
                    country=r.get("country", ""), region=r.get("region", ""),
                    industry=r.get("industry", ""), exchange_ticker=r.get("exchange_ticker", ""),
                    event_type=r.get("event_type", "ipo"), event_date=r.get("event_date", ""),
                    event_value_usd_m=_f(r.get("event_value_usd_m")),
                    stake_pct=_f(r.get("stake_pct")),
                    est_liquid_wealth_usd_m=_f(r.get("est_liquid_wealth_usd_m")),
                    liquidity_signal=r.get("liquidity_signal", "IPO/M&A liquidity event"),
                    public_source=r.get("public_source", "events feed"),
                    source_url=r.get("source_url", ""),
                    addressability=int(r.get("addressability") or 3),
                    diaspora_fit=int(r.get("diaspora_fit") or 4),
                ))
        return leads
