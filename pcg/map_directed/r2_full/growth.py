"""Bounded existing-library → compact demand fill → full R2 instance loop.

The existing generator, regular gate and candidate registry stay authoritative.
No failed room demand is repaired by dropping an exploration edge.
"""
import argparse,json
from pathlib import Path
from ..director import REPO
from ..library import CandidateLibrary
from ..run import write
from .compiler import compile_map
from .pressure import enrich
from .bell_room import install
from .compact_bell import run as compact_fill
from .orchestrate import FullMapEngine
from .validate import case_for
from pcg.tools.r2_compact_holdout import run as independent_holdout


def run(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_growth_run_exists')
    out.mkdir(parents=True)
    # Derive the first supported room request from the previously recorded
    # narrow adapter. General irregular/multiport demands remain unsupported.
    source=REPO/'pcg/results/r2-compact-bell-v1/summary.json'
    spec=json.loads(source.read_text())['request']
    spec['map_seed']='0';spec['id']='full-r2-r12-optional-bell'
    spec['risk_reward'].update(optional=True,amount=8)
    spec['objective']='Optional bell ascent in r12, followed by continuous right-shaft return to the full exploration network'
    write(out/'challenge-specification.json',spec)
    log=[];library=CandidateLibrary();found=library.find(spec)
    log.append(dict(stage='search_verified_candidate_library',matches=len(found),request=spec['id']))
    write(out/'generation-log.json',log)
    if not found:
        # One bounded adaptation pass and one predeclared independent holdout.
        # Both existing CLIs retain raw failures/source snapshots themselves.
        generated_name=name+'-compact';holdout_name=name+'-holdout'
        generated=compact_fill(generated_name)
        log.append(dict(stage='demand_fill',result=generated,run=generated_name))
        write(out/'generation-log.json',log)
        held=independent_holdout(holdout_name,generated_name)
        log.append(dict(stage='existing_regular_gate_and_enrollment',run=holdout_name,result=held))
        write(out/'generation-log.json',log)
        found=library.find(spec)
    if not found:
        result=dict(status='unsatisfied',condition='656x624_compact_bell_regular_candidate',
            director_feedback='retain all 27 places/39 edges; this optional demand requires local content revision',
            budget=dict(generator_calls=1,holdout_calls=1,retries=0),production_admitted=False)
        write(out/'result.json',result);return out
    selected=found[0];log.append(dict(stage='reuse_versioned_candidate',record=selected['record'],path=selected['path']))
    write(out/'generation-log.json',log)
    compiled=install(enrich(compile_map(static_gap_hazards=True)),library_match=selected)
    case=case_for(compiled,['r12','boss'],'library-reuse-bell',optional=True)
    write(out/'compiled.json',compiled);write(out/'cases.json',{'cases':[case]})
    engine=FullMapEngine(out/'physics')
    for _,result,evidence in engine.run([case],'library-reuse-whole-map'):
        write(out/'result.json',dict(status='whole_map_policy_passed'if result['ok']else'whole_map_policy_failed',
            reason=result['reason'],ticks=result.get('ticks'),pilot=result.get('pilot'),mechanics=result.get('extra'),
            evidence=evidence,module_content_version=selected['record']['contentVersion'],
            library_was_reused_before_generation=len(log)==2,generator_calls=int(len(log)>2),
            human_fun='unverified',production_admitted=False))
        print(result['ok'],result['reason'],result.get('ticks'),flush=True)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
