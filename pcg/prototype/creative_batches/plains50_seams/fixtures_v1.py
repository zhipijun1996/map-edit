"""Exact union-preserving seam specimens on two enrolled multiport receivers.

Original WorkshopEngine, instantiate and evaluate provide all actual physics.
No Module enrollment, source document edits, connector geometry or Map layout.
"""
import argparse,copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.transitions import arrival
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evidence import geometry_key
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from pcg.map_directed.library import verified_document
HERE=Path(__file__).parent
REPO=ROOT.parent
SOURCES=[('investment-four-port','106e4362c8388feceff422dc98e9c5105569c546ff8f284f6d822fc75d7517a0','C','D'),('thorn-three-port','ab5d60871a3261241a2057352c88a469f988728f8b94a92728b7a0da0336d345','B','C')]

def binding(path):return dict(path=str(path.relative_to(REPO)),sha256=file_sha(path))

def specimens():
 out=[]
 for label,version,seam_port,final_port in SOURCES:
  root=ROOT/'map_directed/library/candidates'/version
  document=root/'module.mapnote.json';doc=verified_document(document);assert doc['generationContract']['contentVersion']=='sha256:'+version
  cs=json.loads((root/'cases.json').read_text())['cases'];original=next(c for c in cs if c['route_spec']['id']=='reward')
  ports={p['id']:p for p in original['ports']};sp=ports[seam_port];target=ports[final_port];i=sp['support_index'];old=original['platforms'][i][:];sx=sp['position'][0]
  left=[old[0],old[1],sx-old[0],old[3]];right=[sx,old[1],old[0]+old[2]-sx,old[3]]
  assert left[2]>24 and right[2]>24
  assert left[0]==old[0] and left[0]+left[2]==right[0] and right[0]+right[2]==old[0]+old[2]
  assert left[1]==right[1]==old[1] and left[3]==right[3]==old[3]
  assert left[2]*left[3]+right[2]*right[3]==old[2]*old[3]
  source=dict(contentVersion='sha256:'+version,document=binding(document),cases=binding(root/'cases.json'),record=binding(root/'record.json'),original_route_id=original['route_spec']['id'],original_case_id=original['id'],original_port=seam_port,continued_original_port=final_port,original_ports=copy.deepcopy(original['ports']))
  for hold in [20,30]:
   c=copy.deepcopy(original)
   for key in ['ports','layout_uid','factory_id','factory_evidence','recorded_frames','validation_summary','module_sha256','review_alias','map_specification','noise']:c.pop(key,None)
   c['platforms'][i]=left[:];c['platforms'].append(right[:]);part_index=len(c['platforms'])-1
   first=arrival(original)
   if label=='investment-four-port':
    # A->B uses original reward ascent, then the same actor drops toward C.
    route=first+[cmd('axis',value=1),wait_x(sx+40),cmd('axis',value=0),ground(),cmd('wait',hold),cmd('axis',value=-1),wait_x(sx-40,-1),cmd('axis',value=0),ground(),cmd('wait',hold),settle(target['position'][0],0)]
   else:
    # After reward and two-direction traversal, descend outside the receiver
    # and walk under the unchanged rock to original lower exit C.
    route=first+[cmd('axis',value=1),wait_x(sx+40),cmd('axis',value=0),ground(),cmd('wait',hold),cmd('axis',value=-1),wait_x(sx-40,-1),cmd('axis',value=0),ground(),cmd('wait',hold),cmd('axis',value=1),wait_x(old[0]+old[2]+40),cmd('axis',value=0),ground(),cmd('wait',hold),settle(target['position'][0],0)]
   c.update(id=f'plains50-seam-{label}-h{hold}',control_plan=route,entry_port=original['entry_port'][:],exit_port=[sx+40,sp['position'][1]],goal=[target['position'][0]-25,target['position'][1]-4,50,8],max_frames=1500,trace_all=False)
   c['route_spec']=dict(id='seam-excursion',from_port='A',to_port=final_port,role='fixture',via_ports=['B',seam_port],require_bell=False)
   c['seam_specimen']=dict(label=label,x=sx,y=old[1],source=source,original_receiver=old,partition=[left,right],split_indices=[i,part_index],added_solid_area=0,removed_solid_area=0,union_unchanged=True,synthetic_connector=False,definition_exit_marker=[sx+40,sp['position'][1]],final_original_port=copy.deepcopy(target),reward_amount=original['reward_sites'][0]['amount'],scope='exact one-world collider partition and excursion; not arbitrary Module seam or assembly guarantee')
   c['seam_specimen']['fixture_geometry_sha256']=geometry_key(c)
   c['seam_specimen']['fixture_version']='sha256:'+digest(dict(source_version=source['contentVersion'],geometry_sha256=geometry_key(c),control_plan=route))
   out.append(c)
 return out

def check(c,r):
 meta=c['seam_specimen'];sx=meta['x'];surface=meta['y'];fs=r.get('frames',[])
 floor=lambda f:bool(f.get('grounded'))and abs(f['y']+18-surface)<.5
 fwd=[b['frame']for a,b in zip(fs,fs[1:])if a['x']<sx<=b['x']and floor(a)and floor(b)]
 back=[b['frame']for a,b in zip(fs,fs[1:])if a['x']>sx>=b['x']and floor(a)and floor(b)]
 full_right=[f['frame']for f in fs if floor(f)and f['x']-12>=sx+1]
 full_left_after=[f['frame']for f in fs if floor(f)and f['x']+12<=sx-1 and full_right and f['frame']>full_right[0]]
 final=meta['final_original_port']['position'];last=fs[-1]if fs else {};final_hit=bool(last and last['grounded']and abs(last['x']-final[0])<=25 and abs(last['y']-final[1])<1 and r.get('goal_stable_frames',0)>=6)
 coins=r.get('workshop',{}).get('coins',0);reasons=[]
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if not(fwd and back and full_right and full_left_after):reasons.append('both_complete_body_seam_directions_missing')
 if not final_hit:reasons.append('different_original_exit_not_stable')
 if coins!=meta['reward_amount']:reasons.append('original_reward_not_actually_claimed_once')
 if r.get('returns'):reasons.append('unexpected_teleport_or_return')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
 return dict(ok=not reasons,reasons=reasons,causal=dict(forward_frames=fwd,backward_frames=back,complete_body_right_frames=full_right,complete_body_left_after_right_frames=full_left_after,final_original_exit=final,final_exit_observed=final_hit,reward_coins=coins,added_solid_area=0,union_unchanged=True,single_world_no_reset=True),behavior={})

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();protocol=json.loads((HERE/'protocol-v1.json').read_text());out=ROOT/'results'/a.name
 engine=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'protocol-v1.json',ROOT/'prototype/workshop/transitions.py']);bases=specimens();write(out/'protocol.json',protocol);write(out/'source-cases.json',dict(cases=bases));probes=[];witnesses={}
 for c,r,e in engine.run(bases,'seam-probe'):
  q=check(c,r);probes.append(dict(case=c,result=r,check=q,evidence=e));print(json.dumps(dict(id=c['id'],reason=r['reason'],check=q)),flush=True)
  if q['ok']and c['seam_specimen']['label']not in witnesses:witnesses[c['seam_specimen']['label']]=dict(case=c,result=r,evidence=e)
 write(out/'probe-results.json',probes);selected=[witnesses[label]['case']for label,*_ in SOURCES if label in witnesses]
 write(out/'selection-after-probes.json',dict(selected_case_ids=[c['id']for c in selected],probe_sha256=file_sha(out/'probe-results.json'),rule='first passing control per fixture; no holdout selection'))
 if len(selected)!=len(SOURCES):
  write(out/'summary.json',dict(status='gap_after_bounded_probes',selected=len(selected),expected=len(SOURCES),physics_cases=engine.sim.cases,admission=False,whole_map='UNKNOWN',rows=[dict(id=x['case']['id'],check=x['check'])for x in probes]));return
 cal=evaluate(engine,selected,protocol['calibration_seed'],12,'seam-calibration',purpose_fn=check);write(out/'calibration-evaluations.json',cal)
 passed=[e['case']for e in cal if e['quality_gate']['status']=='awaiting_human_review']
 write(out/'selection-before-holdout.json',dict(cases=[c['id']for c in passed],calibration_sha256=file_sha(out/'calibration-evaluations.json'),holdout_seed=protocol['holdout_seed'],fixture_versions=[c['seam_specimen']['fixture_version']for c in passed]))
 if passed:held=evaluate(engine,passed,protocol['holdout_seed'],12,'seam-holdout',purpose_fn=check)
 else:held=[]
 write(out/'holdout-evaluations.json',held)
 success=[e for e in held if e['quality_gate']['status']=='awaiting_human_review'];write(out/'summary.json',dict(schema='pcg/plains50-exact-seam-fixture-result/v1',status='passed_scoped_fixtures'if len(success)==len(SOURCES)else'gap_after_calibration_or_holdout',expected_fixtures=2,passed_fixtures=len(success),physics_cases=engine.sim.cases,budget=120,case_versions=[e['case']['seam_specimen']['fixture_version']for e in success],sources=[e['case']['seam_specimen']['source']for e in success],calibration=[dict(id=e['case']['id'],stats=e['stats'],quality=e['quality_gate'])for e in cal],holdout=[dict(id=e['case']['id'],stats=e['stats'],quality=e['quality_gate'])for e in held],scope='Exact union-identical collider partitions, two-direction full-body traversal and continuation to another source port, one world per trial. No new Module, generic transforms/seams or Map admission.',added_solid_area=0,module_enrollment=False,source_contracts_modified=False,original_module_seam_coverage='UNKNOWN; no upgrade',whole_map='UNKNOWN',production_admitted=False))
 assert engine.sim.cases<=protocol['actual_physics_budget_max']
 print(json.dumps(json.loads((out/'summary.json').read_text())),flush=True)
if __name__=='__main__':main()
