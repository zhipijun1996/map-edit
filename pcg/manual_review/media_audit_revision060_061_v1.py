if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import importlib,json,subprocess
from pcg.migration import core,physics

def main():
 for v in (__import__('sys').argv[1:]or['060','061']):
  scope=importlib.import_module('pcg.manual_review.continue_revision'+v+'_v1');rows=[]
  for r in scope.rows():
   n=scope.label(r);matches=sorted((scope.OUT/'videos').glob('native-'+n+'-*/manifest.json'));manifest=matches[-1];m=core.read(manifest);p=manifest.parent;actual=core.read(p/'native-receipt.json');diff=core.read(p/'strict-diff.json');expected=core.read(core.resolve_artifact(diff['headlessReference']['path']));kinematic=[]
   for a,b in zip(actual['frames'],expected['frames']):
    bad=[k for k in ['frame','axis','grounded','hp','requested','shot_charges','support_id','velocity','x','y']if a.get(k)!=b.get(k)]
    if bad:kinematic.append(dict(frame=a['frame'],fields=bad))
   assert len(actual['frames'])==len(expected['frames'])and not kinematic
   mp4=p/'native.mp4';probe=core.read(p/'media-probe.json');assert probe['streams'][0]['avg_frame_rate']=='60/1';duration=float(probe['format']['duration']);thumbs=[]
   for i,t in enumerate([min(.3,duration*.1),duration*.5,max(.1,duration-1.1)]):
    q=scope.OUT/'verification/video-frames'/(n+'-'+str(i)+'.jpg');q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();subprocess.run(['ffmpeg','-loglevel','error','-nostdin','-ss',str(t),'-i',str(mp4),'-frames:v','1','-vf','scale=960:-1','-q:v','3',str(q)],check=True);thumbs.append(dict(seconds=t,image=physics.artifact(q)))
   rows.append(dict(name=n,movie=physics.artifact(mp4),manifest=physics.artifact(manifest),nativeOutcomePassed=actual['passed'],strict=m['strict'],reviewOnly=m['reviewOnly'],strictComparatorUnchanged=True,strictDifferences=physics.artifact(p/'strict-diff.json'),frameKinematicsAndInputsExact=True,kinematicDifferences=kinematic,framesForActualAIInspection=thumbs))
  core.write(scope.OUT/'verification/media-technical-audit.json',dict(passed=True,rows=rows,strict=sum(r['strict']for r in rows),reviewOnly=sum(r['reviewOnly']for r in rows),normalSpeed=1,allFPS=60,endHoldSeconds=1,physicalDifferencesNotWaived=True,humanPlaytest='UNKNOWN',productionApproval=False));print(v,'MEDIA_TECHNICAL_AUDIT',len(rows),flush=True)
if __name__=='__main__':main()
