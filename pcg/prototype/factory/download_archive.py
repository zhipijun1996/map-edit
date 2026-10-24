"""Reassemble immutable source/data parts with byte/SHA checks. Python stdlib."""
import argparse,hashlib,json,re,urllib.request
from pathlib import Path
PREFIX='https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/'
def run(revision,manifest_path,out):
 if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('Use the full pinned data commit')
 if not manifest_path.startswith('artifacts/PCG-FACTORY-05/')or'..'in manifest_path.split('/'):raise ValueError('Unexpected manifest path')
 base=PREFIX+revision+'/'
 with urllib.request.urlopen(base+manifest_path,timeout=90)as r:manifest=json.load(r)
 target=Path(out or Path(manifest['repository_path']).name)
 if target.exists():raise ValueError('Refuse overwriting existing archive: '+str(target))
 temp=target.with_name(target.name+'.partial')
 if temp.exists():raise ValueError('Keep previous partial evidence; choose another --out')
 digest=hashlib.sha256();total=0
 with temp.open('xb')as output:
  for part in manifest['parts']:
   path=part['repository_path']
   if not path.startswith('artifacts/PCG-FACTORY-05/')or'..'in path.split('/'):raise ValueError('Unexpected part path')
   with urllib.request.urlopen(base+path,timeout=120)as r:data=r.read(part['bytes']+1)
   if len(data)!=part['bytes']or hashlib.sha256(data).hexdigest()!=part['sha256']:raise ValueError('Part integrity failure: '+path)
   output.write(data);digest.update(data);total+=len(data);print('verified',Path(path).name)
 if total!=manifest['bytes']or digest.hexdigest()!=manifest['sha256']:raise ValueError('Combined integrity failure; partial retained')
 temp.rename(target);print(json.dumps(dict(path=str(target),bytes=total,sha256=digest.hexdigest())))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--manifest-path',required=True);p.add_argument('--out');a=p.parse_args();run(a.revision,a.manifest_path,a.out)
