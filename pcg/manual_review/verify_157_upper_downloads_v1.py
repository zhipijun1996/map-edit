"""Anonymous SHA checks for the new 157 revision and its complete raw archive."""
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pathlib import Path
from pcg.migration import core,physics
from .repair_157_upper_block_v1 import ROOT

def run(commit):
 if len(commit)!=40 or any(c not in '0123456789abcdef'for c in commit):raise ValueError('exact_commit_required')
 output=ROOT/'public-downloads.json'
 if output.exists():raise ValueError('immutable_receipt_exists')
 result=core.read(ROOT/'157.json');manifest=core.resolve_artifact(result['video']['path']);movie=manifest.parent/core.read(manifest)['clips'][0]['file'];archive=core.REPO/'pcg/archives/approved-157-upper-block-v1';paths=[ROOT/'157.json',ROOT/'index.json',core.resolve_artifact(result['nativePlayable']['manifest']['path']),movie,archive/'manifest.json']+[archive/p['file']for p in core.read(archive/'manifest.json')['parts']]
 def check(p):
  rel=core.relative(p);url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+rel;expected=core.sha(p)
  for attempt in range(5):
   try:
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'map-edit-evidence-verifier'}),timeout=120)as response:
     while chunk:=response.read(1024*1024):h.update(chunk);size+=len(chunk)
    assert h.hexdigest()==expected and size==p.stat().st_size;print('PUBLIC_SHA_PASS',rel,size,flush=True);return dict(path=rel,url=url,sha256=expected,downloadedSha256=h.hexdigest(),bytes=size,passed=True)
   except Exception:
    if attempt==4:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(check,paths))
 core.write(output,dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(rows),bytes=sum(r['bytes']for r in rows),verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),verificationSource=physics.artifact(__file__),scope='new 157 result/index, playable manifest, selected MP4, archive manifest and complete raw archive part; does not claim individually downloading every package file',rows=rows));print('PUBLIC_VERIFIED',len(rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();run(a.commit)
