"""Fifth relationship: declining wall-slide height must meet a moving safe mouth."""
import sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import gated
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.workshop.production_loop import run
OWN=Path(__file__);ADAPTER=OWN.with_name('runner-capabilities-v1.gd')
FAMILY='wall-slide-launch-window'
def compiler(request):
 cs=[]
 for k in range(4):
  c=copy.deepcopy(json.loads((ROOT/'results/workshop-creative-jump-wall-wallslide-probes-v4/slide-saw-0.85-0.28.json').read_text())['case']);c['id']=FAMILY+'-v4-'+str(k);c.update(production_recipe=FAMILY,parent_family=FAMILY,trace_all=True,max_frames=720)
  c['control_plan'][2]['trigger']['after']=235+(k//2)*3;c['control_plan'][3]['trigger']['dynamic']['window']=[.28,.34]if k%2==0 else [.34,.40]
  c['rule_parameters']=dict(relationship='Wall slide consumes height at original 75 units/s while waiting for a moving mouth window; one extra cycle loses the launch band.',source_type='llm_subagent_proposal',task_name='/root/jump_wall_creator',control_candidate=k,wall_slide_is_not_stationary=True,stamina_gate=False,capability_guard_adapter=str(ADAPTER.relative_to(ROOT.parent)),human_fun='unreviewed',reverse='UNKNOWN')
  c['generation_rule']=dict(id='creative/jump-wall/'+FAMILY,version=4,parameters=c['rule_parameters']);c['idea_ids']=['llm-subagent/jump-wall/'+FAMILY];cs.append(c)
 spec=dict(schema='map-notes/challenge-specification/v1',id='creative/jump-wall/'+FAMILY+'/0',region='plains',required_family=FAMILY,objective=dict(relationship='Continuous wall descent spends vertical reach while a moving saw changes the safe launch window.'),capabilities=dict(version=1,status='defined',allOf=['move','wall_climb'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=0,rise=-300,space=dict(max_width=1800,max_height=1800,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=8,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported actual declared capabilities; pre-input snapshot',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 for c in cs:c['map_specification']=spec
 return dict(status='requires_physics',specifications=[spec],cases=cs)
def purpose(c,r):
 fs=r.get('frames',[]);reasons=[];snap=r.get('capability_snapshot',{});entry=r.get('entry_snapshot',{})
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if sorted(snap.get('declared',[]))!=sorted(c['capabilities'])or snap.get('jump_enabled')or snap.get('shoot_enabled')or not snap.get('wall_enabled')or entry.get('jump_maximum')!=1 or entry.get('can_air_jump'):reasons.append('actual_capability_snapshot_mismatch')
 if r.get('workshop',{}).get('coins',0)<8:reasons.append('reward_not_actually_claimed')
 ks=[f for f in fs if any(e.get('state')=='wall_kick'for e in f.get('accepted',[]))];last=ks[-1]if ks else None
 attach=[f for f in fs if f['traversal_state']=='wall_attach'and(last is None or f['frame']<last['frame'])];dy=(max(f['y']for f in attach)-min(f['y']for f in attach))if attach else 0
 falling=[f for f in attach if 65<=f['vy']<=80];mouth=[f for f in fs if 20<=f['x']<=90 and last and f['frame']>last['frame']]
 if not last or dy<150 or len(falling)<100 or not 270<=last['y']<=390 or not mouth:reasons.append('declining_height_budget_and_mouth_crossing_not_observed')
 if r.get('air_jumps',0)or r.get('shots',0):reasons.append('unexpected_propulsion')
 return dict(ok=not reasons,reasons=reasons,causal=dict(wall_attach_frames=len(attach),actual_slide_dy=dy,frames_at_original_slide_speed=len(falling),kick_position=[last['x'],last['y']]if last else None,kick_saw=last.get('saws')if last else None,mouth_crossing=[dict(frame=f['frame'],actor=[f['x'],f['y']],saws=f.get('saws'))for f in mouth],height_is_not_stamina=True),behavior=dict(wall_jumps=r.get('wall_jumps'),shots=r.get('shots'),air_jumps=r.get('air_jumps')))
def alternatives(c):
 out=[];x=c['exit_port'][0]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']=c['id']+'-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for delay in [0,20,100]:add('left-walk-'+str(delay),[cmd('axis',value=0),cmd('wait',delay),cmd('axis',value=-1),settle(x,5)])
 p=copy.deepcopy(c['control_plan']);p[3]['op']='wait';add('omit-wall-kick',p)
 for delay in [0,30,60,100,150,190,205,220,235,250,270,300,340]:
  p=copy.deepcopy(c['control_plan']);p[2]['trigger']['after']=delay;p[3]['trigger'].pop('dynamic',None);add('blind-height-'+str(delay),p)
 for cycles in [1,2,3]:
  p=copy.deepcopy(c['control_plan']);q=copy.deepcopy(p[3]);q['op']='wait';p[3:4]=[q,cmd('wait',54*cycles),gated('jump','wall_attach',min_after=0)];add('extra-phase-cycle-'+str(cycles),p)
 for window in [[0,.05],[.3,.35],[.6,.65]]:
  p=copy.deepcopy(c['control_plan']);p[3]['trigger'].pop('dynamic',None);p[:0]=[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='mouth-saw',window=window),timeout=120))];add('entry-phase-sync-'+str(window[0]),p)
 for n in [1,2,3]:
  p=[cmd('axis',value=1)]
  for _ in range(n):p += [gated('jump','wall_attach',min_after=3,timeout=120),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),cmd('axis',value=1)]
  p += [gated('wait','wall_attach',min_after=3,timeout=120),cmd('wait',190),gated('jump','wall_attach',min_after=0),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),settle(x,3)];add('repeat-right-wall-reset-'+str(n),p)
 return out
if __name__=='__main__':
 run('workshop-creative-jump-wall-production-v4',[dict(recipe=FAMILY,interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-jump-wall-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=OWN,extra_sources=[ADAPTER],runner_script=ADAPTER)
