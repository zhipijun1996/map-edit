"""Generate standard Module outputs and run existing real whole-world Harness."""
import argparse,copy,json,shutil
from pathlib import Path
from .director import requests
from pcg.map_directed.library import CandidateLibrary
from pcg.prototype.plains.open_landforms import generate
from pcg.map_directed.direct_join.assemble import assemble_modules
from pcg.map_directed.direct_join.canonical import export_reload
from pcg.map_directed.direct_join.audit import audit
from pcg.map_directed.direct_join.run import DirectEngine
from pcg.map_directed.r2_full.orchestrate import make_case
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

class ValleyEngine(DirectEngine):
 def __init__(self,out):
  super().__init__(out)
  for p in Path(__file__).parent.rglob('*'):
   if p.is_file()and p.suffix in ['.py','.gd','.json','.tscn']and '__pycache__'not in p.parts:
    rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes),scope='Open nonrectangular Module landforms; original whole-map physics; no enclosing walls or map fill')
  write(self.out/'source_binding.json',self.binding)

def steps(c,places):
 edges=list(c['edges'].values());result=[]
 for a,b in zip(places,places[1:]):
  e=next(e for e in edges if {e['from'],e['to']}=={a,b})
  result.append(dict(edge_id=e['id'],**{'from':a,'to':b}))
 return result

def case_for(c,places,name,reward=False):
 case=make_case(c,steps(c,places),name)
 case['id']='open-valley-'+name;case['title']='风铃平原 · 开放风谷样品'
 case['extra_script']=str(Path(__file__).with_name('mechanics.gd'))
 case['r2_optional_challenges']=[dict(id='bell-cache',target=c['nodes']['bell']['core_reward_target'],required_bell='bell/valley-bell',reward=8)]
 if reward:
  program=[];inserted=False
  for leg in case['pilot_program']:
   program.append(leg)
   if not inserted and leg.get('edge_to')=='bell'and leg.get('edge_terminal'):
    for i,raw in enumerate(c['nodes']['bell']['core_visit_program']):
     item=copy.deepcopy(raw);item.update(id='bell-challenge/'+str(i),edge_id='optional/bell');program.append(item)
    inserted=True
  if not inserted:raise ValueError('reward_route_does_not_visit_bell')
  case['pilot_program']=program;case['required_optional_challenges']=['bell-cache']
 if places[-1]=='west':
  for i,raw in enumerate(c['nodes']['west']['center_to_port']['e0']):
   leg=copy.deepcopy(raw);leg.update(id='returned-west-dock/'+str(i),edge_id='returned-west');case['pilot_program'].append(leg)
  target=c['nodes']['west']['ports']['e0']['target'];case.update(goal=target['region'],exit_port=target['position'])
 for leg in case['pilot_program']:leg['budget_ticks']=1000 if 'carrier_transfer'in leg else 720 if leg['kind']=='module'else 360
 case['map_budget_ticks']=18000
 case['landform_style']=dict(enclosing_walls=False,bounds_overlay=False,landmark=[1160,460],geometry_source='standard Module objects',map_added_terrain=0)
 case['module_frames']=[dict(id=m['id'],bounds=m['spec']['space']['core_bounds'],placement=m['spec']['placement'],version=m['content_version'])for m in c['modules']]
 return case

def run(name,mode):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_open_valley_run_exists')
 out.mkdir(parents=True)
 graph,specs,seams,mission=requests()
 library=CandidateLibrary();match=library.find_direct_instance(specs)
 modules=match['modules']if match else export_reload([generate(s)for s in specs],out/'module-library',producer='pcg/prototype/plains/open_landforms.py')
 write(out/'generation-log.json',dict(requests=len(specs),reused_modules=len(modules)if match else 0,module_generator_calls=0 if match else len(modules),record=match['record']if match else None,scope='exact-demand isolated candidate reuse; production and general Module state admission remain closed'))
 c=assemble_modules(graph,modules,seams);c['case']['world_bounds']=[-80,100,2470,1360];write(out/'assembly-audit.json',audit(c));write(out/'compiled.json',c)
 write(out/'mission.json',mission);write(out/'exploration.json',graph);write(out/'challenge-specifications.json',specs)
 cases=[case_for(c,['west','ridge','lookout','arch','east'],'upper-main'),
  case_for(c,['west','hollow','bell','east','arch','lookout','ridge','west'],'lower-reward-loop',True),
  case_for(c,['west','hollow','bell','arch','lookout','ridge','west'],'up-shortcut-loop',True),
  case_for(c,['west','ridge','lookout','arch','bell','hollow','west'],'down-shortcut-loop'),
  case_for(c,['west','ridge','lookout','arch','east','bell','hollow','west'],'east-lower-return')]
 if mode=='main':cases=cases[:1]
 elif mode=='lower':cases=cases[1:2]
 elif mode=='shortcut':cases=cases[2:4]
 elif mode=='holdout':
  trials=[]
  for original in cases:
   for ordinal,phase in enumerate([.08,.31,.62,.86]):
    case=copy.deepcopy(original);case['id']+='-held-phase-'+str(ordinal)
    for item in case['saws']:item['initial_phase']=phase
    for item in case['moving_platforms']:item['initial_phase']=phase
    case['perturbation']=dict(initial_phase=phase,selection='fixed independent state set, no candidate reselection',scope='initial-state variants, not a new canonical Module content version')
    trials.append(case)
  cases=trials
 elif mode=='negative':
  originals=cases;trials=[]
  for node in ['west','ridge','arch']:
   for hold in [None,24]:
    case=copy.deepcopy(originals[0]);case['id']='open-negative-omit-'+node+('-long-jump'if hold else'')
    first=next(leg for leg in case['pilot_program']if leg['kind']=='module'and leg['target']['id'].startswith(node+'/'))
    for op in first['control_plan']:
     if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
     if hold and op['op']=='jump_release':op['trigger']['after']=hold
    trials.append(case)
  case=copy.deepcopy(originals[1]);case['id']='open-negative-omit-reward-shot'
  for leg in case['pilot_program']:
   if leg['id'].startswith('bell-challenge/')and leg['kind']=='module':
    for op in leg['control_plan']:
     if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
  trials.append(case);cases=trials
 write(out/'cases.json',{'cases':cases});write(out/'protocol.json',dict(mode=mode,selection='fixed spatial grammar sample; not a seed search',maximum_candidates=1,maximum_physics_ticks=18000,adaptive_retries=0,technical_scope='finite actual whole-world policies, no arbitrary-state or human fun claim'))
 print('OPEN VALLEY',len(c['modules']),len(c['edges']),len(c['case']['platforms']),[(v['id'],len(v['pilot_program']))for v in cases],flush=True)
 engine=ValleyEngine(out/'physics');rows=[]
 for case,r,ev in engine.run(cases,'open-'+mode):
  f=r.get('pilot',{}).get('failure',{})
  row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),legs=r.get('pilot',{}).get('legs_completed'),failure=f,extra=r.get('extra'),evidence=ev);rows.append(row)
  write(out/'summary.json',dict(rows=rows,all_passed=len(rows)==len(cases)and all(v['ok']for v in rows)))
  print(json.dumps(dict(id=row['id'],ok=row['ok'],ticks=row['ticks'],reason=row['reason'],leg=f.get('leg_id'),actual=f.get('actual',{}).get('position'),expected=f.get('expected_target',{}).get('position')),ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['main','lower','shortcut','full','negative','holdout'],default='full');a=p.parse_args();print(run(a.name,a.mode))
