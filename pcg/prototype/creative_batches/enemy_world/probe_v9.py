"""Original charger floor-ray requires authored y420 on floor438 (18-unit foot probe)."""
from pathlib import Path
import json
from pcg.prototype.creative_batches.enemy_world.probe_v7 import cases as previous
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
HERE=Path(__file__).parent

def cases():
 out=previous()
 for c in out:c['id']=c['id'].replace('-v7-','-v9-');c['enemies'][0]['position'][1]=420
 return out
if __name__=='__main__':
 sources=[Path(__file__),HERE/'probe_v7.py',HERE/'probe_v6.py',HERE/'occupancy_runner_v2.gd']+list((HERE.parent/'occupancy').glob('*v1.gd'))+[HERE.parent/'occupancy/main_v1.tscn']
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v9',extra_sources=sources,runner_script=HERE/'occupancy_runner_v2.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['ok'],r['reason'],r.get('hp'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']),f['plains']['enemies'])for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
