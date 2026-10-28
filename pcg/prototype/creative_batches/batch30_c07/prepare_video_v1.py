import argparse,copy,json,subprocess
from pathlib import Path
from . import api_v1 as api
from .probe_v1 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.factory.core.quality import digest,module_hash
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v3.json',HERE/'probe_v1.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);c=api.layouts(api.RECIPES[0],0)[0]
 static_preflight(engine,[c]);subprocess.run(['node',str(HERE.parent/'batch30_runtime/export_v1.mjs'),str(engine.out/'preflight-bundle.json'),str(engine.out/'batch-preflight-documents')],cwd=ROOT.parent,check=True,capture_output=True)
 for case,r,e in engine.run([c],'canonical-video-case'):
  q=api.purpose(case,r);write(engine.out/'canonical-purpose.json',compact(case,r,e,q));print(json.dumps(dict(ok=q['ok'],reasons=q['reasons'],actual_cases=engine.sim.cases)),flush=True)
  if not q['ok']:return
  review=copy.deepcopy(case);review.update(factory_id=digest(case),factory_evidence=e,recorded_frames=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']],review_alias='C07 prototype / not candidate / efficient wall skill');review['module_sha256']=module_hash(review);write(engine.out/'review_cases.json',dict(cases=[review]))
if __name__=='__main__':main()
