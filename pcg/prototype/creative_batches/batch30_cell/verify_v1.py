"""Actual passage/perturbation probes and separately labelled fault injection."""
import argparse,copy,json
from pathlib import Path
from . import probe_v1 as old,probe_v2 as fixed
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.workshop.evaluate import evaluate
HERE=Path(__file__).parent

def passage_cases():
 out=[]
 for which in ['A','B']:
  for shoot in [False,True]:
   c=old.common(f'pass-{which}-'+str(shoot),initial='B' if which=='A'else'A');x=80 if which=='A'else 900;end=650 if which=='A'else 1150
   c.update(spawn=[x,420],entry_port=[x,420],exit_port=[end,420],goal=[end-25,416,50,8],max_frames=260)
   c['latches'][0]['bell']=[x+80,350]
   c['control_plan']=([cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',20)]if shoot else[])+[settle(end)]
   c['expect_passage']=shoot;c['expect_switches']=int(shoot);out.append(c)
 return out

def check_passage(c,r):
 ps=r.get('workshop',{}).get('paired_gates',[{}])[0];fs=[p for f in r.get('frames',[])for p in f.get('workshop',{}).get('paired_gates',[])];bad=[p for p in fs if p['open_a']==p['open_b']or p['gate_a_layer']==p['gate_b_layer']or p['gate_a_disabled']==p['gate_b_disabled']]
 ok=bool(r.get('ok'))==c['expect_passage']and ps.get('switch_count')==c['expect_switches']and not bad and r.get('hp')==5
 return dict(ok=ok,reasons=[]if ok else['actual-passage-mismatch'],expected_arrival=c['expect_passage'],actual_arrival=r.get('ok'),actual_reason=r.get('reason'),final=ps,frames_checked=len(fs))

def fault_cases():
 out=[]
 for mode in ['duplicate-delivery','cancel-pending','cancel-before-hit','stale-target-epoch']:
  c=fixed.cases()[0];c['id']='pair-cell-fault-'+mode;c['cell_fault']=mode;c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',30),settle(120)];out.append(c)
 return out

def check_fault(c,r):
 p=r.get('workshop',{}).get('paired_gates',[{}])[0];events=[e for e in p.get('events',[])if e['type']=='fault_probe'];mode=c['cell_fault'];expected=0 if mode in ['cancel-pending','cancel-before-hit']else 1
 ok=bool(r.get('ok'))and len(events)==1 and p.get('switch_count')==expected
 if events:
  e=events[0]
  if mode=='duplicate-delivery':ok=ok and e['first_accepted']and not e['duplicate_accepted']
  elif mode=='stale-target-epoch':ok=ok and not e['stale_accepted']and e['accepted']
  elif mode=='cancel-before-hit':ok=ok and not e['accepted']
  elif mode=='cancel-pending':ok=ok and e['first_accepted']
 return dict(ok=ok,reasons=[]if ok else['fault-injection-mismatch'],expected_switches=expected,events=events,final=p)

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--fault',action='store_true');a=p.parse_args();runner=HERE/('fault_runner_v1.gd'if a.fault else'runner_v1.gd');sources=[Path(__file__),Path(old.__file__),Path(fixed.__file__)]+old.SOURCE_DEPENDENCIES
 if a.fault:sources.append(runner)
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=sources,runner_script=runner);rows=[]
 for c,r,b in e.run(fault_cases()if a.fault else passage_cases(),'fault-injection'if a.fault else'actual-passage'):
  check=(check_fault if a.fault else check_passage)(c,r);rows.append(dict(case=c,result=r,check=check,evidence=b));print(json.dumps(dict(id=c['id'],check=check)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),fault_injection=a.fault,rows=rows))
 if not a.fault:
  cs=[c for c in fixed.cases()if c['probe_kind']=='twice'];entries=evaluate(e,cs,261027101,12,'cell-perturbation',purpose_fn=old.check)
  write(e.out/'perturbation-summary.json',dict(actual_cases=e.sim.cases,entries=entries,quality_scope='Original regular gate on Cell toggling, not Module admission',production_admitted=False))
if __name__=='__main__':main()
