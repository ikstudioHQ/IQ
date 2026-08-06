"""
tools/continuity/reference_image_manager.py

Discovers reference images already present in the repo (character bible
entries, environment bible entries, prop registry entries -- all
populated by migrate_v272_to_continuity.py), validates they resolve on
disk, and selects a priority-ordered, capability-limited subset for a
given clip.

This module NEVER hardcodes a reference-image count limit. Every limit
comes from the ProviderCapabilities object passed in by the caller.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.providers.base import ProviderCapabilities, ValidationError

Role = Literal["primary_character", "secondary_character", "prop", "environment"]


@dataclass(frozen=True)
class ReferenceImageAsset:
    asset_id: str
    path: str
    role: Role
    owner_id: str  # character_id / prop_id / location_id this image represents
    resolves_on_disk: bool


class ReferenceImageManager:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._character_dir = self.root / "continuity" / "character_bible"
        self._environment_dir = self.root / "continuity" / "environment_bible"
        self._prop_dir = self.root / "continuity" / "prop_registry"

    # -- discovery ----------------------------------------------------

    def _load_bible(self, directory: Path, entity_id: str) -> dict | None:
        path = directory / f"{entity_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def get_for_character(self, character_id: str) -> list[ReferenceImageAsset]:
        bible = self._load_bible(self._character_dir, character_id)
        if not bible:
            return []
        return [
            ReferenceImageAsset(
                asset_id=img["asset_id"],
                path=img["path"],
                role="primary_character",  # role gets downgraded by select_for_clip if secondary
                owner_id=character_id,
                resolves_on_disk=self._resolves(img.get("path")),
            )
            for img in bible.get("reference_images", [])
            if img.get("path")
        ]

    def get_for_environment(self, location_id: str) -> list[ReferenceImageAsset]:
        bible = self._load_bible(self._environment_dir, location_id)
        if not bible:
            return []
        return [
            ReferenceImageAsset(
                asset_id=f"{location_id}_env_{i}",
                path=img["path"],
                role="environment",
                owner_id=location_id,
                resolves_on_disk=self._resolves(img.get("path")),
            )
            for i, img in enumerate(bible.get("reference_images", []))
            if img.get("path")
        ]

    def get_for_prop(self, prop_id: str) -> list[ReferenceImageAsset]:
        bible = self._load_bible(self._prop_dir, prop_id)
        if not bible:
            return []
        return [
            ReferenceImageAsset(
                asset_id=f"{prop_id}_prop_{i}",
                path=img["path"],
                role="prop",
                owner_id=prop_id,
                resolves_on_disk=self._resolves(img.get("path")),
            )
            for i, img in enumerate(bible.get("reference_images", []))
            if img.get("path")
        ]

    def _resolves(self, rel_path: str | None) -> bool:
        if not rel_path:
            return False
        return (self.root / rel_path).exists()

    # -- validation -----------------------------------------------------

    def validate(self, asset: ReferenceImageAsset) -> list[ValidationError]:
        errors: list[ValidationError] = []
        if not asset.resolves_on_disk:
            errors.append(ValidationError(
                field="path",
                message=f"reference image for {asset.owner_id} does not resolve on disk: {asset.path}",
            ))
        suffix = Path(asset.path).suffix.lower()
        if suffix not in (".png", ".jpg", ".jpeg"):
            errors.append(ValidationError(
                field="path",
                message=f"unexpected image format '{suffix}' for {asset.owner_id}",
                severity="warning",
            ))
        return errors

    # -- selection ------------------------------------------------------

    def select_for_clip(
        self,
        *,
        primary_character_ids: list[str],
        secondary_character_ids: list[str],
        environment_id: str | None,
        prop_ids: list[str],
        capabilities: ProviderCapabilities,
        forced_owner_ids: list[str] | None = None,
    ) -> tuple[list[ReferenceImageAsset], list[str]]:
        """Priority order: primary character(s) > secondary character(s) >
        critical prop/environment. Truncates strictly to
        capabilities.max_reference_images -- reads that number from the
        capability object, never a literal.

        forced_owner_ids (Phase 5 addition, default None = unchanged Phase 2
        behavior): owner ids that Auto-Repair has decided must be included
        this attempt even if they'd normally lose out to budget -- e.g. a
        character flagged for drift needs its reference image locked in on
        the retry. Sorted to the very front, ahead of the normal
        primary/secondary/prop/environment priority order.

        Returns (selected_assets, dropped_notes) so callers/QA can see
        what got left out and fall back to text-only lock for it.
        """
        candidates: list[ReferenceImageAsset] = []

        for cid in primary_character_ids:
            candidates.extend(
                a for a in self.get_for_character(cid) if a.resolves_on_disk
            )
        for cid in secondary_character_ids:
            for a in self.get_for_character(cid):
                if a.resolves_on_disk:
                    candidates.append(
                        ReferenceImageAsset(a.asset_id, a.path, "secondary_character", a.owner_id, True)
                    )
        for pid in prop_ids:
            candidates.extend(a for a in self.get_for_prop(pid) if a.resolves_on_disk)
        if environment_id:
            candidates.extend(a for a in self.get_for_environment(environment_id) if a.resolves_on_disk)

        priority = {"primary_character": 0, "secondary_character": 1, "prop": 2, "environment": 3}
        forced = set(forced_owner_ids or [])
        candidates.sort(key=lambda a: (0 if a.owner_id in forced else 1, priority[a.role]))

        if not capabilities.supports_reference_images:
            dropped = [f"{a.owner_id} ({a.role}): provider does not support reference images at all" for a in candidates]
            return [], dropped

        limit = capabilities.max_reference_images
        selected = candidates[:limit]
        dropped = [
            f"{a.owner_id} ({a.role}): dropped, exceeds provider limit of {limit} reference images"
            for a in candidates[limit:]
        ]
        return selected, dropped
