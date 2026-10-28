"""Publish pictures and prose only. Never imports a Module factory, compiler or Godot Harness."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];REVIEW=ROOT/'generation/manual-review'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def publish(folder):
 folder=folder.resolve();assert folder.is_relative_to(REVIEW/'designs');index=read(folder/'index.json');rows=[];diagrams=[]
 for r in index['rows']:
  file=ROOT/r['file'];d=read(file);stage=r.get('reviewStage','design')
  if stage=='design':
   version_data={k:v for k,v in d.items()if k!='designVersion'};d['designVersion']='sha256:'+hashlib.sha256(json.dumps(version_data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();write(file,d);assert d['schema']=='pcg/module-design/v1'and d['reviewStage']=='design';b=d['bounds'];assert b['w']>0 and b['h']>0 and b['w']%128==0 and b['h']%128==0
   for p in d['ports']:
    x,y=p['position'];side=p['face'];edge=x if side in('LEFT','RIGHT')else y;origin=b['y']if side in('LEFT','RIGHT')else b['x'];along=y if side in('LEFT','RIGHT')else x
    assert edge=={'LEFT':b['x'],'RIGHT':b['x']+b['w'],'TOP':b['y'],'BOTTOM':b['y']+b['h']}[side]and abs((along-origin)/128-.5-round((along-origin)/128-.5))<1e-6
   ids={p['id']for p in d['ports']};assert len(ids)==len(d['ports']);assert all(v['from']in ids and v['to']in ids for v in d['intendedRoutes'])
  else:
   assert stage=='reference_display'and d['schema']=='gunman-rush-level-sketch/v1'and sha(file)==r['baseSourceSha256']
   assert d['generationContract']['contentVersion']==r['beforeVersion']
  title=r.get('title',d['title']);summary=r.get('summary',d.get('summary',''))
  row=dict(moduleId=r['moduleId'],reviewId=r['reviewId'],reviewStage=stage,revision=index['id'],baseSourceSha256=r['baseSourceSha256'],file=r['file'],sha256=sha(file),title=title,decisionOnSource='PENDING'if stage=='reference_display'else'CHANGE',verbatim=r['verbatim'],summary=summary,beforeDiagram=r['beforeDiagram'],beforeVersion=r['beforeVersion'],physicsSummary=r.get('displaySummary','设计讨论阶段；定稿后统一实现与验证。'),notes=r.get('notes',[]));rows.append(row)
  diagram=dict(reviewId=r['reviewId'],moduleId=r['moduleId'],title=title,summary=summary,source=r['file'],sourceSha256=sha(file))
  if r.get('hookActionDiagram'):diagram['hookActionDiagram']=r['hookActionDiagram']
  for key in ('actionDiagram','instructions','objectLabels','labelPositions','ghosts','shotGuides'):
   if key in r:diagram[key]=r[key]
  diagrams.append(diagram)
 write(folder/'diagram-batch.json',dict(rows=diagrams));subprocess.run(['python3',str(REVIEW/'batch-001/render_diagrams.py'),'--manifest',str(folder/'diagram-batch.json'),'--out',str(folder/'images'),'--draft'],check=True)
 for r in rows:
  file=folder/'images'/(r['reviewId']+'.png');r.update(diagram=file.relative_to(REVIEW).as_posix(),diagramSha256=sha(file))
 prior=read(REVIEW/'revisions/latest.json')['rows'] if (REVIEW/'revisions/latest.json').exists() else []
 updated={r['reviewId'] for r in rows}
 rows=sorted([r for r in prior if r['reviewId'] not in updated]+rows,key=lambda r:int(r['reviewId']))
 write(REVIEW/'revisions/latest.json',dict(schema='pcg/manual-review-revisions/v1',reviewStage='design',rows=rows,formalLibraryChanged=False))
 subprocess.run(['node',str(ROOT/'tools/build_manual_review.mjs')],cwd=ROOT,check=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);publish(parser.parse_args().folder)
