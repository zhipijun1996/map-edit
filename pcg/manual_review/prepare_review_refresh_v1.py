"""Reuse the existing approved-design materializer; bind actual parameters."""
import argparse,copy,inspect,math,re
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from . import prepare_first40_v1 as shared
from .first30_content_v2 import decode as original_decode
AUTH=core.REPO/'feedback/manual-review/implementation-results/review-refresh-v1/authorization'
CURRENT=None
NOTES=[]

def design_for(row):
    d=core.read(core.REPO/row['designFile'])
    if row.get('designFileKind')=='source_module_reference':
        g=d['generationContract'];return dict(title=d['title'],bounds=g['space']['bounds'],ports=g['ports'],visualObjects=[o for o in d['objects']if o['type']not in('entry','exit')],intendedRoutes=g['routes'])
    return d

def dock(p):
    x,y=p['position'];nx,ny=p['normal']
    if ny:
        floors=[o for o in design_for(CURRENT)['visualObjects']if o['type']in('terrain','platform')and not o.get('trackId')and o['x']+12<=x<=o['x']+o['w']-12 and o['y']-18>=y+20]
        floor=min(floors,key=lambda o:abs(o['y']-18-y));return[x,floor['y']-18]
    return[x-24*nx,y+14]

def decode(doc):
    n=CURRENT['reviewId'];source=core.read(CURRENT['sourceModule']['file']);previous={o['id']:o for o in source['objects']};byid={o['id']:o for o in doc['objects']}
    for o in doc['objects']:
        m=o.setdefault('mechanics',{})
        if o['type']=='enemy':
            old=[o[k]for k in('x','y','w','h')];w,h=28,32;cx=o['x']+o['w']/2;bottom=o['y']+o['h'];cy=o['y']+o['h']/2
            o.update(x=cx-w/2,y=(cy-h/2 if o['definition']=='plains_diver'else bottom-h),w=w,h=h)
            if old!=[o[k]for k in('x','y','w','h')]:NOTES.append(dict(objectId=o['id'],kind='diagram_glyph_to_original_collision',diagram=old,actual=[o[k]for k in('x','y','w','h')],anchor='air center / ground foot center',resource=o['definition']))
        if o['type']=='hazard'and(previous.get(o['id'],{}).get('type')=='gear' or o.get('sourceType')=='gear'):o['type']='gear'
        if o['type']in('spike','wallSpike','gear'):o.setdefault('sourceId',o['id'])
        if o['type']=='gear' and not o.get('trackId') and 'origin'in m and 'travel'in m:
            ident=o['id'].replace('gear','track');assert ident in byid; o['trackId']=ident;o.setdefault('sourceId',o['id'])
        if o['type']=='gear'and o.get('trackId'):
            track=byid[o['trackId']]
            if 'period'in m:track['duration']=m['period']
            if 'initialPhase'in m:track['initialPhase']=m['initialPhase']
            if 'origin'in m and 'travel'in m:
                track['points']=[dict(x=m['origin'][0]-m['travel'][0],y=m['origin'][1]-m['travel'][1]),dict(x=m['origin'][0]+m['travel'][0],y=m['origin'][1]+m['travel'][1])]
            a,b=track['points'];phase=math.sin(2*math.pi*track.get('initialPhase',0));center=[(a[k]+b[k])/2+(b[k]-a[k])/2*phase for k in('x','y')];o.update(x=center[0]-o['w']/2,y=center[1]-o['h']/2)
        if o['type']=='gate'and m.get('openSeconds')=='UNKNOWN':m['openSeconds']=4.0 if n=='147'and o['id'].endswith('sequence-gate')else 3.0
    if n=='147':
        first=next(o for o in doc['objects']if o['type']=='bell'and o['id'].endswith('/bell-0'));second=next(o for o in doc['objects']if o['type']=='bell'and o['id'].endswith('/second'))
        g1=next(o for o in doc['objects']if o['type']=='gate'and o['id'].endswith('/sequence-gate'));g2=next(o for o in doc['objects']if o['type']=='gate'and o['id'].endswith('/gate-0'))
        original_id=first['sourceId'];first.update(targetId=g1['id']);first['mechanics'].pop('sequenceGateId',None);first['mechanics']['runtimeParameters']=dict(kind='timed',prompt='RING 1 / REOPEN FINITE G1');first['mechanics']['service']='ReopenableTimedLatch/v1'
        second.update(sourceId=original_id+'-second-independent',targetId=g2['id']);second['mechanics']=dict(runtimeParameters=dict(kind='timed',prompt='RING 2 / OPEN G2'))
        g1['mechanics'].update(kind='timed_gate',openSeconds=4.0);g2['mechanics'].update(kind='timed_gate',openSeconds=3.0)
    return original_decode(doc)

def at(x,y,after=0):return [dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=after)),dict(op='wait',trigger=dict(state='grounded',migration_goal=[x-5,y-4,10,8],timeout=480))]
def end(x,y):return at(x,y)+[cmd('wait',24)]
def leap(x,y,release=None,shot=None):
    p=[settle(x),cmd('jump')]
    if release is not None:p.append(dict(op='jump_release',height_threshold=release,trigger=dict(state='height_at_most',timeout=100)))
    if shot is not None:p +=[dict(op='shoot',direction=shot,trigger=dict(state='shot_ready',timeout=80))]
    p +=[dict(op='wait',trigger=dict(after=6,state='grounded',migration_goal=[x-5,y-4,10,8],timeout=480)),cmd('jump_release')]
    return p

def kill(enemy,x,y,count=8):
    p=[]
    for _ in range(count):
        rows=[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='grounded_shot_ready',migration_goal=[x-5,y-4,10,8],timeout=240)),cmd('shoot',aim_cell=dict(kind='enemy',id=enemy)),cmd('wait',4)]
        for c in rows:c['skip_if_enemy_dead']=enemy
        p+=rows
    return p

def core_plan(source,bounds):
    p=copy.deepcopy(source[0]['control_plan']);limit=next((i for i,v in enumerate(p)if v['op']=='settle'and not(bounds['x']+12<=v['target_x']<=bounds['x']+bounds['w']-12)),len(p));return p[:limit]

def plan_for(n,target,source,design):
    p=core_plan(source,design['bounds']);a,z=[next(v for v in design['ports']if v['id']==target[k])for k in('from','to')];start=dock(a);goal=dock(z);x,y=goal
    if n in('118','134'):p=[]
    elif n=='116':
        enemy=next(o for o in design['visualObjects']if o['type']=='enemy');p=kill(enemy.get('sourceId',enemy['id']),130,282)+p[:18]
    elif n=='117':
        enemies=[o for o in design['visualObjects']if o['type']=='enemy'];p=[]
        for e in enemies:p+=kill(e.get('sourceId',e['id']),300,582,12)
        p+=at(470,582)+leap(810,582,release=455,shot=[-1,0])
    elif n in('119','123','160'):pass
    elif n=='120':
        for c in p:
            if c['op']=='jump_release':c.clear();c.update(op='jump_release',height_threshold=224,trigger=dict(state='height_at_most',timeout=80))
    elif n=='122':
        if target['from']=='entry':p=p[:28]
        else:
            p=[]
            if target['from']=='exit':p=at(976,420)+leap(900,380,release=379)
    elif n=='125':
        p=[]
        if target['from']in('entry','fork_right')and target['to']in('fork_up','C'):
            if target['from']=='fork_right':p+=at(340,582)
            for xx,yy in [(285,492),(455,402),(285,312),(455,222),(488,70)]:p+=leap(xx,yy)
    elif n=='127':p=at(25,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='design-central-vertical-gear',window=[.1,.2]),timeout=360))]+leap(235,282,release=145,shot=[-1,0])
    elif n=='130':
        p=[]
        if target['from']=='entry':p=at(75,522)+leap(215,412)+at(250,412)+leap(390,302)+at(435,302)+leap(570,266,release=245,shot=[-1,0])
    elif n=='132':p=at(190,282)+leap(460,282,release=235,shot=[-1,0])
    elif n=='133':p=at(145,342)+leap(340,342,release=310,shot=[-1,0])
    elif n=='135':
        p=[]
        if target['from']=='entry':p=at(65,470)+leap(215,342)
    elif n=='138':
        p=[]
        if target['from']=='entry':p=at(55,282)+leap(190,182)+at(225,182)+leap(352,26)
    elif n=='140':
        sign=1 if target['from']=='entry'else-1;takeoff=290 if sign==1 else 870
        p=at(takeoff,582)+[cmd('axis',value=sign),cmd('jump'),cmd('jump_release',4),cmd('shoot',after=2,direction=[-sign,0]),cmd('shoot',after=17,direction=[-sign,0]),cmd('jump',after=12),cmd('jump_release',4)]
    elif n=='146':
        bell=next(o for o in design['visualObjects']if o['type']=='bell');p=at(650,282)+[cmd('jump'),dict(op='jump_release',height_threshold=220,trigger=dict(state='height_at_most',timeout=60)),cmd('shoot',aim_cell=dict(kind='bell',id=bell['sourceId']))]
    elif n=='147':
        enemy=next(o for o in design['visualObjects']if o['type']=='enemy');bells=[o for o in design['visualObjects']if o['type']=='bell'];first=next(o for o in bells if o['id'].endswith('/bell-0'))
        p=kill(enemy.get('sourceId',enemy['id']),160,282)+at(180,282)+[cmd('shoot',aim_cell=dict(kind='bell',id=first['sourceId'])),cmd('wait',12)]+at(520,282)+[cmd('shoot',aim_cell=dict(kind='bell',id=first['sourceId']+'-second-independent')),cmd('wait',16)]
    elif n=='148':
        enemy=next(o for o in design['visualObjects']if o['type']=='enemy');p=kill(enemy.get('sourceId',enemy['id']),65,282,12)+at(70,282)+leap(210,232)+leap(375,182)+leap(535,154,release=133)
    elif n in('150','159'):
        # Keep original actual platform rhythm; add ground-side engagements at
        # protected landing edges before traversing the enemy's platform.
        objects=design['visualObjects'];levels=sorted([o for o in objects if re.search(r'/platform-\d+$',o['id'])],key=lambda o:int(o['id'].split('-')[-1]));p=at(60,levels[0]['y']-18)
        for i,o in enumerate(levels[1:],1):
            enemies=[e for e in objects if e['type']=='enemy'and e.get('definition')=='plains_sentry'and abs(e['y']+e['h']-o['y'])<1]
            center=o['x']+o['w']/2;xx=o['x']+14 if enemies else center;yy=o['y']-18
            p+=leap(xx,yy)
            for e in enemies:p+=kill(e.get('sourceId',e['id']),xx,yy)
            for e in [e for e in objects if e['type']=='enemy'and e.get('definition')=='plains_diver'and abs((e['y']+16)-yy)<160 and abs((e['x']+16)-xx)<350]:p+=kill(e.get('sourceId',e['id']),xx,yy,4)
            p+=at(center,yy)
    elif n=='154':p=at(145,282)+leap(335,282,release=245,shot=[-1,0])+at(375,282)+leap(515,282,release=235,shot=[-1,0])+at(545,282)+leap(735,282,release=245,shot=[-1,0])
    elif n=='156':
        p=at(260 if target['from']=='entry'else 440,282)+leap(352,152)+leap(x,y,release=130)
    elif n=='157':p=at(55,282)+leap(345,282,release=237,shot=[-1,0])+leap(690,282,release=237,shot=[-1,0])
    # Repair source routine observations after approved banks changed height.
    floors=[o for o in design['visualObjects']if o['type']in('terrain','platform')and not o.get('trackId')]
    for c in p:
        q=c.get('trigger',{}).get('migration_goal')
        if q:
            near=[o for o in floors if o['x']<=q[0]+q[2]/2<=o['x']+o['w']and abs((o['y']-18)-(q[1]+q[3]/2))<12]
            if near:q[1]=min(near,key=lambda o:abs((o['y']-18)-(q[1]+q[3]/2)))['y']-18-q[3]/2
    return p+end(x,y),source[0]

def prepare(row):
    global CURRENT,NOTES
    CURRENT=row;NOTES=[]
    text=inspect.getsource(shared.prepare).replace("design=core.read(core.REPO/row['designFile'])","design=design_for(row)").replace("'pcg/manual_review/first40_r'+n+'_v1.py'","('pcg/manual_review/review_refresh_resource_v1.py'if n=='140'else'pcg/manual_review/review_refresh_author_v1.py')")
    scope={**shared.__dict__,'AUTH':AUTH,'dock':dock,'plan_for':plan_for,'decode':decode,'design_for':design_for};exec(compile(text,__file__,'exec'),scope);scope['prepare'](row)
    folder=core.REPO/row['outputDirectory'];doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
    for c in cases:
        c['id']=c['id'].replace('approved-first30','approved-review-refresh-v1');c['max_frames']=3000 if row['reviewId']in('125','159')else 2400
        c.pop('approved_first30',None)
        for key in list(c):
            if key.startswith('migration_')or key in('decoder_pending_behavior',):c.pop(key)
        if row['reviewId']=='147':c['refresh_reopenable_latches']=[c['latches'][0]['id']]
        if row['reviewId']=='116':c['refresh_carried_enemies']=[dict(enemy=c['enemies'][0]['id'],carrier=c['moving_platforms'][0]['platform_id'])]
        assert len(c['control_plan'])<=384,(row['reviewId'],len(c['control_plan']))
    doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(materializer=physics.artifact(shared.__file__),parameterBindings=NOTES,designFileKind=row.get('designFileKind','approved_design'),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],content=original_decode(doc),bindings=NOTES,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if (not a.ids or row['reviewId']in a.ids)and not(core.REPO/row['outputDirectory']).exists():prepare(row)
