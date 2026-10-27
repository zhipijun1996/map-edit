import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives,critical
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','critical','screen','counters'],default='clean');a=p.parse_args();out=ROOT/'results'/a.name
 bases=[rules.candidate(i,w,0)for i in [0,1]for w in [75,96]];checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources(bases),counters=inspect_counter_bindings(bases,alternatives,18))
 if checks['scripts']['status']!='syntax_checked'or any(checks[k]['status']!='requires_physics'for k in ['blocks','counters']):write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py'];select=HERE/'control-selection-v1.json'
 if select.exists():deps.append(select)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);preflight(e,bases)
 if a.stage=='clean':cases=[rules.candidate(i,w,k)for i in [0,1]for w in [75,96]for k in [0,1]]
 elif a.stage=='critical':cases=[v for c in bases for v in critical(c)]
 else:
  choices=json.loads(select.read_text())['controls'];assert set(choices)=={'0','1'}
  chosen=[rules.candidate(int(i),v['width'],v['control'])for i,v in choices.items()]
  if a.stage=='screen':cases=[instantiate(c,271130122,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)]
  else:
   kinds=['omit-recoil','early-ledge-recoil--24','early-ledge-recoil--8','ground-preparation-extra-shot','late-fall-recoil-140','late-fall-recoil-175','bottom-paid-jump-shot','ordinary-jump-o-2-h20','ordinary-jump-o-2-h32','ordinary-jump-o8-h20']
   cases=[v for c in chosen for v in alternatives(c)if v['counterexample_kind']in kinds];assert len(cases)==20
 rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']})
  if a.stage in ['critical','counters']:
   o=common.external_outcome(c,r);v['counter_classification']=common.counter_classification(c,r,q,o)
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],margin=q['causal']['first_bag_body_horizontal_margin'],counter=v.get('counter_classification'))),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),stage=a.stage,new_candidates=0))
if __name__=='__main__':main()
