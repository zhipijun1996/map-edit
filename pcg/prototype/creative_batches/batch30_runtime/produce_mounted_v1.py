"""Run the original multi-route production path with mounted-bell output."""
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
EXPORTER=HERE/'export_mounted_v1.mjs'

def preflight(engine,cases):
    static_preflight(engine,cases)
    subprocess.run(['node',str(EXPORTER),str(engine.out/'preflight-bundle.json'),str(engine.out/'batch-preflight-documents')],cwd=common.REPO,check=True,capture_output=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--rules',required=True);p.add_argument('--index',type=int,default=2)
    a=p.parse_args();authored=importlib.import_module(a.rules)
    protocol_path=common.REPO/'pcg/creative-production/batch30/protocol-v5.json'
    protocol=json.loads(protocol_path.read_text())
    assert 0<=a.index<protocol['maximum_design_proposals']
    rules=SimpleNamespace(__file__=authored.__file__,RECIPES=authored.RECIPES,layouts=authored.layouts,alternatives=authored.alternatives,purpose=lambda c,r:common.checked_purpose(authored,c,r))
    dependencies=[Path(__file__),Path(common.__file__),EXPORTER,HERE/'export_v1.mjs',protocol_path,HERE.parent/'junctions/landing_buffer_v1.py',HERE.parent/'junctions/produce_v1.py']+list(authored.SOURCE_DEPENDENCIES)
    config=dict(calibration_seed=protocol['calibration_seed']+a.index*protocol['seed_stride'],holdout_seed=protocol['holdout_seed']+a.index*protocol['seed_stride'],maximum_cases_per_proposal=protocol['maximum_full_cases_per_relationship'],maximum_source_revisions=protocol['maximum_rule_revisions_per_proposal'])
    run(a.name,recipe_module=rules,export_script=EXPORTER,protocol_config=config,extra_sources=dependencies,outcome_checker=common.external_outcome,runner_script=authored.RUNNER_SCRIPT,preflight_fn=preflight,counter_classifier=common.counter_classification)

if __name__=='__main__':main()
