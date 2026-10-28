"""Bounded regional demand adapter over the existing multiport producer.

Recoil spires replace real carrier transfers with measured vertical-shot action
cores. Intermediate ledges are challenge content owned by this Macro, never
Map-added connector pads. All changed geometry/timing needs whole-world re-test.
"""
import copy,json
from .room_modules import generate as room_generate,routes
from .synthesis import command
from ..factory.core.quality import digest
from .engine import ROOT

def generate(spec):
 m=routes(room_generate(spec));c=m['case'];base=spec['space']['core_bounds'][3]-64
 for ferry in c['moving_platforms']:
  ferry['travel_duration']=1.8;ferry['dwell_duration']=1.2
 # Uneven solid roots only under safe base terrain. Downward exports retain
 # their actual void. Bounds never imply an enclosing collision shell.
 voids=[(p['column_x']-144,p['column_x']+144)for p in m['ports'].values()if p['kind']=='vertical'and p['normal'][1]>0]
 for lo,hi,idx in m['floors'][base]:
  cursor=lo;spans=[(lo,hi)]
  for a,b in voids:
   spans=[part for x,y in spans for part in [(x,min(a,y)),(max(x,b),y)]if part[1]-part[0]>24]
  for x,y in spans:
   for i,(a,b)in enumerate([(0,.23),(.23,.62),(.62,1)]):
    width=(y-x)*(b-a)
    c['platforms'].append([x+(y-x)*a,base+34,width,[18,28,10][i]])
 old=json.loads((ROOT/'results/direct-vertical-bell-v2/selected.json').read_text())['case']
 spires={}
 for column in m['columns']:
  if column['id']not in spec.get('recoil_spires',[]):continue
  if column['level']!=0:raise ValueError('recoil_spire_requires_declared_vertical_export/'+m['id'])
  c['moving_platforms']=[f for f in c['moving_platforms']if f['platform_id']!=column['id']]
  # Keep original horizontal port contact. New intermediate support is inside
  # this Macro's actual reserved shaft. The last landing is the shared export.
  p=m['ports'][column['port']];bearing=p['bearing'];entry=column['right']if bearing>0 else column['left']
  source=copy.deepcopy(entry);program=[];levels=[];remaining=base
  while remaining>0:
   remaining=max(0,remaining-180);levels.append(remaining)
  for i,level in enumerate(levels):
   last=i==len(levels)-1
   if last:dest=copy.deepcopy(p['dock'])
   else:
    x=column['x']+bearing*(24 if i%2 else -24)
    idx=len(c['platforms']);c['platforms'].append([column['x']-80,level+18,160,16]);c['one_way_platform_indices'].append(idx)
    dest=dict(id=m['id']+'/recoil/'+column['id']+'/'+str(i),position=[x,level],region=[x-8,level-4,16,8],support_indices=[idx],grounded=True)
   # Inputs stay the measured kernel; settle handles the exact requested exit.
   plan=copy.deepcopy(old['control_plan']);plan[-1]['target_x']=dest['position'][0]
   plan.insert(0,command('wait',20))
   bell_id='spire-'+column['id']+'-'+str(i)
   ox=source['position'][0]-80;oy=source['position'][1]-420
   raw=copy.deepcopy(old['latches'][0]);raw.update(id=bell_id,bell=[old['latches'][0]['bell'][0]+ox,old['latches'][0]['bell'][1]+oy],
    gate=[column['x']+bearing*52-8,max(20,level-82),16,100],open_seconds=0)
   c['latches'].append(raw)
   program.append(dict(kind='module',target=dest,control_plan=plan,budget_ticks=720,action_intent='airborne downward bell shot couples ascent with opening receiver'))
   source=dest
  spires[column['id']]=program
 # Replace only the actual ascent; every descent/crossing is independently
 # materialized below. A removed carrier must never remain in a route policy.
 def convert(values):
  result=[]
  for leg in values:
   transfer=leg.get('carrier_transfer',{});key=transfer.get('id')
   # A gallery crossing a non-serving shaft is an explicit timed jump, not
   # a blind hop under the parked upper carrier. No terrain is added here.
   cross_column=next((col for col in m['columns']if leg['kind']=='jump'and '/cross/'+col['id']+'/'in leg['target']['id']),None)
   if cross_column is not None and cross_column['id']not in spires:
    tx,level=leg['target']['position'];sx=2*cross_column['x']-tx
    support=next(i for lo,hi,i in m['floors'][level]if lo+12<=sx<=hi-12)
    source=dict(id=m['id']+'/phase-observation/'+cross_column['id'],position=[sx,level],region=[sx-8,level-4,16,8],support_indices=[support],grounded=True)
    phase=.5 if abs(level-base)<abs(level-cross_column['level'])else 0.
    result.append(dict(kind='module',target=source,control_plan=[command('axis',value=0),dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=cross_column['id'],window=[phase,phase+.03]),timeout=360))],budget_ticks=720))
    result.append(leg);continue
   if key not in spires:result.append(leg);continue
   if transfer['mode']=='ascend':result+=copy.deepcopy(spires[key])
   elif transfer['mode']=='cross':result.append(dict(kind='jump',target=copy.deepcopy(leg['target']),hold_ticks=20))
   else:raise ValueError('unresolved_spire_transfer_mode/'+str(transfer))
  return result
 for group in ['center_to_port','port_to_center']:
  m[group]={eid:convert(v)for eid,v in m[group].items()}
  for values in m[group].values():
   for leg in values:
    if leg['kind']=='walk':
     leg.update(kind='module',control_plan=[command('axis',value=0),command('settle',target_x=leg['target']['position'][0],deadband=4)],budget_ticks=720)
 m['origin']='Regional content demand: existing multiport generator, source-owned open roots, real recoil spires and retimed original carriers'
 m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
 return m
