"""Shared-geometry three-port forks, route-specific evidence and continuous rejoin."""
import argparse,copy,json,collections,time
from pathlib import Path
from .engine import ROOT,PlainsEngine
from .synthesis import command,identity
from .evaluation import instantiate,purpose,observed
from ..factory.core.quality import digest,module_hash,counts,POLICY
GEOMETRY_KEYS=('capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports')
def geometry_hash(c):return digest({k:c.get(k,[])for k in GEOMETRY_KEYS})
def wait_x(x,direction):return dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=x),timeout=180))
def ground():return dict(op='wait',trigger=dict(state='grounded',timeout=180))
def settle(x):return command('settle',target_x=x,deadband=4)
def gear_cross(x,gear,direction):
 approach=gear-direction*78
 return [settle(approach),wait_x(approach-direction*5,direction),ground(),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='fork_gear',window=[.20,.25]),timeout=190)),settle(x)]
def layouts(bases):
 source=sorted((e for e in bases if e['case']['family']=='bell_lift'),key=lambda e:identity(e['case']))[:2];out=[]
 for entry in source:
  for offset in (125,175):
   base=copy.deepcopy(entry['case']);upper=base['exit_port'][:];low=[upper[0]+offset+130,420];a=[80,420]
   base['platforms'][0]=[-120,438,low[0]+200,60]
   base['saws']=[dict(source_id='fork_gear',origin=[upper[0]+offset,408],travel=[0,-115],radius=16,period=2.4,initial_phase=0)]
   base['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=low,normal=[1,0],support_index=0),dict(id='C',position=upper,normal=[1,0],support_index=1)]
   base['family']='plains_three_port_fork';base['synthesis']=dict(method='generated_recoil_landing_plus_low_route_and_measured_branch',parent_uid=identity(entry['case']),prefab_modules=0,lower_gear_offset=offset,reward_placement='UNKNOWN: high port is a reward-branch opportunity, no pickup/reward service instantiated')
   base['id']='fork-'+geometry_hash(base)[:12];out.append(base)
 return out

def route_cases(layout):
 a,b,c=[p['position']for p in layout['ports']];gx=layout['saws'][0]['origin'][0];upper_right=layout['platforms'][1][0]+layout['platforms'][1][2]
 upper=copy.deepcopy(layout['control_plan']);low_main=gear_cross(b[0],gx,1)
 descend=[settle(upper_right+45),wait_x(upper_right+25,1),ground()]
 ret=gear_cross(a[0],gx,-1);upper_back=descend+[settle(a[0])]
 approach_upper=copy.deepcopy(upper);approach_upper[0]=settle(10000)
 approach=ret+[wait_x(a[0]+5,-1),command('wait',30)]+approach_upper
 programs=[('main','A','B','main',low_main,False,[]),('upper','A','C','reward',upper,True,[]),('upper_rejoin','A','B','reward',upper+[ground()]+descend+gear_cross(b[0],gx,1),True,['C']),('return_main','B','A','return',ret,False,[]),('drop_to_main','C','B','recovery',descend+gear_cross(b[0],gx,1),False,[]),('return_upper','C','A','return',upper_back,False,[]),('approach_upper','B','C','recovery',approach,True,[])]
 out=[];ps={p['id']:p for p in layout['ports']}
 for rid,fr,to,role,plan,bell,via in programs:
  x=copy.deepcopy(layout);p=ps[to]['position'];x.update(id=layout['id']+'-'+rid,spawn=ps[fr]['position'][:],entry_port=ps[fr]['position'][:],exit_port=p[:],entry_normal=ps[fr]['normal'][:],exit_normal=ps[to]['normal'][:],goal=[p[0]-26,p[1]-24,52,48],control_plan=plan,max_frames=900,trace_all=False,route_spec=dict(id=rid,from_port=fr,to_port=to,role=role,require_bell=bell,via_ports=via),layout_uid=geometry_hash(layout))
  x['challenge_requirements']=dict(min_shots=int(bell),min_ground_jumps=int(bell));out.append(x)
 assert len({geometry_hash(c)for c in out})==1
 return out

def port_purpose(c,r):
 checked=copy.deepcopy(c)
 if not c['route_spec']['require_bell']:checked['latches']=[]
 p=purpose(checked,r)
 # Main/return routes may deliberately require zero shots; generic plains
 # scoring assumes a recoil challenge and must not invent that requirement.
 if not c['route_spec']['require_bell']:p['reasons']=[s for s in p['reasons']if s!='no_recoil_executed']
 ps={v['id']:v for v in c['ports']};visits={}
 for key in c['route_spec']['via_ports']:
  x,y=ps[key]['position'];found=[f['frame']for f in r.get('frames',[])if f['grounded']and abs(f['x']-x)<=28 and abs(f['y']-y)<=1]
  visits[key]=found[0]if found else None
  if not found:p['reasons'].append('missing_actual_via_port_'+key)
 p['visited_ports']=visits;p['ok']=not p['reasons'];return p

def pilot(name,bases):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);ls=layouts(json.loads((ROOT/'results'/bases/'qualified.json').read_text()));cs=[c for l in ls for c in route_cases(l)];rows=[]
 (out/'protocol.json').write_text(json.dumps(dict(scope='Discovery only; same geometry for all routes',layouts=len(ls),route_programs=7,source_bases=bases,seed='not used: fixed enumeration'),indent=2))
 for c,r,ev in engine.run(cs,'three-port-discovery'):rows.append(dict(case=c,result=r,purpose=port_purpose(c,r),evidence=ev))
 summary=dict(layouts=len(ls),physics_cases=engine.sim.cases,route_passes=sum(x['purpose']['ok']for x in rows),rows=[dict(layout=x['case']['layout_uid'][:12],route=x['case']['route_spec']['id'],ok=x['purpose']['ok'],reasons=x['purpose']['reasons'])for x in rows])
 (out/'layouts.json').write_text(json.dumps(ls));(out/'rows.json').write_text(json.dumps(rows));(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--bases',default='plains-phrase-bases-v1');a=p.parse_args();pilot(a.name,a.bases)
