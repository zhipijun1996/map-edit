"""Original evaluate/quality selection; screen stores no duplicate raw frames."""
import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate,evaluate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);protocol=json.loads((HERE/'protocol-v2.json').read_text());rows=[]
 cases=[instantiate(rules.fixture(i,k),protocol['calibration_seed'],l,t)for i in [1]for k in range(4)for l in ['clean','mild','moderate']for t in range(1 if l=='clean'else 6)]
 for c,r,b in e.run(cases,'support-confirmed-recovery-screen'):
  q=rules.purpose(c,r);rows.append(dict(id=c['id'],interface=c['interface'],control=c['validation_fixture']['control'],level=c['id'].split('-')[-2],trial=int(c['id'].split('-')[-1]),purpose=q,evidence=b,ticks=r.get('ticks'),last={k:r['frames'][-1].get(k)for k in ['frame','x','y','support_id']}if r.get('frames')else{}));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],supports=q['causal']['actual_support_sequence'])),flush=True)
 write(e.out/'screen.json',dict(actual_cases=e.sim.cases,rows=rows,raw_frames='original engine gzip only'))
 retained=[];stats=[]
 for i in [1]:
  for k in range(4):
   group=[r for r in rows if r['interface']==i and r['control']==k];rates={l:sum(r['purpose']['ok']for r in group if r['level']==l)/(1 if l=='clean'else 6)for l in ['clean','mild','moderate']};keep=rates['clean']==1 and rates['mild']>=5/6 and rates['moderate']>=4/6;stats.append(dict(interface=i,control=k,rates=rates,retained=keep))
   if keep:retained.append(rules.fixture(i,k))
 write(e.out/'selection-domain.json',dict(stats=stats,retained=[c['id']for c in retained]));cal=evaluate(e,retained,protocol['calibration_seed'],12,'support-confirmed-calibration',rules.purpose)if retained else[];selected=[]
 for i in [1]:
  eligible=[v for v in cal if v['case']['interface']==i and v['quality_gate']['status']=='awaiting_human_review'];eligible.sort(key=lambda v:(min(v['stats']['mild']['rate'],v['stats']['moderate']['rate']),(v['stats']['mild']['rate']+v['stats']['moderate']['rate'])/2,-v['case']['validation_fixture']['control']),reverse=True)
  if eligible:selected.append(eligible[0]['case'])
 write(e.out/'frozen-selection.json',dict(selected=selected,selection_before_holdout=True,actual_cases_before_holdout=e.sim.cases));held=evaluate(e,selected,protocol['holdout_seed'],12,'support-confirmed-independent-holdout',rules.purpose)if selected else[]
 write(e.out/'receipt-v2.json',dict(schema='pcg/c02-same-world-recovery-validation/v2',actual_cases=e.sim.cases,maximum_cases=protocol['maximum_actual_cases'],screen_stats=stats,calibration=cal,holdout=held,selected=[c['id']for c in selected],qualified_interfaces=[v['case']['interface']for v in held if v['quality_gate']['status']=='awaiting_human_review'],new_modules=0,production_admitted=False));assert e.sim.cases<=protocol['maximum_actual_cases']
if __name__=='__main__':main()
