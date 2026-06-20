"""Paid data-provider source: Apollo.io people search (API key required).
Template for Apollo / ZoomInfo / Lusha. No key -> skipped.
Apollo docs: https://docs.apollo.io/reference/people-search
"""
from __future__ import annotations
import json, urllib.request
from typing import Iterable
from .base import Source
from ..models import Lead

APOLLO_URL = "https://api.apollo.io/v1/mixed_people/search"


class ApolloSource(Source):
    name = "apollo"
    requires_key = True

    def available(self) -> bool:
        return bool(self.config.get("api_key"))

    def fetch(self) -> Iterable[Lead]:
        key = self.config.get("api_key")
        if not key:
            return []
        payload = {
            "api_key": key,
            "person_titles": self.config.get("titles", ["Founder", "Chairman", "CEO", "Managing Director"]),
            "person_locations": self.config.get("locations", ["Dubai", "London", "Singapore", "New York"]),
            "q_keywords": self.config.get("keywords", "Indian family office wealth"),
            "page": 1, "per_page": self.config.get("per_page", 25),
        }
        try:
            req = urllib.request.Request(
                APOLLO_URL, data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [apollo] skipped: {e}")
            return []
        leads = []
        for p in data.get("people", []):
            leads.append(Lead(
                name=p.get("name", ""), role=p.get("title", ""),
                company=(p.get("organization") or {}).get("name", ""),
                city=p.get("city", ""), country=p.get("country", ""),
                industry=(p.get("organization") or {}).get("industry", ""),
                public_source="Apollo.io", source_url=p.get("linkedin_url", ""),
                addressability=4, diaspora_fit=3,
                notes="From paid provider - confirm UHNW status, liquidity event & Indian origin before outreach.",
            ))
        return leads
