"""Two visible receivers compete for the ground shot versus the single air shot."""
import copy,json,sys
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.counterexamples import alternatives as standard_alts
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent
RECIPE='ordered-target-transaction'
def candidates():
 out=[]
 for hold,shot in [(12,18),(14,20),(16,22),(18,24)]:
  c=base(f'ordered-target-v1-{hold}-{shot}');c['family']=RECIPE;c['production_recipe']=RECIPE
  c['platforms'] += [[290,250,160,70],[-400,800,1500,60]]
  c['latches']=[dict(id='resource-order',bell=[20,350],gate=[280,-500,24,750],open_seconds=0,sequence_offset=[120,80])]
  c['rule_parameters']=dict(relationship='both targets visible and hittable at entry; swapping the same two accepted projectile targets changes real final gate state; partial first-target progress persists',first=[20,350],second=[140,430],both_entry_visible=True)
  reward(c,365,232,16)
  p=[cmd('shoot',aim_cell=dict(kind='bell',id='resource-order')),cmd('axis',value=1,after=20),wait_x(140),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot-hold,aim_cell=dict(kind='bell',id='resource-order',receiver='second')),settle(365,6)]
  finish(c,365,232,p);c['trace_all']=True;c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule'].update(source_type='llm_subagent_proposal',author_task='/root/resource_routes_creator')
  out.append(c)
 return out

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
 opens=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open']
 primed=any(any(b.get('sequence_step')==1 and not b.get('open')for b in f.get('plains',{}).get('bells',[]))for f in fs)
 air_unlock=bool(opens and any(not f['grounded']and f['frame']<=opens[0]['frame']<=f['frame']+25 for f in shots))
 p['causal'].update(real_primed_state=primed,real_air_unlock=air_unlock,actual_air_shots=sum(not f['grounded']for f in shots))
 if not(primed and opens):p['reasons'].append('ordered_persistent_target_transaction_missing')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=standard_alts(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i in range(6):
  p=copy.deepcopy(c['control_plan']);p[0]['aim_cell']['receiver']='second';p[5]['aim_cell'].pop('receiver',None);p[4]=cmd('jump_release',8+i*4)
  add('swapped-resource-order-'+str(i),p)
 for delay in [8,20,30]:
  add('both-ground-'+str(delay),[cmd('shoot',aim_cell=dict(kind='bell',id='resource-order')),cmd('shoot',delay,aim_cell=dict(kind='bell',id='resource-order',receiver='second')),cmd('axis',value=1),wait_x(140),cmd('jump'),cmd('jump_release',20),settle(365,6)])
 for delay in [18,30,45]:
  add('correct-ground-order-plus-air-shot-'+str(delay),[cmd('shoot',aim_cell=dict(kind='bell',id='resource-order')),cmd('shoot',delay,aim_cell=dict(kind='bell',id='resource-order',receiver='second')),cmd('axis',value=1,after=18),wait_x(140),cmd('jump'),cmd('jump_release',16),cmd('shoot',8,direction=[-.5,.8660254037844386]),settle(365,6)])
  add('wrong-order-then-recover-'+str(delay),[cmd('shoot',aim_cell=dict(kind='bell',id='resource-order',receiver='second')),cmd('shoot',delay,aim_cell=dict(kind='bell',id='resource-order')),cmd('axis',value=1,after=20),wait_x(140),cmd('jump'),cmd('jump_release',16),cmd('shoot',8,aim_cell=dict(kind='bell',id='resource-order',receiver='second')),settle(365,6)])
 return out

def spec():
 c=candidates()[0]
 return dict(schema='map-notes/challenge-specification/v1',id='creative/resource-routes/ordered-target-transaction/v1',region='plains',required_family=RECIPE,objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=188,space=dict(max_width=2200,max_height=1800,max_port_span_x=1000),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=16,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
def compiler(req):
 s=spec();cs=candidates()
 for c in cs:c['map_specification']=s;c['idea_ids']=['resource-routes/ordered-target-transaction/v1']
 return dict(status='requires_physics',specifications=[s],cases=cs)
def main():
 mode=sys.argv[1];name=sys.argv[2]
 if mode=='probe':
  eng=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),HERE/'runner-v2.gd'],runner_script=HERE/'runner-v2.gd');rows=[]
  for c,r,e in eng.run(candidates(),'probe'):
   p=purpose(c,r);print(c['id'],r.get('reason'),p,flush=True);rows.append(dict(case=c,result=r,purpose=p,evidence=e))
  (eng.out/'probe-results.json').write_text(json.dumps(rows))
 else:run(name,[dict(recipe=RECIPE)],1,library_root=ROOT/'results'/name/'CandidateLibrary',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'runner-v2.gd',HERE/'export-v4.mjs'],runner_script=HERE/'runner-v2.gd',export_script=HERE/'export-v4.mjs')
if __name__=='__main__':main()
