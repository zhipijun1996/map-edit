"""Bounded calibration/holdout for one geometry with independently directed routes."""
import argparse,copy,gzip,json,time,collections
from .engine import ROOT,PlainsEngine
from .three_port import geometry_hash,route_cases,port_purpose
from .evaluation import instantiate
from ..factory.core.quality import counts,module_hash,POLICY

def evaluate(engine,layouts,seed,trials,stage):
 entries={l['id']:dict(layout=l,routes={c['route_spec']['id']:dict(base=c,rows=[],witness=None)for c in route_cases(l)})for l in layouts};cases=[];owners={}
 for lid,e in entries.items():
  for rid,route in e['routes'].items():
   for level in ('clean','mild','moderate'):
    for trial in range(trials):
     c=instantiate(route['base'],seed,level,trial);cases.append(c);owners[c['id']]=(lid,rid,level,trial)
 for c,r,ev in engine.run(cases,stage):
  lid,rid,level,trial=owners[c['id']];entry=entries[lid]['routes'][rid];p=port_purpose(c,r);entry['rows'].append(dict(level=level,trial=trial,purpose=p,safe_stable=bool(r.get('ok')),evidence=ev,reason=r['reason']))
  if level=='clean'and trial==0:entry['witness']=dict(case=c,purpose=p,evidence=ev)
 for e in entries.values():
  for r in e['routes'].values():r['stats']={level:counts([x for x in r['rows']if x['level']==level])for level in ('clean','mild','moderate')}
  e['quality']=min(r['stats'][l]['rate']for r in e['routes'].values()for l in ('clean','mild','moderate'))
 return list(entries.values())
def regular(stats):return stats['clean']['rate']>=POLICY['clean_min']and stats['mild']['rate']>=POLICY['regular']['mild_min']and stats['moderate']['rate']>=POLICY['regular']['moderate_min']
def run(name,source,mode,seed):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);start=time.perf_counter();src=ROOT/'results'/source
 if mode=='calibrate':layouts=json.loads((src/'layouts.json').read_text());trials=4
 else:
  source_entries=json.loads((src/'entries.json').read_text());selected=[];parents=set()
  for e in sorted(source_entries,key=lambda e:(-e['quality'],e['layout']['id'])):
   parent=e['layout']['synthesis']['parent_uid']
   if parent in parents:continue
   selected.append(e);parents.add(parent)
   if len(selected)==2:break
  layouts=[e['layout']for e in selected];trials=12
 protocol=dict(schema='pcg/plains-three-port-production/v1',scope='Per-route sampled physics; no implicit bidirectionality, all-to-all or earned-state return guarantee',mode=mode,source=source,seed=seed,trials=trials,selected=[dict(id=l['id'],geometry_sha256=geometry_hash(l),ports=l['ports'])for l in layouts],selection='At most one per generated landing parent; rank minimum per-route calibration rate then layout ID; select two before fresh holdout',policy=POLICY,reward_service='UNKNOWN: not instantiated; upper route is a designated reward opportunity')
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2));entries=evaluate(engine,layouts,seed,trials,'fresh-holdout'if mode=='produce'else mode);reviews=[];cfrows=[]
 if mode=='produce':
  # Test the high port with no shots and longer ordinary jumping; a low route
  # passing without shooting is intentional and is not counted as a shortcut.
  from .produce import alternative_cases
  cs=[];owners={}
  for e in entries:
   for rid in ('upper','upper_rejoin'):
    for kind,c in alternative_cases(e['routes'][rid]['base']):
     if kind not in ('no_shoot','no_shoot_held_jump','wrong_aim'):continue
     for t in range(4):
      a=instantiate(c,seed,'clean',t);cs.append(a);owners[a['id']]=(e['layout']['id'],rid,kind,t)
  for c,r,ev in engine.run(cs,'branch-counterfactual'):
   lid,rid,kind,t=owners[c['id']];physical=bool(r.get('ok')and r.get('hp')==5);purpose=port_purpose(c,r)
   # For A→B via C, simply taking the low main path is legal but must not
   # masquerade as completing the high branch. Confirm actual C visitation.
   visited_c=any(f['grounded']and abs(f['x']-c['ports'][2]['position'][0])<=28 and abs(f['y']-c['ports'][2]['position'][1])<=1 for f in r.get('frames',[]))
   cfrows.append(dict(layout=lid,route=rid,kind=kind,trial=t,physical_pass=physical,visited_high_port=visited_c,branch_bypass=physical and visited_c,evidence=ev,reason=r['reason']))
  for i,e in enumerate(entries):
   title=f'T{i+1:02} · 三端口分支'
   # All routes use CLEAN TRIAL ZERO in the SAME initial mechanism phase.
   # A failed witness is exported as failed; never pick a nicer phase per edge.
   for rid,r in e['routes'].items():
    w=r['witness'];c=copy.deepcopy(w['case']);ev=w['evidence'];raw=json.loads(gzip.decompress((out/ev['output']).read_bytes()))['results'][ev['index']]
    c['factory_id']=e['layout']['id']+'/'+rid;c['factory_evidence']=ev;c['layout_title']=title;c['review_alias']=title+' / '+rid;c['title']=c['review_alias'];c['validation_summary']=r['stats'];c['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in raw['frames']];c['module_sha256']=module_hash(c);reviews.append(c)
  (out/'review_cases.json').write_text(json.dumps(dict(cases=reviews),ensure_ascii=False))
  (out/'counterfactuals.json').write_text(json.dumps(cfrows))
 (out/'entries.json').write_text(json.dumps(entries,ensure_ascii=False))
 summary=dict(mode=mode,layouts=len(layouts),routes_per_layout=7,ordered_pairs_per_layout=6,physics_cases=engine.sim.cases,batches=len(engine.batches),wall_seconds=time.perf_counter()-start,rows=[dict(layout=e['layout']['id'],ports=3,quality=e['quality'],routes={rid:dict(stats=r['stats'],regular=regular(r['stats']),nominal_witness=r['witness']['purpose']['ok'])for rid,r in e['routes'].items()})for e in entries],human_video_feedback=0,human_playtests=0,approved_offline=0,assembly_admitted=0)
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
 if mode=='produce':
  from contract.export import export
  export(out/'review_cases.json',out/'modules',run=out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);p.add_argument('--mode',choices=['calibrate','produce'],required=True);p.add_argument('--seed',type=int,required=True);a=p.parse_args();run(a.name,a.source,a.mode,a.seed)
