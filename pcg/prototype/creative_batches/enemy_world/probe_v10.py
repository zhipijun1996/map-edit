"""Attack-relay robust gate timing and non-jumpable upper rock mass."""
from pathlib import Path
import json
from pcg.prototype.creative_batches.enemy_world.probe_v8 import cases as previous
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
HERE=Path(__file__).parent

def cases():
 out=previous()
 for c in out:
  c['id']=c['id'].replace('ew-attack-relay','ew-attack-relay-v10');c['platforms'][2]=[300,80,440,316];c['latches'][0]['open_seconds']=1.0;c['latches'][0]['bell']=[280,370]
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v10',extra_sources=[Path(__file__),HERE/'probe_v8.py',HERE/'runner_v1.gd',HERE/'attack_relay_v1.gd',HERE/'attack_runner_v1.gd'],runner_script=HERE/'attack_runner_v1.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['ok'],r['reason'],r.get('hp'),r.get('plains',{}).get('events'),r.get('enemy_world'),flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
