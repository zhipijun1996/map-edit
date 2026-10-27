"""Remaining28 preregistered countercases; firstfour are not repeated."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_blockn02_repair.alternatives_v1 import alternatives
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutablecounter')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json',HERE.parent/'batch30_blockn02_repair/alternatives_v1.py',Path(common.__file__)]
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);chosen=json.loads((HERE/'control-selection-v1.json').read_text())['controls'];assert set(chosen)=={'high','low'}
 high=[v for v in alternatives(rules.candidate(0,chosen['high'],'high'))if not v['counterexample_kind'].startswith(('static-P2-rightside-leftup-recoil','early-ordinary-jump-static-P2'))]
 low=alternatives(rules.candidate(0,chosen['low'],'low'))[:14];cases=high+low;assert len(cases)==28
 # Search cheapfloor route first; an actual refutation is stored regardless
 # of purposeword mismatch andcan stop a laterfullcall.
 cases.sort(key=lambda c:(not c['counterexample_kind'].startswith('internal-floor'),c['route_spec']['id'],c['counterexample_kind']))
 rows=[]
 for c,r,ev in e.run(cases,'remainingexactcounters'):
  q=common.checked_purpose(rules,c,r);o=common.external_outcome(c,r);classification=common.counter_classification(c,r,q,o)
  v=dict(case=c,purpose=q,evidence=ev,external_outcome=o,counter_classification=classification,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],outcome=o['ok'],purpose=q['ok'],invalidates=classification['invalidates_design'],reasons=q['reasons'],actual=v['actual'],final=v['final'],causal=q['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,total=len(rows),refutations=[v['case']['id']for v in rows if v['counter_classification']['invalidates_design']],new_candidates=0))

if __name__=='__main__':main()
