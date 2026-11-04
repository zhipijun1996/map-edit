"""Third bounded control revision; observe native phases, preserve geometry."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review029_v1 import AUTH,at,end
from .prepare_review_refresh_v1 import leap
from .repair_review029_v2 import axis

def phase(id,window):return [dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=id,window=window),timeout=900))]
def on(id):return [dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id=id),timeout=240)),axis(0)]
def shoot(id,after=0,**kw):return cmd('shoot',after,aim_cell=dict(kind='bell',id=id,**kw))
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];doc=core.read(f/'module.mapnote.json');cases=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v3-cases.json',dict(cases=cases))
 for c in cases:
  if n=='179':
   c['control_plan']=at(190,168)+[axis(1),dict(op='wait',trigger=dict(state='observed_height',timeout=240),observed_y=dict(direction='gte',value=470)),cmd('shoot',direction=[-.5,.8660254])]+end(616,552)
  elif n=='175':
   c['control_plan']=at(700,420)+leap(800,372,release=330)+[shoot('key-control')]+phase('key-carrier',[.12,.14])+[shoot('key-control')]+at(1065,420)+[shoot('key-control')]+at(1080,420)+phase('key-carrier',[.27,.29])+[axis(1),cmd('jump'),cmd('jump_release',10)]+on('key-carrier')+[dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=900),carrier_id='key-carrier',carrier_value=1430),axis(1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-.97,.243])]+at(1770,420)+end(1896,420)
  elif n=='176':
   c['control_plan']=at(210,420)+leap(330,421,release=340)+[shoot('carrier-bell')]+on('chase-carrier')+[dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=900),carrier_id='chase-carrier',carrier_value=475),axis(1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=520),timeout=180)),cmd('jump'),cmd('jump_release',12),shoot('carrier-bell',6,receiver='access')]+at(848,292)+end(872,292)
  elif n=='193'and c['route_spec']['from_port']=='exit':
   c['control_plan']=at(1370,420)+phase('carrier',[.42,.44])+leap(1050,420,release=320,shot=[.97,.243])+at(1030,420)+leap(730,227,shot=[.5,.8660254])+at(730,227)+phase('carrier',[.8,.82])+[axis(-1),cmd('jump'),cmd('jump_release',8)]+on('carrier')+[cmd('wait',12),axis(-1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[.97,.243])]+end(152,420)
  for v in c['control_plan']:
   if v['op']=='axis':v['cancel_settle']=True
  c['id']=c['id'].replace('review029-v1','review029-v3').replace('review029-v2','review029-v3')
 doc=godot_package.bind_case_behavior(doc,cases);core.write(f/'cases.json',dict(cases=cases));core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
