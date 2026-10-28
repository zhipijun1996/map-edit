"""Actual Godot complementary-cell probes. No candidate admission."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,wait_x
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/n for n in ['pair_latch_v1.gd','runtime_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn','protocol-v1.json']]

def common(label,initial='A'):
 c=base('pair-cell-'+label);c['family']='pair-cell-probe';c['platforms']=[[-250,438,1600,100]];c['spawn']=[80,420];c['entry_port']=[80,420];c['exit_port']=[80,420];c['goal']=[55,416,50,8];c['max_frames']=450;c['trace_all']=False
 c['latches']=[dict(id='pair',bell=[180,350],gate=[450,250,24,188],paired_gate=[850,250,24,188],initial_open=initial,open_seconds=0)]
 return c

def cases():
 out=[]
 for initial in ['A','B']:
  c=common('initial-'+initial,initial);c['control_plan']=[cmd('wait',30),settle(80)];c['probe_kind']='initial';out.append(c)
  c=common('twice-'+initial,initial);c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',45),cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',30),settle(80)];c['probe_kind']='twice';out.append(c)
 c=common('blocked-then-clear');c['latches'][0].update(bell=[480,350],gate=[400,250,180,188]);c['spawn']=[480,420];c['entry_port']=[480,420];c['exit_port']=[650,420];c['goal']=[625,416,50,8];c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',30),cmd('axis',value=1),wait_x(650),cmd('axis',value=0),cmd('wait',12),cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',30),settle(650)];c['probe_kind']='blocked-then-clear';out.append(c)
 c=common('airborne');c['spawn']=[220,420];c['entry_port']=[220,420];c['latches'][0]['bell']=[130,400];c['exit_port']=[650,420];c['goal']=[625,416,50,8];c['control_plan']=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',10,aim_cell=dict(kind='bell',id='pair')),settle(650)];c['probe_kind']='airborne';out.append(c)
 return out

def check(c,r):
 states=[p for f in r.get('frames',[])for p in f.get('workshop',{}).get('paired_gates',[])];final=r.get('workshop',{}).get('paired_gates',[{}])[0];reasons=[]
 if not r.get('ok'):reasons.append(r.get('reason'))
 if not states:reasons.append('no-paired-state')
 for p in states:
  if p['open_a']==p['open_b'] or p['gate_a_disabled']!=p['open_a'] or p['gate_b_disabled']!=p['open_b'] or p['gate_a_layer']!=(0 if p['open_a']else 1) or p['gate_b_layer']!=(0 if p['open_b']else 1):reasons.append('actual-collision-invariant');break
 kind=c['probe_kind'];expected={'initial':0,'twice':2,'blocked-then-clear':1,'airborne':1}[kind]
 if final.get('switch_count')!=expected:reasons.append('wrong-switch-count')
 if kind=='blocked-then-clear'and final.get('blocked_count')!=1:reasons.append('wrong-blocked-count')
 if kind=='twice'and final.get('open_a')!=(c['latches'][0]['initial_open']=='A'):reasons.append('did-not-restore')
 if kind=='airborne'and not any(e.get('type')=='pair_switch'and e.get('airborne')for e in final.get('events',[])):reasons.append('not-original-air-shot')
 return dict(ok=not reasons,reasons=reasons,frames_checked=len(states),final=final)

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+SOURCE_DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,b in e.run(cases(),'cell-probe'):
  q=check(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows))
if __name__=='__main__':main()
