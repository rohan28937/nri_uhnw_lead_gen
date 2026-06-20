"""Orchestrates: collect from sources -> qualify -> dedupe -> score -> sort."""
from __future__ import annotations
from .sources import REGISTRY
from .scoring import score_lead, qualifies
from .dedup import dedupe
from .models import Lead


def run(config: dict) -> list[Lead]:
    enabled = config.get("sources", {})
    collected: list[Lead] = []
    for name, src_cfg in enabled.items():
        if name not in REGISTRY:
            print(f"  [pipeline] unknown source '{name}', skipping")
            continue
        if not (src_cfg or {}).get("enabled", True):
            continue
        src = REGISTRY[name](src_cfg)
        if not src.available():
            print(f"  [{name}] not available (missing key/config) - skipped")
            continue
        rows = list(src.fetch())
        print(f"  [{name}] collected {len(rows)} raw leads")
        collected.extend(rows)
    min_liquid_m = config.get("min_liquid_usd_m", 30.0)
    qualified = [l for l in collected if qualifies(l, min_liquid_m)]
    merged = dedupe(qualified)
    scored = [score_lead(l) for l in merged]
    scored.sort(key=lambda l: l.lead_score, reverse=True)
    print(f"\n  {len(collected)} raw -> {len(qualified)} qualified -> {len(scored)} unique leads")
    return scored
