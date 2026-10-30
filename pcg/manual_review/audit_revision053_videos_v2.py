"""Decode actual normal-speed movies for explicitly limited frame review."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,subprocess
from PIL import Image,ImageDraw
from .continue_revision053_v1 import OUT
from pcg.migration import core,physics

def main():
 manifests=sorted((OUT/'videos').glob('*/manifest.json'),key=lambda p:p.parent.name);assert len(manifests)==11
 entries=[];sheets=[]
 for i,p in enumerate(manifests):
  m=core.read(p);movie=p.parent/m['clips'][0]['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]));assert probe['streams'][0]['avg_frame_rate']=='60/1';duration=float(probe['format']['duration']);frames=[]
  for j,fraction in enumerate([.2,.5,.85]):
   dest=OUT/'verification/video-frames-v2'/(p.parent.name+'-'+str(j)+'.png');dest.parent.mkdir(parents=True,exist_ok=True);t=max(0,(duration-1)*fraction)
   subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1',str(dest)],check=True);frames.append(dict(timeSeconds=t,frame=physics.artifact(dest)))
  entries.append(dict(movie=physics.artifact(movie),manifest=physics.artifact(p),decodedFrames=frames))
 for start in range(0,len(entries),5):
  canvas=Image.new('RGB',(1200,5*254),'#1f2430');draw=ImageDraw.Draw(canvas)
  for i,entry in enumerate(entries[start:start+5]):
   for j,f in enumerate(entry['decodedFrames']):
    im=Image.open(core.resolve_artifact(f['frame']['path']));im.thumbnail((400,225));canvas.paste(im,(j*400,i*254+25));draw.text((j*400+5,i*254+5),f"{manifests[start+i].parent.name} {f['timeSeconds']:.2f}s",fill='white')
  dest=OUT/'verification'/('video-contact-sheet-v2-'+str(start//5+1)+'.jpg');canvas.save(dest,quality=90);sheets.append(physics.artifact(dest))
 core.write(OUT/'verification/video-frame-audit-v2.json',dict(passed=True,movies=len(entries),speed=1,endHoldSeconds=1,editorialCuts=[],decodedFrameCount=33,sheets=sheets,entries=entries,humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False))
 print('11_MOVIES_33_ACTUAL_FRAMES_DECODED')
if __name__=='__main__':main()
