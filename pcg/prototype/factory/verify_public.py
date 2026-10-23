"""Verify exact public portal and reused engine/base bytes after deployment."""
import argparse,concurrent.futures,hashlib,json,urllib.request
from pathlib import Path

def run(staged,out):
 local=json.loads(Path(staged).read_text());url=local['url'];folder=Path(local['path'])
 expected=(folder/'preview.json').read_bytes()
 with urllib.request.urlopen(url+'preview.json',timeout=90)as r:actual=r.read()
 if actual!=expected:raise ValueError('Public preview identity differs')
 receipt=json.loads(expected);items=[(url+'preview.json',hashlib.sha256(expected).hexdigest(),len(expected))]
 items += [(url+name,h,(folder/name).stat().st_size)for name,h in receipt['files'].items()]
 items += [('https://zhipijun1996.github.io'+p,r['sha256'],r['bytes'])for p,r in receipt['dependencies'].items()]
 def check(item):
  target,digest,size=item;h=hashlib.sha256();total=0
  with urllib.request.urlopen(target,timeout=120)as response:
   while chunk:=response.read(1024**2):h.update(chunk);total+=len(chunk)
  if total!=size or h.hexdigest()!=digest:raise ValueError('Public bytes differ: '+target)
  return dict(url=target,bytes=total,sha256=digest)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(check,items))
 result=dict(schema='pcg/factory-public-bytes/v1',source_commit=receipt['source_commit'],build_id=receipt['build_id'],verified=len(results),bytes=sum(r['bytes']for r in results),files=results,failures=[])
 Path(out).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='files'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--staged',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.staged,a.out)
