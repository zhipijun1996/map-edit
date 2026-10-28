"""Budgeted actual controls, original noise and structural alternatives."""
import argparse,json,subprocess
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise','counters'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 selection=HERE/'control-selection-v1.json'
 control=0 if a.stage=='clean' else json.loads(selection.read_text())['control']
 base=rules.candidate(0,control)
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,rules.NATIVE_SCENE.with_suffix('.gd')]),blocks=inspect_sources([base]),counters=inspect_counter_bindings([base],rules.alternatives,18))
 if checks['scripts']['status']!='syntax_checked' or any(checks[k]['status']!='requires_physics'for k in ['blocks','counters']):write(out/'preflight.json',checks);raise ValueError('original preflight rejected; zero physical cases')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES]
 if a.stage!='clean':deps.append(selection)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks)
 if a.stage=='clean':
  static_preflight(e,[base])
  js=subprocess.run(['node',str(rules.EXPORT_SCRIPT),str(out/'preflight-bundle.json'),str(out/'block-preflight-documents')],cwd=ROOT.parent,capture_output=True,text=True)
  write(out/'export-preflight.json',dict(returncode=js.returncode,stderr=js.stderr,stdout=js.stdout))
  if js.returncode:raise ValueError('original Dock/Block exporter rejected')
  cases=[rules.candidate(0,k)for k in [0,1]]
 elif a.stage=='noise':cases=[instantiate(base,271130128,l,k)for l in ['mild','moderate']for k in range(6)]
 else:
  wanted=json.loads((HERE/'protocol-v1.json').read_text())['counter_selection']
  cases=[c for c in rules.alternatives(base)if c['counterexample_kind']in wanted]
  assert len(cases)==8
 rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']})
  if a.stage=='counters':v['counter_classification']=rules.COUNTER_CLASSIFIER(c,r,q,common.external_outcome(c,r))
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],counter=v.get('counter_classification',{}).get('invalidates_design'))),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0))
if __name__=='__main__':main()
