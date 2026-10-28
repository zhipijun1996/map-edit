import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','screen'],default='clean');a=p.parse_args();out=ROOT/'results'/a.name
 bases=[rules.candidate(t,0)for t in ['B','C']];checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources(bases),counters=inspect_counter_bindings(bases,alternatives,18))
 if checks['scripts']['status']!='syntax_checked'or any(checks[k]['status']!='requires_physics'for k in ['blocks','counters']):write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py'];selection=HERE/'control-selection-v1.json'
 if selection.exists():deps.append(selection)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);preflight(e,bases)
 if a.stage=='clean':cases=[rules.candidate(t,k)for t in ['B','C']for k in [0,1]]
 else:
  controls=json.loads(selection.read_text())['controls'];assert set(controls)=={'B','C'},'bothroutesrequired'
  cases=[instantiate(rules.candidate(t,k),271129714,level,j)for t,k in controls.items()for level in ['mild','moderate']for j in range(6)]
 rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},support_margin=rules.support_margin(c,r));rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],margin=v['support_margin'])),flush=True)
 if a.stage=='clean':
  controls={};ranking={}
  for t in ['B','C']:
   valid=[v for v in rows if v['case']['route_spec']['to_port']==t and v['purpose']['ok']and v['support_margin']['eligible']]
   ranked=sorted(valid,key=lambda v:(-v['support_margin']['score'],v['case']['rule_parameters']['control']));ranking[t]=[dict(control=v['case']['rule_parameters']['control'],margin=v['support_margin'])for v in ranked]
   if ranked:controls[t]=ranked[0]['case']['rule_parameters']['control']
  if selection.exists():raise ValueError('immutablemarginselection')
  write(selection,dict(controls=controls,ranking=ranking,registered_formula='protocol-v1.json',before_noise=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),stage=a.stage,parent_cases=52,lineage_cases_before_this_run=52 if a.stage=='clean'else 56,new_candidates=0))
if __name__=='__main__':main()
