"""Real scheduled Godot dynamic-object batches; exact inputs and failures retained."""
from pathlib import Path
import subprocess,json,time,resource,hashlib
ROOT=Path(__file__).resolve().parents[2]
ENGINE=ROOT/'toolchain/Godot_v4.7.2-stable_linux.x86_64'
PROJECT=ROOT/'prototype/godot'
class Simulator:
 def __init__(self,out):
  self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.calls=0;self.cases=0
  self.version=subprocess.check_output([str(ENGINE),'--version'],text=True).strip()
  if not self.version.startswith('4.7.2.stable.official.'):raise RuntimeError('wrong Godot')
 def run(self,cases,label):
  if not cases:return []
  self.calls+=1;self.cases+=len(cases)
  inp=self.out/(label+'.input.json');output=self.out/(label+'.output.json');log=self.out/(label+'.log')
  if output.exists():raise RuntimeError('immutable physics output exists:'+str(output))
  inp.write_text(json.dumps({'cases':cases},allow_nan=False))
  cmd=[str(ENGINE),'--headless','--path',str(PROJECT),'--fixed-fps','60','--script','res://runner_v3.gd','--','--input='+str(inp),'--output='+str(output)]
  files=[PROJECT/n for n in ('runner.gd','runner_v2.gd','runner_v3.gd','dynamic_context.gd','capability_adapter.gd','source_provenance.json') if (PROJECT/n).exists()]
  files+=list(Path(__file__).parent.glob('*.py'))
  hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
  start=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
  with log.open('w') as f:process=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=240)
  usage=resource.getrusage(resource.RUSAGE_CHILDREN)
  (self.out/(label+'.execution.json')).write_text(json.dumps(dict(command=cmd,engine=self.version,exit_code=process.returncode,wall_seconds=time.perf_counter()-start,child_cpu_seconds=usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,children_peak_rss_kib=usage.ru_maxrss,input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),source_sha256=hashes),indent=2))
  text=log.read_text()
  if process.returncode or 'PCG_BATCH_V3_COMPLETE '+str(len(cases))not in text or 'ERROR:'in text or 'SCRIPT ERROR'in text:raise RuntimeError('dynamic engine failed: '+str(log))
  rs=json.loads(output.read_text())['results']
  if len(rs)!=len(cases) or any(c['id']!=r['id'] for c,r in zip(cases,rs)):raise RuntimeError('case identity mismatch')
  return rs
