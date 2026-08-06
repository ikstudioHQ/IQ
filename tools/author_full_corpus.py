#!/usr/bin/env python3
"""Create explicit AUTHORED_PRODUCTION_DIRECTION plans for the existing corpus.
Creative staging here is new production direction; it is never represented as canonical evidence.
"""
from pathlib import Path
import json,re,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'production'/'authored_generation_plans'

def sec(t):
    a,b=map(int,t.split(':')); return a*60+b

def split_phrases(text):
    # Preserve exact words/punctuation while preferring line/phrase boundaries.
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    out=[]
    for line in lines:
        parts=re.split(r'(?<=[,;.!?])\s+',line)
        for p in parts:
            if p.strip(): out.append(p.strip())
    return out

def song_sections(path):
    txt=path.read_text(encoding='utf-8')
    ranges=[]
    for name,a,b in re.findall(r'^\|\s*([^|]+?)\s*\|\s*(\d+:\d+)-(\d+:\d+)\s*\|',txt,re.M):
        if 'intro' not in name.lower(): ranges.append((sec(a),sec(b)))
    body=txt.split('Lyrics contain',1)[0]
    blocks=re.findall(r'^\[([^\]]+)\]\s*\n(.*?)(?=^\[|\Z)',body,re.M|re.S)
    sections=[]
    for idx,(name,content) in enumerate(blocks):
        if idx>=len(ranges): break
        lines=[]
        for x in content.strip().splitlines():
            if re.match(r'^(Chorus|Bridge|Verse|Outro).*ties to|^Lyric word count:|^Lyrics contain|^final seconds',x,re.I): break
            lines.append(x)
        clean='\n'.join(lines)
        sections.append({'name':name,'range':ranges[idx],'phrases':split_phrases(clean)})
    return sections

def scene_rows(songdir):
    txt=(songdir/'scene_breakdown.md').read_text(encoding='utf-8')
    rows=[]
    for line in txt.splitlines():
        if re.match(r'^\| Scene \d+ \|',line):
            cells=[c.strip() for c in line.strip('|').split('|')]
            m=re.match(r'(\d+):(\d+)-(\d+):(\d+)',cells[1]);
            if not m: continue
            a=int(m.group(1))*60+int(m.group(2)); b=int(m.group(3))*60+int(m.group(4))
            chars=[x.strip() for x in cells[3].split(',') if x.strip().startswith('char_')]
            rows.append({'scene_id':'scene_'+cells[0].split()[-1].zfill(2),'start':a,'end':b,'location':cells[2],'chars':chars,'action':cells[4],'look':cells[5]})
    return rows

def phrases_for_scene(sections,a,b):
    phrases=[]
    for s in sections:
        x,y=s['range']
        if max(a,x)<min(b,y): phrases.extend(s['phrases'])
    return phrases

def chunk_phrases(phrases,max_words=16):
    chunks=[]; cur=[]; n=0
    for p in phrases:
        w=len(p.split())
        if cur and n+w>max_words: chunks.append(' '.join(cur)); cur=[]; n=0
        if w>max_words:
            words=p.split()
            while len(words)>max_words:
                chunks.append(' '.join(words[:max_words])); words=words[max_words:]
            if words: cur=[' '.join(words)]; n=len(words)
        else: cur.append(p); n+=w
    if cur: chunks.append(' '.join(cur))
    return chunks

def state(loc,chars,action,axis='stable-front'):
    return {'location':loc,'position':{c:f'stable slot {i+1}' for i,c in enumerate(chars)},'orientation':{c:'toward shared action focus' for c in chars},'props':{},'emotion':'scene-consistent','camera_axis':axis,'action_state':action}

def author_song(songdir):
    sid=songdir.name; sections=song_sections(songdir/'lyrics_and_song.md'); rows=scene_rows(songdir)
    plans=[]
    for r in rows:
        duration=r['end']-r['start']; count=math.ceil(duration/8); unitdur=duration/count
        phrases=chunk_phrases(phrases_for_scene(sections,r['start'],r['end']), max_words=max(6,int(unitdur*2.2)))
        buckets=[[] for _ in range(count)]
        bi=0; cap=max(1,int(unitdur*2.2)); used=0
        for p in phrases:
            w=len(p.split())
            if bi < count-1 and used+w>cap: bi+=1; used=0
            buckets[bi].append(p); used+=w
        units=[]; prev=None
        for i in range(count):
            a=round(i*unitdur,3); b=round((i+1)*unitdur,3)
            chars=r['chars']; text=' '.join(buckets[i]).strip()
            # Authored performer direction: first visible canonical character leads; all others remain silent.
            perf=[]
            if text and chars:
                need=len(text.split())/2.2
                if need>(b-a):
                    # conservative: mark plan for review instead of impossible timing
                    raise RuntimeError(f'{sid} {r["scene_id"]} unit {i+1}: lyric chunk {need:.2f}s > {b-a:.2f}s')
                perf=[{'character_id':chars[0],'type':'singing','text':text,'start_seconds':a,'end_seconds':round(a+need,3)}]
            ina=prev if prev else state(r['location'],chars,'begin scene action')
            out=state(r['location'],chars, 'continue scene action' if i<count-1 else 'scene action settled')
            units.append({'generation_unit_id':f'{sid}_{r["scene_id"]}_u{i+1:02d}','parent_scene_id':r['scene_id'],'sequence':i+1,'start_seconds':a,'end_seconds':b,'exact_character_count':len(chars),'visible_characters':chars,'silent_characters':[c for c in chars if not perf or c!=perf[0]['character_id']],'performance':perf,'primary_action':r['action']+f' Authored beat {i+1}/{count}: use restrained, continuity-safe motion.','secondary_reaction':'Visible non-performers react naturally without lip-sync; keep silhouettes separated.','camera':f'{r["look"]}; stable blocking, no orbit, preserve camera axis','location':r['location'],'lighting':r['look'],'music_continuity':'continue canonical song bed seamlessly','in_state':ina,'out_state':out,'provenance_class':'AUTHORED_PRODUCTION_DIRECTION'})
            prev=out
        plans.append({'schema_version':'2.66','provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'song','parent_id':sid,'logical_scene_id':r['scene_id'],'generation_units':units})
    return plans

def author_episode(epdir):
    data=json.loads((epdir/'scene_contract.json').read_text(encoding='utf-8')); eid=data['episode_id']; plans=[]
    for s in data['scenes']:
        chars=[c for c in s['visible_characters'] if c.startswith('char_')]
        if len(chars) != len(s['visible_characters']) or any(not e.get('character_id','').startswith('char_') for e in s.get('performance_events',[])):
            # Cannot substitute an undefined background performer with a canonical character.
            continue
        dur=float(s['duration_seconds']); count=math.ceil(dur/8); ud=dur/count
        events=s.get('performance_events',[]); pieces=[]
        for e in events:
            words=e['text'].split(); cap=max(5,int(ud*2.8)-1)
            while words:
                part=' '.join(words[:cap]); words=words[cap:]
                pieces.append({'character_id':e['character_id'],'text':part})
        if len(pieces)>count:
            count=max(count,len(pieces)); ud=dur/count
            # re-split against the smaller unit capacity
            pieces=[]
            for e in events:
                words=e['text'].split(); cap=max(5,int(ud*2.8)-1)
                while words:
                    part=' '.join(words[:cap]); words=words[cap:]
                    pieces.append({'character_id':e['character_id'],'text':part})
            if len(pieces)>count: count=len(pieces); ud=dur/count
        buckets=[[] for _ in range(count)]
        for i,e in enumerate(pieces): buckets[min(i,count-1)].append(e)
        units=[]; prev=None
        for i in range(count):
            a=round(i*ud,3); b=round((i+1)*ud,3); perf=[]; cursor=a
            for e in buckets[i]:
                text=e['text']; need=len(text.split())/2.8
                if cursor+need>b+1e-6: raise RuntimeError(f'{eid} {s["scene_id"]}: dialogue does not fit authored unit')
                perf.append({'character_id':e['character_id'],'type':'dialogue','text':text,'start_seconds':round(cursor,3),'end_seconds':round(cursor+need,3)}); cursor+=need+0.25
            st={'location':s['location'],'position':{c:f'stable slot {j+1}' for j,c in enumerate(chars)},'orientation':{c:'toward scene focus' for c in chars},'props':{},'emotion':'scene-consistent','camera_axis':'stable-front','action_state':'episode beat continuity'}
            ina=prev or st; out=dict(st)
            units.append({'generation_unit_id':f'{eid}_{s["scene_id"]}_u{i+1:02d}','parent_scene_id':s['scene_id'],'sequence':i+1,'start_seconds':a,'end_seconds':b,'exact_character_count':len(chars),'visible_characters':chars,'silent_characters':[c for c in chars if c not in {x['character_id'] for x in perf}],'performance':perf,'primary_action':f'Authored staging beat {i+1}/{count} for the existing scene; preserve the source story action and use restrained continuity-safe movement.','secondary_reaction':'Non-speaking visible characters react without lip-sync.','camera':'stable medium composition; preserve axis; no orbiting camera','location':s['location'],'lighting':'preserve source scene lighting and time continuity','music_continuity':'preserve episode audio continuity','in_state':ina,'out_state':out,'provenance_class':'AUTHORED_PRODUCTION_DIRECTION'})
            prev=out
        plans.append({'schema_version':'2.66','provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'episode','parent_id':eid,'logical_scene_id':s['scene_id'],'generation_units':units})
    return plans

def main():
    OUT.mkdir(parents=True,exist_ok=True); total=0
    for sd in sorted((ROOT/'production/songs').glob('song_[0-9][0-9][0-9]')):
        for plan in author_song(sd):
            d=OUT/'songs'/sd.name; d.mkdir(parents=True,exist_ok=True); (d/f'{plan["logical_scene_id"]}.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf-8'); total+=len(plan['generation_units'])
    for ed in sorted((ROOT/'production/episodes').iterdir()):
        if not (ed/'scene_contract.json').exists(): continue
        for plan in author_episode(ed):
            d=OUT/'episodes'/ed.name; d.mkdir(parents=True,exist_ok=True); (d/f'{plan["logical_scene_id"]}.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf-8'); total+=len(plan['generation_units'])
    print('authored generation units:',total)
if __name__=='__main__': main()
