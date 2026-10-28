"""Real LLM-authored local causal proposals; frozen v1."""
import copy,json,math,sys
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish,ground
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.counterexamples import alternatives as standard_alts
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent
RECIPES=['sightline-backtrack','sequence-spatial-lock','drop-key-late-recoil','trapdoor-commit']
def candidates(recipe):
 out=[]
 for k in range(4):
  c=base(recipe+'-v4-'+str(k));c['production_recipe']=recipe;c['family']=recipe;c['trace_all']=True
  if recipe=='sightline-backtrack':
   c['platforms']=[[-480,438,1100,100],[140,340,60,98],[-310,-600,30,900]]
   c['latches']=[dict(id='remote-key',bell=[420,402],gate=[-310,300,30,138],open_seconds=0)]
   c['rule_parameters']=dict(relationship='leave exit direction, cross opaque screen to expose ray, permanently open remote exit then backtrack',screen=[140,340,60,98],peek_x=280)
   reward(c,-400,420,12)
   p=[cmd('axis',value=1),wait_x(105),cmd('jump'),cmd('jump_release',12+k*2),wait_x(285),cmd('axis',value=0),dict(op='wait',trigger=dict(state='grounded',after=20,timeout=150)),cmd('shoot',4,aim_cell=dict(kind='bell',id='remote-key')),cmd('axis',value=-1,after=20),wait_x(240,-1),cmd('jump'),cmd('jump_release',10),settle(-400,20)]
   finish(c,-400,420,p);c['exit_normal']=[-1,0]
  elif recipe=='sequence-spatial-lock':
   c['platforms']=[[-160,438,1100,100],[310,340,65,98],[560,-350,30,650]]
   c['latches']=[dict(id='ordered-key',bell=[180,400],gate=[560,300,30,138],open_seconds=0,sequence_offset=[290,0],sequence_gate=[230,180,26,258])]
   c['rule_parameters']=dict(relationship='first permanent sequence gate reveals locomotion route to second receiver; original ordered transaction',first_station=80,second_station=440)
   reward(c,720,420,16)
   p=[cmd('shoot',aim_cell=dict(kind='bell',id='ordered-key')),cmd('axis',value=1,after=18),wait_x(275),cmd('jump'),cmd('jump_release',18+k*2),wait_x(440),cmd('axis',value=0),dict(op='wait',trigger=dict(state='grounded',after=24,timeout=200)),cmd('shoot',6,aim_cell=dict(kind='bell',id='ordered-key',receiver='second')),settle(720,20)]
   finish(c,720,420,p)
  elif recipe=='drop-key-late-recoil':
   c['platforms']=[[-160,180,400,100],[300,440,150,80],[-400,950,1400,80]]
   c['spawn']=[180,162];c['entry_port']=[180,162]
   c['latches']=[dict(id='under-key',bell=[160,800],gate=[300,280,150,160],open_seconds=0)]
   c['rule_parameters']=dict(relationship='fall below occluding lip to acquire low ray, shoot downward and recoil upward onto gated side pocket',lip=[-160,180,400,100])
   reward(c,385,422,14)
   p=[cmd('axis',value=1),wait_x(265),cmd('axis',value=0),cmd('wait',34+k*2),cmd('shoot',aim_cell=dict(kind='bell',id='under-key')),settle(385,6)]
   finish(c,385,422,p)
  else:
   c['platforms']=[[-160,438,400,310],[430,438,400,310],[180,-500,120,890],[240,718,190,70]]
   c['latches']=[dict(id='bridge-key',bell=[370,245],gate=[240,438,190,20],open_seconds=0)]
   c['rule_parameters']=dict(relationship='stand on removable bridge to see occluded receiver; same accepted shot removes own support and commits to lower shaft',bridge=[240,438,190,20],screen=[180,-500,120,890])
   reward(c,335,700,14)
   p=[cmd('axis',value=1),wait_x(325+k*8),cmd('axis',value=0),cmd('shoot',4,aim_cell=dict(kind='bell',id='bridge-key')),settle(335,6)]
   finish(c,335,700,p)
  c['production_recipe']=recipe;c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule'].update(source_type='llm_subagent_proposal',author_task='/root/resource_routes_creator')
  out.append(c)
 return out

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);ev=r.get('plains',{}).get('events',[]);recipe=c['production_recipe']
 shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
 opens=[e for e in ev if e['type']=='bell_open']
 if recipe=='sightline-backtrack':
  hit=opens[0]['frame']if opens else None
  expose=any(f['x']>220 for f in fs if hit is not None and f['frame']<=hit)
  after=any(f['x']<0 for f in fs if hit is not None and f['frame']>hit)
  p['causal'].update(real_remote_open=hit,exposed_right_station=expose,returned_left_after_unlock=after)
  if not(hit is not None and expose and after):p['reasons'].append('remote_sightline_backtrack_not_demonstrated')
 elif recipe=='sequence-spatial-lock':
  steps=[f for f in fs if any(b.get('sequence_step')==1 for b in f.get('plains',{}).get('bells',[]))]
  before=any(f['x']<230 for f in steps);after=any(f['x']>375 for f in steps)
  p['causal'].update(first_sequence_frames=len(steps),pre_second_gate_crossing=before and after,final_open=bool(opens))
  if not(opens and before and after):p['reasons'].append('ordered_spatial_unlock_not_demonstrated')
 elif recipe=='drop-key-late-recoil':
  below=bool(shots and shots[0]['y']-18>280)
  rise=bool(shots and any(f['y']<shots[0]['y']-30 for f in fs if f['frame']>shots[0]['frame']))
  p['causal'].update(shot_body_below_lip=below,recoil_rise_after_shot=rise,opened=bool(opens))
  if not(below and rise and opens):p['reasons'].append('low_ray_then_recoil_return_missing')
 else:
  hit=opens[0]['frame']if opens else None
  at_hit=next((f for f in fs if hit is not None and f['frame']==hit),None)
  support_removed=bool(hit is not None and any(not f['grounded'] and f['y']>470 for f in fs if f['frame']>hit))
  fired_over_bridge=bool(shots and 252<shots[0]['x']<418 )
  p['causal'].update(bridge_shot_grounded=fired_over_bridge,drop_after_real_open=support_removed)
  if not(fired_over_bridge and support_removed):p['reasons'].append('self_support_removal_missing')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=standard_alts(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for delay in [0,12,30]:
  for receiver in ['primary','second']if c['production_recipe']=='sequence-spatial-lock'else['primary']:
   q=dict(kind='bell',id=c['latches'][0]['id'])if c['latches']else None
   if receiver=='second':q['receiver']='second'
   if q:add('preopen-'+receiver+'-'+str(delay),[cmd('shoot',delay,aim_cell=q),settle(c['exit_port'][0],24)])
 if c['production_recipe']=='sequence-spatial-lock':
  add('second-first-order',[cmd('shoot',aim_cell=dict(kind='bell',id='ordered-key',receiver='second')),cmd('shoot',24,aim_cell=dict(kind='bell',id='ordered-key')),settle(720,24)])
 if c['production_recipe']=='sightline-backtrack':
  for h in [8,20,30]:add('direct-left-jump-'+str(h),[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',h),settle(-400,10)])
 if c['production_recipe']=='sightline-backtrack':
  for x in [80,110,130]:
   for delay in [8,18]:
    add('early-jump-ray-'+str(x)+'-'+str(delay),[cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',12),cmd('shoot',delay,aim_cell=dict(kind='bell',id='remote-key')),settle(-400,18)])
 if c['production_recipe']=='trapdoor-commit':
  for x in [180,220,235,260,290]:
   add('outside-bridge-preopen-'+str(x),[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',4,aim_cell=dict(kind='bell',id='bridge-key')),settle(335,18)])
  for hold in [8,20,30]:
   add('air-open-'+str(hold),[cmd('axis',value=1),wait_x(200),cmd('jump'),cmd('jump_release',hold),cmd('shoot',10,aim_cell=dict(kind='bell',id='bridge-key')),settle(335,18)])
 return out

def specification(recipe):
 c=candidates(recipe)[0]
 return dict(schema='map-notes/challenge-specification/v4',id='creative/resource-routes/'+recipe+'/v4',region='plains',required_family=recipe,objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],c.get('exit_normal',[1,0])]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2200,max_height=1800,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=c['reward_sites'][0]['amount'],mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compile_request(req):
 recipe=req['recipe'];spec=specification(recipe);cs=candidates(recipe)
 for c in cs:c['map_specification']=spec;c['idea_ids']=['resource-routes/'+recipe+'/v4']
 return dict(status='requires_physics',specifications=[spec],cases=cs)
def main():
 mode=sys.argv[1]if len(sys.argv)>1 else'probe';name=sys.argv[2]if len(sys.argv)>2 else'workshop-creative-resource-routes-v4-probe'
 if mode=='probe':
  eng=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),HERE/'runner-v1.gd'],runner_script=HERE/'runner-v1.gd');rows=[]
  for c,r,e in eng.run([c for rec in RECIPES for c in candidates(rec)],'probe'):
   p=purpose(c,r);print(c['id'],r.get('reason'),p,flush=True);rows.append(dict(case=c,result=r,purpose=p,evidence=e))
  (eng.out/'probe-results.json').write_text(json.dumps(rows))
 else:run(name,[dict(recipe=x)for x in RECIPES],4,library_root=ROOT/'results'/name/'CandidateLibrary',compiler=compile_request,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'runner-v1.gd',HERE/'export-v2.mjs'],runner_script=HERE/'runner-v1.gd',export_script=HERE/'export-v2.mjs')
if __name__=='__main__':main()
