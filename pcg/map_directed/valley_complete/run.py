"""One existing assembly/Harness pipeline with versioned new content demands."""
import argparse,copy,json,shutil,time
from pathlib import Path
from .director import requests
from ..open_valley.run import ValleyEngine,case_for
from ..direct_join.assemble import assemble_modules
from ..direct_join.canonical import export_reload
from ..direct_join.audit import audit
from ..director import REPO
from ..run import write
from pcg.prototype.plains.valley_complete import generate
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from ..library import CandidateLibrary

class CompleteEngine(ValleyEngine):
 def __init__(self,out):
  super().__init__(out)
  paths=list(Path(__file__).parent.glob('*'))+[REPO/'pcg/prototype/plains/valley_complete.py']
  art=REPO/'pcg/research/valley-current-art.json';paths.append(art)
  for record in json.loads(art.read_text())['files']:
   p=REPO/'pcg/prototype/godot'/record['path']
   if file_sha(p)!=record['sha256']:raise ValueError('current_main_art_drift/'+record['path'])
   paths.append(p)
  for p in paths:
   if p.is_file()and p.suffix in ['.gd','.py','.json','.tscn','.png','.import']:
    rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  self.sim.runner_script=str(Path(__file__).with_name('runner.gd'))
  self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
  write(self.out/'source_binding.json',self.binding)

def case(c,places,name,reward=False,relay=False):
 v=case_for(c,places,name,reward)
 v['id']='valley-complete-'+name;v['title']='风铃平原 · 回声风谷完整小区域'
 v['extra_script']=str(Path(__file__).with_name('mechanics.gd'))
 v['valley_shop']=copy.deepcopy(c['case']['shop_sites'][0])
 v['automatic_shop_input']=True
 v['r2_optional_challenges']=copy.deepcopy(c['case']['reward_sites'])
 if reward:v['required_optional_challenges']=['bell/bell-cache']
 # The bridge cache is claimed only inside its physical chamber, not at the
 # node center. Lower bypass skips that chest; upper policy earns its coins.
 if relay:
  program=[];done=False
  for leg in v['pilot_program']:
   program.append(leg)
   if not done and leg.get('edge_to')=='relay'and leg.get('edge_terminal'):
    for i,raw in enumerate(c['nodes']['relay']['core_visit_program']):
     item=copy.deepcopy(raw);item.update(id='relay-challenge/'+str(i),edge_id='optional/relay',budget_ticks=720 if raw['kind']=='module'else 360);program.append(item)
    done=True
  v['pilot_program']=program;v['required_optional_challenges']=v.get('required_optional_challenges',[])+['relay/relay-cache']
 return v

def run(name,mode):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_run_exists')
 out.mkdir(parents=True);start=time.perf_counter()
 graph,specs,seams,mission=requests()
 match=CandidateLibrary().find_direct_instance(specs)
 modules=match['modules']if match else export_reload([generate(s)for s in specs],out/'module-library',producer='pcg/prototype/plains/valley_complete.py')
 write(out/'generation-log.json',dict(requests=len(specs),reused_modules=len(modules)if match else 0,module_generator_calls=0 if match else len(modules),record=match['record']if match else None,scope='exact-demand candidate reuse; new and edited demands materialized by the existing Module producer; no production admission'))
 c=assemble_modules(graph,modules,seams);c['case']['world_bounds']=[-80,50,3290,1400]
 write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
 write(out/'mission.json',mission);write(out/'exploration.json',graph);write(out/'challenge-specifications.json',specs)
 cases=[case(c,['west','ridge','lookout','arch','east'],'main'),
  case(c,['west','hollow','bell','arch','lookout','ridge','west'],'cache-park-shop-return',True),
  case(c,['west','ridge','lookout','arch','east','relay','east','bell','hollow','west'],'relay-cache-loop',relay=True),
  case(c,['west','ridge','lookout','arch','bell','hollow','west'],'lower-shortcut'),
  case(c,['west','hollow','bell','east','arch','lookout','ridge','west'],'lower-reward-loop',True)]
 cases[1]['require_purchase']=True
 cases[1]['require_parking']=True
 if mode=='main':cases=cases[:1]
 elif mode=='park':cases=cases[1:2]
 elif mode=='relay':cases=cases[2:3]
 elif mode=='holdout':
  variants=[]
  for v in cases:
   for i,phase in enumerate([.07,.29,.59,.83]):
    trial=copy.deepcopy(v);trial['id']+='-phase-'+str(i)
    for item in trial['saws']+trial['moving_platforms']:item['initial_phase']=phase
    # Controlled carriers always begin at their designed dock. Randomizing
    # that authored anchor is a different geometry/content request.
    for item in trial['moving_platforms']:item['initial_phase']=0
    trial['perturbation']=dict(saw_phase=phase,enemy_initial_idle_cooldown=.12+.16*i)
    for enemy in trial['enemies']:enemy['initial_idle_cooldown']=.12+.16*i
    variants.append(trial)
  cases=variants
 write(out/'cases.json',dict(cases=cases));write(out/'protocol.json',dict(mode=mode,maximum_candidates=1,maximum_map_ticks=18000,retries=0,independent_holdout=[.07,.29,.59,.83],selection='fixed map, five continuous routes; complete original dynamic world',geometry_build_seconds=time.perf_counter()-start))
 engine=CompleteEngine(out/'physics');rows=[]
 for v,r,ev in engine.run(cases,'complete-'+mode):
  f=r.get('pilot',{}).get('failure',{});row=dict(id=v['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=f,extra=r.get('extra'),evidence=ev)
  rows.append(row);write(out/'summary.json',dict(rows=rows,all_passed=len(rows)==len(cases)and all(v['ok']for v in rows)))
  print(json.dumps(dict(id=v['id'],ok=r['ok'],ticks=r.get('ticks'),reason=r['reason'],leg=f.get('leg_id'),actual=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['main','park','relay','full','holdout'],default='full');a=p.parse_args();print(run(a.name,a.mode))
