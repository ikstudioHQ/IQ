"""
tools/orchestration/testing_overrides.py

The ONLY way to skip Duration/Islamic/Continuity gate enforcement in
tools/orchestration/season_orchestrator.py. There is no boolean flag
and no default-off behavior. Real production calls to
generate_season()/advance() always run every required gate unless a
caller deliberately imports this class from this dedicated, obviously-
named test-only module and constructs it with a reason.

This module must never be imported from any production code path.
It exists so unit/integration tests that are deliberately exercising
something OTHER than gate behavior (resumability, safety blocking,
repair-attempt caps, ID validation, etc.) can use minimal fixture
content without every such test having to satisfy a real 10-minute,
fully-sourced, cross-episode-consistent season just to test an
unrelated mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DisableProductionGatesForTesting:
    """Construct this ONLY inside a test. `reason` is required and is
    written into the season's job state for auditability -- if a real
    production run's job state ever contains this override, that's
    itself a signal something is wrong, since production code never
    constructs this object."""
    reason: str

    def __post_init__(self):
        if not self.reason or not self.reason.strip():
            raise ValueError(
                "DisableProductionGatesForTesting requires a non-empty reason -- "
                "this is deliberately not a convenience default-able flag."
            )
