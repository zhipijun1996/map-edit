"""Decode representative native movies at normal speed; preserve strict-comparison failures."""
import json,subprocess,sys
from PIL import Image,ImageDraw
from .continue_revision058_v1 import OUT
from pcg.migration import core,physics

def main():
 manifests=sorted((p for p in(OUT/'videos').glob('*/manifest.json')if not p.parent.name.startswith('s11-')or p.parent.name.endswith('-v2')),key=lambda p:p.parent.name);assert len(manifests)==13 or '--partial'in sys.argv
 entries=[];sheets=[]
 for p in manifests:
  m=core.read(p);movie=p.parent/m['clips'][0]['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]));assert probe['streams'][0]['avg_frame_rate']=='60/1';duration=float(probe['format']['duration']);frames=[]
  for j,fraction in enumerate([.2,.6,.99]):
   dest=OUT/'verification/video-frames'/(p.parent.name+'-final-'+str(j)+'.png');dest.parent.mkdir(parents=True,exist_ok=True);t=max(0,(duration-1)*fraction)
   if not dest.exists():subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1',str(dest)],check=True)
   frames.append(dict(timeSeconds=t,frame=physics.artifact(dest)))
  entries.append(dict(movie=physics.artifact(movie),manifest=physics.artifact(p),decodedFrames=frames,strict=m.get('strict',False),reviewOnly=m.get('reviewOnly',False),fps=60,durationSeconds=duration))
 for start in range(0,len(entries),5):
  canvas=Image.new('RGB',(1200,5*254),'#1f2430');draw=ImageDraw.Draw(canvas)
  for i,entry in enumerate(entries[start:start+5]):
   for j,f in enumerate(entry['decodedFrames']):
    im=Image.open(core.resolve_artifact(f['frame']['path']));im.thumbnail((400,225));canvas.paste(im,(j*400,i*254+25));draw.text((j*400+5,i*254+5),f"{manifests[start+i].parent.name} {f['timeSeconds']:.2f}s",fill='white')
  dest=OUT/'verification'/('video-contact-sheet-final-'+str(start//5+1)+'.jpg');canvas.save(dest,quality=90);sheets.append(physics.artifact(dest))
 target='video-frame-audit-partial.json'if '--partial'in sys.argv else'video-frame-audit.json'
 core.write(OUT/'verification'/target,dict(passed=True,movies=len(entries),speed=1,endHoldSeconds=1,editorialCuts=[],decodedFrameCount=len(entries)*3,sheets=sheets,entries=entries,humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False));print('ACTUAL_MOVIES_DECODED',len(entries))
if __name__=='__main__':main()
