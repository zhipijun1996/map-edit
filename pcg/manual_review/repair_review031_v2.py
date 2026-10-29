"""Remove an unnecessary exposed wait on 200's independently authored descent."""
from pcg.migration import core,godot_package
from .prepare_review031_v1 import rows,axis
from .prepare_review_refresh_v1 import end
def run(row):
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['from_port']=='exit':
   c['control_plan']=[axis(1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=150),timeout=180)),axis(0),dict(op='wait',trigger=dict(state='observed_height',timeout=120),observed_y=dict(direction='gte',value=224))]+end(-104,484)
  c['id']=c['id'].replace('review031-v1','review031-v2')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for r in rows():
  if r['reviewId']=='200':run(r)
