"""Small real probes through original WorkshopEngine and upstream Block checks."""
import argparse,json,subprocess
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as shared
from . import rules_v1 as rules
HERE=Path(__file__).parent
EXPORTER=HERE.parent/'batch30_runtime/export_block_v1.mjs'

def preflight(engine,cases):
 unique={}
 for c in cases:unique.setdefault((c['layout_uid'],c['route_spec']['id']),c)
 selected=list(unique.values());q=inspect_sources(selected);write(engine.out/'map-block-preflight.json',q)
 if q['status']!='requires_physics':raise ValueError('upstream Block input rejected')
 static_preflight(engine,selected)
 result=subprocess.run(['node',str(EXPORTER),str(engine.out/'preflight-bundle.json'),str(engine.out/'block-preflight-documents')],cwd=ROOT.parent,capture_output=True,text=True)
 write(engine.out/'block-export-preflight.json',dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
 if result.returncode:raise ValueError('Block export rejected; evidence retained')

def compact(c,r,e):
 q=shared.checked_purpose(rules,c,r)
 return dict(case=c,purpose=q,evidence=e,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id','grounded','shot_charges']})

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','screen'],required=True);a=p.parse_args()
 out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable probe exists')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(shared.__file__),HERE.parent/'batch30_runtime/block_contract_v1.py',EXPORTER,HERE.parent/'batch30_runtime/export_v1.mjs']
 engine=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 selected_path=HERE/'control-selection-v1.json'
 if a.stage=='clean':cases=[rules.candidate(i,k)for i in [1,0]for k in [0,1]]
 else:
  selected=json.loads(selected_path.read_text())['controls'];bases=[rules.candidate(int(i),k)for i,k in selected.items()]
  cases=[instantiate(c,271128110,level,k)for c in bases for level in ['mild','moderate']for k in range(6)]
 preflight(engine,[rules.candidate(i,0)for i in [1,0]])
 write(out/'protocol.json',json.loads((HERE/'protocol-v1.json').read_text()));rows=[]
 for c,r,e in engine.run(cases,a.stage):
  row=compact(c,r,e);rows.append(row);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=row['purpose']['ok'],reasons=row['purpose']['reasons'],actual=row['actual'],causal=row['purpose']['causal'])),flush=True)
 if a.stage=='clean':
  choices={}
  for i in [1,0]:
   good=[r for r in rows if r['case']['interface']==i and r['purpose']['ok']]
   if good:choices[str(i)]=good[0]['case']['rule_parameters']['control']
  if selected_path.exists():raise ValueError('immutable selection exists')
  write(selected_path,dict(controls=choices,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=engine.sim.cases,passed=sum(r['purpose']['ok']for r in rows),total=len(rows),new_modules=0,stage=a.stage,full_or_held=False))

if __name__=='__main__':main()
