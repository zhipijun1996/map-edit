"""Record exact own frozen candidates via the shared strict native recorder."""
from pathlib import Path
import argparse,json,inspect
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent
RUNS={'clear':'workshop-creative-enemy-world-production-v2/round-00','displace':'workshop-creative-enemy-world-production-v6/round-00','attack':'workshop-creative-enemy-world-attack-relay-production-v7/round-00','lure':'workshop-creative-enemy-world-lure-sensor-production-v7/round-00'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('recipe',choices=RUNS);p.add_argument('--display',default=':106');a=p.parse_args()
 kwargs=dict(display=a.display)
 if a.recipe in ['attack','lure']:
  if 'scene'not in inspect.signature(record).parameters:raise RuntimeError('shared strict recorder scene support not yet available')
  kwargs['scene']=HERE/'main_v1.tscn'
 out=record(RUNS[a.recipe],'pcg/results/workshop-creative-enemy-world-videos-v1/'+a.recipe,**kwargs)
 print(json.dumps(dict(recipe=a.recipe,path=str(out.relative_to(ROOT.parent))),ensure_ascii=False))
