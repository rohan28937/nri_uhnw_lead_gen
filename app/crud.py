"""Seed/refresh the DB from the profile layer, and query helpers."""
from __future__ import annotations
from sqlalchemy import func
from .database import Base, engine, SessionLocal
from .models_db import Person
from .profiles import build_profiles


def init_and_seed(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not force and db.query(Person).count() > 0:
            return db.query(Person).count()
        profiles = build_profiles()
        for p in profiles:
            db.merge(Person(**{k: p.get(k) for k in Person.__table__.columns.keys()}))
        db.commit()
        return db.query(Person).count()
    finally:
        db.close()


def query_people(db, sector=None, region=None, country=None, q=None):
    qry = db.query(Person)
    if sector:
        qry = qry.filter(Person.sector == sector)
    if region:
        qry = qry.filter(Person.region == region)
    if country:
        qry = qry.filter(Person.country == country)
    if q:
        like = f"%{q}%"
        qry = qry.filter((Person.name.ilike(like)) | (Person.company.ilike(like)))
    return qry.order_by(Person.lead_score.desc()).all()


def facet_counts(db):
    def c(col):
        rows = db.query(col, func.count()).group_by(col).order_by(func.count().desc()).all()
        return {(k or "Unknown"): n for k, n in rows}
    return {"sector": c(Person.sector), "region": c(Person.region), "country": c(Person.country)}
