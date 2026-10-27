"""Reassemble local Git archive parts and restore only hash-verified entries."""
import argparse,hashlib,json,shutil,zipfile,io,bisect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ArchiveParts(io.RawIOBase):
 """Seek the existing immutable parts without a second full ZIP on disk."""
 def __init__(self,paths):
  self.paths=paths;self.ends=[];self.pos=0;total=0
  for p in paths:total+=p.stat().st_size;self.ends.append(total)
 def seekable(self):return True
 def readable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.ends[-1]+offset;return self.pos
 def read(self,size=-1):
  if size<0:size=self.ends[-1]-self.pos
  pieces=[]
  while size and self.pos<self.ends[-1]:
   i=bisect.bisect_right(self.ends,self.pos);start=0 if i==0 else self.ends[i-1]
   with self.paths[i].open('rb')as f:f.seek(self.pos-start);data=f.read(min(size,self.ends[i]-self.pos))
   pieces.append(data);self.pos+=len(data);size-=len(data)
  return b''.join(pieces)

def open_parts(name):
 if Path(name).name!=name:raise ValueError('Unsafe archive name')
 folder=ROOT/'archives'/name;m=json.loads((folder/'manifest.json').read_text());paths=[];whole=hashlib.sha256();size=0
 for part in m['parts']:
  p=folder/part['file']
  if p.parent!=folder or p.stat().st_size!=part['bytes']or sha(p)!=part['sha256']:raise ValueError('Part checksum mismatch')
  with p.open('rb')as f:
   while data:=f.read(1024*1024):whole.update(data);size+=len(data)
  paths.append(p)
 if size!=m['archive_bytes']or whole.hexdigest()!=m['archive_sha256']:raise ValueError('Combined checksum mismatch')
 return zipfile.ZipFile(ArchiveParts(paths))

def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check_retired_destinations(index, prefix):
 manifest=ROOT.parent/'archive/mapgen-failed/manifest.json'
 if not manifest.exists():return
 retired={row['path'] for row in json.loads(manifest.read_text())['files']}
 conflicts=[name for name in index if (not prefix or name.startswith(prefix)) and ('pcg/'+name in retired or name.startswith('map_directed/'))]
 if conflicts:raise ValueError('Retired Map or relocated files cannot be restored into the active workspace; inspect fixed archive commit in a separate checkout: '+str(conflicts[:3]))

def restore(name,extract=False,prefix=''):
 folder=ROOT/'archives'/name
 if name not in('module-library-evidence-v1','module-isolation-verification-v1','godot-runtime-v1','research-results-v1','review-delivery-v1','guided-landing-v1','plains-generation-v1','module-contract-v1','plains-review-round2-v1','plains-three-port-v1','map-directed-source-and-failures-v1','r2-full-source-and-failures-v1','r2-full-run-payloads-v1','direct-module-source-and-failures-v1','direct-module-run-payloads-v1','open-valley-sample-v1','valley-complete-v1','formal-style-v2','full-region-spatial-v1','content-ecosystem-v1','woven-region-v1','content-routes-v1','shape-search-calibration-v1','shape-search-source-v1','shape-search-results-v1','catalog-feed-source-and-runs-v1','catalog-feed-media-v1','contact-grammar-v1','block-grid-v1','same-graph-landforms-v1','content-domains-v1','graph-map-materialization-v1'):raise ValueError('Unknown archive')
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
  if extract:check_retired_destinations(index,prefix)
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
