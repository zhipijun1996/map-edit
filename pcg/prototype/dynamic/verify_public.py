"""Stream and hash all public preview bytes and immutable runtime dependencies."""
from pathlib import Path
import concurrent.futures,hashlib,json,time,urllib.request
ROOT=Path(__file__).resolve().parents[2]
def run():
 s=json.load(open(ROOT/'delivery/dynamic-v3/staged-preview.json'))
 local=json.load(open(Path(s['path'])/'preview.json'));tasks=[]
 for name,h in local['files'].items():tasks.append((s['url']+name,h))
 for path,d in local['dependencies'].items():tasks.append(('https://zhipijun1996.github.io'+path,d['sha256']))
 def check(item):
  url,expected=item;h=hashlib.sha256();n=0
  with urllib.request.urlopen(url+'?integrity='+expected[:12],timeout=90)as response:
   while block:=response.read(1048576):h.update(block);n+=len(block)
  actual=h.hexdigest()
  if actual!=expected:raise ValueError('public bytes differ: '+url)
  return dict(url=url,bytes=n,sha256=actual)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:records=list(pool.map(check,tasks))
 with urllib.request.urlopen(s['url']+'preview.json?identity='+s['build_id'],timeout=30)as response:identity=json.load(response)
 assert identity==local,'public preview identity differs'
 receipt=dict(source_commit=s['source_commit'],build_id=s['build_id'],files=len(records),records=records,preview_identity_equal=True,checked_utc=time.time())
 (ROOT/'delivery/dynamic-v3/public-integrity.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(dict(verified=len(records),bytes=sum(r['bytes']for r in records))))
if __name__=='__main__':run()
