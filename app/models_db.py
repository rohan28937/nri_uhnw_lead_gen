"""ORM model. Profile fields stored flat; list/dict fields as JSON."""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, Float, JSON, Text
from .database import Base


class Person(Base):
    __tablename__ = "persons"
    slug = Column(String, primary_key=True)
    name = Column(String, index=True)
    role = Column(String, default="")
    company = Column(String, default="")
    sector = Column(String, index=True, default="")
    industry = Column(String, default="")
    region = Column(String, index=True, default="")
    country = Column(String, index=True, default="")
    city = Column(String, default="")
    diaspora_category = Column(String, default="")
    exchange_ticker = Column(String, default="")
    event_type = Column(String, default="")
    event_date = Column(String, default="")
    liquidity_signal = Column(Text, default="")
    est_liquid_wealth_usd_m = Column(Float, nullable=True)
    stake_pct = Column(Float, nullable=True)
    lead_score = Column(Integer, default=0, index=True)
    priority = Column(String, default="")
    public_source = Column(String, default="")
    source_url = Column(String, default="")
    notes = Column(Text, default="")
    photo_url = Column(String, default="")
    linkedin = Column(String, default="")
    contact_pathway = Column(Text, default="")
    funds_affiliations = Column(JSON, default=list)
    good_to_knows = Column(JSON, default=list)
    news = Column(JSON, default=list)
    photo_file = Column(String, default="")
    background = Column(Text, default="")
    trivia = Column(JSON, default=list)
    movements = Column(JSON, default=list)
    upcoming = Column(JSON, default=list)
    family_office = Column(String, default="")
    wealth_managers = Column(JSON, default=list)
    fund_managers = Column(JSON, default=list)
    investment_preferences = Column(JSON, default=list)
    investment_appetite = Column(String, default="")
    openness_to_meet = Column(String, default="")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
