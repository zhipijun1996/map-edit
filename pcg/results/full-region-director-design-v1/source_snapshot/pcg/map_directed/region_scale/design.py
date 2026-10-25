"""Scale existing PR#1 regional Director, without a second graph algorithm.

Outputs are explicitly UNEMBEDDED designs and unresolved content demands.
The previous eight-Module world is not resized/stamped and is not counted as
the full-region result. No abstract result is entered into a physics library.
"""
import argparse,copy,hashlib,json,math,sys,time
from pathlib import Path
from ..director import REPO
from ..run import write
from ..valley_complete.compare import svg
sys.path.insert(0,str(REPO/'experiments/l4-mapgen'))
import region_network as network
import mapgen as base

def annotate(graph):
 g=copy.deepcopy(graph);by={v['id']:v for v in g['nodes']}
 # Three original real graph landmarks, plus a fourth separated route hub.
 chosen=list(g['landmarks']);ordinary=[v for v in g['nodes']if v['id']in g['core_nodes']and v['id']not in chosen+[g['entry'],g['mission_policy']['boss_forecourt']]]
 fourth=max(ordinary,key=lambda n:min(math.dist(n['ideal'],by[k]['ideal'])for k in chosen))
 chosen.append(fourth['id']);names=['风车群落','回声溪谷','钟楼上廊','悬索岩壁']
 for key,title in zip(chosen,names):by[key]['label']=title;by[key]['landmark']=True
 for node in g['nodes']:
  idx=min(range(4),key=lambda i:math.dist(node['ideal'],by[chosen[i]]['ideal']))
  node['district']=names[idx]
 # Existing outer expeditions retain their distinct rewards/earned shortcuts.
 # Add minor rewards off the concise route; these are graph responsibilities,
 # never pre-claimed items or automatically generated chest geometry.
 main=set(network.approach_routes(g)[0]['nodes'])
 candidates=[n for n in ordinary if n['id']not in main and n['role']=='hub']
 candidates.sort(key=lambda n:(-network.shortest_path(g,g['entry'],n['id'])[0],n['id']))
 rewards=[]
 for node in candidates:
  if any(math.dist(node['ideal'],by[k]['ideal'])<16 for k in rewards):continue
  node.update(reward=8+4*len(rewards),risk=2,label=node.get('label','')+' · 支路宝箱',intent='reward a distinct optional discovery; actual sealed chest location unresolved')
  rewards.append(node['id'])
  if len(rewards)==4:break
 g['landmarks']=chosen
 g['full_region_status']='mission_and_exploration_only_unembedded'
 return g

def demands(g,seed):
 families={'风车群落':['air_shot_bell','enemy_refund'], '回声溪谷':['motion_toggle_ferry','gear_phase_passage'],
  '钟楼上廊':['low_arch_recoil','air_shot_bell'], '悬索岩壁':['motion_toggle_ferry','enemy_refund']}
 result=[]
 for node in g['nodes']:
  edges=[e for e in g['edges']if node['id']in [e['from'],e['to']]]
  result.append(dict(schema='map-notes/challenge-specification/v1',id='full-region/'+seed+'/'+node['id'],node_id=node['id'],region='plains',
   objective=dict(role=node['role'],intent=node['intent'],district=node['district'],reward=node['reward']),
   actions=dict(preferred_families=families[node['district']],status='design_request_not_materialized',minimum_distinct_actions=2 if node['role']=='challenge'else 1),
   ports=dict(count=len(edges),edge_ids=[e['id']for e in edges],physical_normals='UNKNOWN_PENDING_REAL_MACRO_EMBEDDING',ordered_relations='UNKNOWN_PENDING_STATEFUL_VERIFICATION'),
   capabilities={'allOf':['move','jump','shot_recoil'],'grants_new_ability':False},
   resources=dict(entry='actual upstream exit, never assumed full',transfer='UNKNOWN'),
   space=dict(shape='open landforms; no default room shell',bounds='UNKNOWN_PENDING_CONTENT_MATCH',action_clearance='UNKNOWN'),
   risk_reward=dict(optional=node['id']not in network.approach_routes(g)[0]['nodes'],value=node['reward'],actual_risk_and_return_cost='UNKNOWN'),
   budget=dict(maximum_local_revisions=3,unbounded_search=False),
   status='unresolved_module_demand',production_admitted=False))
 return result

def run(name):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_full_region_design_exists')
 out.mkdir(parents=True);protocol=json.loads(Path(__file__).with_name('protocol.json').read_text());write(out/'protocol.json',protocol)
 history=[];selected=[]
 for seed in protocol['seeds']:
  for attempt in range(protocol['maximum_design_attempts_per_seed']):
   identity=seed+'/attempt/'+str(attempt);started=time.perf_counter();folder=out/seed/str(attempt);folder.mkdir(parents=True)
   try:
    graph=annotate(network.construct(identity,'plains',protocol['minimum_core_places']))
    errors,proof=base.validate_graph(graph);errors+=network.validate_region_intent(graph)
    write(folder/'exploration.json',graph);write(folder/'logical-proof.json',dict(errors=errors,proof=proof))
    row=dict(seed=seed,attempt=attempt,ok=not errors,errors=errors,nodes=len(graph['nodes']),edges=len(graph['edges']),seconds=time.perf_counter()-started)
    if not errors:
     requests=demands(graph,seed);write(folder/'challenge-specifications.json',requests)
     mission=dict(schema='map-notes/mission-graph/v1',entry=graph['entry'],goal=graph['goal'],objectives=[dict(id=n['id'],role=n['role'],district=n['district'],reward=n['reward'],opens=n['opens'])for n in graph['nodes']if n['role']not in ['challenge','hub']or n['reward']],
      scope='Design obligations only; no instantiated Boss, chest or route physics')
     write(folder/'mission.json',mission)
     (folder/'design.svg').write_text(svg({n['id']:n['ideal']for n in graph['nodes']},[(e['from'],e['to'])for e in graph['edges']],seed+' · 未嵌入设计蓝图，非可玩地图'))
     row.update(diagnostics=network.diagnostics(graph),physical_verification='NOT_RUN',spatial_embedding='NOT_RUN',module_demands=len(requests),actual_modules=0,qualified_for_playable_delivery=False,
      structural_digest=base.digest(dict(nodes=[n['id']for n in graph['nodes']],edges=sorted((e['from'],e['to'],e['purpose'])for e in graph['edges']))))
     selected.append(row)
   except ValueError as exc:row=dict(seed=seed,attempt=attempt,ok=False,error=str(exc),seconds=time.perf_counter()-started)
   history.append(row);write(out/'history.json',history)
   if row['ok']:break
 summary=dict(schema='pcg/full-region-design-study/v1',selected=selected,all_seeds_logically_designed=len(selected)==len(protocol['seeds']),
  target_met=False,scope='PR#1 Director scaled to 32 core places. Design only; no spatial or physical success claimed. Eight-Module sample is not counted.',next_blockers=['resolve real variable Macro footprints/ports and action envelopes','match/generate Module content, bounded local feedback','whole-world assembly, gameplay and Boss/campaign adapter','same-scale exploration and human review'])
 write(out/'summary.json',summary);return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
