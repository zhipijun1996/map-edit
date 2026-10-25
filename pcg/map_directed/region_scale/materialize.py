"""Physical stress stage of the existing regional Director, not quality admission.

Reuses contact embedding, canonical Module export, exact-object assembler and
actual Godot Harness. The old box-room vocabulary is NOT silently promoted to a
larger-region design: the content diagnostics remain acceptance blockers.
"""
import argparse,copy,json,shutil,time
from pathlib import Path
from ..director import REPO
from ..run import write
from ..direct_join.director import requests
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..r2_full.orchestrate import make_case,logical_route,partitioned_cover
from ..valley_complete.run import CompleteEngine
from ..library import CandidateLibrary
from pcg.prototype.plains.room_modules import generate,routes
from pcg.prototype.plains.regional_macros import generate as regional_generate
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

class RegionEngine(CompleteEngine):
 def __init__(self,out):
  super().__init__(out,formal_style=True)
  for p in Path(__file__).parent.glob('*'):
   if p.is_file() and p.suffix in ['.gd','.py','.json','.tscn']:
    rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
    dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
  write(self.out/'source_binding.json',self.binding)

def case_for(c,steps,name):
 v=make_case(c,steps,name)
 v.update(id='full-region-'+name,title='风铃平原 · 完整区域接缝压力候选（设计未准入）',
  extra_script=str(Path(__file__).with_name('mechanics.gd')),formal_style_v2=True,
  automatic_shop_input=False,valley_shop=c['shop'],r2_optional_challenges=c['case']['reward_sites'],
  map_budget_ticks=36000,
  landform_style=dict(enclosing_walls=False,bounds_overlay=False,geometry_source='canonical open Module objects',map_added_terrain=0),
  module_frames=[dict(id=m['id'],bounds=m['spec']['space']['core_bounds'],placement=m['spec']['placement'],version=m['content_version'])for m in c['modules']])
 # Visiting a demand location is never a substitute for physically earning its
 # challenge chest. This stage grants no unmaterialized reward or return flag.
 for n in v['r2_semantics']['nodes']:
  n['reward']=0
  if n['id'] in c['unresolved_rewards']:n['opens']=[]
 for leg in v['pilot_program']:
  if leg['kind']=='jump':
   x,y=leg['target']['position']
   # Explicit case-scoped permission to use the original drop-through input
   # if an actual upper one-way bank intercepts this jump. Destination and
   # foot-ray checks stay unchanged. This is a policy, not clearance proof.
   transit=[i for i in v['one_way_platform_indices']if 0<y-(v['platforms'][i][1]-18)<=220 and v['platforms'][i][0]-240<=x<=v['platforms'][i][0]+v['platforms'][i][2]+240]
   if transit:
    leg['target']['allowed_transit_support_indices']=transit
    leg['target']['walk_off_transit_support_indices']=[i for i in transit if x<v['platforms'][i][0]-12 or x>v['platforms'][i][0]+v['platforms'][i][2]+12]
  leg['budget_ticks']=1200 if 'carrier_transfer'in leg else 720 if leg['kind']=='module'else 360
 return v

def run(name,layout_path,mode='main',profile='stress'):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_region_materialization_exists')
 out.mkdir(parents=True);started=time.perf_counter()
 # Freeze producers/consumers before even a failed materialization. Physical
 # engine subsequently freezes its own complete protected runtime binding.
 hashes={}
 for p in list(Path(__file__).parent.glob('*'))+[REPO/'pcg/prototype/plains/regional_macros.py',REPO/'pcg/prototype/plains/room_modules.py',REPO/'pcg/map_directed/direct_join/assemble.py',REPO/'pcg/map_directed/direct_join/director.py',REPO/'pcg/map_directed/direct_join/layout.py']:
  if p.is_file()and p.suffix in ['.py','.gd','.json']:
   rel=p.relative_to(REPO/'pcg');target=out/'design-source'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);hashes[str(rel)]=file_sha(p)
 write(out/'design-binding.json',dict(files=hashes,digest=digest(hashes),layout_sha256=file_sha(Path(layout_path))))
 raw=json.loads(Path(layout_path).read_text());write(out/'layout.json',raw)
 g,specs,seams=requests(out/'layout.json')
 for s in specs:
  s.update(id='full-region-contact-v1/'+s['node_id'],boundary_policy='open',enclosing_walls=False,
   objective='Resolve real multiport geometry and continuous route state; no quality admission from scale',
   content_status='legacy_action_vocabulary_stress_candidate_not_final_district_content')
 if profile=='recoil':
  # Director allocates the first two moderate vertical climbs encountered on
  # its selected primary approach. This is a bounded calibration allocation,
  # not a claim that the other districts already have complete content.
  draft=assemble_modules(g,[routes(generate(s))for s in specs],seams)
  approach=logical_route(draft,[g['goal']]);selected=[]
  for step in approach:
   node=step['from'];m=next(m for m in draft['modules']if m['id']==node)
   leg=next((v for v in m['center_to_port'][step['edge_id']]if v.get('carrier_transfer',{}).get('mode')=='ascend'),None)
   if leg and leg['carrier_transfer']['destination_level']==0 and 480<=leg['carrier_transfer']['source_level']<=540:
    selected.append((node,leg['carrier_transfer']['id']))
    if len(selected)==2:break
  for s in specs:
   s.update(id='full-region-recoil-v1/'+s['node_id'],include_optional_core=False,
    recoil_spires=[key for node,key in selected if node==s['node_id']])
  write(out/'director-content-feedback.json',dict(rejected_parent='full-region-physical-stress-v2',observed_main_shots=0,
   revised_demands=selected,selection='first two moderate vertical ascents on logical approach; no pass-based content selection',
   missing_districts_and_rewards=True))
 write(out/'challenge-specifications.json',specs);write(out/'exploration.json',g)
 match=CandidateLibrary().find_direct_instance(specs)
 modules=match['modules'] if match else export_reload([(regional_generate(s)if profile=='recoil'else routes(generate(s)))for s in specs],out/'module-library',producer='pcg/prototype/plains/regional_macros.py'if profile=='recoil'else'pcg/prototype/plains/room_modules.py')
 write(out/'generation-log.json',dict(requests=len(specs),reused_modules=len(modules)if match else 0,module_generator_calls=(len(specs)if profile=='recoil'else 0)+(0 if match else len(modules)),structural_route_allocation_calls=len(specs)if profile=='recoil'else 0,canonical_materializations=0 if match else len(modules),library_record=match['record']if match else None,
  feedback='Room shells explicitly forbidden; non-serving shaft now requires a real jump policy, not width growth or Map-created filler',production_admitted=False))
 c=assemble_modules(g,modules,seams);write(out/'assembly-audit.json',audit(c))
 for gate in c['gate_specs']:gate.update(x=gate['bounds'][0],y=gate['bounds'][1],w=gate['bounds'][2],h=gate['bounds'][3])
 # The graph's reward responsibility is intentionally unresolved: the old
 # template cannot earn regional approval by auto-granting coins at its center.
 c['unresolved_rewards']=[n['id']for n in g['nodes']if n['reward']]
 merchant=next(n['id']for n in g['nodes']if n['role']=='rest')
 c['shop']=dict(id='region-merchant',position=c['nodes'][merchant]['center']['position'],price=8,item='damage_blue')
 write(out/'compiled.json',c)
 if mode=='first':
  neighbour=next(e['to']if e['from']==g['entry']else e['from']for e in g['edges']if g['entry']in[e['from'],e['to']])
  cases=[case_for(c,logical_route(c,[neighbour]),'first-real-contact')]
 elif mode=='main':cases=[case_for(c,logical_route(c,[g['goal']]),'main-approach')]
 elif mode=='cover':
  cases=partitioned_cover(c,12)
  cases=[case_for(c,v['r2_semantics']['logical_route'],'coverage-'+str(i))for i,v in enumerate(cases)]
 else:raise ValueError('unknown_region_physical_mode')
 write(out/'cases.json',dict(cases=cases))
 protocol=dict(schema='pcg/full-region-physical-stress/v1',selection='First existing design seed; frozen supplied contact layout, no pass-seed selection',
  maximum_local_revisions=3,automatic_retries_in_run=0,independent_holdout='NOT_RUN until content is selected',mode=mode,whole_world=True,world_resets_within_route=0,
  target_met=False,quality_admitted=False,unresolved_rewards=c['unresolved_rewards'],
  blockers=['district action vocabulary and risk pacing unresolved','reward chambers not materialized; rewards and earned return flags withheld','physical gate enclosure/bypass unverified','generic relation admission remains UNKNOWN','boss area is a destination, no actual boss encounter'],
  build_seconds=time.perf_counter()-started)
 write(out/'protocol.json',protocol)
 engine=RegionEngine(out/'physics');rows=[]
 for v,r,ev in engine.run(cases,'region-'+mode):
  f=r.get('pilot',{}).get('failure',{})
  row=dict(id=v['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=f,extra=r.get('extra'),evidence=ev)
  rows.append(row);write(out/'summary.json',dict(rows=rows,all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),target_met=False,quality_admitted=False))
  print(json.dumps(dict(id=v['id'],ok=r['ok'],ticks=r.get('ticks'),reason=r['reason'],failure_leg=f.get('leg_id'),actual=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--layout',required=True);p.add_argument('--mode',choices=['first','main','cover'],default='main');p.add_argument('--profile',choices=['stress','recoil'],default='stress');a=p.parse_args();print(run(a.name,a.layout,a.mode,a.profile))
