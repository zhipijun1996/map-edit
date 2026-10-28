import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();cs=[rules.candidate(k,'loop')for k in range(4)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'loop-clean'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,margin=rules.margin(c,r),result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,loop_fixture_not_standard_module_route=True))
 valid=sorted([r for r in rows if r['purpose']['ok']and r['margin']['eligible']],key=lambda r:(-r['margin']['score'],int(r['id'][-1])))
 choice=HERE/'control-selection-v1.json'
 if choice.exists():raise ValueError('immutable controlselection')
 write(choice,dict(schema='pcg/N08-control-selection/v1',source_run=str(e.out.relative_to(ROOT.parent)),chosen_control=int(valid[0]['id'][-1])if valid else None,ranking=[dict(id=r['id'],margin=r['margin'])for r in valid],selected_before_noise_counters_full_held=True,previous_failed_cases=4,new_clean_cases=4,new_modules=0))
if __name__=='__main__':main()
