"""SEC EDGAR source (FREE, no API key) -- the exclusivity engine.

Given a watchlist of Indian-origin-led US-listed companies (data/watchlist.csv or config),
EDGAR full-text search surfaces the individual insiders behind each ticker:
  Form 4 -> insider transaction (often a SALE = realised liquidity event)
  Form 3 -> NEW insider (new exec/director, frequently an IPO/onboarding event)

This finds the non-obvious leads: not the famous founder, but the CFOs, VPs and directors
with disclosed, sellable stakes whom no rich list covers. EDGAR requires a real User-Agent.
Docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
"""
from __future__ import annotations
import csv, json, os, time, urllib.parse, urllib.request
from typing import Iterable
from .base import Source
from ..models import Lead

FTS_URL = "https://efts.sec.gov/LATEST/search-index?q={q}&forms={forms}"
FORM_EVENT = {"4": "insider_sale", "3": "new_insider", "5": "insider_sale"}


class SECEdgarSource(Source):
    name = "sec_edgar"

    def available(self) -> bool:
        return bool(self.config.get("enabled", True))

    def _queries(self):
        q = list(self.config.get("queries", []))
        wl = self.config.get("watchlist_csv", os.path.join("data", "watchlist.csv"))
        if self.config.get("use_watchlist", True) and os.path.exists(wl):
            with open(wl, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("company"):
                        q.append(row["company"])
        return list(dict.fromkeys(q))

    def _get(self, url):
        ua = self.config.get("user_agent", "nri-leadgen research contact@example.com")
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))

    def fetch(self) -> Iterable[Lead]:
        forms = str(self.config.get("forms", "4"))
        leads = []
        for q in self._queries():
            url = FTS_URL.format(q=urllib.parse.quote('"%s"' % q), forms=forms)
            try:
                data = self._get(url)
            except Exception as e:
                print(f"  [sec_edgar] skipped '{q}': {e}")
                continue
            hits = (data.get("hits") or {}).get("hits") or []
            seen = set()
            for h in hits[: self.config.get("max_per_query", 10)]:
                src = h.get("_source", {})
                names = src.get("display_names", []) or []
                issuer = names[-1].split("(")[0].strip() if names else q
                file_date = src.get("file_date", "")
                primary_form = (src.get("root_forms") or src.get("forms") or [forms])[0]
                for disp in (names[:-1] or names):
                    person = disp.split("(")[0].strip()
                    if not person or person.lower() in seen or person == issuer:
                        continue
                    seen.add(person.lower())
                    leads.append(Lead(
                        name=_titlecase(person), company=issuer, role="Insider (SEC filer)",
                        exchange_ticker="US-listed (SEC filer)",
                        event_type=FORM_EVENT.get(str(primary_form), "insider_sale"),
                        event_date=file_date,
                        liquidity_signal=f"SEC Form {primary_form} filed {file_date} (insider of {issuer})",
                        addressability=4, diaspora_fit=2, geo_fit=5,
                        public_source="SEC EDGAR full-text search",
                        source_url="https://efts.sec.gov/LATEST/search-index",
                        notes="Insider at US-listed co; confirm Indian origin & enrich holdings before outreach.",
                    ))
            time.sleep(self.config.get("sleep", 0.3))
        return leads


def _titlecase(name):
    return " ".join(w.capitalize() for w in name.split())
