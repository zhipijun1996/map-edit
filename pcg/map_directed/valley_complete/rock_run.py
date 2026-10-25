"""Content iteration on the existing two-loop Map, with original real services."""
import argparse,copy,json,time,shutil,random
from pathlib import Path
from .director import requests as original_requests
from .run import CompleteEngine
from ..library import CandidateLibrary
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..region_scale.materialize import case_for
from ..r2_full.orchestrate import logical_route
from ..director import REPO
from ..run import write
from pcg.prototype.plains.rock_recoil import adapt
from pcg.prototype.factory.core.engine import file_sha

PROTOCOL=dict(schema='pcg/rock-recoil-content/v1',maximum_geometry_revisions=3,candidates_per_revision=1,
 selection='First admissible fixed content adaptation; no seed or holdout selection',
 independent_seed=94016631,independent_phases=[.137,.427,.719,.913],
 goals=['Zero mandatory lift waiting','Source-owned solid rock and purposeful one-way platforms','Bell doors protect physically sealed treasure only','Optional reward excursion with continuous real-state return'],
 larger_region_goal_met=False,human_fun='unreviewed',production_admitted=False)

def build(out):
 g,old,seams,mission=original_requests();match=CandidateLibrary().find_direct_instance(old)
 if not match:raise ValueError('verified_open_landform_source_missing_restore_valley_complete_archive')
 specs=copy.deepcopy(old)
 for s in specs:
  s['id']='rock-recoil-v1/'+s['node_id'];s['revision']='rock-bank-and-optional-treasure'
  s['mechanic_requirements']=[v for v in s.get('mechanic_requirements',[])if 'gate'in v or 'chest'in v]+['recoil/rock traversal; no lift dependency']
 modules=export_reload([adapt(m,s)for m,s in zip(match['modules'],specs)],out/'module-library',producer='pcg/prototype/plains/rock_recoil.py')
 c=assemble_modules(g,modules,seams);c['case']['world_bounds']=[-80,50,3290,1400]
 c['shop']=copy.deepcopy(c['case']['shop_sites'][0]);c['unresolved_rewards']=[]
 write(out/'generation-log.json',dict(library_search='existing CandidateLibrary exact-demand source',source_record=match['record'],source_templates_adapted=len(modules),unchanged_reuse=0,new_content_validation_required=True))
 write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));write(out/'challenge-specifications.json',specs);write(out/'exploration.json',g)
 return c

def make_case(c,targets,name,collect=(),buy=False):
 v=case_for(c,logical_route(c,targets),name);v['title']='风铃平原 · 岩拱与反冲 · 完整双回环内容样品'
 v['id']='rock-recoil-'+name;v['extra_script']=str(Path(__file__).with_name('rock_mechanics.gd'))
 v['automatic_shop_input']=buy;v['require_purchase']=buy
 program=[];done=set()
 for leg in v['pilot_program']:
  program.append(leg)
  node=leg.get('edge_to')if leg.get('edge_terminal')else None
  if node in collect and node not in done:
   for i,raw in enumerate(c['nodes'][node]['core_visit_program']):
    added=copy.deepcopy(raw);added.update(id='optional/'+node+'/'+str(i),edge_id='optional/'+node,budget_ticks=720 if raw['kind']=='module'else 360);program.append(added)
   done.add(node)
 v['pilot_program']=program
 reward_ids={'arch':'arch/bridge-cache','bell':'bell/bell-cache','relay':'relay/relay-cache'}
 v['required_optional_challenges']=[reward_ids[n]for n in collect]
 if targets[-1]=='west':
  # Original Definition requires distinct source/destination points; finish
  # after the actual return on the existing source-owned upper dock.
  for i,raw in enumerate(c['nodes']['west']['center_to_port']['e0']):
   leg=copy.deepcopy(raw);leg.update(id='returned-west/'+str(i),edge_id='returned-west',budget_ticks=720 if raw['kind']=='module'else 360);v['pilot_program'].append(leg)
  target=c['nodes']['west']['ports']['e0']['target'];v.update(goal=target['region'],exit_port=target['position'])
 return v

def cases_for(c,mode):
 cases=[make_case(c,['ridge','lookout','arch','east'],'main'),
  make_case(c,['bell','arch','lookout','west'],'cache-recoil-return',('bell',),True),
  make_case(c,['arch','east','relay','east','arch','lookout','west'],'upper-cache-enemy-return',('arch','relay')),
  make_case(c,['ridge','lookout','arch','bell','hollow','west'],'fast-descent-return'),make_case(c,['hollow','bell','east'],'lower-recoil-alternative'),
  make_case(c,['ridge','lookout','arch','east','bell','hollow','west'],'east-lower-return')]
 if mode=='main':return cases[:1]
 if mode=='climb':return cases[1:2]
 if mode=='reward':return cases[2:3]
 if mode=='holdout':
  result=[]
  for original in cases:
   for phase in PROTOCOL['independent_phases']:
    v=copy.deepcopy(original);v['id']+='-phase-'+str(phase)
    for s in v['saws']:s['initial_phase']=phase
    for e in v['enemies']:e['initial_idle_cooldown']=.12+phase*.4
    result.append(v)
  return result
 return cases

def run(name,mode,source=None):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_rock_run_exists')
 out.mkdir(parents=True);write(out/'protocol.json',dict(PROTOCOL,mode=mode))
 # Source frozen before even geometry rejection; protected runtime subsequently
 # frozen by the existing CompleteEngine as in previous content generations.
 for p in [Path(__file__),REPO/'pcg/prototype/plains/rock_recoil.py']:
  dest=out/'design-source'/p.relative_to(REPO);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 c=json.loads((Path(source)/'compiled.json').read_text())if source else build(out)
 if source:write(out/'compiled.json',c)
 cases=cases_for(c,mode);write(out/'cases.json',dict(cases=cases))
 engine=CompleteEngine(out/'physics',formal_style=True);rows=[]
 for v,r,ev in engine.run(cases,'rock-'+mode):
  f=r.get('pilot',{}).get('failure',{});row=dict(id=v['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),failure=f,extra=r.get('extra'),evidence=ev);rows.append(row)
  write(out/'summary.json',dict(rows=rows,all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),larger_region_goal_met=False,human_fun='unreviewed'))
  print(json.dumps(dict(id=v['id'],ok=r['ok'],ticks=r.get('ticks'),shots=r.get('shots'),reason=r['reason'],leg=f.get('leg_id'),actual=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['main','climb','reward','full','holdout'],default='full');p.add_argument('--source');a=p.parse_args();print(run(a.name,a.mode,a.source))
