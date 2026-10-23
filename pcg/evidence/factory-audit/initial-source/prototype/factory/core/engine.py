"""Bounded batches, complete frozen sources and compressed full failure traces."""
import gzip,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'prototype/dynamic'))
from simulator import Simulator,ENGINE,PROJECT

def file_sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

class Engine:
 def __init__(self,out,batch_size=12):
  self.out=Path(out)
  if self.out.exists():raise ValueError('Refuse existing factory run: '+str(self.out))
  self.out.mkdir(parents=True);self.batch_size=batch_size
  if not 1<=batch_size<=24:raise ValueError('batch_size must be 1..24')
  # Full actual source bytes, not just hashes of mutable working files.
  files=set((ROOT/'prototype/factory/core').glob('*.py'))
  files.update((ROOT/'prototype/dynamic').glob('*.py'))
  files.update((ROOT/'prototype/composable').glob('*.py'))
  files.update((ROOT/'prototype/composable').glob('*.json'))
  files.update(PROJECT.glob('runner*.gd'))
  files.update(PROJECT/n for n in ('dynamic_context.gd','capability_adapter.gd','source_provenance.json','project.godot'))
  original=json.loads((PROJECT/'source_provenance.json').read_text());bad=[]
  for rel,h in original['files'].items():
   p=PROJECT/rel
   if file_sha(p)!=h:bad.append(rel)
   if p.suffix in ('.gd','.tscn','.tres','.json','.gdshader','.cfg'):files.add(p)
  if bad:raise ValueError('Protected game source drift: '+str(bad))
  self.hashes={}
  for p in sorted(files):
   rel=p.relative_to(ROOT).as_posix();self.hashes[rel]=file_sha(p)
   q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  self.binding=dict(engine_sha256=file_sha(ENGINE),game_source_commit=original['commit'],source_index_sha256=file_sha(PROJECT/'source_provenance.json'),protected_files=len(original['files']),protected_mismatches=0,source_files=self.hashes)
  (self.out/'source_binding.json').write_text(json.dumps(self.binding,indent=2))
  self.sim=Simulator(self.out/'physics');self.batches=[];self.serial=0
 def run(self,cases,stage):
  for start in range(0,len(cases),self.batch_size):
   for rel,h in self.hashes.items():
    if file_sha(ROOT/rel)!=h:raise RuntimeError('Frozen factory source changed: '+rel)
   chunk=cases[start:start+self.batch_size];name=f'{self.serial:04d}-{stage}';self.serial+=1
   results=self.sim.run(chunk,name)
   output=self.sim.out/(name+'.output.json');original_sha=file_sha(output);original_bytes=output.stat().st_size
   packed=output.with_suffix('.json.gz')
   with output.open('rb')as source,gzip.open(packed,'wb',compresslevel=5)as target:shutil.copyfileobj(source,target)
   # Only this newly created duplicate raw file is compressed. Existing results
   # are never opened for writing. Original byte hash/length remain recoverable.
   output.unlink()
   receipt=dict(batch=name,stage=stage,cases=len(chunk),raw_output_sha256=original_sha,raw_output_bytes=original_bytes,gzip_path=str(packed.relative_to(self.out)),gzip_sha256=file_sha(packed),execution=str((self.sim.out/(name+'.execution.json')).relative_to(self.out)))
   self.batches.append(receipt);(self.out/'batches.json').write_text(json.dumps(self.batches,indent=2))
   for index,(case,result)in enumerate(zip(chunk,results)):
    yield case,result,dict(batch=name,index=index,output=receipt['gzip_path'],raw_output_sha256=original_sha)
