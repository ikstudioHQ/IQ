"""
tools/providers/veo31_fast.py — Veo 3.1 Fast provider adapter.

Same request/payload shape as Veo 3.1 (same model family, same API
surface) so this is a thin subclass that just points at the Fast
capability file and Fast model id. If Fast ever diverges in payload
shape, override build_payload() here rather than branching inside
Veo31Provider.
"""
from __future__ import annotations

from pathlib import Path

from tools.providers.veo31 import Veo31Provider

CAPABILITY_FILE = (
    Path(__file__).resolve().parents[2] / "continuity" / "providers" / "capabilities" / "veo_3_1_fast.json"
)


class Veo31FastProvider(Veo31Provider):
    def __init__(self, capability_file: str | Path = CAPABILITY_FILE):
        super().__init__(capability_file=capability_file)
