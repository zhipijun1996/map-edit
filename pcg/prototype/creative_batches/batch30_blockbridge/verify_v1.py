"""Fixed exact-world counter/recovery probes; original Engine and input policy."""
import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_c01 import api_v1 as source_api
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent

def same_goal(c,r):return bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and r.get('workshop',{}).get('coins',0)>=12

def selected_counters(c):
 all=source_api.alternatives(c);basic=[v for v in all if v['counterexample_kind'].startswith(('omit-shot-','ordinary-long-jump-'))];shore=[v for v in all if v['counterexample_kind'].startswith('shore-flip-active-')];extra=[v for v in all if v['counterexample_kind']=='extra-air-shot-skip-landing']
 result=basic+[shore[i]for i in [0,5,13,21,26]]+extra
 assert len(result)==12
 return result

def row(c,r,e,q):
 return dict(case=c,purpose=q,evidence=e,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id','shot_charges']})

def recovery_purpose(c,r):
 q=rules.recovery_purpose(c,r);states=r.get('workshop',{}).get('paired_gates',[]);switches=[e for p in states for e in p.get('events',[])if e.get('type')=='pair_switch'];restore=next((e for e in switches if e.get('open')=='B'),None)
 if restore:
  tail=dict(r);tail['frames']=[f for f in r['frames']if f['frame']>restore['frame']];tail['workshop']=copy.deepcopy(r['workshop'])
  for p in tail['workshop'].get('paired_gates',[]):p['events']=[e for e in p.get('events',[])if e.get('frame',-1)>restore['frame']]
  retry=rules.old.parent_rules.purpose(c,tail);q['causal']['retry_core']=retry
  if not retry['ok']:q['reasons'].append('retry_support_swap_core_not_demonstrated')
 else:q['reasons'].append('missing_actual_original_state_restore')
 q['ok']=not q['reasons'];return q

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['counters','recovery-clean','recovery-noise'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable verification run exists')
 selection=HERE/'recovery-selection-v1.json';deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(common.__file__)]
 if selection.exists():deps.append(selection)
 engine=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 if a.stage=='counters':cases=[v for i in [1,0]for v in selected_counters(rules.candidate(i,0))]
 elif a.stage=='recovery-clean':cases=[rules.recovery(i,k)for i in [1,0]for k in range(4)]
 else:
  chosen=json.loads(selection.read_text())['controls'];cases=[instantiate(rules.recovery(int(i),k),271128111,level,j)for i,k in chosen.items()for level in ['mild','moderate']for j in range(4)]
 write(out/'protocol.json',json.loads((HERE/'protocol-v2.json').read_text()));rows=[]
 for c,r,e in engine.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r)if a.stage=='counters'else recovery_purpose(c,r);v=row(c,r,e,q)
  if a.stage=='counters':v.update(same_external_goal=same_goal(c,r),invalidates_design=same_goal(c,r)and not q['ok'])
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],same_goal=v.get('same_external_goal'),invalidates=v.get('invalidates_design'),actual=v['actual'],causal=q['causal'])),flush=True)
 if a.stage=='recovery-clean':
  controls={}
  for i in [1,0]:
   good=[r for r in rows if r['case']['interface']==i and r['purpose']['ok']]
   if good:controls[str(i)]=good[0]['case']['validation_fixture']['control']
  if selection.exists():raise ValueError('immutable recovery selection exists')
  write(selection,dict(controls=controls,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=engine.sim.cases,passed=sum(r['purpose']['ok']for r in rows),total=len(rows),counter_refutations=sum(r.get('invalidates_design',False)for r in rows),new_modules=0,stage=a.stage,full_or_held=False))

if __name__=='__main__':main()
