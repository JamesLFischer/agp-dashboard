#!/usr/bin/env python3
"""Regenerate AGP dashboard site/ from v4/METRICS_HISTORY.jsonl + evidence. Free/local only."""
import json,os,glob,shutil,subprocess,html,datetime
from PIL import Image
A='/workspace/agp'; D=os.path.dirname(os.path.abspath(__file__)); S=os.environ.get('AGP_SITE','/workspace/agp-dashboard/docs'); M=os.path.join(S,'media')
os.makedirs(M,exist_ok=True)
H=[json.loads(l) for l in open(f'{A}/v4/METRICS_HISTORY.jsonl') if l.strip()]
base=H[0]; keep=[h for h in H if h.get('decision')!='REVERT']; cur=dict(base['kpi']); src=dict(base.get('source',{}))
for h in keep[1:]:
    for k,v in h['kpi'].items():
        if v is not None: cur[k]=v
    src.update(h.get('source',{}))
KP=[('win_rate','Live win rate','Win rate','pct',1,True),('win_rate_sim','Practice win rate (SIM)','Win rate','pct',1,False),
('placement_heatmap_sim','Placement accuracy vs pros','Placement','pct',1,False),('deck_meta_alignment','Deck vs meta','Deck building','pct',1,False),
('threat_coverage','Meta threat coverage','Deck building','pct',1,False),('counter_success_strict','Counter success (strict)','Counters','pct',1,False),
('spell_hit','Spell aim hit rate','Spell aim','pct',1,False),('wasted_spells_per_match','Wasted spells / match','Spell aim','num',-1,False),
('elixir_waste_s','Elixir leaked (s/match)','Elixir & movement','num',-1,False),('decision_match','Decision match vs pros','Imitation','pct',1,False),
('deck_upgrades_day','Deck upgrades / day','Upgrades & rewards','num',1,True),('claim_rate','Reward claim rate','Upgrades & rewards','pct',1,True),
('pro_plays','Pro plays learned','Learning','int',1,False),('own_matches','Own-match sample','Sample','int',1,False)]
def fmt(v,t):
    if v is None: return '—'
    if isinstance(v,str): return html.escape(v)
    return f'{v*100:.1f}%' if t=='pct' else (f'{int(v):,}' if t=='int' else f'{v:.2f}')
def spark(k):
    pts=[h['kpi'].get(k) for h in keep]; pts=[p for p in pts if isinstance(p,(int,float))]
    if len(pts)<2: return '<svg class=sp></svg>'
    lo,hi=min(pts),max(pts); r=(hi-lo) or 1
    xy=' '.join(f'{i*100/(len(pts)-1):.1f},{28-(p-lo)/r*24:.1f}' for i,p in enumerate(pts))
    return f'<svg class=sp viewBox="0 0 100 30" preserveAspectRatio=none><polyline points="{xy}"/></svg>'
cards=[]
for k,name,axis,t,good,live in KP:
    b,c=base['kpi'].get(k),cur.get(k); s=src.get(k,'LIVE' if live else '—')
    paused = live and (c is None or k=='win_rate' and base.get('mode')=='offline')
    if k=='win_rate': s='LIVE'; paused=True; b_lbl=f"LOG {fmt(b,t)} (n={base['kpi'].get('win_rate_n')})"
    else: b_lbl=fmt(b,t)
    d=''; cls=''
    if isinstance(b,(int,float)) and isinstance(c,(int,float)) and not paused:
        dv=c-b; cls='up' if dv*good>0 else ('down' if dv*good<0 else ''); d=(f'{dv*100:+.1f} pts' if t=='pct' else f'{dv:+,.2f}'.rstrip('0').rstrip('.'))
    cv='Paused' if paused else fmt(c,t)
    cards.append(f'<div class="kpi {"paused" if paused else ""}"><div class=ax>{axis}<span class="tag {s.split("+")[0].lower()}">{s}</span></div><h3>{name}</h3><div class=cv>{cv}</div><div class=row><span>Baseline {b_lbl}</span><span class="d {cls}">{d}</span></div>{spark(k)}</div>')
# evidence
pref=['v4/dashboard.png','contact.png','sheet.png','spells.jpg','v4/end-0943-batch.png','v4/end-batch-confirm.png','v4/cal_deck_equipped.png','after_meta.png','cmp.png','v4/diag-2342.png','pair.jpg','home.png']
imgs=[p for p in pref if os.path.exists(f'{A}/{p}')]
for d in ['evidence','publish','v4/evidence','../agp-dashboard/docs/evidence']:
    imgs+= [os.path.relpath(p,A) for p in sorted(glob.glob(f'{A}/{d}/**/*.*',recursive=True)) if p.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
imgs+= [os.path.relpath(p,A) for p in sorted(glob.glob(f'{A}/v4/end-*.png'))[-8:] if os.path.relpath(p,A) not in imgs]
imgs=list(dict.fromkeys(imgs))[:30]
gal=[]
for p in imgs:
    o=p.replace('/','_').rsplit('.',1)[0]+'.jpg'
    if not os.path.exists(f'{M}/{o}'):
        try: im=Image.open(f'{A}/{p}').convert('RGB'); im.thumbnail((1400,1400)); im.save(f'{M}/{o}',quality=82)
        except Exception: continue
    gal.append(f'<a href="media/{o}" target=_blank class=g><img loading=lazy src="media/{o}"><span>{html.escape(p)}</span></a>')
vids=[]
for v in sorted(glob.glob(f'{A}/**/*.mp4',recursive=True)+glob.glob(f'{A}/**/*.webm',recursive=True)):
    if '/dashboard/' in v: continue
    o=os.path.relpath(v,A).replace('/','_').rsplit('.',1)[0]+'_web.mp4'
    if not os.path.exists(f'{M}/{o}'):
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',v,'-t','60','-vf','scale=-2:720','-c:v','libx264','-crf','30','-preset','veryfast','-an','-movflags','+faststart',f'{M}/{o}'])
        subprocess.run(['ffmpeg','-y','-loglevel','error','-ss','3','-i',f'{M}/{o}','-frames:v','1',f'{M}/{o}.jpg'])
    vids.append(f'<figure class=v><video controls muted playsinline preload=metadata poster="media/{o}.jpg" src="media/{o}"></video><figcaption>{html.escape(os.path.basename(v))}</figcaption></figure>')
hero=f'<video class=herov autoplay muted loop playsinline src="media/{vids and vids[0].split("src=\"media/")[1].split("\"")[0]}"></video>' if vids else (f'<img class=herov src="media/{imgs[0].replace("/","_").rsplit(".",1)[0]}.jpg">' if imgs else '')
rows=''.join(f'<tr class="{h["decision"].lower()}"><td>{h["cycle"]}</td><td>{h["ts"][:16].replace("T"," ")}</td><td>{html.escape(h["change"])}</td><td><b>{h["decision"]}</b></td><td>{html.escape(h.get("notes",""))}</td></tr>' for h in reversed(H))
last=H[-1]; now=datetime.datetime.now().strftime('%b %d, %Y %I:%M %p PT')
page=open(os.path.join(D,'template.html')).read()
for k,v in {'HERO':hero,'CARDS':''.join(cards),'GALLERY':''.join(gal) or '<p class=muted>Evidence lands here each cycle.</p>','VIDEOS':''.join(vids) or '<p class=muted>Recordings land here each cycle.</p>','ROWS':rows,'UPDATED':now,'CYCLE':str(last['cycle']),'MODE':last.get('mode','offline').upper(),'NMATCH':f"{cur.get('own_matches',0):,}",'NPRO':f"{cur.get('pro_plays',0):,}",'NKEEP':str(len(keep)-1)}.items():
    page=page.replace('{{'+k+'}}',v)
open(f'{S}/index.html','w').write(page); open(f'{S}/.nojekyll','w').close()
json.dump({'baseline':base,'current':cur,'history':H},open(f'{S}/data.json','w'),indent=1)
print('built',S,len(gal),'imgs',len(vids),'videos')
