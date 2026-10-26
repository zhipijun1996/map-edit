"""Actual native scene replay and strict existing trace fields; retains failures."""
from pathlib import Path
import json,gzip,subprocess,hashlib
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.record import KEYS
from pcg.tools.record_plains import event_key
HERE=Path(__file__).parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-enemy-world-native-consumer-v1';out.mkdir(exist_ok=False);results=[]
 for recipe in ['attack-relay','lure-sensor']:
  run=ROOT/('results/workshop-creative-enemy-world-'+recipe+'-production-v7/round-00');cs=run/'review_cases.json';c=json.loads(cs.read_text())['cases'][0];ev=c['factory_evidence'];bs=json.loads((run/'batches.json').read_text());b=next(b for b in bs if b['batch']==ev['batch']);physics=json.loads(gzip.decompress((run/b['gzip_path']).read_bytes()))['results'][ev['index']]
  trace=out/(recipe+'.trace.json');log=out/(recipe+'.log');cmd=[str(ROOT/'toolchain/Godot_v4.7.2-stable_linux.x86_64'),'--headless','--path',str(ROOT/'prototype/godot'),'--fixed-fps','60',str(HERE/'main_v1.tscn'),'--','--cases-json',str(cs),'--case','0','--trace-json',str(trace)]
  with log.open('w')as f:proc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  errors=[]
  if proc.returncode:errors.append(dict(exit_code=proc.returncode))
  if trace.exists():
   native=json.loads(trace.read_text());nf=native['frames'];pf=physics['frames']
   if len(nf)!=len(pf):errors.append(dict(field='frame_count',native=len(nf),physics=len(pf)))
   for i,(a,b)in enumerate(zip(nf,pf)):
    for k in KEYS:
     if a[k]!=b[k]:errors.append(dict(frame=i,field=k,native=a[k],physics=b[k]))
    for k in ['bells','enemies']:
     if a['plains'][k]!=b['plains'][k]:errors.append(dict(frame=i,field='plains.'+k,native=a['plains'][k],physics=b['plains'][k]))
    if [event_key(e)for e in a['plains']['events']]!=[event_key(e)for e in b['plains']['events']]:errors.append(dict(frame=i,field='plains.events'))
    if a['workshop']!=b['workshop']:errors.append(dict(frame=i,field='workshop'))
    if 'enemy_world'in b and a['enemy_world']!=b['enemy_world']:errors.append(dict(frame=i,field='enemy_world',native=a['enemy_world'],physics=b['enemy_world']))
  else:errors.append(dict(field='missing_native_trace'))
  row=dict(recipe=recipe,ok=not errors,errors=errors,command=cmd,log_sha256=sha(log),module_sha256=c['module_sha256']);results.append(row);print(recipe,not errors,len(errors),errors[:3],flush=True)
 (out/'comparison.json').write_text(json.dumps(results,indent=2))
 (out/'source-manifest.json').write_text(json.dumps({str(p.relative_to(ROOT.parent)):sha(p)for p in[Path(__file__),HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE/'world_cells_binding_v1.gd',HERE/'guard_charger_v1.tres',HERE/'attack_relay_v1.gd']},indent=2))
