"""Contact embedding of the preserved R2 exploration graph, no corridor edges."""
import argparse,json,time
from pathlib import Path
from pcg.map_directed.director import REPO

def solve(name,seconds=45,seed=0,graph=None,content_constraints=None,settings=None):
 from ortools.sat.python import cp_model
 source=REPO/'experiments/l4-mapgen/results/region-network-v2/runs.json'
 graph=graph or next(r for r in json.loads(source.read_text())['runs']if r['region']=='plains'and str(r['seed'])=='0')['exploration_graph']
 content_constraints=content_constraints or {}
 settings=settings or {}
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_contact_layout_exists')
 out.mkdir(parents=True)
 m=cp_model.CpModel();rooms={};xs=[];ys=[]
 for node in graph['nodes']:
  key=node['id'];x=m.new_int_var(0,28,key+'/x');y=m.new_int_var(0,28,key+'/y')
  need=content_constraints.get(key,{})
  w=m.new_int_var(need.get('min_w',2 if key in ['r5','r10','r6','r12'] else 1),need.get('max_w',6),key+'/w');h=m.new_int_var(need.get('min_h',3 if key in ['r5','r10','r6','r12'] else 2),need.get('max_h',5),key+'/h')
  r=m.new_int_var(2,36,key+'/r');b=m.new_int_var(2,34,key+'/b')
  m.add(r==x+w);m.add(b==y+h)
  xs.append(m.new_interval_var(x,w,r,key+'/xrange'));ys.append(m.new_interval_var(y,h,b,key+'/yrange'))
  rooms[key]=(x,y,w,h,r,b)
 m.add_no_overlap_2d(xs,ys)
 for edge in graph['edges']:
  a=rooms[edge['from']];b=rooms[edge['to']];directions=[m.new_bool_var(edge['id']+'/'+str(i))for i in range(4)]
  m.add_exactly_one(directions)
  for i,d in enumerate(directions):
   if i==0:m.add(a[4]==b[0]).only_enforce_if(d)
   if i==1:m.add(b[4]==a[0]).only_enforce_if(d)
   if i in [0,1]:
    m.add(a[1]+1<=b[5]).only_enforce_if(d);m.add(b[1]+1<=a[5]).only_enforce_if(d)
    if content_constraints.get(edge['from'],{}).get('side_ports_at_base'):m.add(a[5]<=b[5]).only_enforce_if(d)
    if content_constraints.get(edge['to'],{}).get('side_ports_at_base'):m.add(b[5]<=a[5]).only_enforce_if(d)
   if i==2:m.add(a[5]==b[1]).only_enforce_if(d)
   if i==3:m.add(b[5]==a[1]).only_enforce_if(d)
   if i in [2,3]:
    m.add(a[0]+1<=b[4]).only_enforce_if(d);m.add(b[0]+1<=a[4]).only_enforce_if(d)
 maxx=m.new_int_var(1,36,'maxx');maxy=m.new_int_var(1,34,'maxy');m.add_max_equality(maxx,[r[4]for r in rooms.values()]);m.add_max_equality(maxy,[r[5]for r in rooms.values()])
 # Existing ideal points are a search hint only, not corridors or a fixed road.
 if 'boss' in rooms and settings.get('boss_at_top',True):m.add(rooms['boss'][1]==0)
 m.minimize((maxx+maxy)*1000+sum(r[2]+r[3]for r in rooms.values()))
 solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=settings.get('workers',8);solver.parameters.random_seed=seed
 if settings.get('deterministic_budget') is not None:solver.parameters.max_deterministic_time=settings['deterministic_budget']
 start=time.perf_counter();status=solver.solve(m)
 result={'units':settings.get('units',[448,192]),'schema':'pcg/direct-room-contact-layout/v1','source_graph':graph,'status':solver.status_name(status),'wall_seconds':time.perf_counter()-start,'solver':'OR-Tools CP-SAT','seed':seed,'budget_seconds':seconds,'corridors':[],'settings':settings}
 if content_constraints:result['content_constraints']=content_constraints
 if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
  result['rooms']={k:{'x':solver.value(r[0]),'y':solver.value(r[1]),'w':solver.value(r[2]),'h':solver.value(r[3])}for k,r in rooms.items()}
  result['objective']=solver.objective_value
 (out/'layout.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['status'],result.get('rooms'),flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=45);a=p.parse_args();solve(a.name,a.seconds)
