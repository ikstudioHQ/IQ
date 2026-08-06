#!/usr/bin/env python3
"""v2.65 production-contract validation primitives.

These validators are deliberately fail-closed. They validate authored facts; they
never invent choreography, timing, ownership, continuity, or Islamic approval.
"""
from __future__ import annotations
import json, re
from pathlib import Path

MAX_GENERATION_UNIT_SECONDS = 10.0

class ContractError(ValueError): pass

def load_character_master(root: Path):
    data=json.loads((root/'sources/characters/character_master_library.json').read_text(encoding='utf-8'))
    chars=data['characters']
    ids=[c['character_id'] for c in chars]
    if len(ids)!=len(set(ids)): raise ContractError('duplicate canonical character_id')
    return {c['character_id']:c for c in chars}

def canonical_song_ids(root: Path):
    return {p.name for p in (root/'production/songs').glob('song_[0-9][0-9][0-9]') if p.is_dir()}

def validate_character_ref(cid, chars):
    if cid not in chars: raise ContractError(f'unknown/noncanonical character_id: {cid}')

def validate_generation_unit(unit, chars):
    required=('generation_unit_id','parent_scene_id','start_seconds','end_seconds','visible_characters','performance','in_state','out_state')
    missing=[k for k in required if k not in unit]
    if missing: raise ContractError('missing generation-unit fields: '+', '.join(missing))
    start=float(unit['start_seconds']); end=float(unit['end_seconds'])
    if start < 0 or end <= start: raise ContractError('invalid generation-unit timing')
    if end-start > MAX_GENERATION_UNIT_SECONDS+1e-9: raise ContractError(f'generation unit exceeds {MAX_GENERATION_UNIT_SECONDS:g}s')
    visible_list=unit['visible_characters']
    if len(visible_list)!=len(set(visible_list)): raise ContractError('duplicate visible character_id')
    visible=set(visible_list)
    for cid in visible: validate_character_ref(cid, chars)
    occupied=[]
    for event in unit['performance']:
        cid=event.get('character_id'); typ=event.get('type')
        validate_character_ref(cid, chars)
        if cid not in visible and not event.get('off_screen',False): raise ContractError(f'performer absent from visible characters: {cid}')
        if typ not in {'dialogue','singing','silent','reaction'}: raise ContractError(f'unknown performance type: {typ}')
        if typ=='silent' and (event.get('text') or event.get('lip_sync')): raise ContractError(f'silent character has speech/lip-sync: {cid}')
        if typ in {'dialogue','singing'}:
            if not event.get('text','').strip(): raise ContractError(f'missing performer text: {cid}')
            a=float(event.get('start_seconds',start)); b=float(event.get('end_seconds',end))
            if a < start or b > end or b <= a: raise ContractError(f'invalid event timing: {cid}')
            occupied.append((a,b,cid,typ))
    for i,(a,b,cid,typ) in enumerate(occupied):
        for c,d,cid2,typ2 in occupied[i+1:]:
            if max(a,c) < min(b,d) and cid==cid2: raise ContractError(f'conflicting simultaneous ownership: {cid}')
    return True

def validate_continuity(prev_out, next_in):
    """Compare only facts explicitly present in both states. Intentional changes
    must be represented by next_in.transition_from_previous."""
    transitions=set(next_in.get('transition_from_previous',[])) if isinstance(next_in,dict) else set()
    for key in ('location','wardrobe','props','position','orientation','emotion','camera_axis'):
        if key in prev_out and key in next_in and prev_out[key] != next_in[key] and key not in transitions:
            raise ContractError(f'continuity mismatch without transition: {key}')
    return True

def require_generation_units_for_scene(scene):
    duration=float(scene.get('duration_seconds') or scene.get('duration') or 0)
    units=scene.get('generation_units')
    if duration > MAX_GENERATION_UNIT_SECONDS and not units:
        raise ContractError('AUTHORING_REQUIRED: long logical scene has no authored generation units')
    return units or []

def validate_song_reference(root: Path, song_id: str):
    if song_id not in canonical_song_ids(root): raise ContractError(f'unknown canonical song_id: {song_id}')
    return True
