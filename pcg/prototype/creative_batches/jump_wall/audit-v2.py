"""Read-only byte/resource audit of four immutable selected content candidates."""
import json,gzip,hashlib
from pathlib import Path
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT.parent
LIB=ROOT/'results/workshop-creative-jump-wall-library-v1'
DEST=ROOT/'creative-production/jump_wall/delivery-audit-v2.json'
if DEST.exists():raise ValueError('immutable_audit_exists')
rows=[];all_cases=0;byte_batches=0;source_files=0
for run,roundno in [('v2',1),('v2',2),('v3',0),('v3',1),('v5',0)]:
 p=ROOT/f'results/workshop-creative-jump-wall-production-{run}/round-{roundno:02d}'
 review=json.loads((p/'review_cases.json').read_text())['cases'];assert len(review)==1
 c=review[0];family=c['family'];evaluations=json.loads((p/'evaluations.json').read_text());cal=json.loads((p/'calibration-evaluations.json').read_text());manifest=json.loads((p/'modules/manifest.json').read_text());entry=manifest['modules'][0]
 canonical=None;checked_cases=0;cap_checks=0
 for batch in json.loads((p/'batches.json').read_text()):
  packed=p/batch['gzip_path'];raw=gzip.decompress(packed.read_bytes());assert file_sha(packed)==batch['gzip_sha256'];assert hashlib.sha256(raw).hexdigest()==batch['raw_output_sha256'];byte_batches+=1
  execution=json.loads((p/batch['execution']).read_text());inp=p/'physics'/(batch['batch']+'.input.json');assert file_sha(inp)==execution['input_sha256'];assert execution['exit_code']==0
  cs=json.loads(inp.read_text())['cases'];rs=json.loads(raw)['results'];assert len(cs)==len(rs)==batch['cases']
  for case,r in zip(cs,rs):
   assert case['id']==r['id'];checked_cases+=1
   if r.get('rejected'):continue
   snap=r['capability_snapshot'];entry_snap=r['entry_snapshot'];caps=case['capabilities']
   assert sorted(snap['declared'])==sorted(caps)
   assert snap['jump_enabled']==('jump'in caps) and snap['double_enabled']==('double_jump'in caps) and snap['wall_enabled']==('wall_climb'in caps) and snap['shoot_enabled']==('shot_recoil'in caps)
   assert entry_snap['jump_maximum']==(2 if 'double_jump'in caps else 1)
   if 'jump'not in caps:assert not entry_snap['can_air_jump']
   assert entry_snap['sampling_point']=='before_first_router_input_after_dynamic_update'
   cap_checks+=1
   if batch['stage']=='clean-screen'and case['id']==c['id']:canonical=r
 assert canonical and canonical['ok']
 binding=json.loads((p/'source_binding.json').read_text());source_drift=[n for n,h in binding['source_files'].items()if file_sha(ROOT/n)!=h];assert not source_drift;source_files+=len(binding['source_files'])
 hits=WorkshopLibrary(LIB).find_single_exact(c['map_specification']);assert len(hits)==1 and hits[0]['record']['contentVersion']==entry['contentVersion']
 counters=json.loads((p/'counterexamples.json').read_text());decisions=json.loads((p/'counter-decisions.json').read_text());assert len(counters)>=18 and not any(q['invalidates_design']for q in counters)
 row=dict(family=family,case_id=c['id'],case_path=str((p/'review_cases.json').relative_to(REPO)),run=str(p.relative_to(REPO)),module_path=str((p/'modules'/entry['file']).relative_to(REPO)),svg_path=str((p/'modules'/(entry['id']+'.svg')).relative_to(REPO)),contentVersion=entry['contentVersion'],canonical_case_sha256=c['module_sha256'],document_sha256=file_sha(p/'modules'/entry['file']),svg_sha256=file_sha(p/'modules'/(entry['id']+'.svg')),calibration=cal[0]['stats'],holdout=evaluations[0]['stats'],quality_gate=evaluations[0]['quality_gate'],counterexamples=len(counters),safe_core_alternatives=sum(q['safe_stable']and not q['invalidates_design']for q in counters),invalidating_counterexamples=0,actual_physics_cases=checked_cases,capability_entry_audited_cases=cap_checks,canonical_capability_snapshot=canonical['capability_snapshot'],canonical_entry_snapshot=canonical['entry_snapshot'],canonical_causal=[q for q in json.loads((p/'screen.json').read_text())if q['id']==c['id']and q['stage']=='clean'][0]['purpose'],library_retrieval_versions=[h['record']['contentVersion']for h in hits],holdout_failures=[dict(level=q['level'],trial=q['trial'],reasons=q['purpose']['reasons'])for q in evaluations[0]['rows']if not q['purpose']['ok']],assembly_admitted=False,human_fun='unreviewed',manual_play='not_done',production_admitted=False)
 rows.append(row);all_cases+=checked_cases
report=dict(schema='pcg/creative-delivery-audit/v1',task_name='/root/jump_wall_creator',source_type='llm_subagent_proposal',implemented_technical_candidates=len(rows),independent_relationship_count='pending_global_novelty_review',private_library=str(LIB.relative_to(REPO)),delivery=rows,selected_round_physics_cases=all_cases,verified_compressed_batches=byte_batches,verified_source_file_bindings=source_files,all_source_binding_drift=[],fresh_process_retrievals=5,full_production_v2_v3_v4_v5_cases=sum(json.loads((ROOT/f'results/workshop-creative-jump-wall-production-{r}/summary.json').read_text())['physics_cases']for r in ['v2','v3','v4','v5']),design_cards='pcg/creative-production/jump_wall/design-cards-v2.json',limits=['Finite automated strategy evidence only; no human fun or manual play approval.','One two-port interface each. Reverse direction, arbitrary entry states, transforms, seams and whole-map assembly remain UNKNOWN.','Late-air-rise has calibration/holdout failures retained; use exact reported statistics, not 100% claims.','Legacy guard adapter changes routing only; original capability Adapter applies actual caps, independently audited for every selected round case.','Original exporter source.path labels its shared adapter; exact producer/adapter files are frozen in source_binding and source_snapshot, rule metadata declares actual creator.','Ground-reset and contact-refill duplicates were not counted; all failed versions and probes retained.'],fifth_card='pcg/creative-production/jump_wall/wallslide-design-card-v1.json',videos='parent agent owns new native recording and public delivery',production_admitted=False)
DEST.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(file=str(DEST.relative_to(REPO)),candidates=len(rows),selected_round_physics_cases=all_cases,compressed_batches=byte_batches,stats=[dict(family=r['family'],calibration={l:[v['purpose_valid'],v['trials']]for l,v in r['calibration'].items()},holdout={l:[v['purpose_valid'],v['trials']]for l,v in r['holdout'].items()})for r in rows]),ensure_ascii=False),flush=True)
