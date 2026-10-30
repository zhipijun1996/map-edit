"""Observe height and stop horizontal drift before the refund ascent."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review031_v1 import rows,axis
from .prepare_review_refresh_v1 import at,end
def height(y,direction='lte'):return dict(op='wait',observed_y=dict(direction=direction,value=y),trigger=dict(state='observed_height',timeout=240))
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v3-cases.json',dict(cases=cs))
 for c in cs:
  if n=='197':
   p=c['control_plan'];i=next(i for i,v in enumerate(p)if v['op']=='shoot');p[i-1]=height(660,'gte')
  if n=='200'and c['route_spec']['from_port']=='entry':
   c['control_plan']=at(80,484)+[axis(1),cmd('jump'),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=145),timeout=120)),axis(0),height(350),cmd('jump_release'),cmd('shoot',aim_cell=dict(kind='enemy',id='ammo-sentry')),height(235),dict(op='shoot',direction=[.5,.866025403784],trigger=dict(state='shot_ready',timeout=90))]+at(30,100)+end(-104,100)
  c['id']=c['id'].replace('review031-v1','review031-v3').replace('review031-v2','review031-v3')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for r in rows():
  if r['reviewId']in ('197','200'):apply(r)
