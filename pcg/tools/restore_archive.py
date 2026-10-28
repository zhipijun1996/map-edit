"""Reassemble local Git archive parts and restore only hash-verified entries."""
import argparse,bisect,hashlib,io,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
class JoinedParts(io.RawIOBase):
 """Seekable view over verified parts, without reassembling their ZIP bytes."""
 def __init__(self,folder,parts):
  self.folder=folder;self.parts=parts;self.offsets=[0];self.position=0;self.current=None;self.current_index=None
  for part in parts:self.offsets.append(self.offsets[-1]+part['bytes'])
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.position
 def seek(self,offset,whence=io.SEEK_SET):
  position=offset if whence==io.SEEK_SET else self.position+offset if whence==io.SEEK_CUR else self.offsets[-1]+offset if whence==io.SEEK_END else None
  if position is None or position<0:raise ValueError('Invalid archive seek')
  self.position=position;return position
 def read(self,size=-1):
  if self.closed:raise ValueError('Read from closed archive')
  remaining=max(0,self.offsets[-1]-self.position)
  if size is not None and size>=0:remaining=min(remaining,size)
  chunks=[]
  while remaining:
   index=bisect.bisect_right(self.offsets,self.position)-1
   if self.current_index!=index:
    if self.current is not None:self.current.close()
    self.current=(self.folder/self.parts[index]['file']).open('rb');self.current_index=index
   self.current.seek(self.position-self.offsets[index])
   amount=min(remaining,self.offsets[index+1]-self.position);data=self.current.read(amount)
   if len(data)!=amount:raise ValueError('Part changed during verification')
   chunks.append(data);self.position+=len(data);remaining-=len(data)
  return b''.join(chunks)
 def close(self):
  if self.current is not None:self.current.close();self.current=None
  super().close()

def verify_parts(folder,manifest):
 """One bounded pass verifies every physical part and the exact combined ZIP."""
 if manifest.get('schema')!='pcg/repository-archive/v1':raise ValueError('Unknown archive schema')
 parts=manifest['parts'];whole=hashlib.sha256();size=0;seen=set()
 if not parts:raise ValueError('Archive parts missing')
 for part in parts:
  name=part['file'];p=folder/name
  if not isinstance(name,str)or Path(name).name!=name or'\\'in name or name in seen or not p.resolve().is_relative_to(folder.resolve()):raise ValueError('Unsafe or duplicate archive part')
  seen.add(name)
  if not isinstance(part['bytes'],int)or part['bytes']<=0 or p.stat().st_size!=part['bytes']:raise ValueError('Part size mismatch')
  hashed=hashlib.sha256()
  with p.open('rb')as stream:
   while block:=stream.read(1024*1024):hashed.update(block);whole.update(block);size+=len(block)
  if hashed.hexdigest()!=part['sha256']:raise ValueError('Part checksum mismatch')
 if size!=manifest['archive_bytes']or whole.hexdigest()!=manifest['archive_sha256']:raise ValueError('Combined checksum mismatch')

def _unique_object(pairs):
 value={}
 for key,item in pairs:
  if key in value:raise ValueError('Duplicate archive index field: '+key)
  value[key]=item
 return value

def verify_index(z,manifest):
 """Hash decompressed entries in chunks, reusing actual hashes for aliases."""
 names=z.namelist()
 if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entry')
 index=json.loads(z.read('PCG-ARCHIVE-INDEX.json'),object_pairs_hook=_unique_object)
 if not isinstance(index,dict)or len(index)!=manifest['files']:raise ValueError('Archive index count mismatch')
 entries={info.get('archive_entry',name)for name,info in index.items()}
 if set(names)!=entries|{'PCG-ARCHIVE-INDEX.json'}or len(entries)!=manifest.get('unique_entries',len(entries)):raise ValueError('ZIP/index entry set mismatch')
 if sum(info['bytes']for info in index.values())!=manifest['uncompressed_bytes']:raise ValueError('Index byte count mismatch')
 facts={}
 for name,info in index.items():
  path=Path(name)
  if not name or path.is_absolute()or'..'in path.parts or'\\'in name or not(ROOT/path).resolve().is_relative_to(ROOT.resolve()):raise ValueError('Unsafe archive path')
  entry=info.get('archive_entry',name)
  if entry not in facts:
   size=0;hashed=hashlib.sha256()
   with z.open(entry)as stream:
    while block:=stream.read(1024*1024):size+=len(block);hashed.update(block)
   facts[entry]=(size,hashed.hexdigest())
  if facts[entry]!=(info['bytes'],info['sha256']):raise ValueError('Entry checksum mismatch: '+name)
 return len(index)

def restore(name,extract=False,prefix='',verify_parts_only=False):
 folder=ROOT/'archives'/name
 if name not in('godot-runtime-v1','research-results-v1','review-delivery-v1','guided-landing-v1','plains-generation-v1','module-contract-v1','plains-review-round2-v1','plains-three-port-v1','map-directed-source-and-failures-v1','r2-full-source-and-failures-v1','r2-full-run-payloads-v1','direct-module-source-and-failures-v1','direct-module-run-payloads-v1','open-valley-sample-v1','valley-complete-v1','formal-style-v2','full-region-spatial-v1','content-ecosystem-v1','workshop-a1-first-v1','content-workshop-v1','content-workshop-a2-rework-v2','content-workshop-macro-v1','content-workshop-creative20-v1','woven-region-v1','content-routes-v1','content-workshop-plains-method-v1','content-workshop-plains-batch-v1','content-workshop-plains50-v1','content-workshop-junctions-v1','content-workshop-plains30-core-v1','content-workshop-plains30-core-v2','content-workshop-plains30-c02-v1','content-workshop-plains30-seams-v1','content-workshop-plains30-block-v1','content-workshop-plains30-block-v2','content-workshop-plains30-block-v3','content-workshop-plains30-block-v4','content-workshop-plains30-block-v5','content-workshop-plains30-block-v6','content-workshop-plains30-block-v7','content-workshop-plains30-block-v8','content-workshop-plains30-block-v9','content-workshop-plains30-block-v10','content-workshop-plains30-block-v11','content-workshop-plains30-block-v12','content-workshop-plains30-block-v13','content-workshop-plains30-block-v14','content-workshop-plains30-block-v15','content-workshop-plains30-block-v16','module-foundation-migration-v1','module-foundation-migration-v2','corner-open-interface-pilot-v2','manual-review-batch001-feedback001-v1','content-workshop-plains30-prototypes-v1','approved-designs-batch001-implementation-v1','approved-first30-implementation-v2'):raise ValueError('Unknown archive')
 manifest=json.loads((folder/'manifest.json').read_text())
 if verify_parts_only:
  if extract or prefix:raise ValueError('--verify-parts-only requires no --extract or --prefix; every entry is verified')
  verify_parts(folder,manifest)
  with JoinedParts(folder,manifest['parts'])as reader:
   with zipfile.ZipFile(reader)as z:count=verify_index(z,manifest)
  result=dict(archive=str(folder),verified_files=count,extracted=False,sha256=manifest['archive_sha256'],verification='all_parts_whole_zip_and_every_entry',reassembled=False)
  print(json.dumps(result));return result
 work=ROOT/'archives/_work';work.mkdir(exist_ok=True);archive=work/(name+'.zip')
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
 result=dict(archive=str(archive),verified_files=count,extracted=extract,sha256=manifest['archive_sha256']);print(json.dumps(result));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--extract',action='store_true');p.add_argument('--prefix',default='');p.add_argument('--verify-parts-only',action='store_true',help='Verify all parts, whole ZIP and every entry without reassembly; incompatible with --extract/--prefix');a=p.parse_args();restore(a.name,a.extract,a.prefix,a.verify_parts_only)
