"""LOS-corrected stationary native charger. Explicit custom resource SHA."""
from pathlib import Path
import json,hashlib
from pcg.prototype.creative_batches.enemy_world.probe_v6 import cases as previous
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
HERE=Path(__file__).parent
SHA='e91ce88ad2a803cfb0b9b3ee7ad824b39c918078c67be9bb90f9854d38ad2d1f'
def cases():
 out=previous()
 sha=hashlib.sha256((HERE/'guard_charger_v1.tres').read_bytes()).hexdigest()
 for c in out:
  c['id']=c['id'].replace('ew-lure-guard','ew-lure-guard-v7');c['platforms'][0][2]=312
  c['enemies'][0]['position'][0]=250;c['enemies'][0]['variant_tres_sha256']=sha
  c['latches'][0]['occupancy']['rect'][0]=132;c['latches'][0]['bell'][0]=144
 return out
if __name__=='__main__':
 sources=[Path(__file__),HERE/'probe_v6.py',HERE/'occupancy_runner_v2.gd']+list((HERE.parent/'occupancy').glob('*v1.gd'))+[HERE.parent/'occupancy/main_v1.tscn']
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v7',extra_sources=sources,runner_script=HERE/'occupancy_runner_v2.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['ok'],r['reason'],r.get('hp'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']),f['plains']['enemies'])for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
