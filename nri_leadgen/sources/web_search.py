"""Web-search source (API key required). Works with Serper.dev (Google).
Captures result titles/snippets as raw leads to enrich. No key -> skipped."""
from __future__ import annotations
import json, urllib.request
from typing import Iterable
from .base import Source
from ..models import Lead

SERPER_URL = "https://google.serper.dev/search"


class WebSearchSource(Source):
    name = "web_search"
    requires_key = True

    def available(self) -> bool:
        return bool(self.config.get("serper_api_key"))

    def fetch(self) -> Iterable[Lead]:
        key = self.config.get("serper_api_key")
        if not key:
            return []
        leads = []
        for q in self.config.get("queries", []):
            try:
                body = json.dumps({"q": q, "num": self.config.get("num", 10)}).encode()
                req = urllib.request.Request(
                    SERPER_URL, data=body,
                    headers={"X-API-KEY": key, "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = json.loads(r.read().decode())
            except Exception as e:
                print(f"  [web_search] skipped '{q}': {e}")
                continue
            for item in data.get("organic", []):
                leads.append(Lead(
                    name=item.get("title", "")[:120],
                    liquidity_signal=item.get("snippet", "")[:200],
                    event_type=self.config.get("event_hint", ""),
                    public_source=f"web: {item.get('link', '')}",
                    source_url=item.get("link", ""),
                    region=self.config.get("region_hint", ""),
                    notes="Raw web hit - needs identity resolution & enrichment before use.",
                    addressability=2, diaspora_fit=3,
                ))
        return leads
