"""Four frozen grapple relationship movies using original exact recorder checks."""
import json,traceback
from pathlib import Path
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
HERE=Path(__file__).parent
PLANS=[('anchor-gap',1,0),('bounce-brake',5,1),('jump-refill',7,0),('hazard-window',7,2)]
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-grapple-videos-v2';out.mkdir();rows=[]
 sources=[Path(__file__),HERE/'movie_v1.gd',HERE/'movie_v2.gd',HERE/'movie_v2.tscn',ROOT/'prototype/workshop/record.py',ROOT/'prototype/workshop/main.gd',ROOT/'prototype/workshop/mechanics.gd']
 binding={str(p.relative_to(ROOT.parent)):file_sha(p)for p in sources}
 for recipe,version,index in PLANS:
  run=f'workshop-creative-grapple-production-v{version}/round-{index:02d}';dest=out/recipe
  try:
   record(run,str(dest.relative_to(ROOT.parent)),display=':106',main_scene=HERE/'movie_v2.tscn')
   manifest=json.loads((dest/'manifest.json').read_text());rows.append(dict(recipe=recipe,status='exact_native_recording_pass',manifest=str((dest/'manifest.json').relative_to(ROOT.parent)),clips=manifest['clips']))
  except Exception as exc:
   (out/(recipe+'-failure.json')).write_text(json.dumps(dict(error=repr(exc),traceback=traceback.format_exc()),indent=2));rows.append(dict(recipe=recipe,status='recording_or_strict_comparison_failed',failure=str((out/(recipe+'-failure.json')).relative_to(ROOT.parent))))
  (out/'index.json').write_text(json.dumps(dict(schema='pcg/creative-grapple-video-index/v1',recording_sources=binding,main_scene=str((HERE/'movie_v2.tscn').relative_to(ROOT.parent)),rows=rows,human_fun='unreviewed',manual_play='unreviewed',production_admitted=False),ensure_ascii=False,indent=2))
 print(json.dumps(dict(out=str(out),rows=[dict(recipe=r['recipe'],status=r['status'])for r in rows])),flush=True)
