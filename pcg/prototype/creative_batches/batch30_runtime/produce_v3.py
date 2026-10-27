"""Current Module workshop entry: upstream Map Block constraints are required."""
import argparse
import importlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from . import produce_v1 as common
from .block_contract_v1 import inspect_counter_bindings,POLICY
from .block_contract_v2 import inspect_sources
from .script_preflight_v1 import check as check_scripts
from pcg.prototype.creative_batches.plains50_ports.produce_v2 import run
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.workshop.experiments import write

HERE=Path(__file__).parent
EXPORTER=HERE/'export_block_v1.mjs'


def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--rules',required=True)
    p.add_argument('--index',type=int,required=True);p.add_argument('--interfaces',type=int,nargs='+',choices=[0,1])
    p.add_argument('--protocol',type=Path,default=common.REPO/'pcg/creative-production/batch30/protocol-map-block-v2.json')
    args=p.parse_args();authored=importlib.import_module(args.rules)
    exporter=Path(getattr(authored,'EXPORT_SCRIPT',EXPORTER)).resolve()
    if not exporter.is_relative_to(common.REPO)or not exporter.is_file()or exporter.suffix!='.mjs':raise ValueError('explicit repository-owned Module exporter required')
    protocol_path=args.protocol.resolve();protocol=json.loads(protocol_path.read_text())
    if not 0<=args.index<protocol['maximum_design_proposals']:raise ValueError('outside declared proposal budget')
    sources=[c for i in(args.interfaces or[0,1])for c in authored.layouts(authored.RECIPES[0],i)]
    response=inspect_sources(sources)
    if response['status']=='requires_physics':
        counters=inspect_counter_bindings(sources,authored.alternatives,protocol['minimum_counters_per_exact_route_geometry'])
        response['counter_bindings']=counters
        if counters['status']!='requires_physics':response.update(status='needs_design',conflicts=counters['conflicts'])
    if response['status']!='requires_physics':
        out=common.PCG/'results'/args.name
        if out.exists():raise ValueError('immutable request response exists')
        write(out/'request-response.json',dict(response,rule_source=args.rules,protocol=str(protocol_path.relative_to(common.REPO))))
        print(json.dumps(response,ensure_ascii=False));return
    rules=SimpleNamespace(__file__=authored.__file__,RECIPES=authored.RECIPES,layouts=authored.layouts,alternatives=authored.alternatives,purpose=lambda c,r:common.checked_purpose(authored,c,r))
    config=dict(calibration_seed=protocol['calibration_seed']+args.index*protocol['seed_stride'],holdout_seed=protocol['holdout_seed']+args.index*protocol['seed_stride'],maximum_cases_per_proposal=protocol['maximum_full_cases_per_relationship'],maximum_source_revisions=protocol['maximum_rule_revisions_per_proposal'])
    dependencies=[Path(__file__),Path(common.__file__),HERE/'block_contract_v1.py',HERE/'block_contract_v2.py',HERE/'script_preflight_v1.py',exporter,EXPORTER,HERE/'export_v1.mjs',HERE/'export_mounted_v1.mjs',POLICY,protocol_path,common.PCG/'map_directed/block_grid/contracts.py',HERE.parent/'junctions/landing_buffer_v1.py',HERE.parent/'junctions/produce_v1.py']+list(getattr(authored,'SOURCE_DEPENDENCIES',[]))
    paired=any(l.get('paired_gate')for c in sources for l in c.get('latches',[]))
    if paired:dependencies += [common.CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn','protocol-v1.json']]
    runner=getattr(authored,'RUNNER_SCRIPT',common.CELL/'runner_v3.gd'if paired else None)
    def preflight(engine,cases):
        scripts=[Path(runner)if runner else common.PCG/'prototype/workshop/runner.gd']
        for c in cases:
            scene=c.get('native_block_scene')or getattr(authored,'NATIVE_SCENE',None)
            if scene:
                path=Path(scene)
                if str(scene).startswith('res://'):path=common.PCG/str(scene).removeprefix('res://')
                elif not path.is_absolute():path=common.REPO/path
                scripts.append(path.with_suffix('.gd'))
        syntax=check_scripts(scripts);write(engine.out/'script-preflight.json',syntax)
        if syntax['status']!='syntax_checked':
            write(engine.out/'request-response.json',dict(status='needs_design',conflicts=syntax,actual_physics_cases=0,negotiable=['repair the registered source syntax, then use a new run name'],production_admitted=False))
            raise ValueError('Original Godot syntax preflight rejected; no physics cases executed')
        write(engine.out/'map-block-preflight.json',inspect_sources(cases))
        static_preflight(engine,cases)
        command=['node',str(exporter),str(engine.out/'preflight-bundle.json'),str(engine.out/'block-preflight-documents')]
        result=subprocess.run(command,cwd=common.REPO,capture_output=True,text=True)
        write(engine.out/'block-export-preflight.json',dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,physics='NOT_RUN',map_added_terrain=0))
        if result.returncode:raise ValueError('Map Block export rejected; see block-export-preflight.json')
    counter_classifier=getattr(authored,'COUNTER_CLASSIFIER',common.counter_classification)
    run(args.name,interfaces=args.interfaces,recipe_module=rules,export_script=exporter,protocol_config=config,extra_sources=dependencies,outcome_checker=common.external_outcome,runner_script=runner,preflight_fn=preflight,counter_classifier=counter_classifier)


if __name__=='__main__':main()
