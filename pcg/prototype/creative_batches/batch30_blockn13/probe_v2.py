import argparse,json,subprocess
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean'],default='clean');a=p.parse_args();out=ROOT/'results'/a.name
 bases=[rules.candidate(0,0)];checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources(bases))
 if checks['scripts']['status']!='syntax_checked'or checks['blocks']['status']!='requires_physics':write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);static_preflight(e,bases)
 js=subprocess.run(['node',str(rules.EXPORT_SCRIPT),str(out/'preflight-bundle.json'),str(out/'block-preflight-documents')],cwd=ROOT.parent,capture_output=True,text=True);write(out/'export-preflight.json',dict(returncode=js.returncode,stderr=js.stderr,stdout=js.stdout))
 if js.returncode:raise ValueError('isolatedoriginalDock/Blockexportpreflightfailed')
 rows=[]
 for c,r,ev in e.run([rules.candidate(0,k)for k in range(4)],'clean'):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],causal=q['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0))
if __name__=='__main__':main()
