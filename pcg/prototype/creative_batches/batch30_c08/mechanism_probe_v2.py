import argparse,json
from pathlib import Path
from . import mechanism_probe_v1 as prior
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
DEPENDENCIES=prior.DEPENDENCIES+[Path(prior.__file__),HERE/'mechanism-protocol-v2.json',HERE.parent/'enemy_world/probe_v9.py']
def cases():
 out=prior.cases()
 for c in out:c['id']+='-floor420';c['enemies'][0]['position'][1]=420
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+DEPENDENCIES,runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(cases(),'charger-aligned-floor-gate-space'):
  fs=r.get('frames',[]);actors=[f['plains']['enemies'][0]for f in fs if f.get('plains',{}).get('enemies')];pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0]
  row=dict(id=c['id'],test=c['mechanism_test'],ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),enemy_x_range=[min((v['x']for v in actors),default=None),max((v['x']for v in actors),default=None)],enemy_final=r.get('plains',{}).get('enemies'),pair=pair,actual_attack_positions=[dict(frame=f['frame'],x=f['plains']['enemies'][0]['x'],state=f['plains']['enemies'][0]['state'])for f in fs if f.get('plains',{}).get('enemies')and f['plains']['enemies'][0]['state']=='attack'][::3],evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'mechanism-results.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
