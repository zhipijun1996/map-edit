"""Audit original compressed real traces and publish a scoped B fixture index."""
import gzip,json
from pathlib import Path
from . import fixtures_v2 as fixtures
from . import audit_v1 as audit
from pcg.prototype.factory.core.engine import file_sha
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent
REPO=HERE.parents[3]
def binding(p):return dict(path=str(p.relative_to(REPO)),sha256=file_sha(p),bytes=p.stat().st_size)
def main():
 run=REPO/'pcg/results/workshop-batch30-blockn04-seam-full-v2';c=fixtures.fixture();owned=set(map(tuple,c['block_grid']['cells']));rows=[];ready=[]
 for b in json.loads((run/'batches.json').read_text()):
  packed=run/b['gzip_path'];assert file_sha(packed)==b['gzip_sha256'];raw=gzip.decompress(packed.read_bytes())
  import hashlib
  assert hashlib.sha256(raw).hexdigest()==b['raw_output_sha256']
  for i,r in enumerate(json.loads(raw)['results']):
   q=fixtures.purpose(c,r);fs=r['frames'];cross=[f for f in fs if f['x']-12<1280<f['x']+12 and abs(f['y']-334)<1]
   outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
   contiguous=all(b['frame']==a['frame']+1 for a,b in zip(fs,fs[1:]));clock=all(b['module_clock']>=a['module_clock']for a,b in zip(fs,fs[1:]))
   ingress=q['causal']['observed_right_ingress'];first=ingress[0]['frame']if ingress else-1
   early_open=[f['frame']for f in fs if 0<=f['frame']<first and f['n04_seam']['right/return-catch']['open']]
   if q['ok']:ready+=ingress
   row=dict(id=r['id'],purpose_passed=q['ok'],purpose_reasons=q['reasons'],raw_safe_stable=r['ok'],outside_body_frames=outside,continuous_frame_sequence=contiguous,monotonic_world_clock=clock,early_foreign_right_gate_open_frames=early_open,all_seam_straddling_grounded=bool(cross)and all(f['grounded']for f in cross),left_stable_frames=q['causal']['left_dock_stable_frames'],right_stable_frames=q['causal']['right_dock_stable_frames'],left_gate_cycle=q['causal']['left_core']['causal'],right_gate_cycle=q['causal']['right_core']['causal'],claims=q['causal']['claims'],right_ingress=ingress,final={k:fs[-1].get(k)for k in ['frame','x','y','vx','vy','grounded','support_id','shot_charges','shot_cooldown','jumps_used','energy','hp']},evidence=dict(batch=b['batch'],index=i,gzip_path=b['gzip_path'],gzip_sha256=b['gzip_sha256'],raw_output_sha256=b['raw_output_sha256']))
   assert not outside and contiguous and clock and not early_open
   rows.append(row)
 assert len(rows)==50 and sum(r['purpose_passed']for r in rows)==48
 ranges={k:[min(f[k]for f in ready),max(f[k]for f in ready)]for k in ['x','y','vx','shot_charges','shot_cooldown','jumps_used','energy','hp']}
 result=dict(schema='pcg/N04-exact-seam-body-state-audit/v1',source_version='sha256:'+audit.VERSION,fixture_version=c['seam_specimen']['fixture_version'],actual_cases=50,purpose_passed=48,purpose_failed=2,all_body_inside_exact_union=True,all_single_world_frame_clock_checks=True,ingress_ranges_are_observed_samples_not_guarantees=ranges,source_binding=binding(run/'source_binding.json'),batches=binding(run/'batches.json'),rows=rows,new_modules=0,generic_ingress='UNKNOWN',production_admitted=False)
 out=HERE/'body-and-state-audit-v1.json'
 if out.exists():raise ValueError('immutable post audit exists')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 parts=[]
 for name,count in [('workshop-batch30-blockn04-seam-clean-v1',2),('workshop-batch30-blockn04-seam-noise-v1',6),('workshop-batch30-blockn04-seam-full-v1',25),('workshop-batch30-blockn04-seam-screen-v2',7),('workshop-batch30-blockn04-seam-full-v2',50)]:
  p=REPO/'pcg/results'/name;parts.append(dict(run=str(p.relative_to(REPO)),actual_cases=count,receipt=binding(p/'receipt.json'),source_binding=binding(p/'source_binding.json'),batches=binding(p/'batches.json')))
 full=json.loads((run/'receipt.json').read_text());cal=full['calibration'][0];held=full['holdout'][0]
 spec=dict(schema='pcg/existing-module-continuous-fixture/v1',id='N04-C-to-N04-A-exact-Block-join',status='technical_scoped_fixture',source_standard_document=c['seam_specimen']['source_binding'],instances=[dict(id='left',contentVersion='sha256:'+audit.VERSION,translation=[0,0]),dict(id='right',contentVersion='sha256:'+audit.VERSION,translation=[1280,-384])],connection=dict(from_component='left',from_port='C',to_component='right',to_port='A',anchor=[1280,320],profile='ground64/v1',crossing_offset=[0,14],map_added_platforms=0,resource_reset=False),tested_route=dict(entry='left.A',source_left_route='A-to-C',left_staging=[1256,334],crossing_anchor=[1280,320],right_staging=[1304,334],source_right_route='A-to-C',exit='right.C',exit_staging=[2536,-50]),external_port_aliases=c['seam_specimen']['external_ports'],controller=dict(module='pcg.prototype.creative_batches.batch30_blockn04_seam.fixtures_v2',factory='fixture',fixture_version=c['seam_specimen']['fixture_version'],source=binding(Path(fixtures.__file__)),selected_before_calibration_holdout=binding(HERE/'frozen-controller-v2.json')),physical_union_audit=binding(HERE/'entity-union-audit-v1.json'),placement_audit=binding(HERE/'static-placement-v1.json'),body_and_state_audit=binding(out),review_cases=binding(run/'review_cases.json'),native_scene=binding(HERE/'main_v1.tscn'),actual_case_cost=90,probe_cases=15,maximum_probe_cases=80,maximum_total_cases=160,calibration=dict(stats=cal['stats'],quality_gate=cal['quality_gate']),holdout=dict(stats=held['stats'],quality_gate=held['quality_gate']),observed_right_ingress=ranges,qualification='One exact two-source/translation/controller route; internal same-gate cycles and real state crossing verified. Standard source documents remain immutable.',generic_seam='UNKNOWN',generic_transform='UNKNOWN',arbitrary_ingress='UNKNOWN',return_conditions='UNKNOWN',whole_map='UNKNOWN',assembly_admission_granted=False,new_modules=0,new_families=0,library_enrollment=False,human_fun='UNKNOWN',production_admitted=False,runs=parts)
 # `return` is a JSON field, not a Python keyword argument.
 target=HERE/'handoff-v1.json';target.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(handoff=str(target),actual_cases=90,full_purpose_passed=48,full_trials=50,new_modules=0)))
if __name__=='__main__':main()
