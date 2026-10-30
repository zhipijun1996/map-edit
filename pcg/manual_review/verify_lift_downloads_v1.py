"""Anonymous readback of current results, movies, native manifests and raw parts."""
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pcg.migration import core,physics
from pcg.manual_review.lift_idea_v1 import OUT

def run(commit):
 assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit);assert not(OUT/'public-downloads.json').exists()
 index=core.read(OUT/'index.json');paths=[OUT/'README.md',OUT/'index.json',OUT/'authorization/request.json',OUT/'verification/source-audit.json',OUT/'verification/latest-main.json',OUT/'verification/raw-archive.json']
 for row in index['results']:
  result=core.resolve_artifact(row['result']['path']);r=core.read(result);paths.append(result)
  if r.get('nativePlayable'):paths +=[core.resolve_artifact(r['nativePlayable'][k]['path'])for k in ['manifest','result']]
  for v in r.get('videos',[]):paths +=[core.resolve_artifact(v['movie']['path']),core.resolve_artifact(v['manifest']['path'])]
 archive=core.REPO/'pcg/archives/approved-lift-idea-implementation-v1';paths+=[archive/'manifest.json'];paths +=[archive/p['file']for p in core.read(archive/'manifest.json')['parts']]
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
 core.write(OUT/'public-downloads.json',dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(rows),bytes=sum(r['bytes']for r in rows),verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=physics.artifact(__file__),scope='One lift record, two movies/manifests, one native manifest/result, frozen authorization and audits, whole raw archive manifest and every part. Native dependencies are SHA-bound but not all anonymously downloaded.',rows=rows));print('PUBLIC_VERIFIED',len(rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();run(a.commit)
