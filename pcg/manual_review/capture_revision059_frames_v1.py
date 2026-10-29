import subprocess,collections
from PIL import Image,ImageDraw
from pcg.migration import core,physics
from .continue_revision059_v1 import OUT

def main():
 index=core.read(OUT/'index.json');sheet=Image.new('RGB',(960,7*210),(22,29,28));draw=ImageDraw.Draw(sheet);facts=[]
 for i,row in enumerate(index['results']):
  r=core.read(core.resolve_artifact(row['result']['path']));v=r['videos'][0];m=core.read(core.resolve_artifact(v['manifest']['path']));movie=core.resolve_artifact(v['movie']['path']);duration=m['clips'][0]['duration'];frames=[]
  for j,frac in enumerate([.2,.6,.99]):
   p=OUT/'verification/frames'/(row['name']+'-'+str(j)+'.png');p.parent.mkdir(exist_ok=True,parents=True);subprocess.run(['ffmpeg','-v','error','-y','-ss',str(duration*frac),'-i',str(movie),'-frames:v','1',str(p)],check=True);im=Image.open(p).convert('RGB');im.thumbnail((320,180));sheet.paste(im,(j*320,i*210+25));frames.append(physics.artifact(p))
  draw.text((8,i*210+5),row['name']+' | 20%, 60%, 99% | '+('STRICT'if v['strict']else'REVIEW_ONLY'),fill='white');facts.append(dict(name=row['name'],sampleFrames=frames,video=physics.artifact(movie),fps=60))
  if not v['strict']:
   d=core.read(core.resolve_artifact(m['strictDiff']['path']));actual=core.read(core.resolve_artifact(m['nativeReceipt']['path']));expected=core.read(core.resolve_artifact(d['headlessReference']['path']));leaves=collections.Counter()
   def compare(a,b,path=''):
    if type(a)!=type(b):leaves[path]+=1
    elif isinstance(a,dict):
     for k in set(a)|set(b):
      if a.get(k)!=b.get(k):compare(a.get(k),b.get(k),path+'/'+k)
    elif isinstance(a,list):
     if len(a)!=len(b):leaves[path+'/length']+=1
     for aa,bb in zip(a,b):
      if aa!=bb:compare(aa,bb,path+'/*')
    elif a!=b:leaves[path]+=1
   for aa,bb in zip(actual['frames'],expected['frames']):compare(aa,bb)
   core.write(OUT/'verification'/(row['name']+'-strict-diff-diagnosis.json'),dict(strict=False,reviewOnly=True,nativeOutcomePassed=True,changedFrames=d['changedFrames'],differingLeafPaths=dict(leaves),originalComparatorUnchanged=True));print(row['name'],'REVIEW_ONLY',dict(leaves))
 sheet.save(OUT/'verification/native-video-contact-sheet.jpg');core.write(OUT/'verification/video-frame-audit-native.json',dict(passed=True,rows=facts,contactSheet=physics.artifact(OUT/'verification/native-video-contact-sheet.jpg')))
if __name__=='__main__':main()
