"""Anonymous SHA readback of the actual published delivery and raw archive."""
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pcg.migration import core,physics
from .continue_revision063_v1 import OUT
def run(commit):
 assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit)
 assert not(OUT/'public-downloads.json').exists()
 index=core.read(OUT/'index.json');paths=[OUT/'README.md',OUT/'index.json']
 paths+=list((OUT/'authorization').glob('*.json'))+list((OUT/'verification').glob('*.json'))
 paths+=list((core.REPO/'feedback/manual-review/implementation-results/revision-064-v1').rglob('*.json'))
 for row in index['results']:
  p=core.resolve_artifact(row['result']['path']);r=core.read(p);paths.append(p)
  paths+=[core.resolve_artifact(r[k]['path'])for k in ['sourceModule','parameters','qualification','designSource','implementationProvenance','selection']]
  paths+=[core.resolve_artifact(r['nativePlayable'][k]['path'])for k in ['scene','manifest','result','zip']]
  native=core.resolve_artifact(r['nativePlayable']['scene']['path']).parent
  paths+=[native/n for n in ['module.tscn','compiled-content.json','cases.json','load-evidence/index.json']]
  paths+=list((native/'load-evidence').glob('case-*/receipt.json'))
 for p in(OUT/'videos').glob('*/manifest.json'):
  m=core.read(p);paths+=[p,p.parent/'native.mp4',core.resolve_artifact(m['nativeReceipt']['path']),core.resolve_artifact(m['strictDiff']['path'])]
 paths+=[OUT/'videos/native-s04-B-to-T-v1/native.avi',OUT/'downloads/index.json',OUT/'downloads/lift-optional-chest-native.zip',OUT/'fixtures/lift-optional-chest-v1/reward-evidence.json',OUT/'fixtures/lift-optional-chest-v1/playable/load-evidence/case-0/receipt.json']
 archive=core.REPO/'pcg/archives/approved-revision063-064-implementation-v1';paths+=[archive/'manifest.json']+[archive/p['file']for p in core.read(archive/'manifest.json')['parts']]
 for prefix in ['approved-revision063-v1-*','approved-revision064-v1-*']:paths+=list((core.REPO/'pcg/migration/foundation-v1/holdout-pools').glob(prefix+'/*.json'))
 paths+=[core.REPO/p for p in ['.agents/skills/pcg-physics-contract/SKILL.md','.agents/skills/pcg-module-factory/references/module-workflow.md','feedback/manual-review/spec-sync-r063-receipt.json']]
 paths=list(dict.fromkeys(paths))
 def check(p):
  rel=core.relative(p);url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+rel;expected=core.sha(p)
  for attempt in range(5):
   try:
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'map-edit-evidence-verifier'}),timeout=120)as response:
     while data:=response.read(1048576):h.update(data);size+=len(data)
    assert h.hexdigest()==expected and size==p.stat().st_size
    print('PUBLIC_SHA_PASS',rel,size,flush=True);return dict(path=rel,url=url,sha256=expected,downloadedSha256=h.hexdigest(),bytes=size,passed=True)
   except Exception:
    if attempt==4:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:checked=list(pool.map(check,paths))
 core.write(OUT/'public-downloads.json',dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(checked),bytes=sum(r['bytes']for r in checked),verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=physics.artifact(__file__),scope='12 current native samples,23 native receipts,13 ZIPs,all17 completed movie artifacts plus incomplete AVI,exact designs,qualification and pool records,skills and all19 raw archive parts. Full engine/assets restored separately perWORKSPACE.',rows=checked))
 print('R063_PUBLIC_VERIFIED',len(checked),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);run(p.parse_args().commit)
