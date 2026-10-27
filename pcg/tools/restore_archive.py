"""Reassemble local Git archive parts and restore only hash-verified entries."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def restore(name,extract=False,prefix=''):
 folder=ROOT/'archives'/name
 if name not in('godot-runtime-v1','research-results-v1','review-delivery-v1','guided-landing-v1','plains-generation-v1','module-contract-v1','plains-review-round2-v1','plains-three-port-v1','map-directed-source-and-failures-v1','r2-full-source-and-failures-v1','r2-full-run-payloads-v1','direct-module-source-and-failures-v1','direct-module-run-payloads-v1','open-valley-sample-v1','valley-complete-v1','formal-style-v2','full-region-spatial-v1','content-ecosystem-v1','workshop-a1-first-v1','content-workshop-v1','content-workshop-a2-rework-v2','content-workshop-macro-v1','content-workshop-creative20-v1','woven-region-v1','content-routes-v1','content-workshop-plains-method-v1','content-workshop-plains-batch-v1','content-workshop-plains50-v1','content-workshop-junctions-v1','content-workshop-plains30-core-v1','content-workshop-plains30-core-v2','content-workshop-plains30-c02-v1','content-workshop-plains30-seams-v1','content-workshop-plains30-block-v1','content-workshop-plains30-block-v2','content-workshop-plains30-block-v3','content-workshop-plains30-block-v4','content-workshop-plains30-block-v5','content-workshop-plains30-block-v6','content-workshop-plains30-block-v7','content-workshop-plains30-block-v8','content-workshop-plains30-prototypes-v1'):raise ValueError('Unknown archive')
 manifest=json.loads((folder/'manifest.json').read_text());work=ROOT/'archives/_work';work.mkdir(exist_ok=True);archive=work/(name+'.zip')
 if archive.exists():
  if sha(archive)!=manifest['archive_sha256']:raise ValueError('Existing archive differs; retained')
 else:
  temp=archive.with_suffix('.zip.partial')
  with temp.open('xb')as out:
   for part in manifest['parts']:
    p=folder/part['file']
    if p.parent!=folder or p.stat().st_size!=part['bytes']or sha(p)!=part['sha256']:raise ValueError('Part checksum mismatch')
    with p.open('rb')as f:shutil.copyfileobj(f,out)
  if temp.stat().st_size!=manifest['archive_bytes']or sha(temp)!=manifest['archive_sha256']:raise ValueError('Combined checksum mismatch')
  temp.rename(archive)
 count=0
 with zipfile.ZipFile(archive)as z:
  index=json.loads(z.read('PCG-ARCHIVE-INDEX.json'))
  for name,info in index.items():
   if prefix and not name.startswith(prefix):continue
   p=ROOT/name
   if not p.resolve().is_relative_to(ROOT.resolve())or'..'in Path(name).parts:raise ValueError('Unsafe archive path')
   if extract and p.exists():
    if sha(p)!=info['sha256']:raise ValueError('Changed existing file retained: '+name)
   else:
    data=z.read(info.get('archive_entry',name))
    if len(data)!=info['bytes']or hashlib.sha256(data).hexdigest()!=info['sha256']:raise ValueError('Entry checksum mismatch: '+name)
    if extract:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
   count+=1
 print(json.dumps(dict(archive=str(archive),verified_files=count,extracted=extract,sha256=manifest['archive_sha256'])))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--extract',action='store_true');p.add_argument('--prefix',default='');a=p.parse_args();restore(a.name,a.extract,a.prefix)
