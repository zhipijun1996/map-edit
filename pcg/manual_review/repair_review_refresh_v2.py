"""Actual controls and staging repair. Approved terrain/ports remain unchanged."""
import copy,math,shutil
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review_refresh_v1 import at,end,leap,kill
from .probe_review_refresh_v1 import AUTH
IDS={'116','119','120','122','123','125','127','133','138','140','148','150','154','156','157','159','160'}
def pulse(start,base_y,target,threshold):
    return at(start,base_y)+[cmd('axis',value=0),cmd('jump'),dict(op='jump_release',height_threshold=base_y-17,trigger=dict(state='height_at_most',timeout=80)),dict(op='shoot',height_threshold=threshold,direction=[-1,0],trigger=dict(state='descending_height',timeout=100)),settle(target),dict(op='wait',trigger=dict(state='grounded',timeout=240)),cmd('wait',12)]
def prepare(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v2';before.mkdir(parents=True,exist_ok=False)
    for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract'];floors=[o for o in doc['objects']if o['type']in('terrain','platform')and not o.get('trackId')]
    for q in g['ports']:
        if not q['normal'][0]:continue
        x,y=q['stagingPosition'];valid=[o for o in floors if abs(o['y']-(y+18))<.01 and o['w']>=24]
        positions=[(min(max(x,o['x']+12),o['x']+o['w']-12),o)for o in valid];xx,support=min(positions,key=lambda pair:abs(pair[0]-x));q['stagingPosition']=[xx,y];q['support']=dict(objectId=support['id'],face='top',status='actual_complete_body_native_standing_support')
    for c in cases:
        a,z=[next(p for p in g['ports']if p['id']==c['route_spec'][k])for k in('from_port','to_port')];c.update(spawn=a['stagingPosition'][:],entry_port=a['stagingPosition'][:],exit_port=z['stagingPosition'][:],goal=[z['stagingPosition'][0]-7,z['stagingPosition'][1]-4,14,8]);x,y=z['stagingPosition'];p=c['control_plan'];c['id']+='-control-v2';c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_author_v2.py'
        if n=='116':
            p=kill(c['enemies'][0]['id'],185,282)+copy.deepcopy(p[32:-3])
            for v in p:
                if v.get('aim_cell',{}).get('kind')=='enemy':v['aim_cell']['body_offset']=[0,-14]
        elif n=='119':p=at(90,282)+leap(285,282,release=249,shot=[-1,0])+at(315,282)+leap(520,282,release=249,shot=[-1,0])+at(560,282)+leap(770,282,release=249,shot=[-1,0])
        elif n=='120':p=at(95,382)+leap(215,312,release=312,shot=[-.8,.6])+at(240,312)+leap(400,242,release=250,shot=[-math.sqrt(1-.15**2),.15])+at(590,312)+at(640,312)+leap(810,382,release=270)
        elif n=='122':
            if a['id']=='entry':
                p=copy.deepcopy(p[:28]);p[16]['requires_saw_phase']=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.7,.8])
            else:p=at(976,420)+leap(900,380,release=390)if a['id']=='exit'else[]
        elif n in('123','160'):p=p[:-3]
        elif n=='125':
            if a['id']in('entry','fork_right')and z['id']in('fork_up','C'):p=p[:-7]+leap(488,70,release=160,shot=[-.8,.6])
            elif a['id']in('fork_up','C')and z['id']=='fork_right':p=at(548,70)+[cmd('drop_through'),cmd('wait',after=6)]
            else:p=p[:-3]
        elif n=='127':p=at(-60,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='design-central-vertical-gear',window=[.1,.2]),timeout=360))]+leap(235,282,release=145,shot=[-1,0])
        elif n=='133':p=pulse(145,342,350,304)
        elif n=='138':p=at(55,282)+leap(190,182)+at(210,182)+leap(352,26,release=120,shot=[-math.sqrt(1-.65**2),.65])if a['id']=='entry'else[]
        elif n=='140':
            base=core.read('pcg/manual_review/implementation/first-40-final-v1/game-challenge-long-gap/cases.json')['cases'][0];p=copy.deepcopy(base['control_plan'][:7]);sgn=1 if a['id']=='entry'else-1;takeoff=290 if sgn==1 else 870
            p[0]['target_x']=takeoff;p[1]['trigger']['migration_goal']=[takeoff-5,578,10,8]
            for v in p:
                if 'value'in v and v['op']=='axis':v['value']=sgn
                if 'direction'in v:v['direction'][0]=abs(v['direction'][0])*(-sgn)
            p +=[dict(op='jump',height_threshold=582,trigger=dict(state='height_at_least',timeout=180)),cmd('jump_release')];c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_resource_v3.py'
        elif n=='148':
            p=copy.deepcopy(p[:-3])
            for v in p[:48]:
                if v['op']=='settle':v['target_x']=85
                if v.get('trigger',{}).get('migration_goal'):v['trigger']['migration_goal']=[80,278,10,8]
        elif n in('150','159'):
            p=copy.deepcopy(p[:-3]);enemies={e['id']:e for e in c['enemies']}
            for v in p:
                ident=v.get('skip_if_enemy_dead')
                if not ident or enemies[ident]['definition']!='plains_sentry':continue
                if v['op']=='settle'or v.get('trigger',{}).get('state')=='grounded_shot_ready':
                    v['follow_enemy']=dict(id=ident,side=1,distance=50)
                    if v['op']=='wait':v['trigger'].pop('migration_goal',None)
                if v.get('aim_cell',{}).get('kind')=='enemy':v['aim_cell']['body_offset']=[0,-14]
        elif n=='154':p=pulse(145,282,335,239)+at(375,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.2,.3]),timeout=480))]+leap(500,282,release=260)+pulse(545,282,735,239)
        elif n=='156':p=at(210 if a['id']=='entry'else 500,282)+leap(352,152)
        elif n=='157':
            def cross(target):return leap(target,282,release=250,shot=[-math.sqrt(1-.1**2),-.1])
            # Defer the real shot until the release arc has entered the 4px band.
            first=cross(345);second=cross(690)
            for v in first+second:
                if v['op']=='shoot':v.update(height_threshold=225);v['trigger']=dict(state='height_at_most',timeout=80)
            p=at(110,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.55,.56]),timeout=480))]+first+at(345,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][1]['source_id'],window=[.425,.435]),timeout=480))]+at(430,282)+second
        c['control_plan']=p+end(x,y);c['max_frames']=3000 if n in('122','125','159')else 2400
        c['ports']=[dict(id=q['id'],position=q['stagingPosition'],normal=q['normal'],support_index=next(o['sourceIndex']for o in floors if o['id']==q['support']['objectId']))for q in g['ports']]
    doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect_source(cases[0])))
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases],stagingBoundToCompleteNativeSupport=True);core.write(folder/'parameters.json',params);print(n,'control-v2',flush=True)
def inspect_source(c):
    import inspect
    return inspect.getsourcefile(physics.author_for(c).purpose)
if __name__=='__main__':
    for r in core.read(AUTH/'handoff.json')['rows']:
        if r['reviewId']in IDS:prepare(r)
