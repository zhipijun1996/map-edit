"""Versioned PCG archive with per-entry/part/whole hashes; refuses replacement."""
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def build(name,paths,deduplicate=False):
 folder=ROOT/'archives'/name;folder.mkdir();work=ROOT/'archives/_work';work.mkdir(exist_ok=True);archive=work/(name+'.zip');index={};files={}
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
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  written=set()
  for name,f in sorted(files.items()):
   entry=index[name].get('archive_entry',name)
   if entry in written:continue
   z.write(f,entry);written.add(entry)
  z.writestr('PCG-ARCHIVE-INDEX.json',json.dumps(index,ensure_ascii=False,sort_keys=True))
 parts=[]
 with archive.open('rb')as f:
  while data:=f.read(10*1024*1024):
   p=folder/f'{folder.name}.zip.part{len(parts)+1:03}';p.write_bytes(data);parts.append(dict(file=p.name,bytes=len(data),sha256=sha(p)))
 m=dict(schema='pcg/repository-archive/v1',name=folder.name,files=len(files),unique_entries=len(written),deduplicated=deduplicate,uncompressed_bytes=sum(v['bytes']for v in index.values()),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),parts=parts,scope='All selected raw artifacts and immutable source snapshots; rebuildable AVI, import/cache and bytecode excluded')
 (folder/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps(m,ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('paths',nargs='+');p.add_argument('--deduplicate',action='store_true');a=p.parse_args();build(a.name,a.paths,a.deduplicate)
