"""Move on the retained real step before jumping back inside owned space."""
import argparse,json
from pathlib import Path
from . import recovery_v1 as old
from . import api_v1 as api
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def candidate(control=0):
 c=old.candidate();lip=[775,780][control];c['id']+=f'-leftlip-{lip}'
 c['control_plan'][-4:]=[settle(lip),ground(),cmd('wait',8),cmd('axis',value=-1),*c['control_plan'][-4:]]
 c['validation_fixture'].update(recovery_control=control,actual_leftlip_target=lip,source_world_unchanged=True)
 return c

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutablerecovery')
 deps=[Path(__file__),Path(old.__file__),HERE/'recovery-protocol-v1.json',HERE/'recovery-protocol-v2.json',Path(api.__file__),*api.SOURCE_DEPENDENCIES,HERE.parent/'batch30_c07/recovery_v1.py',HERE.parent/'batch30_c07/counter_v3.py']
 e=WorkshopEngine(out,extra_sources=deps,runner_script=api.RUNNER_SCRIPT);rows=[];selected=[]
 def save(c,r,ev):
  q=old.purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],causal=q['causal'])),flush=True);return q['ok']
 for c,r,ev in e.run([candidate(k)for k in range(2)],'leftlipclean'):
  if save(c,r,ev)and not selected:selected.append(c)
 write(out/'selection-before-perturb.json',dict(ids=[c['id']for c in selected],holdout_used=False))
 if selected:
  for c,r,ev in e.run([instantiate(selected[0],271128509,l,k)for l in ['mild','moderate']for k in range(3)],'leftlipperturb'):save(c,r,ev)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),selected_ids=[c['id']for c in selected],new_candidates=0,quality='small_exact_fixture_not_regular_or_held'))

if __name__=='__main__':main()
