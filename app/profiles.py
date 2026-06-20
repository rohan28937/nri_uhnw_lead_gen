"""Profile data layer (dependency-light: stdlib only).

Loads the lead snapshot, merges curated profile extras, derives sector, detects European
public appearances, resolves photos, and derives wealth/advisory-intelligence signals
(investment appetite & openness-to-meet are MODELLED estimates, clearly labelled).
Shared by FastAPI routes and the static preview — must not import fastapi/sqlalchemy.
"""
from __future__ import annotations
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SNAPSHOT = os.path.join(DATA, "snapshot.json")
EXTRAS = os.path.join(DATA, "profile_extras.json")
PHOTO_DIR = os.path.join(ROOT, "app", "static", "photos")

SECTOR_RULES = [
    ("Cybersecurity", ["cyber", "security"]),
    ("Semiconductors / Hardware", ["semiconductor", "chip", "connectivity", "hardware"]),
    ("AI / Software", ["ai", "software", "saas", "cloud", "data", "search", "database", "enterprise"]),
    ("Fintech", ["fintech", "broking", "bank", "payments", "insurance"]),
    ("Consumer / Retail", ["retail", "consumer", "e-commerce", "ecommerce", "edtech", "mobility", "ev", "services"]),
    ("Healthcare / Pharma", ["pharma", "health", "biotech", "vaccine"]),
    ("IT Services", ["it services", "bpm", "consulting"]),
    ("Industrial / Energy", ["energy", "steel", "mining", "auto", "infrastructure", "construction"]),
    ("Media / Entertainment", ["media", "entertainment", "film"]),
]
EUROPE = ["uk", "united kingdom", "london", "europe", "france", "paris", "germany", "berlin",
          "munich", "switzerland", "zurich", "geneva", "davos", "ireland", "dublin", "spain",
          "madrid", "barcelona", "italy", "milan", "rome", "netherlands", "amsterdam",
          "portugal", "lisbon", "monaco", "stockholm", "sweden", "luxembourg", "vienna", "austria"]
LIQUID_EVENTS = {"ipo", "lockup_expiry", "acquisition", "secondary_sale", "insider_sale"}


def slugify(name): return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-") or "unknown"


def _norm(name):
    n = (name or "").lower().strip()
    for t in (" & family", " and family", " & co", "(", ")"):
        n = n.split(t)[0]
    return " ".join(n.split())


def sector_of(industry):
    t = (industry or "").lower()
    for sector, kws in SECTOR_RULES:
        if any(k in t for k in kws):
            return sector
    return "Other"


def _to_float(v):
    try: return float(v) if v not in (None, "") else None
    except (TypeError, ValueError): return None


def _photo_file(slug):
    for ext in ("jpg", "jpeg", "png", "webp"):
        if os.path.exists(os.path.join(PHOTO_DIR, f"{slug}.{ext}")):
            return f"{slug}.{ext}"
    return ""


def _is_europe(place):
    p = (place or "").lower()
    return any(k in p for k in EUROPE)


def appetite_estimate(event_type, recency):
    fresh = (recency or 0) >= 4          # within ~12 months
    liq = event_type in LIQUID_EVENTS
    if fresh and liq:
        return "High (est.) — recent liquidity event; capital likely seeking deployment"
    if liq:
        return "Moderate (est.) — past liquidity, may already be allocated"
    return "Assess — no clear recent liquidity event"


def openness_estimate(addressability, recency):
    s = (addressability or 3) + (recency or 1)
    return ("High (est.)" if s >= 8 else "Medium (est.)" if s >= 6 else "Low (est.)")


def load_snapshot(path=SNAPSHOT):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []


def load_extras(path=EXTRAS):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def build_profiles(snapshot_path=SNAPSHOT, extras_path=EXTRAS):
    extras = load_extras(extras_path)
    out = []
    for lead in load_snapshot(snapshot_path):
        name = lead.get("name", "")
        slug = slugify(name)
        ex = extras.get(_norm(name), {})
        moves = ex.get("movements", []) or []
        eu = [m for m in moves if _is_europe(m.get("place", ""))]
        recency = lead.get("recency_score")
        addressability = lead.get("addressability")
        out.append({
            "slug": slug, "name": name, "role": lead.get("role", ""),
            "company": lead.get("company", ""), "sector": sector_of(lead.get("industry", "")),
            "industry": lead.get("industry", ""), "region": lead.get("region", ""),
            "country": lead.get("country", ""), "city": lead.get("city", ""),
            "diaspora_category": lead.get("diaspora_category", ""),
            "exchange_ticker": lead.get("exchange_ticker", ""),
            "event_type": lead.get("event_type", ""), "event_date": lead.get("event_date", ""),
            "liquidity_signal": lead.get("liquidity_signal", ""),
            "est_liquid_wealth_usd_m": _to_float(lead.get("est_liquid_wealth_usd_m")),
            "stake_pct": _to_float(lead.get("stake_pct")),
            "lead_score": lead.get("lead_score", 0), "priority": lead.get("priority", ""),
            "public_source": lead.get("public_source", ""), "source_url": lead.get("source_url", ""),
            "notes": lead.get("notes", ""),
            "photo_url": ex.get("photo_url", ""), "photo_file": _photo_file(slug),
            "linkedin": ex.get("linkedin", ""), "background": ex.get("background", ""),
            "trivia": ex.get("trivia", []), "funds_affiliations": ex.get("funds_affiliations", []),
            "contact_pathway": ex.get("contact_pathway", ""),
            "good_to_knows": ex.get("good_to_knows", []),
            "movements": moves, "europe_movements": eu, "has_europe": bool(eu),
            "upcoming": ex.get("upcoming", []), "news": ex.get("news", []),
            # --- wealth / advisory intelligence ---
            "family_office": ex.get("family_office", "None publicly known — verify"),
            "wealth_managers": ex.get("wealth_managers", []),
            "fund_managers": ex.get("fund_managers", []),
            "investment_preferences": ex.get("investment_preferences", []),
            "investment_appetite": ex.get("investment_appetite") or appetite_estimate(lead.get("event_type", ""), recency),
            "openness_to_meet": ex.get("openness_to_meet") or openness_estimate(addressability, recency),
        })
    out.sort(key=lambda p: p.get("lead_score", 0), reverse=True)
    return out


def facets(profiles):
    def counts(key):
        c = {}
        for p in profiles:
            v = p.get(key) or "Unknown"
            c[v] = c.get(v, 0) + 1
        return dict(sorted(c.items(), key=lambda kv: -kv[1]))
    return {"sector": counts("sector"), "region": counts("region"), "country": counts("country")}


def filter_profiles(profiles, sector=None, region=None, country=None, q=None):
    res = profiles
    if sector:  res = [p for p in res if p["sector"] == sector]
    if region:  res = [p for p in res if p["region"] == region]
    if country: res = [p for p in res if p["country"] == country]
    if q:
        ql = q.lower()
        res = [p for p in res if ql in p["name"].lower() or ql in p["company"].lower()]
    return res


def get_profile(profiles, slug):
    return next((p for p in profiles if p["slug"] == slug), None)


def initials(name):
    parts = [w for w in re.split(r"\s+", name or "") if w]
    return ((parts[0][:1] + (parts[-1][:1] if len(parts) > 1 else "")) or "?").upper()
