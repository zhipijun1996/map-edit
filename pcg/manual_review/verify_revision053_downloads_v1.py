"""Anonymous readback of current results, movies, native manifests and raw parts."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pcg.migration import core,physics
from pcg.manual_review.continue_revision053_v1 import OUT

def run(commit):
 assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit);assert not(OUT/'public-downloads.json').exists()
 index=core.read(OUT/'index.json');paths=[OUT/'README.md',OUT/'index.json',OUT/'authorization/request.json',OUT/'verification/geometry-source-budget.json',OUT/'verification/final-checks.json',OUT/'verification/delivery-reference-audit.json',OUT/'verification/ai-video-observation.json',OUT/'verification/raw-archive.json']
 for row in index['results']:
  result=core.resolve_artifact(row['result']['path']);r=core.read(result);paths.append(result)
  paths += [core.resolve_artifact(r[k]['path'])for k in ['sourceModule','parameters','qualification','designSource']]
  if r.get('nativePlayable'):paths +=[core.resolve_artifact(r['nativePlayable'][k]['path'])for k in ['scene','manifest','result']]
  for v in r.get('videos',[]):paths +=[core.resolve_artifact(v['movie']['path']),core.resolve_artifact(v['manifest']['path'])]
 archive=core.REPO/'pcg/archives/approved-revision053-implementation-v1';paths+=[archive/'manifest.json'];paths +=[archive/p['file']for p in core.read(archive/'manifest.json')['parts']]
 paths=list(dict.fromkeys(paths))
 def check(p):
  rel=core.relative(p);url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+rel;expected=core.sha(p)
  for attempt in range(5):
   try:
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'map-edit-evidence-verifier'}),timeout=120)as response:
     while data:=response.read(1048576):h.update(data);size+=len(data)
    assert h.hexdigest()==expected and size==p.stat().st_size;print('PUBLIC_SHA_PASS',rel,size,flush=True);return dict(path=rel,url=url,sha256=expected,downloadedSha256=h.hexdigest(),bytes=size,passed=True)
   except Exception:
    if attempt==4:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(check,paths))
 core.write(OUT/'public-downloads.json',dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(rows),bytes=sum(r['bytes']for r in rows),verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=physics.artifact(__file__),scope='Eight current result records, nine selected movies/manifests, eight native scenes/manifests/results, exact Module/parameters/qualification/design sources, frozen authorization/audits and every raw archive part. Native dependency files are SHA-bound, not individually downloaded.',rows=rows));print('PUBLIC_VERIFIED',len(rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();run(a.commit)
