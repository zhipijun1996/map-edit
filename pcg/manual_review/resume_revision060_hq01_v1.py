"""Continue the same frozen campaign after an original Godot native SIGSEGV.
No new candidate, seed, pool or observed condition. Completed raw bytes reused.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,inspect,json,os,shutil,types
from pcg.migration import core,physics,pool_protocols,holdout_guard
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.plains.engine import PlainsSimulator
from pcg.prototype.factory.core.engine import Engine,file_sha,ROOT
from .continue_revision060_v1 import rows,label,OUT
from .finalize_revision060_v1 import folder_for
OLD='approved-r060-hq01-qualified-final-v1';NEW=OLD+'-same-input-resume-v1';old=core.REPO/'pcg/results'/OLD;dest=core.REPO/'pcg/results'/NEW
r=next(r for r in rows()if label(r)=='hq01');folder=folder_for(r);protocol=core.resolve_artifact(core.read(folder/'preflight.json')['protocol']['path']);binding=core.read(old/'source_binding.json');oldb={b['batch']:b for b in core.read(old/'batches.json')};audit=[]
def guard():
 assert core.sha(folder/'module.mapnote.json')==core.read(old/'input-binding.json')['module']['sha256']
 assert core.sha(folder/'physics-input-cases.json')==core.read(old/'input-binding.json')['cases']['sha256']
 assert core.read(protocol)==core.read(old/'protocol.json')
 for p,h in binding['source_files'].items():assert file_sha(ROOT/p)==h,('frozen_source_drift',p)
 assert not (old/'migration-physics.json').exists();assert 'signal 11'in(old/'physics/0008-migration-calibration.log').read_text()
 return dict(sameFrozenProgram=True,samePool=True,sameSeeds=True,noNewIndependentHoldout=True)
class Resume(WorkshopEngine):
 def run(self,cases,stage):
  for start in range(0,len(cases),self.batch_size):
   guard();chunk=cases[start:start+self.batch_size];name=f'{self.serial:04d}-{stage}';previous=old/'physics'/(name+'.input.json')
   if previous.exists():assert core.read(previous)['cases']==chunk,('not_identical_resume_input',name)
   if name in oldb:
    b=oldb[name];packed=old/b['gzip_path'];rawbytes=gzip.decompress(packed.read_bytes());assert __import__('hashlib').sha256(rawbytes).hexdigest()==b['raw_output_sha256'];rs=json.loads(rawbytes)['results'];assert len(rs)==len(chunk)
    for suffix in ['.input.json','.log','.execution.json','.output.json.gz']:
     p=old/'physics'/(name+suffix);q=self.out/'physics'/p.name
     if p.exists():os.link(p,q)
    self.serial+=1;self.sim.calls+=1;self.sim.cases+=len(chunk);self.batches.append(copy.deepcopy(b));core.write(self.out/'batches.json',self.batches);audit.append(dict(batch=name,mode='read_only_same_raw',cases=len(chunk),rawSha256=b['raw_output_sha256']))
    for i,(c,result)in enumerate(zip(chunk,rs)):yield c,result,dict(batch=name,index=i,output=b['gzip_path'],raw_output_sha256=b['raw_output_sha256'])
   else:
    audit.append(dict(batch=name,mode='identical_crashed_batch_retry'if previous.exists()else'previously_unexecuted_continuation',cases=len(chunk)))
    yield from Engine.run(self,chunk,stage)
   core.write(self.out/'continuation-audit.json',dict(original=OLD,noNewCandidate=True,noNewSeeds=True,noNewPool=True,rows=audit))
def engine(f,name,p):
 assert name==NEW;guard();dest.mkdir();(dest/'physics').mkdir();eng=Resume.__new__(Resume);eng.out=dest;eng.batch_size=24;eng.hashes=binding['source_files'];eng.binding=binding;eng.serial=0;eng.batches=[];eng.sim=PlainsSimulator(dest/'physics');eng.sim.runner_script=binding['runner'];core.write(dest/'source_binding.json',binding)
 shutil.copytree(old/'source_snapshot',dest/'source_snapshot',copy_function=os.link);cs=core.read(folder/'physics-input-cases.json')['cases'];return eng,cs,[physics.author_for(c)for c in cs]
def main():
 assert not dest.exists();guard();s=inspect.getsource(physics.run).replace('holdout_guard.check(folder,protocol_path=protocol_path)','resume_guard()').replace('pool_protocols.assert_unstarted(folder,protocol_path)','resume_guard()').replace('pool_protocols.reserve_holdout(folder,protocol_path,name)',"pool_protocols.reserve_holdout(folder,protocol_path,OLD)").replace('pool_protocols.report_binding(folder,protocol_path,name)',"pool_protocols.report_binding(folder,protocol_path,OLD)")
 ns={**physics.__dict__,'_engine':engine,'resume_guard':guard,'OLD':OLD};exec(compile(s,__file__,'exec'),ns);report=ns['run'](folder,NEW,protocol_path=protocol);core.write(folder/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(dest/'migration-physics.json'),sameInputContinuation=physics.artifact(dest/'continuation-audit.json'),originalCrash=physics.artifact(old/'physics/0008-migration-calibration.log'),rawPriorBatchesUnchanged=True));print('hq01 SAME_INPUT_CONTINUATION',report['passed'],report['actualAttempts'],flush=True)
if __name__=='__main__':main()
