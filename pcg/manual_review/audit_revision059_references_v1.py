if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,zipfile
from pcg.migration import core,physics
from pcg.tools.restore_archive import JoinedParts
from .continue_revision059_v1 import OUT

def main():
 archive=core.REPO/'pcg/archives/approved-revision059-implementation-v1';manifest=core.read(archive/'manifest.json')
 with JoinedParts(archive,manifest['parts'])as joined:
  with zipfile.ZipFile(joined)as z:rawindex=json.loads(z.read('PCG-ARCHIVE-INDEX.json'))
 refs={}
 def visit(v):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str):refs[v['path']]=v
   for w in v.values():visit(w)
  elif isinstance(v,list):
   for w in v:visit(w)
 index=core.read(OUT/'index.json');visit(index)
 for row in index['results']:visit(core.read(core.resolve_artifact(row['result']['path'])))
 for p in(OUT/'verification').glob('*.json'):
  if p.name not in ['delivery-reference-audit.json']:visit(core.read(p))
 facts=[]
 for rel,ref in sorted(refs.items()):
  p=core.resolve_artifact(rel);assert p.exists()and core.sha(p)==ref['sha256'],rel;mode='tracked_artifact'
  if rel.startswith('pcg/results/'):
   assert rawindex[rel.removeprefix('pcg/')]['sha256']==ref['sha256'],rel;mode='verified_raw_archive_restore_required'
  facts.append(dict(path=rel,sha256=ref['sha256'],delivery=mode))
 core.write(OUT/'verification/delivery-reference-audit.json',dict(passed=True,currentSpecs=7,nativeDirections=31,references=len(facts),archive=physics.artifact(archive/'manifest.json'),rows=facts));print('CURRENT_REFERENCES_SHA_AND_ARCHIVE_MEMBERSHIP_PASS',len(facts))
if __name__=='__main__':main()
