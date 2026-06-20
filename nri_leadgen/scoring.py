"""Signal-driven lead scoring.

Composite 0-100, weighted:
  Event recency 30% + Event magnitude 25% + Addressability 20% + Diaspora fit 15% + Geo fit 10%
"""
from __future__ import annotations
from .models import Lead, TARGET_REGIONS, EVENT_WEIGHTS, months_since

UHNW_FLOOR_USD_M = 30.0
WEIGHTS = {"recency": 0.30, "magnitude": 0.25, "address": 0.20, "diaspora": 0.15, "geo": 0.10}


def recency_score(lead: Lead) -> int:
    m = months_since(lead.event_date)
    if m is None:
        return EVENT_WEIGHTS.get(lead.event_type, 1)
    if m < 0:
        return 5
    if m <= 6:
        return 5
    if m <= 12:
        return 4
    if m <= 24:
        return 3
    if m <= 48:
        return 2
    return 1


def magnitude_score(lead: Lead) -> int:
    val = lead.est_liquid_wealth_usd_m or lead.event_value_usd_m
    if val is None:
        return EVENT_WEIGHTS.get(lead.event_type, 1)
    if val >= 1000:
        return 5
    if val >= 250:
        return 4
    if val >= 100:
        return 3
    if val >= 30:
        return 2
    return 1


def geo_fit_from_region(region: str) -> int:
    return 5 if (region or "").lower().strip() in TARGET_REGIONS else 2


def clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, int(round(v or 0))))


def score_lead(lead: Lead) -> Lead:
    lead.recency_score = recency_score(lead)
    lead.event_score = magnitude_score(lead)
    if lead.geo_fit == 3:
        lead.geo_fit = geo_fit_from_region(lead.region)
    score = (
        lead.recency_score * WEIGHTS["recency"]
        + lead.event_score * WEIGHTS["magnitude"]
        + clamp(lead.addressability) * WEIGHTS["address"]
        + clamp(lead.diaspora_fit) * WEIGHTS["diaspora"]
        + clamp(lead.geo_fit) * WEIGHTS["geo"]
    ) / 5 * 100
    lead.lead_score = round(score)
    lead.priority = (
        "A - Hot" if lead.lead_score >= 80
        else "B - Warm" if lead.lead_score >= 65
        else "C - Develop"
    )
    return lead


def qualifies(lead: Lead, min_liquid_usd_m: float = UHNW_FLOOR_USD_M) -> bool:
    val = lead.est_liquid_wealth_usd_m or lead.event_value_usd_m
    if val is not None and val < min_liquid_usd_m:
        return False
    return bool(lead.name)
