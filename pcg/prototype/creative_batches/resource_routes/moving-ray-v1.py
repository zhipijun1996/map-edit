"""Predict a moving collision occluder for the outgoing projectile ray."""
import copy,json,sys
from pathlib import Path
from pcg.prototype.workshop.rules import timed,cmd,settle
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.counterexamples import alternatives as standard_alts
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent;RECIPE='moving-ray-window'
def phase(lo,hi):return dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='ray-shutter',window=[lo,hi]),timeout=240))
def candidates():
 out=[]
 for k,lo in enumerate([.78,.82,.86,.9]):
  c=timed(0,.7);c['id']='moving-ray-v1-'+str(k);c['family']=RECIPE;c['production_recipe']=RECIPE
  c['spawn']=[205,420];c['entry_port']=[205,420]
  c['latches'][0]['bell']=[20,405]
  c['moving_platforms']=[dict(platform_id='ray-shutter',start=[140,180],finish=[140,500],size=[20,110],travel_duration=1.4,dwell_duration=.15,initial_phase=0)]
  c['rule_parameters']=dict(relationship='outgoing projectile path is periodically occluded by real moving platform; player never rides or touches shutter; choose launch/shot timing so projectile reaches actual clear ray',shutter='ray-shutter',bell=[20,405],gate_window=.7,phase_start=[lo,lo+.025])
  c['control_plan']=[cmd('axis',value=0),phase(lo,lo+.025),cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,aim_cell=dict(kind='bell',id='short-bell')),settle(665,6)]
  c['max_frames']=720;c['trace_all']=True;c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule']=dict(id='creative/'+RECIPE,version=1,parameters=c['rule_parameters'],source_type='llm_subagent_proposal',author_task='/root/resource_routes_creator');out.append(c)
 return out

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[]);opens=[e for e in events if e['type']=='bell_open']
 contacts=[f['frame']for f in fs if f.get('support_id')=='ray-shutter']
 shots=[e for e in events if e['type']=='shot_origin']
 p['causal'].update(real_bell_open=opens,shutter_support_frames=contacts,shot_origins=shots,occluder='original ModuleMovingPlatform collision, not synthetic ray test')
 if not opens:p['reasons'].append('moving_occluder_ray_did_not_unlock')
 if contacts:p['reasons'].append('shutter_used_as_carriage')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=standard_alts(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for lo in [.02,.06,.1,.14,.18,.22,.26,.3,.4,.5,.6,.7,.8,.9]:
  p=copy.deepcopy(c['control_plan']);p[1]=phase(lo,lo+.02);add('other-ray-phase-'+str(lo),p)
 for lo in [0,.2,.4,.6,.8]:
  add('ground-preopen-'+str(lo),[cmd('axis',value=0),phase(lo,lo+.02),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell')),cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',8,direction=[-1,.15]),settle(665,6)])
 for delay in [0,4,12,20,28]:
  p=copy.deepcopy(c['control_plan']);p[5]=cmd('shoot',delay,aim_cell=dict(kind='bell',id='short-bell'));add('other-flight-delay-'+str(delay),p)
 return out

def spec():
 c=candidates()[0]
 return dict(schema='map-notes/challenge-specification/v1',id='creative/resource-routes/moving-ray-window/v1',region='plains',required_family=RECIPE,objective={k:v for k,v in c['rule_parameters'].items()if k!='phase_start'},capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=0,space=dict(max_width=2200,max_height=1800,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(req):
 s=spec();cs=candidates()
 for c in cs:c['map_specification']=s;c['idea_ids']=['resource-routes/moving-ray-window/v1']
 return dict(status='requires_physics',specifications=[s],cases=cs)
def main():
 mode=sys.argv[1];name=sys.argv[2]
 if mode=='probe':
  eng=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__)]);rows=[]
  for c,r,e in eng.run(candidates(),'probe'):
   p=purpose(c,r);print(c['id'],r.get('reason'),p,flush=True);rows.append(dict(case=c,result=r,purpose=p,evidence=e))
  (eng.out/'probe-results.json').write_text(json.dumps(rows))
 else:run(name,[dict(recipe=RECIPE)],1,library_root=ROOT/'results'/name/'CandidateLibrary',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'export-v4.mjs'],export_script=HERE/'export-v4.mjs')
if __name__=='__main__':main()
