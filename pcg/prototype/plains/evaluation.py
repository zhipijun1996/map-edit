"""Evaluate executed mechanics/decisions; labels never create diversity."""
import copy,random
from .synthesis import identity
from ..factory.core.quality import counts,gate,POLICY,digest

def observed(case,result):
 frames=result.get('frames',[]);events=result.get('plains',{}).get('events',[]);timeline=[];air_shots=[];refunds=[]
 for f in frames:
  for e in f.get('accepted',[]):
   if e['type']=='ground_jump':timeline.append((f['frame'],'jump'))
   if e['type']=='shot':
    dx,dy=e['direction'];token='recoil_up'if dy>.7 else'recoil_horizontal'if abs(dy)<.2 else'recoil_diagonal';timeline.append((f['frame'],token))
    if not f['grounded']:air_shots.append(f['frame'])
 for e in events:
  if e['type']=='bell_open':timeline.append((e['frame'],'open_bell'))
  if e['type']=='enemy_hit'and e['fired_airborne']and e['player_airborne']:timeline.append((e['frame'],'air_hit'))
 for a,b in zip(frames,frames[1:]):
  if not a['grounded']and not b['grounded']and b['shot_charges']>a['shot_charges']:
   recent=[e for e in events if e['type']=='enemy_hit'and e['fired_airborne']and 0<=b['frame']-e['frame']<=2]
   if recent:refunds.append(b['frame']);timeline.append((b['frame'],'air_hit_refund'))
  if not a['grounded']and b['grounded']:timeline.append((b['frame'],'land_recover'))
 sequence=[t for _,t in sorted(timeline,key=lambda p:p[0])]
 continuous_two=any(all(not f['grounded']for f in frames if x<=f['frame']<=y)for x,y in zip(air_shots,air_shots[1:]))
 return dict(sequence=sequence,signature=digest(sequence)[:16],air_shots=len(air_shots),refunds=len(refunds),continuous_two_air_shots=continuous_two,opened_bells=sorted(set(e['id']for e in events if e['type']=='bell_open')),air_enemy_hits=sum(e['type']=='enemy_hit'and e.get('fired_airborne',False)for e in events))
def purpose(case,result):
 behavior=observed(case,result);reasons=[]
 if not result.get('ok'):reasons.append(result.get('reason','not_stable'))
 if result.get('hp')!=5 or result.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if result.get('air_jumps',0)or result.get('grapples',0)or result.get('wall_jumps',0):reasons.append('forbidden_advanced_ability')
 for id in [x['id']for x in case.get('latches',[])]:
  if id not in behavior['opened_bells']:reasons.append('required_bell_not_opened')
 if case.get('enemies')and(behavior['refunds']<1 or not behavior['continuous_two_air_shots']):reasons.append('no_real_air_hit_refund_chain')
 if result.get('shots',0)<1:reasons.append('no_recoil_executed')
 return dict(ok=not reasons,reasons=reasons,behavior=behavior)
def instantiate(base,seed,level,trial):
 rng=random.Random(seed+trial*104729+{'clean':0,'mild':1000003,'moderate':2000006}[level]);c=copy.deepcopy(base)
 c['id']+=f'-{level}-{trial}'
 for saw in c.get('saws',[]):saw['initial_phase']=rng.random()
 for enemy in c.get('enemies',[]):enemy['initial_idle_cooldown']=rng.uniform(0,.6)
 if level!='clean':c['noise']=dict(seed=rng.randrange(2**30),timing_frames=1 if level=='mild'else 3,aim_degrees=2 if level=='mild'else 6)
 return c
def evaluate(engine,cases,seed,trials,stage,levels=('clean','mild')):
 entries={identity(c):dict(uid=identity(c),case=c,rows=[],witness=None)for c in cases};expanded=[];owners={}
 for uid,e in entries.items():
  for level in levels:
   n=trials if level!='clean'or e['case'].get('saws')or e['case'].get('enemies')else 1
   for trial in range(n):
    c=instantiate(e['case'],seed,level,trial);c['id']=uid[:12]+'-'+c['id'];expanded.append(c);owners[c['id']]=(uid,level,trial)
 for c,r,ev in engine.run(expanded,stage):
  uid,level,trial=owners[c['id']];e=entries[uid];p=purpose(c,r);e['rows'].append(dict(level=level,trial=trial,purpose=p,safe_stable=bool(r.get('ok')),phase=[x['initial_phase']for x in c.get('saws',[])],enemy_idle=[x['initial_idle_cooldown']for x in c.get('enemies',[])],evidence=ev))
  if level=='clean'and p['ok']and e['witness']is None:
   e['witness']=dict(case=c,evidence=ev,recorded_frames=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']],final=dict(frame=r['ticks'],position=[r['frames'][-1]['x'],r['frames'][-1]['y']],hp=r['hp'],behavior=p['behavior']))
 for e in entries.values():
  e['stats']={l:counts([r for r in e['rows']if r['level']==l])for l in levels};e['quality']=sum(s['rate']for s in e['stats'].values())/len(levels)
  e['behavior']=e['witness']['final']['behavior']if e['witness']else None
 return list(entries.values())
