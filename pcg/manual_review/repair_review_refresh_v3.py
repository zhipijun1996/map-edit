"""Second bounded control repair: real gun timing, safe engagement and landing."""
import copy,math,re,shutil,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review_refresh_v1 import at,end,leap
from .probe_review_refresh_v1 import AUTH
IDS={'116','122','123','127','133','140','148','150','154','157','159'}
def gunhop(start,sy,target,ty,height,direction,stationary=False):
    p=at(start,sy)+([cmd('axis',value=0)]if stationary else[settle(target)])
    return p+[cmd('jump'),dict(op='shoot',height_threshold=height,direction=direction,trigger=dict(state='height_at_most',timeout=120)),settle(target),dict(op='wait',trigger=dict(state='grounded',migration_goal=[target-5,ty-4,10,8],timeout=480)),cmd('jump_release')]
def engage(enemy,hx,hy,shoot_height,cycles=5):
    p=at(hx,hy)
    for _ in range(cycles):
        pre=[cmd('axis',value=0),cmd('jump'),dict(op='shoot',height_threshold=shoot_height,aim_cell=dict(kind='enemy',id=enemy['id']),trigger=dict(state='height_at_most',timeout=100))]
        for v in pre:v['skip_if_enemy_dead']=enemy['id']
        p+=pre+at(hx,hy)+[cmd('jump_release'),cmd('wait',8)]
    return p

def prepare(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v3';before.mkdir(parents=True,exist_ok=False)
    for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract']
    for c in cases:
        a,z=[next(p for p in g['ports']if p['id']==c['route_spec'][k])for k in('from_port','to_port')];x,y=z['stagingPosition'];p=copy.deepcopy(c['control_plan']);c['id']+='-control-v3'
        if n=='116':
            c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_author_v3.py';c['refresh_carrier_warmup_frames']=2
            for o in doc['objects']:
                if o['type']=='enemy':o.setdefault('mechanics',{})['trackerWarmupPhysicsFrames']=2
            p=p[:-3]
        elif n=='122':
            if a['id']=='entry':
                p=p[:28];p[16]['requires_saw_phase']['window']=[.15,.35]
            elif a['id']=='exit':p=gunhop(976,420,900,380,380,[1,0],stationary=True)
            else:p=[]
        elif n=='123':
            p=p[:10]+[settle(720),cmd('jump'),dict(op='shoot',height_threshold=690,direction=[-math.sqrt(1-.1**2),.1],trigger=dict(state='height_at_most',timeout=100))]+at(720,682)+[cmd('jump_release')]
        elif n=='127':p=at(-35,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='design-central-vertical-gear',window=[.1,.2]),timeout=360))]+leap(300,282,release=145,shot=[-1,0])
        elif n=='133':p=gunhop(145,342,350,342,310,[-1,0],stationary=True)
        elif n=='140':
            p=p[:7];sgn=1 if a['id']=='entry'else-1;takeoff=310 if sgn==1 else 850;p[0]['target_x']=takeoff;p[1]['trigger']['migration_goal']=[takeoff-5,578,10,8]
            p +=[dict(op='jump',height_threshold=640,trigger=dict(state='height_at_least',timeout=180)),dict(op='jump_release',height_threshold=555,trigger=dict(state='height_at_most',timeout=80))]
            c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_resource_v4.py'
        elif n=='148':
            p=p[:48]
            for v in p:
                if v['op']=='settle':v['target_x']=110
                if v.get('trigger',{}).get('migration_goal'):v['trigger']['migration_goal']=[105,278,10,8]
            p+=at(70,282)+leap(210,232)+gunhop(240,232,375,182,175,[-math.sqrt(1-.05**2),.05])+at(410,182)+leap(550,154,release=133)
        elif n in('150','159'):
            levels=sorted([o for o in doc['objects']if re.search(r'/platform-\d+$',o['id'])],key=lambda o:int(o['id'].split('-')[-1]));p=at(60,levels[0]['y']-18);done=set();hx=60;hy=levels[0]['y']-18
            air=[e for e in c['enemies']if e['definition']=='plains_diver'];last_air=air[-1]if air else None
            for i,o in enumerate(levels[1:],1):
                for e in c['enemies']:
                    if e['id']in done:continue
                    if e['definition']=='plains_sentry'and abs(e['position'][1]+16-o['y'])<.1:
                        p+=engage(e,hx,hy,o['y']-36);done.add(e['id'])
                    elif e['definition']=='plains_diver'and e!=last_air and hy<=e['position'][1]+110 and abs(hx-e['position'][0])<350:
                        p+=engage(e,hx,hy,e['position'][1]-80);done.add(e['id'])
                xx=o['x']+o['w']/2;yy=o['y']-18
                if i==len(levels)-1:p+=gunhop(595,hy,xx,yy,400,[-math.sqrt(1-.25**2),.25])
                else:p+=leap(xx,yy)
                hx,hy=xx,yy;p+=at(hx,hy)
            if last_air:
                from .prepare_review_refresh_v1 import kill
                p+=kill(last_air['id'],670,382,8)
        elif n=='154':
            p=gunhop(145,282,335,282,250,[-1,0],stationary=True)+at(385,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.2,.3]),timeout=480))]+gunhop(385,282,500,282,235,[-math.sqrt(1-.054**2),-.054])+gunhop(545,282,735,282,250,[-1,0],stationary=True)
        elif n=='157':
            def crossing(start,target,saw,window,walk=None):
                result=at(start,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=saw,window=window),timeout=600))]
                if walk is not None:result+=at(walk,282)
                result +=[settle(target),cmd('jump'),dict(op='jump_release',height_threshold=250,trigger=dict(state='height_at_most',timeout=80)),dict(op='shoot',height_threshold=225,direction=[-math.sqrt(1-.1**2),-.1],trigger=dict(state='height_at_most',timeout=80))]+at(target,282)+[cmd('jump_release')]
                return result
            p=crossing(110,345,c['saws'][0]['source_id'],[.55,.56])+crossing(345,690,c['saws'][1]['source_id'],[.425,.435],430)
        c['control_plan']=p+end(x,y);c['max_frames']=3000 if n in('122','150','159')else 2400
        assert len(c['control_plan'])<=384,(n,len(c['control_plan']))
    doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',params);print(n,'control-v3',flush=True)
if __name__=='__main__':
    for r in core.read(AUTH/'handoff.json')['rows']:
        if r['reviewId']in IDS:prepare(r)
