"""Actual direct-Module world generation and original Godot verification."""
import argparse,copy,json,shutil
from pathlib import Path
from .assemble import compile_map
from .canonical import export_reload
from .audit import audit
from .director import requests
from pcg.map_directed.library import CandidateLibrary
from pcg.map_directed.director import REPO
from pcg.map_directed.r2_full.orchestrate import FullMapEngine,make_case,logical_route,partitioned_cover
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

class DirectEngine(FullMapEngine):
 def __init__(self,out):
  super().__init__(out)
  for p in Path(__file__).parent.rglob('*'):
   if p.is_file()and p.suffix in ['.py','.gd','.json','.mjs']and '__pycache__'not in p.parts:
    rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  for p in [REPO/'pcg/map_directed/library.py', REPO/'pcg/map_directed/r2_full/web_build.py']:
   rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  self.sim.runner_script=str(Path(__file__).with_name('runner.gd'))
  self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,source_manifest_sha256=digest(self.hashes),scope='directly touching exact Module objects; no L4 terrain creation')
  write(self.out/'source_binding.json',self.binding)

def build_case(c,targets,name):
 case=make_case(c,logical_route(c,targets),name)
 for leg in case['pilot_program']:
  if leg['kind']=='module':leg['budget_ticks']=1000 if 'carrier_transfer'in leg else 720
 case['extra_script']=str(Path(__file__).with_name('challenge_extra.gd'))
 case['r2_optional_challenges']=[dict(id='challenge/'+k,target=v['core_reward_target'],required_bell=k+'/core-bell',reward=8)for k,v in c['nodes'].items()if v.get('core_visit_program')]
 if name=='lower-loop':
  program=[];done=set();wanted={'r5','r14'}
  for leg in case['pilot_program']:
   program.append(leg)
   at='r5'if leg['id']=='initial-supported-entry'else leg.get('edge_to')if leg.get('edge_terminal')else None
   if at in wanted and at not in done:
    for ordinal,raw in enumerate(c['nodes'][at]['core_visit_program']):
     item=copy.deepcopy(raw);item.update(id='optional-core/'+at+'/'+str(ordinal),edge_id='core/'+at,budget_ticks=1000 if 'carrier_transfer'in raw else 720 if raw['kind']=='module'else 360);program.append(item)
    done.add(at)
  case['pilot_program']=program;case['required_optional_challenges']=['challenge/'+k for k in sorted(wanted)]
 if targets[-1]==c['exploration_graph']['entry']:
  # Finish at an existing distinct dock after physically returning to entry.
  endpoint=c['nodes'][targets[-1]];eid='e13'
  for i,raw in enumerate(endpoint['center_to_port'][eid]):
   leg=copy.deepcopy(raw);leg.update(id='returned-entry-dock/'+str(i),edge_id='entry-room',budget_ticks=1000 if raw['kind']=='module'else 360);case['pilot_program'].append(leg)
  t=endpoint['ports'][eid]['target'];case.update(goal=t['region'],exit_port=t['position'])
 case['map_budget_ticks']=36000
 case['title']='风铃平原 · 直接拼接 Module 地图'
 case['direct_assembly']=c['hard_checks'];case['module_frames']=[{'id':m['id'],'bounds':m['spec']['space']['core_bounds'],'placement':m['spec']['placement'],'version':m['content_version']}for m in c['modules']]
 return case

def run(name,mode,layout=None):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_direct_map_run_exists')
 out.mkdir(parents=True)
 layout=layout or REPO/'pcg/results/direct-contact-shapes-v3/layout.json'
 _,specs,_=requests(layout)
 library=CandidateLibrary();match=library.find_direct_instance(specs)
 if match:
  loaded=match['modules'];generator_calls=0
 else:
  proposed=compile_map(layout)
  loaded=export_reload(proposed['modules'],out/'module-library');generator_calls=len(loaded)
 write(out/'generation-log.json',dict(requests=len(specs),reused_modules=len(loaded)if match else 0,module_generator_calls=generator_calls,catalog_record=match['record']if match else None,scope='quarantined exact-demand reuse; no independent relation or production admission inferred'))
 c=compile_map(layout,loaded)
 write(out/'assembly-audit.json',audit(c))
 write(out/'map-recipe.json',dict(schema='pcg/direct-module-map-recipe/v1',modules=[dict(instance=m['id'],document=m['canonical_document'],placement=m['spec']['placement'])for m in loaded],seams=c['seams'],hard_checks=c['hard_checks']))
 for gate in c['gate_specs']:gate.update(x=gate['bounds'][0],y=gate['bounds'][1],w=gate['bounds'][2],h=gate['bounds'][3])
 write(out/'compiled.json',c)
 for module in c['modules']:write(out/'modules'/(module['id']+'.json'),module)
 if mode=='short':cases=[build_case(c,['r10'],'adjacent-modules')]
 elif mode=='main':cases=[build_case(c,['boss'],'main')]
 elif mode=='loop':cases=[build_case(c,['r14','r18','r5'],'lower-loop')]
 elif mode=='full':
  cases=[build_case(c,['r14','r18','r5'],'lower-loop'),build_case(c,['boss'],'main'),build_case(c,['exp0_2','r5','boss'],'west-reward'),build_case(c,['exp1_2','r5','boss'],'east-reward')]+partitioned_cover(c,10)
 elif mode=='negative':
  locked=build_case(c,['boss'],'closed-boss')
  for node in locked['r2_semantics']['nodes']:
   if node['id']=='r6':node['opens']=[]
  omitted=build_case(c,['r14','r18','r5'],'lower-loop')
  omitted['id']='direct-negative-omitted-core-shot'
  for leg in omitted['pilot_program']:
   if leg['id'].startswith('optional-core/r5/')and leg['kind']=='module':leg['control_plan']=[op for op in leg['control_plan']if op['op']!='shoot']
  cases=[locked,omitted]
 elif mode=='routes':cases=[build_case(c,['boss'],'main'),build_case(c,['exp0_2','r5','boss'],'west-reward'),build_case(c,['exp1_2','r5','boss'],'east-reward')]
 else:
  cases=partitioned_cover(c,10)
  if mode=='repair':cases=cases[8:]
  for case in cases:
   for leg in case['pilot_program']:
    if leg['kind']=='module':leg['budget_ticks']=1000 if 'carrier_transfer'in leg else 720
   case['map_budget_ticks']=36000
 for case in cases:
  case['module_frames']=[dict(id=m['id'],bounds=m['spec']['space']['core_bounds'],placement=m['spec']['placement'],version=m['content_version'])for m in c['modules']]
  case['direct_assembly']=c['hard_checks']
  for leg in case['pilot_program']:
   if leg['kind']=='module':leg['budget_ticks']=1000 if 'carrier_transfer'in leg else 720
  case['map_budget_ticks']=36000
 write(out/'cases.json',{'cases':cases});write(out/'protocol.json',{'scope':'direct module contacts / zero interstitial terrain','hard_checks':c['hard_checks'],'cases':len(cases),'adaptive_retries_in_run':0})
 print(c['hard_checks'],[(v['id'],len(v['pilot_program']))for v in cases],flush=True)
 engine=DirectEngine(out/'physics');rows=[]
 for case,r,ev in engine.run(cases,'direct-'+mode):
  row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),legs=r.get('pilot',{}).get('legs_completed'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=ev);rows.append(row)
  write(out/'summary.json',{'rows':rows,'hard_checks':c['hard_checks'],'all_passed':len(rows)==len(cases)and all(v['ok']for v in rows)})
  f=row['failure']or{}
  print(json.dumps(dict(id=row['id'],ok=row['ok'],ticks=row['ticks'],legs=row['legs'],reason=row['reason'],failure_reason=f.get('reason'),failure_leg=f.get('leg_id')),ensure_ascii=False),flush=True)
 if mode=='full' and all(row['ok']for row in rows)and not match:
  write(out/'candidate-enrollment.json',library.enroll_direct_instance(out))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--layout',type=Path);p.add_argument('--mode',choices=['short','main','loop','routes','cover','repair','full','negative'],default='short');a=p.parse_args();print(run(a.name,a.mode,a.layout))
