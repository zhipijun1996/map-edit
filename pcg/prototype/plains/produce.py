"""Freeze semantic finalists, fresh holdout once, retain failed counterfactuals."""
import argparse,copy,json,collections,time
from .engine import ROOT,PlainsEngine
from .synthesis import identity
from .evaluation import evaluate,instantiate
from ..factory.core.quality import module_hash,gate,POLICY

def alternative_cases(base):
 out=[]
 no=copy.deepcopy(base);no['id']+='-without-shoot';no['control_plan']=[p for p in no['control_plan']if p['op']!='shoot'];out.append(('no_shoot',no))
 held=copy.deepcopy(no);held['id']+='-held-jump'
 for p in held['control_plan']:
  if p['op']=='jump_release':p['trigger']['after']=18
 out.append(('no_shoot_held_jump',held))
 if base.get('enemies'):
  no=copy.deepcopy(base);no['id']+='-without-enemy';no['enemies']=[];out.append(('no_enemy_same_shots',no))
 if base.get('latches'):
  no=copy.deepcopy(base);no['id']+='-wrong-aim'
  for p in no['control_plan']:
   if p['op']=='shoot':p['direction']=[-1,0]
  out.append(('wrong_aim',no))
 if base.get('saws'):
  no=copy.deepcopy(base);no['id']+='-without-wait';no['control_plan']=[p for p in no['control_plan']if p.get('trigger',{}).get('dynamic',{}).get('kind')!='saw_phase'];out.append(('no_saw_observation',no))
 return out

def run(name,calibration,holdout_seed=1240810,families=None):
 started=time.perf_counter();source=ROOT/'results'/calibration;entries=json.loads((source/'entries.json').read_text());out=ROOT/'results'/name;engine=PlainsEngine(out,12)
 groups=collections.defaultdict(list)
 for e in entries:
  if families and e['case']['family']not in families:continue
  if e['behavior']:groups[e['behavior']['signature']].append(e)
 selected=[]
 for signature,es in sorted(groups.items()):selected+=sorted(es,key=lambda e:(-e['quality'],identity(e['case'])))[:2]
 cases=[e['case']for e in selected]
 protocol=dict(schema='pcg/plains-production/v1',source_calibration=calibration,holdout_seed=holdout_seed,trials=12,requested_tier='regular',finalists=[dict(uid=identity(e['case']),calibration_uid=e['uid'],calibration_signature=e['behavior']['signature'],sequence=e['behavior']['sequence'])for e in selected],selection='At most two per actually executed sequence; fixed before holdout, no geometry tuning or lucky-seed retries',scope='Movement, ordinary one jump, recoil only; original bell/enemy/resource components')
 (out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2))
 tested=evaluate(engine,cases,holdout_seed,12,'fresh-holdout',levels=('clean','mild','moderate'));held={e['uid']:e for e in tested};alts=[];owners={}
 for c in cases:
  uid=identity(c)
  for name,alt in alternative_cases(c):
   for trial in range(4):
    a=instantiate(alt,holdout_seed,'clean',trial);a['id']=uid[:12]+'-'+a['id'];alts.append(a);owners[a['id']]=(uid,name,trial)
 alternatives=[];shortcuts=collections.defaultdict(list)
 for c,r,ev in engine.run(alts,'counterfactuals'):
  uid,kind,trial=owners[c['id']];physical=bool(r.get('ok')and r.get('hp')==5 and not r.get('plains',{}).get('player_damage'))
  row=dict(uid=uid,kind=kind,trial=trial,physical_pass=physical,shots=r.get('shots',0),ticks=r.get('ticks',0),reason=r['reason'],evidence=ev);alternatives.append(row)
  # Missing the saw read may be a legitimate higher-risk strategy, not lower cost.
  if physical and kind in('no_shoot','no_shoot_held_jump','no_enemy_same_shots'):shortcuts[uid].append(row)
 catalog=[];reviews=[];representatives={}
 for selected_entry in selected:
  uid=identity(selected_entry['case']);h=held[uid];base=h['case'];stats=h['stats'];admission=gate(stats,shortcuts[uid],bool(base.get('saws')or base.get('enemies')),POLICY,requested_tier='regular')
  row=dict(uid=uid,family=base['family'],calibration=selected_entry['stats'],validation=stats,admission=admission,behavior=h['behavior'],shortcuts=shortcuts[uid]);catalog.append(row)
  if admission['status']!='awaiting_human_review'or not h['witness']:continue
  w=h['witness'];c=copy.deepcopy(w['case']);c.pop('noise',None);c['recorded_frames']=w['recorded_frames'];c['factory_id']=uid;c['factory_evidence']=w['evidence'];c['module_sha256']=module_hash(c);c['title']=c['review_alias']=f'平原候选 {len(reviews)+1:02}';reviews.append(c)
  signature=selected_entry['behavior']['signature']
  if signature not in representatives:representatives[signature]=c
 shown=list(representatives.values())
 for i,c in enumerate(shown):c['title']=c['review_alias']=f'P{i+1:02}'
 summary=dict(schema='pcg/plains-summary/v1',finalists=len(cases),decision_signatures=len(groups),qualified=len(reviews),representatives=len(shown),physics_cases=engine.sim.cases,batches=len(engine.batches),wall_seconds=time.perf_counter()-started,human_video_feedback=0,human_playtests=0,approved_offline=0,limits=['Finite scripted policy and sampled perturbations, not human success rates','Counterfactuals are tested input policies, not an optimal-path proof','Variant count is not distinct gameplay count'])
 for filename,value in [('summary',summary),('catalog',catalog),('counterfactuals',alternatives),('heldout_entries',tested),('all_review_cases',dict(cases=reviews)),('review_cases',dict(cases=shown))]:(out/(filename+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2 if filename in('summary','catalog')else None))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--calibration',default='plains-calibration-v2');p.add_argument('--holdout-seed',type=int,default=1240810);p.add_argument('--families');a=p.parse_args();run(a.name,a.calibration,a.holdout_seed,a.families.split(',')if a.families else None)
