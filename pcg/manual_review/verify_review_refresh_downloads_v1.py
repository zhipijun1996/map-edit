"""Anonymous, commit-pinned SHA checks of selected public delivery artifacts."""
import argparse,concurrent.futures,datetime,hashlib,json,time,urllib.request
from pathlib import Path
from pcg.migration import core,physics
ROOT=core.REPO/'feedback/manual-review/implementation-results/review-refresh-v1'

def run(commit,output):
 if len(commit)!=40 or any(c not in '0123456789abcdef'for c in commit):raise ValueError('exact_commit_required')
 output=Path(output)
 if output.exists():raise ValueError('immutable_download_receipt_already_exists')
 paths=[ROOT/'index.json',ROOT/'design-feedback/157.json'];index=core.read(ROOT/'index.json')
 for row in index['results']:
  result=core.read(core.resolve_artifact(row['result']['path']));paths.append(core.resolve_artifact(result['nativePlayable']['manifest']['path']));mfile=core.resolve_artifact(result['videos'][0]['path']);m=core.read(mfile);paths.append(mfile.parent/m['clips'][0]['file'])
 archive=core.REPO/'pcg/archives/approved-review-refresh-implementation-v1';paths +=[archive/r['file']for r in core.read(archive/'manifest.json')['parts']];assert len(paths)==68
 def check(path):
  rel=path.relative_to(core.REPO).as_posix();url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+rel;expected=core.sha(path)
  for attempt in range(6):
   try:
    h=hashlib.sha256();size=0;request=urllib.request.Request(url,headers={'User-Agent':'map-edit-public-evidence-verifier'})
    with urllib.request.urlopen(request,timeout=120)as response:
     while chunk:=response.read(1024*1024):h.update(chunk);size+=len(chunk)
    assert h.hexdigest()==expected and size==path.stat().st_size,rel
    print('PUBLIC_SHA_PASS',rel,size,flush=True);return dict(path=rel,url=url,bytes=size,sha256=expected,downloadedSha256=h.hexdigest(),passed=True)
   except Exception:
    if attempt==5:raise
    time.sleep(min(2**attempt,30))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(check,paths))
 receipt=dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=len(rows),bytes=sum(r['bytes']for r in rows),scope='25 playable manifests, 25 selected current MP4s, 16 complete raw archive parts, current index and 157 design feedback; package artifact bytes also checked in staged exact Git tree',verificationSource=physics.artifact(__file__),rows=rows);core.write(output,receipt);print('PUBLIC_DOWNLOADS_VERIFIED',len(rows),receipt['bytes'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--output',default=str(ROOT/'public-downloads.json'));a=p.parse_args();run(a.commit,a.output)
