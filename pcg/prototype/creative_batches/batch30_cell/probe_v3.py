"""Last five Cell regressions for close-first hardening; no other new behavior."""
import argparse,json
from pathlib import Path
from . import probe_v1 as old,probe_v2 as fixed,probe_enemy_v2 as enemy,verify_v1 as checks,regression_v2 as regression
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn','protocol-v1.json']]

def cases():
 out=[c for c in fixed.cases()if c['probe_kind']in ['twice','blocked-then-clear']]
 out+=[c for c in enemy.cases()if 'body-edge'in c['id']]
 out+=[c for c in regression.cases()if c['id'].startswith('pair-cell-pass-B-True')]
 for c in out:c['id']+='-v3'
 assert len(out)==5
 return out

def check(c,r):
 if'expect_passage'in c:return checks.check_passage(c,r)
 if not'expect_enemy_block'in c:return old.check(c,r)
 ps=r.get('workshop',{}).get('paired_gates',[{}])[0];es=r.get('plains',{}).get('enemies',[]);reasons=[]
 if not r.get('ok')or ps.get('blocked_count')!=1 or ps.get('switch_count')!=0:reasons.append('wrong-enemy-guard-outcome')
 if not es or es[0].get('hp')!=3 or es[0].get('dead'):reasons.append('enemy-harmed')
 blockers=[b for event in ps.get('events',[])if event['type']=='pair_switch_blocked'for b in event.get('blockers',[])if b['kind']=='enemy']
 if not blockers or not all(b['position'][0]>474 for b in blockers):reasons.append('full-body-edge-overlap-not-demonstrated')
 if any(p['open_a']==p['open_b']or p['gate_a_layer']==p['gate_b_layer']or p['gate_a_disabled']==p['gate_b_disabled']for f in r.get('frames',[])for p in f.get('workshop',{}).get('paired_gates',[])):reasons.append('frame-complementarity-lost')
 return dict(ok=not reasons,reasons=reasons,final=ps,enemy=es)

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(old.__file__),Path(fixed.__file__),Path(enemy.__file__),Path(checks.__file__),Path(regression.__file__)]+SOURCE_DEPENDENCIES,runner_script=HERE/'runner_v3.gd');rows=[]
 for c,r,b in e.run(cases(),'close-first-regression'):
  q=check(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows))
if __name__=='__main__':main()
