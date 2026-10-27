"""Two final API clean witnesses and original standard-export preflight."""
import argparse,json,subprocess
from pathlib import Path
from . import api_v1 as api
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name;cs=api.layouts(api.RECIPES[0],0)
 checks=dict(scripts=check([api.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources(cs),counters=inspect_counter_bindings(cs,api.alternatives,18))
 if checks['scripts']['status']!='syntax_checked'or any(checks[k]['status']!='requires_physics'for k in ['blocks','counters']):write(out/'preflight.json',checks);raise ValueError('finalAPI0physicsrejection')
 e=WorkshopEngine(out,extra_sources=[Path(__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);write(out/'preflight.json',checks);static_preflight(e,cs)
 exporter=HERE.parent/'batch30_runtime/export_block_v1.mjs';js=subprocess.run(['node',str(exporter),str(out/'preflight-bundle.json'),str(out/'block-preflight-documents')],cwd=ROOT.parent,capture_output=True,text=True);write(out/'export-preflight.json',dict(returncode=js.returncode,stdout=js.stdout,stderr=js.stderr))
 if js.returncode:raise ValueError('originalModule/Blockexportrejected')
 rows=[]
 for c,r,ev in e.run(cs,'final-API-clean'):
  q=common.checked_purpose(api,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),new_candidates=0))
if __name__=='__main__':main()
