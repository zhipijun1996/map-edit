"""Return the unresolved active-transfer need rather than a one-exit fork."""
import argparse,json
from pathlib import Path
HERE=Path(__file__).parent

def compile_request(request=None):
 receipt=json.loads((HERE/'probe-receipt-v1.json').read_text())
 return dict(schema='pcg/Module-generation-response/v1',status='needs_design',request_id=request.get('id','TaskA/N02/active-transfer-fork')if isinstance(request,dict)else'TaskA/N02/active-transfer-fork',conflicts=[dict(field='mechanics.intercept-start.projectile_clearance',reason='Both actualworld revisions block originalbullet before staticreceiver: v1P1top andv2P2rightface'),dict(field='relations.A_to_B',reason='No highroute programme startsP2 and achievestrueinterception; 4/4finalhigh fail'),dict(field='ports.count',reason='Final4/4low prototypes are not a qualified3portfork; requiredA_to_B cannotbedeleted')],searched=dict(rule_versions=receipt['actual_rule_versions'],actual_cases=receipt['actual_cases'],interfaces=[0],source_phase=.6,phase_generalization='NOT_RUN',full_and_held='NOT_RUN'),negotiable=['New exposed staticreceiver corridor with wholebody/shotphase evidence','New preregistered physical/control proposal before moreexperiments','Reconsider activecatch geometry while preserving a meaningful low/high choice','Explicitly request a twoport lowprototype instead of3portfork; it still needs ownqualification'],may_delete_required_relations=False,may_add_Map_terrain=False,may_reset_resources=False,proposals_only=receipt['next_revision'],new_physics_cases=0,new_candidates=0,human_fun='UNKNOWN',production_admitted=False)

def main():
 p=argparse.ArgumentParser();p.add_argument('--request',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();v=compile_request(json.loads(a.request.read_text())if a.request else None)
 if a.out:
  if a.out.exists():raise ValueError('immutablefailureinterface')
  a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(v,ensure_ascii=False))

if __name__=='__main__':main()
