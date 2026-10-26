"""Finite reverse searches; failures leave reverse reachability UNKNOWN."""
import copy,json,math
from pathlib import Path
from pcg.prototype.creative_batches.junction_windgap import rules_v3 as r
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,wait_x,settle
out=ROOT/'results/junction-windgap-reverse-probe-v3';e=WorkshopEngine(out,extra_sources=[Path(r.__file__),Path(__file__),*r.SOURCE_DEPS]);cs=[]
for i in range(2):
 bases=r.layouts(r.RECIPES[0],i);a=next(p for p in bases[0]['ports']if p['id']=='A');east=bases[0]['platforms'][5][0]
 for from_port in ['B','C']:
  parent=next(c for c in bases if c['route_spec']['id']==('b-c'if from_port=='B'else'c-b'))
  approach=copy.deepcopy(parent['control_plan'][:-1])if from_port=='B'else[]
  for hold in [6,12,20]:
   for dy in [.7,.8660254037844386,1.]:
    c=copy.deepcopy(parent);c['id']=f'junction-windgap-reverse-{i}-{from_port}-A-{hold}-{dy}'
    c['exit_port']=a['position'];c['goal']=[a['position'][0]-25,a['position'][1]-4,50,8];c['route_spec']=dict(id='reverse-search',from_port=from_port,to_port='A',role='return',via_ports=[],require_bell=False)
    c['control_plan']=approach+[cmd('axis',value=-1),wait_x(east+28,-1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[math.sqrt(1-dy*dy),dy]),settle(a['position'][0])]
    c['max_frames']=1600;cs.append(c)
rows=[]
for c,v,b in e.run(cs,'reverse-search'):
 fs=v.get('frames',[]);rows.append(dict(id=c['id'],from_port=c['route_spec']['from_port'],to_port='A',safe_stable=bool(v.get('ok')),purpose=r.purpose(c,v),last=[fs[-1]['x'],fs[-1]['y']]if fs else None,evidence=b))
write(out/'summary.json',dict(actual_cases=e.sim.cases,successful=[r['id']for r in rows if r['safe_stable']],relation_status='UNKNOWN',conclusion='Finite failed policies are not a no_path proof; any successful actual reverse must be retained.',rows=rows))
print(json.dumps(dict(actual_cases=e.sim.cases,successes=sum(x['safe_stable']for x in rows),relation_status='UNKNOWN')),flush=True)
