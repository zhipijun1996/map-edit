"""New-process exact private CandidateLibrary retrieval, no new physics."""
from pathlib import Path
from pcg.prototype.creative_batches.enemy_world.production_v2 import compiler as clear
from pcg.prototype.creative_batches.enemy_world.production_v6 import compiler as displace
from pcg.prototype.creative_batches.enemy_world.production_v7 import compiler as world
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT

def compiler(request):
 return {'clear-sightline':clear,'displace-landing':displace}.get(request.get('recipe'),world)(request)
if __name__=='__main__':
 run('workshop-creative-enemy-world-reuse-v1',requests=[dict(recipe=r,interfaces=[0])for r in ['clear-sightline','displace-landing','attack-relay','lure-sensor']],cycles=4,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,source_file=Path(__file__))
