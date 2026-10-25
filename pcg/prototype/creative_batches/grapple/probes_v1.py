import json
from pathlib import Path
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle

def gate(op,state,n=0,timeout=120,**kw):return dict(op=op,trigger=dict(state=state,min_after=n,timeout=timeout),**kw)
def probes():
 out=[]
 for typ in ['hang','bounce','double','recast']:
  for delay in [8,16,24]:
   c=base(f'grapple-probe-{typ}-{delay}');c['capabilities']=['move','jump','grapple','double_jump','shot_recoil'];c['platforms']=[[-160,438,400,100],[-800,900,2200,60]];c['hooks']=[dict(x=210,y=230,kind='bounce'if typ=='bounce'else'hang')];c['max_frames']=220
   plan=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',8)]
   if typ=='double':plan += [cmd('jump',12),cmd('jump_release',8)];c['hooks'][0]['y']=100
   plan += [cmd('grapple',delay,aim_target=[c['hooks'][0]['x'],c['hooks'][0]['y']])]
   if typ=='bounce':plan += [gate('wait','free',25),cmd('shoot',direction=[-.8,.6])]
   else:
    plan += [gate('wait','hook_hang',1),cmd('axis',value=1),gate('jump','hook_hang',3),cmd('jump_release',12)]
    if typ=='double':plan += [cmd('jump',20),cmd('jump_release',12)]
    if typ=='recast':
     c['hooks'].append(dict(x=360,y=30,kind='hang'));plan += [cmd('grapple',2,aim_target=[360,30]),gate('jump','hook_hang',3),cmd('jump_release',12)]
   c['control_plan']=plan;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-grapple-probes-v1',extra_sources=[Path(__file__)]);rows=[]
 for c,r,e in engine.run(probes(),'motion'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['reason'],r.get('plan_error'),r.get('hook_contacts'),r.get('anchor_jumps'),r.get('air_jumps'),[(f['frame'],round(f['x']),round(f['y']),f['traversal_state'],f.get('remaining_jumps'),f.get('air_shots'))for f in r['frames'][::12]],flush=True)
 (engine.out/'measured.json').write_text(json.dumps(rows))
