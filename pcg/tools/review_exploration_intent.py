"""Reject the content fixture and ask the original Director/library for gaps.

Produces design evidence only. No abstract graph is counted as a playable map.
"""
import argparse,copy,json,math,sys
from pathlib import Path
from pcg.map_directed.director import REPO,regional
from pcg.map_directed.run import write
from pcg.map_directed.catalog_feed.design_review import review,graph_review,reward_requests,targets
from pcg.map_directed.woven_region.design import graph_for,load_policy
from pcg.map_directed.valley_complete.compare import svg
from pcg.prototype.creative_batches.plains_workshop.catalog_v2 import query

def demands(graph,allocation):
    result=[];by={n['id']:n for n in graph['nodes']}
    for node in graph['nodes']:
        edges=[e for e in graph['edges']if node['id']in [e['from'],e['to']]]
        if len(edges)<3:continue
        ports=[]
        for e in edges:
            other=e['to']if e['from']==node['id']else e['from'];a=node['ideal'];b=by[other]['ideal'];dx,dy=b[0]-a[0],b[1]-a[1]
            normal=[1 if dx>0 else-1,0]if abs(dx)>=abs(dy)else[0,1 if dy>0 else-1]
            ports.append(dict(id=e['id'],normal=normal,onward_node=other,ingress=e['bidirectional']or e['to']==node['id'],egress=e['bidirectional']or e['from']==node['id']))
        relations=[dict(from_port=a['id'],to_port=b['id'],role='regional_transfer',intended=True,evidence_status='UNKNOWN')for a in ports for b in ports if a!=b and a['ingress']and b['egress']]
        result.append(dict(schema='map-notes/challenge-specification/v1',id='exploration-redesign/'+node['id'],region='plains',node_id=node['id'],
            required_family='plains_spatial_interchange',junction_role='interchange',
            objective=dict(role='regional_interchange',onward_ports=ports,common_choice_required=True,internal_recovery_is_not_an_extra_exit=True,
                composition='Continuous rock and void with identifiable onward directions; no wide rectangular catch shore substituted for spatial design'),
            capabilities=dict(version=1,status='defined',allOf=['move','jump','shot_recoil'],anyOfGroups=[]),
            ports=dict(count=len(ports),required_normals=[p['normal']for p in ports],source='Requested directions from conceptual regional arrangement, not measured Godot ports'),relations=relations,
            resource_state=dict(entry='Actual upstream grounded/resource/cooldown state; no implicit refill or reset',transfer='UNKNOWN until real continuous test'),
            space=dict(shape='irregular continuous landform',max_exterior_padding=48,physical_dimensions='UNKNOWN_PENDING_REAL_MACRO',concept_coordinates_are_not_world_units=True),
            risk_reward=copy.deepcopy(allocation['requests'][node['id']]),return_conditions=dict(required=True,evidence='UNKNOWN until real direction/state witnesses'),
            budget=dict(maximum_local_revisions=3,generator_called=False),status='unresolved_demand'))
    return result

def run(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_review_exists')
    out.mkdir();write(out/'targets.json',targets());old=[]
    for i in range(3):
        source=REPO/f'pcg/results/catalog94-evaluation-{i}-v1';compiled=json.loads((source/'compiled.json').read_text());result=review(compiled)
        write(out/f'old-map-{i}.json',result);old.append(dict(seed=compiled['exploration_graph']['seed'],ok=result['ok'],chests=result['actual_chests'],currency=result['actual_currency'],reentrant_core_fraction=result['graph']['reentrant_core_fraction'],mandatory_nodes=result['graph']['goal_unavoidable_nodes']))
    protocol=dict(seeds=['exploration-redesign-0','exploration-redesign-1','exploration-redesign-2'],attempts_per_seed=3,selection='first graph satisfying existing R2 intent and global reward demands; failed attempts retained',physics='NOT_RUN',old_maps='All three rejected user-facing design; old technical evidence unchanged')
    write(out/'protocol.json',protocol);planned=[]
    for seed in protocol['seeds']:
        history=[]
        for attempt in range(protocol['attempts_per_seed']):
            try:
                policy=load_policy();policy['topology']['core_count']=16;g=graph_for(seed+'/'+str(attempt),policy)
                allocation=reward_requests(g);intent=graph_review(g)
                row=dict(attempt=attempt,ok=allocation['ok']and intent['ok'],errors=allocation['errors']+intent['errors'])
            except ValueError as error:row=dict(attempt=attempt,ok=False,error=str(error))
            history.append(row);write(out/(seed+'-attempts.json'),history)
            if row['ok']:break
        if not row['ok']:
            planned.append(dict(seed=seed,status='unsatisfied_design',history=history));continue
        write(out/(seed+'-exploration.json'),g);write(out/(seed+'-reward-requests.json'),allocation)
        specs=demands(g,allocation);write(out/(seed+'-macro-demands.json'),specs)
        # Original strict lookup, with no fallback to a renamed old fork.
        retrieved=[dict(id=s['id'],node=s['node_id'],port_count=s['ports']['count'],result=query(s,REPO/'generation/workshop/plains50-v1/manifest.json'))for s in specs]
        write(out/(seed+'-retrieval.json'),retrieved)
        (out/(seed+'-concept.svg')).write_text(svg({n['id']:n['ideal']for n in g['nodes']},[(e['from'],e['to'])for e in g['edges']],seed+' · 概念拓扑，未拼装/未验证物理'))
        planned.append(dict(seed=seed,status='unembedded_design',nodes=len(g['nodes']),core_nodes=len(g['core_nodes']),chests=len(allocation['chest_nodes']),currency=sum(v['value']for v in allocation['requests'].values()),graph_review=intent,macro_demands=len(specs),exact_library_matches=sum(r['result']['status']=='supported_candidate'for r in retrieved),physical_validation='NOT_RUN',playable=False))
    write(out/'summary.json',dict(old_maps=old,designs=planned,new_playable_maps=0,production_admitted=False,
        scope='Concrete rejected-map audit plus existing R2 redesign demands and original-library gap lookup. Graphs are not physics or fun proof.'))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
