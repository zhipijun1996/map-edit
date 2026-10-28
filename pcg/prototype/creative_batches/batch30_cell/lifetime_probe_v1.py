import argparse,json
from pathlib import Path
from . import probe_v2 as source,probe_enemy_v2 as deps
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,settle
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();c=source.cases()[0];c['id']='pair-cell-lifetime-actor-invalidation';c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',20),settle(120)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'lifetime_fault_v1.gd']+deps.SOURCES,runner_script=HERE/'lifetime_fault_v1.gd');rows=[]
 for c,r,b in e.run([c],'lifetime-fault-injection'):
  ps=r.get('workshop',{}).get('paired_gates',[{}])[0];events=[v for v in ps.get('events',[])if v['type']=='fault_probe'];ok=bool(r.get('ok'))and ps.get('switch_count')==0 and len(events)==1 and events[0]['first_accepted']and events[0]['new_actor_epoch']==2
  row=dict(case=c,result=r,check=dict(ok=ok,events=events,actual_switch_count=ps.get('switch_count')),evidence=b);rows.append(row);print(json.dumps(row['check']),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),fault_injection=True,rows=rows))
