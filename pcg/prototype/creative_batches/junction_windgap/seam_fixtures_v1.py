"""Two exact collider partitions on enrolled J06/J03 junctions.

Reuse the original seam purpose checker, WorkshopEngine, instantiate/evaluate
and regular gate. No candidate enrollment, connector solids or contract upgrade.
"""
import argparse, copy, json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_seams.fixtures_v1 import check
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest, module_hash
from pcg.prototype.workshop.engine import ROOT, WorkshopEngine
from pcg.prototype.workshop.evidence import geometry_key
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd, wait_x, ground
from pcg.map_directed.library import verified_document

REPO=ROOT.parent
SOURCE_RULES=[('J06','windgap-junction','b-c',1,140),('J03','woven-bridge-interchange','lower-east',2,180)]
PROTOCOL=dict(schema='pcg/junction-exact-seam-fixtures/v1',actual_physics_budget_max=120,expected_fixtures=2,clean_candidates_per_fixture=1,calibration_seed=261026711,holdout_seed=261026712,trials_per_noise_level=12,selection='Both clean cases must pass; then original regular calibration; freeze selection before independent holdout. No holdout selection or source edits.',body_size=[24,36],added_solid_area=0,removed_solid_area=0,module_enrollment=False,source_contracts_modified=False,production_admitted=False)

def binding(p):return dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))
def exact_path(value):
 p=(REPO/value).resolve()
 if not p.is_relative_to(REPO)or not p.is_file():raise ValueError('missing_or_outside_repository/'+str(value))
 return p

def read_sources(manifest):
 m=json.loads(manifest.read_text());out=[]
 for entry in m['modules']:
  rb=entry['record'];rp=exact_path(rb['path'])
  if file_sha(rp)!=rb['sha256']:raise ValueError('manifest_record_hash_drift')
  record=json.loads(rp.read_text());cp=rp.parent/'cases.json';dp=rp.parent/'module.mapnote.json'
  if file_sha(cp)!=record['cases_sha256']or file_sha(dp)!=record['document_sha256']:raise ValueError('original_candidate_bytes_drift')
  if record['technical_status']!='passed_scoped_multi_route':raise ValueError('source_candidate_not_multi_route_passed')
  document=verified_document(dp);gc=document['generationContract'];version=record['contentVersion']
  if version!=entry['contentVersion']or gc['contentVersion']!=version:raise ValueError('source_content_version_drift')
  cases=json.loads(cp.read_text())['cases']
  declared={x['sourceCaseId']:x['moduleSha256']for x in gc['generation']['source']['routeCases']}
  if declared!={c['id']:module_hash(c)for c in cases}:raise ValueError('source_route_binding_drift')
  out.append(dict(record_path=rp,document_path=dp,cases_path=cp,record=record,cases=cases,contentVersion=version))
 return out

def specimens(manifest):
 sources=read_sources(manifest);out=[]
 for label,recipe,route,index,sx in SOURCE_RULES:
  matches=[(s,c)for s in sources for c in s['cases']if c.get('production_recipe')==recipe and c.get('interface')==0 and c.get('route_spec',{}).get('id')==route]
  if len(matches)!=1:raise ValueError('exact_enrolled_source_missing_or_ambiguous/'+label)
  s,original=matches[0];old=copy.deepcopy(original['platforms'][index]);x,y,w,h=old
  left=[x,y,sx-x,h];right=[sx,y,x+w-sx,h]
  assert left[2]>24 and right[2]>24
  assert left[0]==x and left[0]+left[2]==right[0] and right[0]+right[2]==x+w
  assert left[1]==right[1]==y and left[3]==right[3]==h
  assert left[2]*left[3]+right[2]*right[3]==w*h
  assert original['spawn'][0]+12<sx and abs(original['spawn'][1]+18-y)<.1
  assert not original.get('reward_sites') and not original.get('one_way_platform_indices')
  final=next(p for p in original['ports']if p['id']==original['route_spec']['to_port'])
  source=dict(contentVersion=s['contentVersion'],record=binding(s['record_path']),document=binding(s['document_path']),cases=binding(s['cases_path']),original_case_id=original['id'],original_route_id=route,original_port=original['route_spec']['from_port'],continued_original_port=final['id'],original_ports=copy.deepcopy(original['ports']))
  c=copy.deepcopy(original)
  for key in ['ports','layout_uid','factory_id','factory_evidence','recorded_frames','validation_summary','module_sha256','review_alias','map_specification','noise']:
   c.pop(key,None)
  c['platforms'][index]=left;c['platforms'].append(right);part_index=len(c['platforms'])-1
  excursion=[cmd('axis',value=1),wait_x(sx+40),cmd('axis',value=0),ground(),cmd('wait',10),cmd('axis',value=-1),wait_x(sx-40,-1),cmd('axis',value=0),ground(),cmd('wait',10)]
  c.update(id='junction-seam-'+label.lower()+'-i0',control_plan=excursion+copy.deepcopy(original['control_plan']),exit_port=[sx+40,y-18],max_frames=min(3600,original['max_frames']+250),trace_all=False)
  c['route_spec']=dict(id='seam-excursion',from_port=original['route_spec']['from_port'],to_port=final['id'],role='fixture',via_ports=[],require_bell=False)
  c['seam_specimen']=dict(label=label,x=sx,y=y,source=source,original_receiver=old,partition=[left,right],split_indices=[index,part_index],added_solid_area=0,removed_solid_area=0,union_unchanged=True,synthetic_connector=False,definition_exit_marker=[sx+40,y-18],final_original_port=copy.deepcopy(final),reward_amount=0,scope='Exact collider partition and two-way 24x36 body excursion before original onward route; no general Module seam/assembly guarantee')
  c['seam_specimen']['fixture_geometry_sha256']=geometry_key(c)
  c['seam_specimen']['fixture_version']='sha256:'+digest(dict(source_version=s['contentVersion'],geometry_sha256=geometry_key(c),control_plan=c['control_plan']))
  out.append(c)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',default='generation/workshop/junctions-v1/manifest.json');p.add_argument('--name',default='workshop-junction-seams-v1');a=p.parse_args()
 manifest=exact_path(a.manifest);out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable_seam_run_exists')
 bases=specimens(manifest)
 e=WorkshopEngine(out,extra_sources=[Path(__file__),ROOT/'prototype/creative_batches/plains50_seams/fixtures_v1.py'])
 write(out/'protocol.json',dict(PROTOCOL,manifest=binding(manifest)));write(out/'source-cases.json',dict(cases=bases));rows=[]
 for c,r,b in e.run(bases,'clean-seam-probe'):
  q=check(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q)),flush=True)
 write(out/'clean-probe-results.json',rows)
 if not all(x['check']['ok']for x in rows):
  write(out/'summary.json',dict(status='gap_after_clean_probes',physics_cases=e.sim.cases,checks=[dict(id=x['case']['id'],check=x['check'])for x in rows],production_admitted=False));return
 cal=evaluate(e,bases,PROTOCOL['calibration_seed'],12,'seam-calibration',purpose_fn=check);write(out/'calibration-evaluations.json',cal)
 selected=[x['case']for x in cal if x['quality_gate']['status']=='awaiting_human_review']
 write(out/'selection-before-holdout.json',dict(case_ids=[c['id']for c in selected],fixture_versions=[c['seam_specimen']['fixture_version']for c in selected],calibration_sha256=file_sha(out/'calibration-evaluations.json'),holdout_seed=PROTOCOL['holdout_seed']))
 held=evaluate(e,selected,PROTOCOL['holdout_seed'],12,'seam-holdout',purpose_fn=check)if len(selected)==len(bases)else[]
 write(out/'holdout-evaluations.json',held);passed=[x for x in held if x['quality_gate']['status']=='awaiting_human_review']
 summary=dict(schema='pcg/junction-exact-seam-fixture-result/v1',status='passed_scoped_fixtures'if len(passed)==len(bases)else'gap_after_calibration_or_holdout',expected_fixtures=2,passed_fixtures=len(passed),physics_cases=e.sim.cases,budget=120,source_versions=[c['seam_specimen']['source']['contentVersion']for c in bases],fixture_versions=[c['seam_specimen']['fixture_version']for c in bases],sources=[c['seam_specimen']['source']for c in bases],calibration=[dict(id=x['case']['id'],stats=x['stats'],quality=x['quality_gate'])for x in cal],holdout=[dict(id=x['case']['id'],stats=x['stats'],quality=x['quality_gate'])for x in held],added_solid_area=0,removed_solid_area=0,union_unchanged=True,resource_writes=0,world_resets_within_trial=0,module_enrollment=False,source_contracts_modified=False,original_module_seam_coverage='UNKNOWN; fixture does not upgrade source contract',whole_map='UNKNOWN',production_admitted=False)
 assert e.sim.cases<=PROTOCOL['actual_physics_budget_max']
 write(out/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
