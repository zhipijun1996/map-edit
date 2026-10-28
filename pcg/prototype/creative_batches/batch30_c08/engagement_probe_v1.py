import argparse,json
from pathlib import Path
from . import mechanism_probe_v2 as prior
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def cases():
 out=[]
 for c in prior.cases():
  if c['mechanism_test']['label']not in ['released','released-close-36','released-close-48']:continue
  c['id']+='-entry140';c['spawn']=[140,420];c['entry_port']=[140,420];c['exit_port']=[160,420];c['goal']=[115,416,50,8]
  for q in c['control_plan']:
   if q['op']=='settle':q['target_x']=140
  out.append(c)
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(prior.__file__),HERE/'engagement-protocol-v1.json']+prior.DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(cases(),'charger-real-home-range-engagement'):
  fs=r.get('frames',[]);pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0];attack=[dict(frame=f['frame'],x=f['plains']['enemies'][0]['x'])for f in fs if f.get('plains',{}).get('enemies')and f['plains']['enemies'][0]['state']=='attack']
  row=dict(id=c['id'],ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),pair=pair,actual_attack_positions=attack,enemy_final=r.get('plains',{}).get('enemies'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'mechanism-results.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
