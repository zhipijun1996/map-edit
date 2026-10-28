"""Versioned PCG archive with per-entry/part/whole hashes; refuses replacement."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
class PartWriter(io.RawIOBase):
 """Non-seekable ZIP sink; retains only one bounded output part at a time."""
 def __init__(self,folder,part_bytes):
  if not isinstance(part_bytes,int)or part_bytes<=0:raise ValueError('Invalid part size')
  self.folder=folder;self.part_bytes=part_bytes;self.parts=[];self.total=0
  self.whole=hashlib.sha256();self.current=None;self.part_hash=None;self.part_count=0
 def writable(self):return True
 def seekable(self):return False
 def tell(self):return self.total
 def write(self,data):
  if self.closed:raise ValueError('Write to closed archive')
  view=memoryview(data);size=len(view)
  while view:
   if self.current is None:
    self.current_path=self.folder/f'{self.folder.name}.zip.part{len(self.parts)+1:03}'
    self.current=self.current_path.open('xb');self.part_hash=hashlib.sha256();self.part_count=0
   chunk=view[:self.part_bytes-self.part_count];self.current.write(chunk)
   self.part_hash.update(chunk);self.whole.update(chunk);self.part_count+=len(chunk);self.total+=len(chunk)
   view=view[len(chunk):]
   if self.part_count==self.part_bytes:self._finish_part()
  return size
 def _finish_part(self):
  if self.current is None:return
  self.current.close();self.parts.append(dict(file=self.current_path.name,bytes=self.part_count,sha256=self.part_hash.hexdigest()));self.current=None
 def flush(self):
  if self.current is not None:self.current.flush()
 def close(self):
  if not self.closed:self._finish_part()
  super().close()

def build(name,paths,deduplicate=False,stream_parts=False,*,part_bytes=10*1024*1024):
 if not name or Path(name).name!=name or name in('.','..')or'\\'in name:raise ValueError('Unsafe archive name')
 if not isinstance(part_bytes,int)or part_bytes<=0:raise ValueError('Invalid part size')
 folder=ROOT/'archives'/name;folder.mkdir();index={};files={}
 for arg in paths:
  p=ROOT/arg
  if not p.exists():raise ValueError('Missing path '+arg)
  for f in(p.rglob('*')if p.is_dir()else[p]):
   if not f.is_file()or f.suffix=='.avi'or any(x in f.parts for x in('__pycache__','.godot')):continue
   if not f.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Path escapes archive root')
   files[str(f.relative_to(ROOT))]=f
 for name,f in sorted(files.items()):
  index[name]=dict(bytes=f.stat().st_size,sha256=sha(f))
  if deduplicate:index[name]['archive_entry']='objects/'+index[name]['sha256']
 def write_zip(destination,mode):
  written=set()
  with zipfile.ZipFile(destination,mode,compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
   for name,f in sorted(files.items()):
    entry=index[name].get('archive_entry',name)
    if entry in written:continue
    z.write(f,entry);written.add(entry)
   z.writestr('PCG-ARCHIVE-INDEX.json',json.dumps(index,ensure_ascii=False,sort_keys=True))
  return written
 if stream_parts:
  with PartWriter(folder,part_bytes)as sink:written=write_zip(sink,'w')
  parts=sink.parts;archive_bytes=sink.total;archive_hash=sink.whole.hexdigest()
 else:
  work=ROOT/'archives/_work';work.mkdir(exist_ok=True);archive=work/(folder.name+'.zip')
  written=write_zip(archive,'x');parts=[]
  with archive.open('rb')as f:
   while data:=f.read(part_bytes):
    p=folder/f'{folder.name}.zip.part{len(parts)+1:03}';p.write_bytes(data);parts.append(dict(file=p.name,bytes=len(data),sha256=sha(p)))
  archive_bytes=archive.stat().st_size;archive_hash=sha(archive)
 m=dict(schema='pcg/repository-archive/v1',name=folder.name,files=len(files),unique_entries=len(written),deduplicated=deduplicate,uncompressed_bytes=sum(v['bytes']for v in index.values()),archive_bytes=archive_bytes,archive_sha256=archive_hash,parts=parts,scope='All selected raw artifacts and immutable source snapshots; rebuildable AVI, import/cache and bytecode excluded')
 (folder/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps(m,ensure_ascii=False));return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('paths',nargs='+');p.add_argument('--deduplicate',action='store_true');p.add_argument('--stream-parts',action='store_true',help='Write ZIP directly to 10MB parts; do not retain a second whole ZIP');a=p.parse_args();build(a.name,a.paths,a.deduplicate,a.stream_parts)
