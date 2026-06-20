"""Crunchbase source (API key required) -- funded/exited founder discovery.
No key -> skipped. Docs: https://data.crunchbase.com/docs
Respect Crunchbase licence terms for storage and downstream use.
"""
from __future__ import annotations
import json, urllib.request
from typing import Iterable
from .base import Source
from ..models import Lead

SEARCH_URL = "https://api.crunchbase.com/api/v4/searches/organizations"


class CrunchbaseSource(Source):
    name = "crunchbase"
    requires_key = True

    def available(self) -> bool:
        return bool(self.config.get("api_key"))

    def fetch(self) -> Iterable[Lead]:
        key = self.config.get("api_key")
        if not key:
            return []
        body = {
            "field_ids": ["identifier", "short_description", "location_identifiers",
                          "founder_identifiers", "last_funding_type", "last_funding_at"],
            "query": [{"type": "predicate", "field_id": "last_funding_type",
                       "operator_id": "includes",
                       "values": self.config.get("funding_types", ["series_c", "series_d", "series_e"])}],
            "limit": self.config.get("limit", 50),
        }
        try:
            req = urllib.request.Request(
                f"{SEARCH_URL}?user_key={key}", data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [crunchbase] skipped: {e}")
            return []
        leads = []
        for ent in data.get("entities", []):
            p = ent.get("properties", {})
            for fo in (p.get("founder_identifiers") or [{}]):
                leads.append(Lead(
                    name=fo.get("value", "") if isinstance(fo, dict) else str(fo),
                    role="Founder", company=(p.get("identifier") or {}).get("value", ""),
                    industry=p.get("short_description", "")[:120],
                    event_type="funding_round", event_date=(p.get("last_funding_at") or "")[:7],
                    liquidity_signal=f"Recent {p.get('last_funding_type', 'funding')} round",
                    public_source="Crunchbase", addressability=3, diaspora_fit=3,
                    notes="Filter for Indian-origin founders & confirm liquidity before outreach.",
                ))
        return leads
