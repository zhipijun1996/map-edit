"""One physical resource: preserve an open gate, then surrender it for transport."""
import copy,math
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v13 import candidates as probes
from pcg.prototype.creative_batches.machinery.production_v3 import alternatives as old_alts,specification as old_spec
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def compiler(request):
 cs=[]
 for source in probes()[:2]:
  for wait in [20,30]:
   c=copy.deepcopy(source);c['id']=c['id'].replace('v13','v14')+'-d'+str(wait);c['control_plan'][13]['trigger']['after']=wait;c['trace_all']=False;c['production_recipe']='carrier-dual-service';c['parent_family']='moving_platform';c['rule_parameters']=dict(relationship='same carrier holds remote gate then is released for indispensable transport',departure_wait=wait,source_task='/root/machinery_creator',human_fun='unreviewed');c['generation_rule']=dict(id='creative-machinery/carrier-dual-service',version=14,source_type='llm_subagent_proposal',source_task='/root/machinery_creator',parameters=c['rule_parameters']);cs.append(c)
 s=old_spec('carrier-rendezvous');s.update(id='creative-machinery/v14/carrier-dual-service',required_family='carrier-dual-service',objective=dict(relationship='same body first remote sustained key, then surrendered and recaptured as transport'),rise=0,space=dict(max_width=2400,max_height=1400,max_port_span_x=1900))
 for c in cs:c['map_specification']=s;c['idea_ids']=['machinery/carrier-dual-service']
 return dict(status='requires_physics',specifications=[s],cases=cs)
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<8:why.append('reward_not_claimed')
 events=r.get('plains',{}).get('events',[]);occupied=[e for e in events if e['type']=='dock_occupied'and e['occupied']];released=[e for e in events if e['type']=='dock_occupied'and not e['occupied']]
 support=[f for f in fs if f.get('support_id')=='key-carrier'and f['x']>1130];neutral=[f for f in support if abs(f.get('axis',0))<.01];dx=max((f['x']for f in neutral),default=0)-min((f['x']for f in neutral),default=0)
 cross=[f for f in fs if f['x']-12>1024 and any(b['id']=='dock-gate'and b['open']for b in f.get('plains',{}).get('bells',[]))]
 causal=dict(real_dock_occupations=len(occupied),real_dock_releases=len(released),open_body_cross_frames=len(cross),subsequent_support_frames=len(support),neutral_transport_dx=dx)
 if not occupied or not released or not cross or len(support)<6 or dx<70:why.append('dual_use_physical_resource_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=causal)
def alternatives(c):
 out=old_alts(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for takeoff in [1060,1100,1115]:
  for dy in [.15,.5,.8660254]:
   p=copy.deepcopy(c['control_plan'][:6])+[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',after=20),cmd('shoot',after=6,direction=[-math.sqrt(1-dy*dy),dy]),settle(1770,6)]
   add('leave-key-parked-direct-'+str(takeoff)+'-'+str(dy),p)
 for x in [500,600,900,980]:
  p=[cmd('axis',value=1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=x),timeout=400)),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='key-control',receiver='access')),cmd('axis',value=1),settle(1770,6)];add('pre-gate-access-'+str(x),p)
 for delay in [0,25,45,95,120]:
  p=copy.deepcopy(c['control_plan']);p[2]['trigger']['after']=delay;add('wrong-park-'+str(delay),p)
 for x in [920,970,990,1020]:
  p=copy.deepcopy(c['control_plan']);p[4]['trigger']['dynamic']['value']=x;add('early-release-'+str(x),p)
 return out
if __name__=='__main__':
 extras=[p for p in HERE.iterdir()if p.suffix in ['.py','.gd','.mjs','.tscn']and p!=Path(__file__)]
 run('workshop-creative-machinery-production-v14',requests=[dict(recipe='carrier-dual-service')],cycles=1,library_root=ROOT/'results/workshop-creative-machinery-library-v14',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extras,runner_script=HERE/'dock_runner_v11.gd',export_script=HERE/'dock_export_v13.mjs')
