"""Retain full native clips and explicitly label a short 174 presentation cut."""
import json,subprocess,shutil
from pcg.migration import core,physics
from pcg.manual_review.repair_clarified_three_v1 import OUT
root=OUT/'videos/174-v3';m=core.read(root/'manifest.json');src=root/m['clips'][0]['file'];short=root/'174-short-review.mp4'
subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(src),'-vf','trim=duration=3,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1','-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(short)],check=True)
core.write(root/'short-review-manifest.json',dict(schema='pcg/video-excerpt/v1',source=physics.artifact(src),excerpt=physics.artifact(short),sourceIntervalSeconds=[0,3],omittedSourceIntervalSeconds=[3,m['clips'][0]['duration']],omissionReason='Original trace_all case records idle to tick3000 after plan completes at tick143; full native clip and trace retained.',consistentWholeFrameEndFreezeSeconds=1,speed=1,strictComparison='source FAIL; review-only',newPhysicsAttempts=0))
for name in ['index.json','171.json','174.json','175.json']:shutil.copy2(OUT/name,OUT/'history'/('before-display-v2-'+name))if (OUT/'history').exists()else None
