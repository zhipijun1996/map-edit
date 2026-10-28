"""Next bounded controls, original geometry and all attempts retained."""
import copy,shutil,inspect,math,re
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from .probe_review_refresh_v1 import AUTH
from .prepare_review_refresh_v1 import at,end,leap
from .repair_review_refresh_v3 import gunhop,engage
IDS={'122','150','157','159'}
def prepare(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v6';before.mkdir(parents=True,exist_ok=False)
 for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
 doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract']
 for c in cases:
  z=next(p for p in g['ports']if p['id']==c['route_spec']['to_port']);x,y=z['stagingPosition'];p=copy.deepcopy(c['control_plan'][:-3]);c['id']+='-control-v6';c['max_frames']=3600
  if n=='122':
   if c['route_spec']['from_port']=='entry':p[16]['requires_saw_phase']['window']=[.55,.7];p[16]['trigger']['timeout']=2200
  elif n in('150','159'):
   levels=sorted([o for o in doc['objects']if re.search(r'/platform-\d+$',o['id'])],key=lambda o:int(o['id'].split('-')[-1]));p=at(60,levels[0]['y']-18);hx=60;hy=levels[0]['y']-18;done=set()
   for i,o in enumerate(levels[1:],1):
    for e in c['enemies']:
     if e['definition']!='plains_sentry'or e['id']in done:continue
     if abs(e['position'][1]+16-o['y'])<.1:
      if n=='150'and e['id']=='design-ground-enemy-3':continue
      p+=engage(e,hx,hy,o['y']-36);done.add(e['id'])
    if n=='150'and i==8:
     # Recoil up through the existing one-way shelf, then defeat the lower
     # guard from above instead of firing a projectile inside an upper shelf.
     p+=gunhop(190,757,190,607,680,[0,1],stationary=True)+at(135,607)
     e=next(e for e in c['enemies']if e['id']=='design-ground-enemy-3');p+=engage(e,135,607,550);done.add(e['id']);hx,hy=135,607;continue
    xx=o['x']+o['w']/2;yy=o['y']-18
    p+=gunhop(595,hy,xx,yy,400,[-math.sqrt(1-.25**2),.25])if i==len(levels)-1 else leap(xx,yy);hx,hy=xx,yy;p+=at(hx,hy)
    if n=='159':
     if i==4:p+=engage(c['enemies'][3],690,yy,1680);p+=at(hx,hy)
     elif i==12:p+=engage(c['enemies'][4],710,yy,960);p+=at(hx,hy)
     elif i==16:p+=engage(c['enemies'][5],50,yy,600);p+=at(hx,hy)
  elif n=='157':p=at(85,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.15,.17]),timeout=600))]+gunhop(145,282,370,282,235,[-math.sqrt(1-.04**2),.04])+gunhop(370,282,690,282,235,[-math.sqrt(1-.04**2),.04])
  c['control_plan']=p+end(x,y);assert len(c['control_plan'])<=384,(n,len(c['control_plan']))
 doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
 core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',params);print(n,'control-v6',flush=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in IDS:prepare(r)
