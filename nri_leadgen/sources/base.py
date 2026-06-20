"""Source connector interface. Every source yields Lead objects and must
degrade gracefully (return [] on any failure) so the pipeline always runs."""
from __future__ import annotations
from typing import Iterable
from ..models import Lead


class Source:
    name = "base"
    requires_key = False

    def __init__(self, config=None):
        self.config = config or {}

    def available(self) -> bool:
        return True

    def fetch(self) -> Iterable[Lead]:
        raise NotImplementedError
