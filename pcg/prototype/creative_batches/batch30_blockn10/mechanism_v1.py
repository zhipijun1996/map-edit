"""Three actual short-range original receiver collision/lifecycle controls."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
HERE=Path(__file__).parent
def candidate(k):
 c=base('N10-receiver-control-'+str(k));c['capabilities']=['move','jump','shot_recoil'];c['platforms']=[[480,618,240,64]];c['spawn']=[600,600];c['entry_port']=[600,600];c['exit_port']=[600,600]
 c['latches']=[dict(id='near',bell=[600,480],gate=[900,128,16,600],open_seconds=1.8),dict(id='far',bell=[600,440],gate=[1000,128,16,600],open_seconds=0)]
 aim=dict(kind='bell',id='far');p=[cmd('shoot',aim_cell=aim),ground(),cmd('wait',20)]
 if k==1:p +=[cmd('shoot',aim_cell=aim),ground(),cmd('wait',20)]
 if k==2:p +=[cmd('wait',130),cmd('shoot',aim_cell=aim),ground(),cmd('wait',20)]
 c.update(control_plan=p,goal=[593,596,14,8],max_frames=220,trace_all=True,control=k)
 return c
def purpose(c,r):
 fs=r.get('frames',[]);k=c['control'];n=[next(v for v in f.get('n10',[])if v['id']=='near')for f in fs];far=next(v for v in r['n10']if v['id']=='far');near=next(v for v in r['n10']if v['id']=='near');events=[e for e in r['plains']['events']if e['type']=='bell_open'];why=[]
 if not r.get('ok')or r.get('hp')!=5 or r.get('returns'):why.append('actual_stable_safe_original_resource_control_failed')
 if not any(v['open']and v['bell_layer']==0 and v['gate_layer']==0 and v['gate_disabled']for v in n):why.append('actual_near_layer0_release_missing')
 expect_far=1 if k==1 else 0;expect_near=2 if k==2 else 1
 if far['count']!=expect_far or near['count']!=expect_near:why.append('actual_projectile_target_order_failed')
 if k==2:
  closed=[f['frame']for f,v in zip(fs,n)if f['frame']>20 and not v['open']and v['bell_layer']==8 and v['gate_layer']==1 and not v['gate_disabled']]
  if not closed:why.append('actual_near_layer8_restore_missing')
 else:closed=[]
 return dict(ok=not why,reasons=why,actual_events=events,actual_final=r['n10'],near_restored_frames=closed,actual_shots=r.get('shots'),projectile_impacts=[e for e in r['plains']['events']if e['type']=='projectile_impact'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 checks=check([HERE/'runner_v1.gd'])
 if checks['status']!='syntax_checked':write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'runner_v1.gd',HERE/'observe_v1.gd',HERE/'protocol-v1.json',HERE/'idea-source-v1.json'],runner_script=HERE/'runner_v1.gd');write(out/'preflight.json',checks);rows=[]
 for c,r,ev in e.run([candidate(k)for k in [0,1,2]],'receiver-controls'):
  q=purpose(c,r);rows.append(dict(case=c,purpose=q,evidence=ev));write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],purpose=q)),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0))
if __name__=='__main__':main()
