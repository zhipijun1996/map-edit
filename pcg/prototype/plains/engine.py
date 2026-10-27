import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
from ..factory.core.engine import ROOT,Engine,file_sha
from ..dynamic.simulator import Simulator,ENGINE,PROJECT

class PlainsSimulator(Simulator):
 runner_script='res://runner_plains.gd'
 def run(self,cases,label):
  if not cases:return []
  self.calls+=1;self.cases+=len(cases);inp=self.out/(label+'.input.json');output=self.out/(label+'.output.json');log=self.out/(label+'.log')
  if output.exists():raise ValueError('Refuse existing physics output')
  inp.write_text(json.dumps(dict(cases=cases),allow_nan=False))
  cmd=[str(ENGINE),'--headless','--path',str(PROJECT),'--fixed-fps','60','--script',self.runner_script,'--','--input='+str(inp),'--output='+str(output)]
  started=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
  with log.open('w')as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=240)
  usage=resource.getrusage(resource.RUSAGE_CHILDREN)
  (self.out/(label+'.execution.json')).write_text(json.dumps(dict(command=cmd,engine=self.version,exit_code=p.returncode,wall_seconds=time.perf_counter()-started,child_cpu_seconds=usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,children_peak_rss_kib=usage.ru_maxrss,input_sha256=file_sha(inp)),indent=2))
  text=log.read_text()
  if p.returncode or 'PCG_BATCH_V3_COMPLETE '+str(len(cases))not in text or 'ERROR:'in text or 'SCRIPT ERROR'in text or 'were leaked'in text:raise RuntimeError('Plains engine failure: '+str(log))
  result=json.loads(output.read_text())['results']
  if len(result)!=len(cases)or any(c['id']!=r['id']for c,r in zip(cases,result)):raise ValueError('Result identity mismatch')
  return result

class PlainsEngine(Engine):
 def __init__(self,out,batch_size=12):
  super().__init__(out,batch_size)
  files=list((ROOT/'prototype/plains').glob('*.py'))+[PROJECT/'plains_cells.gd',PROJECT/'runner_plains.gd',PROJECT/'plains_lifecycle.gd']
  additions=json.loads((ROOT/'research/plains-runtime-additions.json').read_text())
  files += [ROOT/'research/plains-runtime-additions.json',ROOT/'research/plains-source-audit.json']+[PROJECT/n for n in additions['files']]
  for p in files:
   rel=p.relative_to(ROOT).as_posix();self.hashes[rel]=file_sha(p);q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  self.binding['source_files']=self.hashes;self.binding['source_manifest_sha256']=hashlib.sha256(json.dumps(self.hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  self.binding['runner']='runner_plains.gd';self.binding['audited_game_main']='cd4989a68613e0b457cdfd5e252634dd57008505'
  (self.out/'source_binding.json').write_text(json.dumps(self.binding,indent=2));self.sim=PlainsSimulator(self.out/'physics')
