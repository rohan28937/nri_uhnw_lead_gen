"""De-duplicate and merge leads collected from multiple sources."""
from __future__ import annotations
from .models import Lead


def merge(a: Lead, b: Lead) -> Lead:
    for f in vars(a):
        av, bv = getattr(a, f), getattr(b, f)
        if not av and bv:
            setattr(a, f, bv)
    if (b.est_liquid_wealth_usd_m or 0) > (a.est_liquid_wealth_usd_m or 0):
        a.est_liquid_wealth_usd_m = b.est_liquid_wealth_usd_m
    if b.event_date > a.event_date:
        a.event_type, a.event_date = b.event_type, b.event_date
        if b.liquidity_signal:
            a.liquidity_signal = b.liquidity_signal
    if b.public_source and b.public_source not in a.public_source:
        a.public_source = "; ".join(filter(None, [a.public_source, b.public_source]))
    return a


def dedupe(leads: list[Lead]) -> list[Lead]:
    seen: dict[str, Lead] = {}
    for lead in leads:
        k = lead.dedup_key()
        if k in seen:
            seen[k] = merge(seen[k], lead)
        else:
            seen[k] = lead
    return list(seen.values())
