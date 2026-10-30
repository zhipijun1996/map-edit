"""Download commit-pinned public deliverables anonymously and verify exact bytes."""
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pcg.migration import core,physics
ROOT=core.REPO/'feedback/manual-review/implementation-results/review-029-v1'
def run(commit):
 assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit)
 out=ROOT/'public-downloads.json';assert not out.exists()
 index=core.read(ROOT/'index.json');paths=[ROOT/'index.json',ROOT/'README.md',ROOT/'deletions.json']
 for r in index['results']:
  p=core.resolve_artifact(r['result']['path']);d=core.read(p);paths.append(p)
  if 'nativePlayable'in d:paths.append(core.resolve_artifact(d['nativePlayable']['manifest']['path']))
  if 'movie'in d:paths.extend([core.resolve_artifact(d['movie']['path']),core.resolve_artifact(d['video']['path'])])
 archive=core.REPO/'pcg/archives/approved-review029-implementation-v1';paths.append(archive/'manifest.json');paths.extend(archive/p['file']for p in core.read(archive/'manifest.json')['parts'])
 def check(p):
  rel=core.relative(p);url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+rel;expected=core.sha(p)
  for attempt in range(5):
   try:
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'map-edit-evidence-verifier'}),timeout=120)as response:
     while chunk:=response.read(1048576):h.update(chunk);size+=len(chunk)
    assert h.hexdigest()==expected and size==p.stat().st_size;print('PUBLIC_SHA_PASS',rel,size,flush=True);return dict(path=rel,url=url,sha256=expected,downloadedSha256=h.hexdigest(),bytes=size,passed=True)
   except Exception:
    if attempt==4:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(check,paths))
 core.write(out,dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(rows),bytes=sum(r['bytes']for r in rows),verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),verificationSource=physics.artifact(__file__),scope='all thirteen result files, twelve package manifests, ten complete MP4s and video manifests, result index/README/deletions, archive manifest and all three raw parts; does not claim downloading each package dependency individually',rows=rows));print('PUBLIC_VERIFIED',len(rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();run(a.commit)
