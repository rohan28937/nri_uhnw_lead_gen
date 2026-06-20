"""Auto-enrichment (gated on API keys; graceful without them).

Fills, per person:
  - news clippings        (Serper.dev Google News)
  - public appearances    -> movements + upcoming  (Serper.dev Google Search; events feed)
  - contact pathway + photo (Apollo.io people match)

Two modes:
  python -m app.enrich            -> update the live DB (used by /admin/refresh)
  python -m app.enrich --extras   -> update data/profile_extras.json (stateless; the weekly
                                     GitHub Action commits the result)

No keys -> no-op; curated data is preserved. Appearance/visit data is limited to PUBLICLY
announced events (conferences, keynotes) — not private travel.
"""
from __future__ import annotations
import argparse, datetime, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT = os.path.join(ROOT, "data", "snapshot.json")
EXTRAS = os.path.join(ROOT, "data", "profile_extras.json")
SERPER_NEWS = "https://google.serper.dev/news"
SERPER_SEARCH = "https://google.serper.dev/search"
APOLLO_URL = "https://api.apollo.io/v1/people/match"
THIS_YEAR = datetime.date.today().year

# light place extraction for the movement timeline / Europe detection
PLACES = ["London", "Paris", "Davos", "Zurich", "Geneva", "Dublin", "Amsterdam", "Lisbon",
          "Munich", "Berlin", "Madrid", "Barcelona", "Milan", "Monaco", "Stockholm", "Vienna",
          "Dubai", "Abu Dhabi", "Singapore", "Hong Kong", "New York", "San Francisco",
          "Las Vegas", "Boston", "Mumbai", "Bengaluru", "Delhi", "Gurugram", "Toronto"]


def _post(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


def _serper(url, q, key, num=8, key_field="organic"):
    try:
        return _post(url, {"q": q, "num": num}, {"X-API-KEY": key}).get(key_field, [])
    except Exception as e:
        print(f"  [enrich] '{q}': {e}")
        return []


def _place(text):
    for p in PLACES:
        if re.search(rf"\b{re.escape(p)}\b", text, re.I):
            return p
    return ""


def _year(text):
    m = re.search(r"\b(20\d{2})\b", text or "")
    return m.group(1) if m else ""


def news_for(name, company, key, limit=5):
    items = _serper(SERPER_NEWS, f'"{name}" {company}', key, limit, "news")
    return [{"title": i.get("title", ""), "url": i.get("link", "")}
            for i in items[:limit] if i.get("link")]


def appearances_for(name, company, key):
    """Return (movements, upcoming) from public search hits. Best-effort + tagged for verify."""
    movements, upcoming = [], []
    for it in _serper(SERPER_SEARCH, f'"{name}" {company} (conference OR keynote OR summit OR speaker)', key, 8):
        title, snip, link = it.get("title", ""), it.get("snippet", ""), it.get("link", "")
        blob = f"{title} {snip}"
        yr, place = _year(blob), _place(blob)
        entry = {"date": yr, "place": place or "—", "event": title[:140],
                 "source": link, "auto": True}
        if yr and yr.isdigit() and int(yr) > THIS_YEAR:
            upcoming.append(entry)
        else:
            movements.append(entry)
    # dedupe by event text
    def dedupe(rows):
        seen, out = set(), []
        for r in rows:
            k = r["event"].lower()[:60]
            if k not in seen:
                seen.add(k); out.append(r)
        return out[:8]
    return dedupe(movements), dedupe(upcoming)


def contact_for(name, company, key):
    parts = name.split()
    payload = {"api_key": key, "first_name": parts[0],
               "last_name": parts[-1] if len(parts) > 1 else "", "organization_name": company}
    try:
        data = _post(APOLLO_URL, payload, {})
    except Exception as e:
        print(f"  [enrich.contact] {name}: {e}")
        return None, ""
    p = data.get("person") or {}
    bits = []
    if p.get("email"):
        bits.append(f"Email: {p['email']}")
    if p.get("linkedin_url"):
        bits.append(p["linkedin_url"])
    if (p.get("organization") or {}).get("name"):
        bits.append(f"via {p['organization']['name']}")
    return ("; ".join(bits) or None), (p.get("photo_url") or "")


def _merge(curated, auto):
    """Keep curated entries first; append auto entries whose event isn't already present."""
    have = {(e.get("event") or "").lower()[:60] for e in curated}
    return curated + [a for a in auto if (a.get("event") or "").lower()[:60] not in have]


def _keys():
    return os.getenv("SERPER_API_KEY"), os.getenv("APOLLO_API_KEY")


def run_db():
    serper, apollo = _keys()
    if not serper and not apollo:
        print("  [enrich] no keys set — skipping (curated data kept).")
        return 0
    from .database import SessionLocal
    from .models_db import Person
    db = SessionLocal(); updated = 0
    try:
        for person in db.query(Person).all():
            ch = False
            if serper:
                nws = news_for(person.name, person.company, serper)
                if nws: person.news = nws; ch = True
                mv, up = appearances_for(person.name, person.company, serper)
                if mv: person.movements = _merge(person.movements or [], mv); ch = True
                if up: person.upcoming = _merge(person.upcoming or [], up); ch = True
            if apollo:
                c, photo = contact_for(person.name, person.company, apollo)
                if c: person.contact_pathway = c; ch = True
                if photo: person.photo_url = photo; ch = True
            if ch: updated += 1
        db.commit()
    finally:
        db.close()
    print(f"  [enrich] updated {updated} DB profiles")
    return updated


def _norm(name):
    n = (name or "").lower().strip()
    for t in (" & family", " and family", " & co", "(", ")"):
        n = n.split(t)[0]
    return " ".join(n.split())


def run_extras():
    serper, apollo = _keys()
    if not serper and not apollo:
        print("  [enrich] no keys set — skipping extras enrichment.")
        return 0
    snap = json.load(open(SNAPSHOT, encoding="utf-8")) if os.path.exists(SNAPSHOT) else []
    extras = json.load(open(EXTRAS, encoding="utf-8")) if os.path.exists(EXTRAS) else {}
    updated = 0
    for lead in snap:
        name, company = lead.get("name", ""), lead.get("company", "")
        e = extras.get(_norm(name), {})
        if serper:
            nws = news_for(name, company, serper)
            if nws: e["news"] = nws
            mv, up = appearances_for(name, company, serper)
            if mv: e["movements"] = _merge(e.get("movements", []), mv)
            if up: e["upcoming"] = _merge(e.get("upcoming", []), up)
        if apollo:
            c, photo = contact_for(name, company, apollo)
            if c: e["contact_pathway"] = c
            if photo: e["photo_url"] = photo
        if e:
            extras[_norm(name)] = e; updated += 1
    json.dump(extras, open(EXTRAS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"  [enrich] wrote extras for {updated} profiles -> {EXTRAS}")
    return updated


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extras", action="store_true")
    (run_extras if ap.parse_args().extras else run_db)()
