"""Independent original-regular same-world loop fixture; no Module enrollment."""
import argparse,json,shutil
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from pcg.prototype.creative_batches.batch30_d04_validation.run_v1 import public_witness
from pcg.prototype.factory.core.quality import digest,module_hash
from pcg.prototype.factory.core.engine import file_sha
HERE=Path(__file__).parent

def world_binding(c):return digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports','block_reservations']})

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable N08 loop run exists')
 protocol=json.loads((HERE/'protocol-v1.json').read_text());sel=HERE/'control-selection-v1.json';control=json.loads(sel.read_text())['chosen_control'];assert control==0,'frozenpre-noiseselection0'
 base=rules.candidate(control,'loop');deps=[Path(__file__),sel,HERE/'fixture-seed-formula-clarification-v1.json',Path(public_witness.__code__.co_filename),ROOT/'creative-production/batch30/protocol-map-block-v4.json',*rules.SOURCE_DEPENDENCIES]
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'fixture-protocol.json',dict(schema='pcg/N08-independent-loop-full/v1',source_protocol=str((HERE/'protocol-v1.json').relative_to(ROOT.parent)),calibration_seed=protocol['fixture_seeds']['calibration'],held_seed=protocol['fixture_seeds']['held'],trials=12,original_regular=True,source_control=control,standard_Module_route=False,definition_entry='A',definition_exit_static_marker='B',actual_goal_and_endpoint='A',same_world=True,resource_resets=0,maximum_actual_cases=50,selection='Onefrozencontroller; calibration thenheldonlyiforiginalregularpasses; noheldrepair',new_module_count=0))
 write(out/'source-case.json',dict(cases=[base]));check=lambda c,r:checked_purpose(rules,c,r)
 cal=evaluate(e,[base],protocol['fixture_seeds']['calibration'],12,'loop-calibration',purpose_fn=check);shutil.copy2(out/'evaluations.json',out/'calibration-evaluations.json')
 good=cal[0]['quality_gate']['status']=='awaiting_human_review';write(out/'selection-before-held.json',dict(accepted_for_held=good,source_case_sha256=digest(base),calibration_sha256=file_sha(out/'calibration-evaluations.json'),selected_before_held=True,controller_changed=False,held_seed=protocol['fixture_seeds']['held']))
 if good:write(out/'review_cases.json',dict(schema='pcg/continuous-loop-review/v1',cases=[public_witness(cal[0])],scope='Exactfrozenloop, notModulecandidate'))
 held=evaluate(e,[base],protocol['fixture_seeds']['held'],12,'loop-held',purpose_fn=check)if good else[]
 passed=good and held[0]['quality_gate']['status']=='awaiting_human_review'
 binding=dict(schema='pcg/N08-continuous-loop-evidence/v1',status='scoped_regular_pass'if passed else'needs_design',standard_Module_route=False,actual_start='A',actual_end='A',visited='Bafterreal16coinclaim',original_definition_exit_is_only_static_marker='B',same_world_no_reset=True,layout_uid=base['layout_uid'],world_binding_sha256=world_binding(base),source_case_sha256=digest(base),source_case_module_sha256=module_hash(base),program_sha256={route:digest(rules.candidate(control,route)['control_plan'])for route in ['out','back','loop']},source_manifest_sha256=e.binding['source_manifest_sha256'],actual_cases=e.sim.cases,calibration_stats=cal[0]['stats'],calibration_quality=cal[0]['quality_gate'],held_stats=held[0]['stats']if held else'NOT_RUN',held_quality=held[0]['quality_gate']if held else'NOT_RUN',artifacts=[dict(path=str(p.relative_to(ROOT.parent)),sha256=file_sha(p))for p in [out/'source-case.json',out/'source_binding.json',out/'fixture-protocol.json',out/'calibration-evaluations.json',out/'selection-before-held.json',out/'evaluations.json',out/'batches.json']],scope='ExactCell/geometry/ports/worldstate andfrozencontinuouscontroller; doesnotcertifyarbitraryenterystate,Moduleboundary,seam,wholeMap,funorproduction',new_modules=0,human_fun='UNKNOWN',production_admitted=False)
 write(out/'continuous-evidence-v1.json',binding);print(json.dumps(dict(status=binding['status'],actual_cases=e.sim.cases,calibration=cal[0]['quality_gate'],held=held[0]['quality_gate']if held else'NOT_RUN',path=str(out/'continuous-evidence-v1.json'))),flush=True)
if __name__=='__main__':main()
