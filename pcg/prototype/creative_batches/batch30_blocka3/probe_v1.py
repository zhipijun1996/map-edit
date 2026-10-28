"""Boundedoriginal Godot probes, parser/contract checks before actualphysics."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives,preliminary
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check as check_scripts
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_sources,inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['static','clean','screen','counters'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutableA3run')
 bases=[rules.candidate(i,0,s)for i in [0,1]for s in ['outbound','return']]
 scripts=check_scripts([rules.RUNNER_SCRIPT,HERE/'main_v1.gd'])
 checks=dict(source=inspect_sources(bases),counters=inspect_counter_bindings(bases,alternatives,18))
 if scripts['status']!='syntax_checked'or any(v['status']!='requires_physics'for v in checks.values()):
  write(out/'godot-check-only.json',scripts);write(out/'block-binding-preflight.json',checks)
  write(out/'summary.json',dict(status='needs_design',actual_cases=0,new_candidates=0));return
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE.parent/'batch30_blockbridge/probe_v2.py',Path(common.__file__)]
 select=HERE/'control-selection-v1.json'
 if select.exists():deps.append(select)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 write(out/'godot-check-only.json',scripts);write(out/'block-binding-preflight.json',checks);preflight(e,bases)
 if a.stage=='static':write(out/'summary.json',dict(status='ready_for_realphysics',actual_cases=0,new_candidates=0));return
 if a.stage=='clean':cases=[rules.candidate(i,k,'outbound')for i in [0,1]for k in range(2)]+[rules.candidate(i,k,'return')for i in [0,1]for k in range(3)]
 else:
  controls=json.loads(select.read_text())['controls'];assert len(controls)==4,'allfourorderedroutesrequired'
  chosen=[rules.candidate(int(key.split('/')[0]),control,key.split('/')[1])for key,control in controls.items()]
  if a.stage=='screen':cases=[instantiate(c,271129513,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)]
  else:cases=[v for c in chosen for v in preliminary(c)]
 rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']},coins=r.get('workshop',{}).get('coins'))
  if a.stage=='counters':o=common.external_outcome(c,r);v.update(external_outcome=o,counter_classification=common.counter_classification(c,r,q,o))
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'],coins=v['coins'],counter=v.get('counter_classification'),door=q['causal']['door'])),flush=True)
 if a.stage=='clean':
  selected={}
  for i in [0,1]:
   for route in ['outbound','return']:
    good=[v for v in rows if v['case']['interface']==i and v['case']['route_spec']['id']==route and v['purpose']['ok']]
    if good:selected[f'{i}/{route}']=good[0]['case']['rule_parameters']['control']
  if select.exists():raise ValueError('immutableselection')
  write(select,dict(controls=selected,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),stage=a.stage,new_candidates=0,full_or_held=False))

if __name__=='__main__':main()
