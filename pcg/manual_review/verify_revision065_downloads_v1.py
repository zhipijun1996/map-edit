"""Anonymous exact-byte downloads for relay scenes, samples, films and raw parts."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,concurrent.futures,datetime,hashlib,time,urllib.request
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import OUT
from .run_revision066_lift_v1 import folder_for,rows
def run(commit):
 assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit);assert not(OUT/'public-downloads.json').exists()
 paths=[OUT/'README.md']+list(OUT.glob('*.json'))+list((OUT/'authorization').glob('*.json'))+list((OUT/'verification').glob('*.json'))+list((core.REPO/'feedback/manual-review/implementation-results/revision-066-v1').rglob('*.json'))
 r=core.read(OUT/'lift.json');paths+=[core.resolve_artifact(r[k]['path'])for k in ['sourceModule','parameters','qualification','designSource','implementationProvenance']]
 paths+=[core.resolve_artifact(d['file']['path'])for d in core.read(OUT/'downloads/index.json')['rows']]+[OUT/'downloads/index.json']
 for f in [folder_for(rows()[0]),OUT/'fixtures/missed-boarding-wait-chest-v2']:
  paths+=[f/'playable'/n for n in ['demo.tscn','module.tscn','godot-package.json','compiled-content.json','cases.json','load-evidence/index.json']]+[f/'package-result.json'];paths+=list((f/'playable/load-evidence').glob('case-*/receipt.json'))
 paths+=[OUT/'fixtures/missed-boarding-wait-chest-v2/recovery-reward-evidence.json']
 for p in(OUT/'videos').glob('*/manifest.json'):
  m=core.read(p);paths+=[p,p.parent/'native.mp4',core.resolve_artifact(m['nativeReceipt']['path']),core.resolve_artifact(m['strictDiff']['path'])]
 archive=core.REPO/'pcg/archives/approved-revision065-066-lift-relay-v1';paths+=[archive/'manifest.json']+[archive/p['file']for p in core.read(archive/'manifest.json')['parts']]
 paths+=list((core.REPO/'pcg/migration/foundation-v1/holdout-pools/approved-revision063-v1-lift').glob('*.json'));paths+=[core.REPO/'feedback/manual-review/lift-relay-r065-receipt.json']
 for item in core.read(OUT/'index.json')['completedOriginalTwelve']:paths.append(core.resolve_artifact(item['result']['path']))
 paths=list(dict.fromkeys(paths))
 def check(p):
  url='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+commit+'/'+core.relative(p);expected=core.sha(p)
  for attempt in range(5):
   try:
    h=hashlib.sha256();count=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'map-edit-evidence-verifier'}),timeout=120)as stream:
     while data:=stream.read(1048576):h.update(data);count+=len(data)
    assert h.hexdigest()==expected and count==p.stat().st_size;print('PUBLIC_SHA_PASS',core.relative(p),count,flush=True);return dict(path=core.relative(p),url=url,sha256=expected,downloadedSha256=h.hexdigest(),bytes=count,passed=True)
   except Exception:
    if attempt==4:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:checked=list(pool.map(check,paths))
 core.write(OUT/'public-downloads.json',dict(schema='pcg/public-download-verification/v1',passed=True,commit=commit,anonymous=True,files=len(checked),bytes=sum(x['bytes']for x in checked),rows=checked,verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=physics.artifact(__file__),scope='Current final lift plus same-world recovery/chest native scene,2ZIPs,2actual movies,qualification and original twelve summary,exact specification and all7raw archive parts. Engine/original assets restored separately.'));print('R065_PUBLIC_DOWNLOADS_VERIFIED',len(checked),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);run(p.parse_args().commit)
