"""Evacuate a moving support before interdiction, meet that same body again."""
import copy,math
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v8 import candidates as probes
from pcg.prototype.creative_batches.machinery.production_v3 import specification as old_spec,alternatives as original_alts
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT

def compiler(request):
 cs=probes();s=old_spec('carrier-rendezvous');s.update(id='creative-machinery/v9/evacuate-rejoin',required_family='evacuate-rejoin',objective=dict(relationship='evacuate same moving support before hazard, refuge, intercept same support beyond hazard'),rise=0)
 for c in cs:
  c['id']=c['id'].replace('v8','v9');c['saws'][0]['radius']=120;c['saws'][0]['travel']=[0,20];c['trace_all']=False;c['production_recipe']='evacuate-rejoin';c['parent_family']='moving_platform';c['rule_parameters']=dict(relationship='continuous support evacuation and future interception',saw_radius=120,human_fun='unreviewed',source_task='/root/machinery_creator');c['generation_rule']=dict(id='creative-machinery/evacuate-rejoin',version=9,source_type='llm_subagent_proposal',source_task='/root/machinery_creator',parameters=c['rule_parameters']);c['map_specification']=s;c['idea_ids']=['machinery/evacuate-rejoin']
 return dict(status='requires_physics',specifications=[s],cases=cs)
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<8:why.append('reward_not_claimed')
 first=[f for f in fs if f.get('support_id')=='carrier'and f['x']<620];ref=[f for f in fs if f.get('support_id')=='Platform1'];last=[f for f in fs if f.get('support_id')=='carrier'and f['x']>890]
 seq=bool(first and ref and last and first[0]['frame']<ref[0]['frame']<last[0]['frame']);causal=dict(first_carrier_frames=len(first),refuge_support_frames=len(ref),same_carrier_recapture_frames=len(last),sequence=seq)
 if not seq:why.append('moving_support_refuge_same_support_not_demonstrated')
 return dict(ok=not why,reasons=why,causal=causal)
def alternatives(c):
 out=original_alts(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for takeoff in [500,540,580,610]:
  for dy in [.15,.5,.8660254]:
   p=copy.deepcopy(c['control_plan'][:9])+[wait_x(takeoff),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=20),cmd('shoot',after=6,direction=[-math.sqrt(1-dy*dy),dy])]+copy.deepcopy(c['control_plan'][21:])
   add('skip-refuge-'+str(takeoff)+'-'+str(dy),p)
 for phase in [.25,.5,.75]:
  p=copy.deepcopy(c['control_plan']);p[3]['trigger']['dynamic']['window']=[phase,phase+.02];add('late-boarding-'+str(phase),p)
 # Waiting aboard and attempting the far shore rather than evacuating.
 p=copy.deepcopy(c['control_plan'][:9])+[wait_x(1060),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1430,6)];add('stay-aboard',p)
 return out
if __name__=='__main__':
 run('workshop-creative-machinery-production-v9',requests=[dict(recipe='evacuate-rejoin')],cycles=1,library_root=ROOT/'results/workshop-creative-machinery-library-v9',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[p for p in Path(__file__).parent.glob('*.py')if p!=Path(__file__)])
