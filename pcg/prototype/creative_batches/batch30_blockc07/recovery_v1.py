import argparse,json
from pathlib import Path
from . import api_v1 as api
from pcg.prototype.creative_batches.batch30_c07.recovery_v1 import purpose as original
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.map_directed.block_grid.contracts import raster
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def candidate():
 c=api.layouts(api.RECIPES[0],0)[0];source=c['control_plan'];c['id']+='-firstmiss-recovery';c['max_frames']=2300
 c['control_plan']=source[:7]+[cmd('shoot',direction=[1,0]),cmd('axis',value=0,after=6),cmd('wait',75),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(700),cmd('jump'),cmd('jump_release',32),settle(760),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),cmd('wait',8),settle(820),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[0,1]),settle(744,8)]
 c['validation_fixture']=dict(kind='first_miss_floor_rightstep_exit_same_world',no_module_enrollment=True,canonical_world_state_not_claimed=True)
 return c

def purpose(c,r):
 q=original(c,r);owned=set(map(tuple,c['block_grid']['cells']));outside=[dict(frame=f['frame'],body=[f['x']-12,f['y']-18,24,36],cells=sorted(map(list,raster([f['x']-12,f['y']-18,24,36])-owned)))for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:q['reasons'].append('actual_complete_body_outside_frozen_block_ownership')
 q['causal'].update(outside_body_frames=outside[:16],outside_count=len(outside));q['ok']=not q['reasons'];return q

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable recovery')
 deps=[Path(__file__),HERE/'recovery-protocol-v1.json',Path(api.__file__),*api.SOURCE_DEPENDENCIES,HERE.parent/'batch30_c07/recovery_v1.py',HERE.parent/'batch30_c07/counter_v3.py']
 engine=WorkshopEngine(out,extra_sources=deps,runner_script=api.RUNNER_SCRIPT);rows=[];base=candidate();good=False
 def save(c,r,e):
  q=purpose(c,r);v=dict(case=c,purpose=q,evidence=e,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],causal=q['causal'])),flush=True);return q['ok']
 for c,r,e in engine.run([base],'exactclean'):good=save(c,r,e)
 if good:
  for c,r,e in engine.run([instantiate(base,271128508,l,k)for l,n in [('mild',5),('moderate',6)]for k in range(n)],'recoveryperturb'):save(c,r,e)
 write(out/'summary.json',dict(actual_cases=engine.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),clean_passed=good,status='limited_exact_fixture'if good else'needs_design',new_candidates=0,third_rule_allowed=False))

if __name__=='__main__':main()
