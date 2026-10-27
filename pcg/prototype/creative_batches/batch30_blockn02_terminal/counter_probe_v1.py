"""Four preregistered static-platform falsifiers before costly terminalsearch."""
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
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE.parent/'batch30_blockn02_repair/alternatives_v1.py',Path(common.__file__)]
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);base=rules.candidate(0,0,'high')
 cases=[v for v in alternatives(base)if v['counterexample_kind'].startswith(('static-P2-rightside-leftup-recoil','early-ordinary-jump-static-P2'))];assert len(cases)==4
 rows=[]
 for c,r,ev in e.run(cases,'firststaticP2counters'):
  q=common.checked_purpose(rules,c,r);o=common.external_outcome(c,r)
  samecost=r.get('shots',999)<=2 and r.get('jumps',999)<=3
  v=dict(case=c,purpose=q,evidence=ev,external_outcome=o,same_or_lower_action_cost=samecost,invalidates_activecatch=o['ok']and samecost and not q['causal'].get('outside_count')and not q['causal'].get('P2_toggles'),actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],outcome=o['ok'],samecost=samecost,invalidates=v['invalidates_activecatch'],reasons=q['reasons'],actual=v['actual'],final=v['final'],causal=q['causal'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,total=len(rows),staticP2_same_goal_refutations=[v['case']['id']for v in rows if v['invalidates_activecatch']],new_candidates=0))

if __name__=='__main__':main()
