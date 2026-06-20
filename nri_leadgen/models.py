"""Core data model for a signal-driven UHNW NRI/OCI lead.

This engine targets the NON-obvious tier: sub-billionaire founders/execs/ESOP holders
who just had (or are about to have) a liquidity event. The unit of value is the EVENT,
not a rich-list ranking.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional

TARGET_REGIONS = {
    "gulf", "uae", "usa", "canada", "usa & canada", "uk", "europe",
    "uk & europe", "singapore", "apac", "singapore & apac", "india",
}

NRI = "NRI"
OCI = "OCI"
RESIDENT = "Resident India"

EVENT_WEIGHTS = {
    "ipo": 5, "lockup_expiry": 5, "acquisition": 5, "secondary_sale": 5,
    "insider_sale": 4, "funding_round": 3, "new_insider": 3, "promoter_holding": 3, "": 1,
}


@dataclass
class Lead:
    name: str
    role: str = ""
    company: str = ""
    diaspora_category: str = ""
    city: str = ""
    country: str = ""
    region: str = ""
    industry: str = ""
    exchange_ticker: str = ""
    event_type: str = ""
    event_date: str = ""
    event_value_usd_m: Optional[float] = None
    stake_pct: Optional[float] = None
    est_liquid_wealth_usd_m: Optional[float] = None
    liquidity_signal: str = ""
    public_source: str = ""
    source_url: str = ""
    addressability: int = 3
    diaspora_fit: int = 3
    geo_fit: int = 3
    recency_score: int = 0
    event_score: int = 0
    lead_score: int = 0
    priority: str = ""
    notes: str = "Verify identity, origin/residency & current holdings before outreach"

    def dedup_key(self) -> str:
        return _normalise(self.name)

    def to_dict(self) -> dict:
        return asdict(self)


def _normalise(name: str) -> str:
    n = name.lower().strip()
    for token in (" & family", " and family", " & co", "(", ")"):
        n = n.split(token)[0]
    return " ".join(n.split())


def months_since(iso_date: str, today: Optional[date] = None) -> Optional[int]:
    if not iso_date:
        return None
    parts = iso_date.split("-")
    try:
        y = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 1
    except (ValueError, IndexError):
        return None
    today = today or date.today()
    return (today.year - y) * 12 + (today.month - m)
