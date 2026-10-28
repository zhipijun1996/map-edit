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
  file=ROOT/r['file'];d=read(file);version_data={k:v for k,v in d.items()if k!='designVersion'};d['designVersion']='sha256:'+hashlib.sha256(json.dumps(version_data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();write(file,d);assert d['schema']=='pcg/module-design/v1'and d['reviewStage']=='design';b=d['bounds'];assert b['w']>0 and b['h']>0 and b['w']%128==0 and b['h']%128==0
  for p in d['ports']:
   x,y=p['position'];side=p['face'];edge=x if side in('LEFT','RIGHT')else y;origin=b['y']if side in('LEFT','RIGHT')else b['x'];along=y if side in('LEFT','RIGHT')else x
   assert edge=={'LEFT':b['x'],'RIGHT':b['x']+b['w'],'TOP':b['y'],'BOTTOM':b['y']+b['h']}[side]and abs((along-origin)/128-.5-round((along-origin)/128-.5))<1e-6
  ids={p['id']for p in d['ports']};assert len(ids)==len(d['ports']);assert all(r['from']in ids and r['to']in ids for r in d['intendedRoutes'])
  row=dict(moduleId=d['id'],reviewId=d['reviewId'],reviewStage='design',revision=index['id'],baseSourceSha256=r['baseSourceSha256'],file=r['file'],sha256=sha(file),decisionOnSource='CHANGE',verbatim=r['verbatim'],summary=d['summary'],beforeDiagram=r['beforeDiagram'],beforeVersion=r['beforeVersion'],physicsSummary='设计讨论阶段；定稿后统一实现与验证。');rows.append(row);diagrams.append(dict(reviewId=d['reviewId'],moduleId=d['id'],title=d['title'],summary=d['summary'],source=r['file'],sourceSha256=sha(file)))
 write(folder/'diagram-batch.json',dict(rows=diagrams));subprocess.run(['python3',str(REVIEW/'batch-001/render_diagrams.py'),'--manifest',str(folder/'diagram-batch.json'),'--out',str(folder/'images'),'--draft'],check=True)
 for r in rows:
  file=folder/'images'/(r['reviewId']+'.png');r.update(diagram=file.relative_to(REVIEW).as_posix(),diagramSha256=sha(file))
 write(REVIEW/'revisions/latest.json',dict(schema='pcg/manual-review-revisions/v1',reviewStage='design',rows=rows,formalLibraryChanged=False))
 subprocess.run(['node',str(ROOT/'tools/build_manual_review.mjs')],cwd=ROOT,check=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);publish(parser.parse_args().folder)
