"""FastAPI app: browse UHNW NRI/OCI prospects by sector/region/country + profile pages.

Run locally:  uvicorn app.main:app --reload
On startup it seeds the DB from data/snapshot.json if empty.
"""
from __future__ import annotations
import os
from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .crud import init_and_seed, query_people, facet_counts
from .models_db import Person
from .profiles import initials, _is_europe as is_europe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI(title="UHNW NRI/OCI Lead Intelligence", version="1.0.0")
app.mount("/static", StaticFiles(directory=os.path.join(ROOT, "app", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(ROOT, "app", "templates"))


@app.on_event("startup")
def _startup():
    n = init_and_seed()
    print(f"DB ready with {n} persons")


def _ctx(p):
    d = p.as_dict() if isinstance(p, Person) else dict(p)
    d["initials"] = initials(d["name"])
    d["url"] = f"/p/{d['slug']}"
    moves = d.get("movements") or []
    d["europe_movements"] = [mv for mv in moves if is_europe(mv.get("place", ""))]
    d["has_europe"] = bool(d["europe_movements"])
    return d


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db),
          sector: str | None = Query(None), region: str | None = Query(None),
          country: str | None = Query(None), q: str | None = Query(None)):
    people = [_ctx(p) for p in query_people(db, sector, region, country, q)]
    return templates.TemplateResponse(request, "index.html", {
        "request": request, "profiles": people, "facets": facet_counts(db),
        "home_url": "/", "static": "/static"})


@app.get("/p/{slug}", response_class=HTMLResponse)
def profile(slug: str, request: Request, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.slug == slug).first()
    if not person:
        raise HTTPException(404, "Profile not found")
    return templates.TemplateResponse(request, "profile.html", {
        "request": request, "p": _ctx(person), "home_url": "/", "static": "/static"})


@app.get("/api/leads")
def api_leads(db: Session = Depends(get_db), sector: str | None = None,
              region: str | None = None, country: str | None = None, q: str | None = None):
    return JSONResponse([p.as_dict() for p in query_people(db, sector, region, country, q)])


@app.get("/api/leads/{slug}")
def api_lead(slug: str, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.slug == slug).first()
    if not person:
        raise HTTPException(404, "Not found")
    return person.as_dict()


@app.get("/api/facets")
def api_facets(db: Session = Depends(get_db)):
    return facet_counts(db)


@app.post("/admin/refresh")
def admin_refresh(token: str = Query(...)):
    if token != os.getenv("ADMIN_TOKEN", ""):
        raise HTTPException(403, "Bad token")
    from .enrich import run_db
    n = init_and_seed(force=True)
    enriched = run_db()
    return {"reseeded": n, "enriched": enriched}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
