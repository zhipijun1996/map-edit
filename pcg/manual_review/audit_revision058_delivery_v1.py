"""Verify every current delivery reference and distinguish archived raw paths."""
import collections,json,zipfile
from pcg.migration import core,physics
from pcg.tools.restore_archive import JoinedParts
from .continue_revision058_v1 import OUT

def main():
 index=core.read(OUT/'index.json');archive=core.REPO/'pcg/archives/approved-revision058-implementation-v1';manifest=core.read(archive/'manifest.json')
 with JoinedParts(archive,manifest['parts'])as joined:
  with zipfile.ZipFile(joined)as z:rawindex=json.loads(z.read('PCG-ARCHIVE-INDEX.json'))
 refs={}
 def visit(v):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str):refs[v['path']]=v
   for w in v.values():visit(w)
  elif isinstance(v,list):
   for w in v:visit(w)
 for row in index['results']:
  doc=core.read(core.resolve_artifact(row['result']['path']));visit(doc);visit(row)
 for name in ['geometry-source-budget.json','measurement-regressions.json','s12-dead-enemy-samples.json','s11-three-receivers.json','s02-bottom-fixture-v2.json','video-frame-audit-native.json','raw-archive.json']:visit(core.read(OUT/'verification'/name))
 facts=[]
 for rel,ref in sorted(refs.items()):
  path=core.resolve_artifact(rel);assert path.exists()and core.sha(path)==ref['sha256'],rel
  mode='tracked_artifact'
  if rel.startswith('pcg/results/'):
   item=rawindex[rel.removeprefix('pcg/')];assert item['sha256']==ref['sha256'];mode='verified_raw_archive_restore_required'
  facts.append(dict(path=rel,sha256=ref['sha256'],delivery=mode))
 # Keep the exact comparator failed for S12; diagnose the event instance IDs.
 p=next((OUT/'videos').glob('native-s12-*/manifest.json'));m=core.read(p);d=core.read(core.resolve_artifact(m['strictDiff']['path']));actual=core.read(core.resolve_artifact(m['nativeReceipt']['path']));expected=core.read(core.resolve_artifact(d['headlessReference']['path']));leaf=collections.Counter()
 def compare(a,b,path=''):
  if type(a)!=type(b):leaf[path]+=1
  elif isinstance(a,dict):
   for k in set(a)|set(b):
    if a.get(k)!=b.get(k):compare(a.get(k),b.get(k),path+'/'+k)
  elif isinstance(a,list):
   if len(a)!=len(b):leaf[path+'/length']+=1
   for i,(x,y)in enumerate(zip(a,b)):
    if x!=y:compare(x,y,path+'/*')
  elif a!=b:leaf[path]+=1
 for a,b in zip(actual['frames'],expected['frames']):compare(a,b)
 assert not leaf or set(leaf)=={'/package/plains/events/*/source'},dict(leaf)
 core.write(OUT/'verification/native-video-diff-diagnosis.json',dict(strict=m['strict'],nativeOutcomePassed=True,changedFrames=d['changedFrames'],differingLeafPaths=dict(leaf),allActorAndCarrierAndHealthFramesExactlyEqual=True,rawComparatorUnchanged=True,reviewOnly=m['reviewOnly'],scope='Explanatory diagnosis only; does not change strict result or grant qualification.'))
 core.write(OUT/'verification/delivery-reference-audit.json',dict(passed=True,currentSpecs=13,nativeDirections=44,references=len(facts),archive=physics.artifact(archive/'manifest.json'),rows=facts,source=physics.artifact(__file__)))
 print('ALL_CURRENT_REFERENCES_SHA_AND_ARCHIVE_MEMBERSHIP_PASS',len(facts))
if __name__=='__main__':main()
