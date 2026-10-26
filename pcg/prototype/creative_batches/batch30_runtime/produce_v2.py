"""Register a new bounded repair cycle on the original production path."""
import argparse
import importlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from . import produce_v1 as common
from pcg.prototype.creative_batches.plains50_ports.produce_v2 import run
from pcg.prototype.workshop.production_loop import static_preflight

HERE=Path(__file__).parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--rules',required=True)
    p.add_argument('--index',type=int,required=True);p.add_argument('--cycle',choices=['PR-D03','PR-D04'])
    p.add_argument('--interfaces',type=int,nargs='+',choices=[0,1])
    p.add_argument('--protocol',type=Path,default=common.REPO/'pcg/creative-production/batch30/protocol-v7.json')
    a=p.parse_args();authored=importlib.import_module(a.rules)
    protocol_path=a.protocol.resolve();protocol=json.loads(protocol_path.read_text())
    assert 0<=a.index<protocol['maximum_design_proposals']
    if a.cycle:
        cycle=next(c for c in protocol['core_refutation_repair_cycles']if c['proposal']==a.cycle)
        config=dict(calibration_seed=cycle['calibration_seed'],holdout_seed=cycle['holdout_seed'],maximum_cases_per_proposal=cycle['maximum_new_full_cases'],maximum_source_revisions=cycle['maximum_new_rule_revisions'])
    else:
        config=dict(calibration_seed=protocol['calibration_seed']+a.index*protocol['seed_stride'],holdout_seed=protocol['holdout_seed']+a.index*protocol['seed_stride'],maximum_cases_per_proposal=protocol['maximum_full_cases_per_relationship'],maximum_source_revisions=protocol['maximum_rule_revisions_per_proposal'])
        config.update(protocol.get('proposal_overrides',{}).get(str(a.index),{}))
    rules=SimpleNamespace(__file__=authored.__file__,RECIPES=authored.RECIPES,layouts=authored.layouts,alternatives=authored.alternatives,purpose=lambda c,r:common.checked_purpose(authored,c,r))
    sources=[c for i in (a.interfaces or[0,1])for c in authored.layouts(authored.RECIPES[0],i)]
    assert all(len(authored.alternatives(c))>=protocol['minimum_counters_per_exact_route_geometry']for c in sources)
    paired=any(l.get('paired_gate')for c in sources for l in c.get('latches',[]))
    mounted=any(l.get('carrier_mount')for c in sources for l in c.get('latches',[]))
    exporter=HERE/('export_mounted_v1.mjs'if mounted else'export_v1.mjs')
    dependencies=[Path(__file__),Path(common.__file__),exporter,HERE/'export_v1.mjs',protocol_path,HERE.parent/'junctions/landing_buffer_v1.py',HERE.parent/'junctions/produce_v1.py']+list(getattr(authored,'SOURCE_DEPENDENCIES',[]))
    if paired:dependencies += [common.CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn','protocol-v1.json']]
    runner=getattr(authored,'RUNNER_SCRIPT',common.CELL/'runner_v3.gd'if paired else None)
    def preflight(engine,cases):
        static_preflight(engine,cases)
        subprocess.run(['node',str(exporter),str(engine.out/'preflight-bundle.json'),str(engine.out/'batch-preflight-documents')],cwd=common.REPO,check=True,capture_output=True)
    run(a.name,interfaces=a.interfaces,recipe_module=rules,export_script=exporter,protocol_config=config,extra_sources=dependencies,outcome_checker=common.external_outcome,runner_script=runner,preflight_fn=preflight,counter_classifier=common.counter_classification)

if __name__=='__main__':main()
