#!/usr/bin/env python3
"""Compile explicitly authored production plans into <=10s Gemini units.
Creative direction in these plans is AUTHORING data, never canonical-source inference.
"""
from __future__ import annotations
import json
from pathlib import Path
from .production_contracts import ContractError, load_character_master, validate_generation_unit, validate_continuity, validate_song_reference

WORDS_PER_SECOND_SPOKEN=2.8
WORDS_PER_SECOND_SUNG=2.2

def _words(text): return len(str(text).replace('\n',' ').split())

def validate_authored_plan(root: Path, plan: dict):
    if plan.get('provenance_class') != 'AUTHORED_PRODUCTION_DIRECTION':
        raise ContractError('authoring plan must declare AUTHORED_PRODUCTION_DIRECTION')
    chars=load_character_master(root)
    if plan.get('parent_type')=='song': validate_song_reference(root,plan['parent_id'])
    units=plan.get('generation_units') or []
    if not units: raise ContractError('AUTHORING_REQUIRED: no authored generation units')
    prior=None
    for u in units:
        vis=u.get('visible_characters',[])
        if len(vis)!=len(set(vis)): raise ContractError('duplicate physical character/canonical ID in visible characters')
        if u.get('exact_character_count') != len(vis): raise ContractError('exact character count does not match visible characters')
        validate_generation_unit(u,chars)
        for ev in u.get('performance',[]):
            if ev.get('type') in ('dialogue','singing'):
                dur=float(ev.get('end_seconds',u['end_seconds']))-float(ev.get('start_seconds',u['start_seconds']))
                rate=WORDS_PER_SECOND_SUNG if ev['type']=='singing' else WORDS_PER_SECOND_SPOKEN
                if _words(ev.get('text','')) > dur*rate+0.01:
                    raise ContractError(f'AUTHORING_REQUIRED: {ev["type"]} text exceeds feasible authored timing')
        if prior is not None: validate_continuity(prior['out_state'],u['in_state'])
        prior=u
    return True

def render_gemini_prompt(root: Path, plan: dict, unit: dict):
    chars=load_character_master(root); validate_authored_plan(root,plan)
    visible=unit['visible_characters']
    locks=[]
    for cid in visible:
        c=chars[cid]
        desc=c.get('canonical_image_prompt') or c.get('visual_identity') or c.get('appearance') or c.get('canonical_visual_description') or ''
        locks.append(f"{cid} — {c.get('canonical_name',c.get('name',cid))} — {desc}")
    perf=[]
    for e in unit.get('performance',[]):
        if e['type'] in ('dialogue','singing'):
            perf.append(f"{e['character_id']} — {e['type'].upper()}: {e['text']}")
    return '\n'.join([
        f"# READY-TO-PASTE GEMINI PROMPT — {plan['parent_id']} {unit['parent_scene_id']} {unit['generation_unit_id']}",
        f"EPISODE/SONG ID: {plan['parent_id']}",
        f"SOURCE SCENE ID: {unit['parent_scene_id']}",
        f"GENERATION UNIT ID: {unit['generation_unit_id']}",
        f"CLIP SEQUENCE: {unit['generation_unit_id']}",
        f"PARENT: {plan['parent_type']} {plan['parent_id']} / {unit['parent_scene_id']}",
        f"DURATION: {float(unit['end_seconds'])-float(unit['start_seconds']):g}s (maximum 10s)",
        f"EXACT CHARACTER COUNT: {unit['exact_character_count']}",
        "VISIBLE CANONICAL CHARACTER IDS: "+', '.join(visible),
        "CHARACTER IDENTITY LOCKS:\n"+'\n'.join(locks),
        "INSTANCE LOCK: Exactly one instance of each listed character. No clones, twins, duplicate bodies, background copies, reflected full-character copies, replacement instances, extra people or extra animals.",
        "UNLISTED CHARACTER LOCK: Do not add any character, person, child, adult, animal, performer, or replacement instance not listed above.",
        "PERFORMANCE OWNERSHIP:\n"+('\n'.join(perf) if perf else 'No spoken/sung performance.'),
        "EXACT DIALOGUE/LYRICS:\n"+('\n'.join(perf) if perf else 'None.'),
        "SILENT CHARACTERS: "+', '.join(unit.get('silent_characters',[])),
        "LIP-SYNC: only explicitly speaking/singing performers may lip-sync; silent characters must keep mouths non-speaking.",
        "GENERATION OBJECTIVE: Render this authored production beat as one self-contained continuity-safe clip.",
        "VISUAL / ANIMATION STYLE: Preserve the repository canonical Islamic Kids Studio character and environment style.",
        "REFERENCE IMAGE LOCK: Use each canonical approved/supplied reference binding when available; never substitute identity.",
        "VOICE LOCKS: Use only canonical voice identity for assigned speaking/singing characters; unresolved human voice approval remains unresolved.",
        "PROP LOCK: Preserve props exactly as stated in IN_STATE/OUT_STATE; do not create or remove props without authored transition.",
        "INITIAL FRAME: Reconstruct IN_STATE exactly; do not rely on memory of a previous clip.",
        "ACTION: "+unit.get('primary_action',''),
        "REACTION: "+unit.get('secondary_reaction',''),
        "FACIAL PERFORMANCE / REACTION: "+unit.get('secondary_reaction',''),
        "CAMERA: "+unit.get('camera',''),
        "LIGHTING: "+unit.get('lighting',''),
        "MUSIC: "+unit.get('music_continuity',''),
        "SOUND EFFECTS: Use only scene-appropriate subtle effects; never add speech or religious recitation.",
        "LOCATION: "+unit.get('location',''),
        "IN_STATE: "+json.dumps(unit['in_state'],sort_keys=True),
        "OUT_STATE: "+json.dumps(unit['out_state'],sort_keys=True),
        "CONTINUITY: first frame must match IN_STATE; final frame must match OUT_STATE exactly unless an authored transition explicitly owns a change.",
        "FINAL FRAME: Match OUT_STATE exactly and hold a stable continuity-safe handoff pose.",
        "NEXT-CLIP HANDOFF: The next independently generated clip must be able to reconstruct this OUT_STATE as its IN_STATE.",
        "NEGATIVE CONSTRAINTS: No identity drift, wardrobe drift, unexplained teleportation, prop disappearance, camera-axis reversal, random mouth movement, extra limbs, merged bodies, or unlisted performers.",
        "CHARACTER DUPLICATION NEGATIVE LOCK: Render exactly the listed character instances and no others. Each named character appears exactly once. No clones, twins, duplicated bodies, repeated faces, background copies, reflected full-character copies, replacement instances, extra children, extra adults, extra animals, merged characters, or extra limbs.",
        "RELIGIOUS SAFETY: Do not invent Islamic claims, quotations, citations, or religious actions beyond supplied content.",
        "PROVENANCE: creative choreography/state in this unit is AUTHORED_PRODUCTION_DIRECTION, not canonical-source evidence.",
    ])

def compile_plan(root: Path, plan_path: Path, out_dir: Path):
    plan=json.loads(plan_path.read_text(encoding='utf-8')); validate_authored_plan(root,plan)
    out_dir.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':'2.66','parent_type':plan['parent_type'],'parent_id':plan['parent_id'],'provenance_class':plan['provenance_class'],'generation_ready':True,'units':[]}
    for u in plan['generation_units']:
        p=out_dir/f"{u['generation_unit_id']}.md"; p.write_text(render_gemini_prompt(root,plan,u),encoding='utf-8')
        manifest['units'].append({'generation_unit_id':u['generation_unit_id'],'prompt':p.name,'duration_seconds':u['end_seconds']-u['start_seconds'],'exact_character_count':u['exact_character_count']})
    (out_dir/'generation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest
