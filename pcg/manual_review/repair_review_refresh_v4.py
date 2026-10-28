"""Bounded control repair; no approved geometry changes."""
import copy,math,shutil,inspect,re
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review_refresh_v1 import at,end,leap
from .repair_review_refresh_v3 import gunhop,engage
from .probe_review_refresh_v1 import AUTH
IDS={'116','119','122','123','125','148','150','154','157','159'}
def prepare(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v4';before.mkdir(parents=True,exist_ok=False)
 for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
 doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract']
 for c in cases:
  a,z=[next(p for p in g['ports']if p['id']==c['route_spec'][k])for k in('from_port','to_port')];x,y=z['stagingPosition'];p=copy.deepcopy(c['control_plan'][:-3]);c['id']+='-control-v4'
  if n=='116':
   tail=copy.deepcopy(p[32:]);p=engage(c['enemies'][0],175,282,230,5)+tail
  elif n=='119':p=gunhop(90,282,285,282,250,[-1,0],stationary=True)+gunhop(315,282,520,282,250,[-1,0],stationary=True)+gunhop(560,282,770,282,250,[-1,0],stationary=True)
  elif n=='122':
   if a['id']=='entry':p[16]['requires_saw_phase']['window']=[.85,1.0];p[16]['trigger']['timeout']=1200
  elif n=='123':
   for v in p:
    if v['op']=='shoot':v['direction']=[-math.sqrt(1-.22**2),.22]
  elif n=='125':
   if a['id']in('entry','fork_right')and z['id']in('fork_up','C'):
    for v in reversed(p):
     if v['op']=='shoot':v['direction']=[-math.sqrt(1-.75**2),.75];break
  elif n=='148':p=p[:62]+gunhop(400,182,550,154,145,[-math.sqrt(1-.1**2),.1])
  elif n=='150':
   for v in p:
    if v.get('aim_cell',{}).get('id')=='design-ground-enemy-3':v['aim_cell']['body_offset']=[0,-12]
  elif n=='154':p=gunhop(145,282,335,282,250,[-1,0],stationary=True)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[0,.1]),timeout=480))]+gunhop(335,282,520,282,235,[-math.sqrt(1-.04**2),.04])+gunhop(545,282,735,282,250,[-1,0],stationary=True)
  elif n=='157':
   # Safe waiting regions outside the full sweep; burst clips the jump to 224px.
   def cross(s,t,saw,window):return at(s,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=saw,window=window),timeout=600))]+gunhop(s,282,t,282,235,[-math.sqrt(1-.04**2),.04])
   p=cross(85,370,c['saws'][0]['source_id'],[.55,.56])+cross(370,680,c['saws'][1]['source_id'],[.4,.42])
  elif n=='159':
   # Engage divers before entering their activation band; same real gun/jump resources.
   for i,v in enumerate(p):
    if v['op']=='jump'and i>0 and p[i-1].get('target_x')in(370.0,190.0):pass
   levels=sorted([o for o in doc['objects']if re.search(r'/platform-\d+$',o['id'])],key=lambda o:int(o['id'].split('-')[-1]));p=at(60,levels[0]['y']-18);done=set();hx=60;hy=levels[0]['y']-18
   for i,o in enumerate(levels[1:],1):
    for e in c['enemies']:
     if e['id']in done:continue
     ground=e['definition']=='plains_sentry'and abs(e['position'][1]+16-o['y'])<.1
     air=e['definition']=='plains_diver'and hy<=e['position'][1]+210 and abs(hx-e['position'][0])<350
     if ground or air:
      p+=engage(e,hx,hy,(o['y']-36 if ground else hy-90));done.add(e['id'])
    xx=o['x']+o['w']/2;yy=o['y']-18;p+=gunhop(595,hy,xx,yy,400,[-math.sqrt(1-.25**2),.25])if i==len(levels)-1 else leap(xx,yy);hx,hy=xx,yy;p+=at(hx,hy)
  c['control_plan']=p+end(x,y);c['max_frames']=4800 if n in('122','159')else 3200;assert len(c['control_plan'])<=384,(n,len(c['control_plan']))
 doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
 core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',params);print(n,'control-v4',flush=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in IDS:prepare(r)
