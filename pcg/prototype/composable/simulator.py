from pathlib import Path
import json,subprocess,time,hashlib,resource
ROOT=Path(__file__).resolve().parents[2]
ENGINE=ROOT/'toolchain/Godot_v4.7.2-stable_linux.x86_64'
PROJECT=ROOT/'prototype/godot'
class Simulator:
 def __init__(self,out):
  self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.calls=0;self.cases=0
  version=subprocess.check_output([str(ENGINE),'--version'],text=True).strip()
  if not version.startswith('4.7.2.stable.official.'):raise RuntimeError('Wrong engine:'+version)
 def run(self,cases,label):
  if not cases:return []
  self.calls+=1;self.cases+=len(cases)
  inp=self.out/(label+'.input.json');output=self.out/(label+'.output.json');log=self.out/(label+'.log')
  if output.exists():raise RuntimeError('Refusing to overwrite physics output:'+str(output))
  inp.write_text(json.dumps({'cases':cases},allow_nan=False))
  cmd=[str(ENGINE),'--headless','--path',str(PROJECT),'--fixed-fps','60','--script','res://runner_v2.gd','--','--input='+str(inp),'--output='+str(output)]
  t=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
  with log.open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  usage=resource.getrusage(resource.RUSAGE_CHILDREN)
  files=[PROJECT/'runner.gd',PROJECT/'runner_v2.gd',PROJECT/'capability_adapter.gd',PROJECT/'source_provenance.json',*Path(__file__).parent.glob('*.py'),Path(__file__).with_name('capabilities.json')]
  hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
  self.out.joinpath(label+'.execution.json').write_text(json.dumps(dict(command=cmd,exit_code=p.returncode,wall_seconds=time.perf_counter()-t,child_cpu_seconds=usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,children_peak_rss_kib=usage.ru_maxrss,input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),source_sha256=hashes),indent=2))
  data=log.read_text()
  if p.returncode or 'PCG_BATCH_V2_COMPLETE '+str(len(cases)) not in data or 'ERROR:'in data or 'SCRIPT ERROR'in data:raise RuntimeError('Godot batch failed:'+str(log))
  rs=json.loads(output.read_text())['results']
  if len(rs)!=len(cases) or any(c['id']!=r['id'] for c,r in zip(cases,rs)):raise RuntimeError('Mismatched case IDs')
  return rs
