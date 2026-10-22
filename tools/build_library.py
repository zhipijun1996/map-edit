"""Translate evaluated Godot data to editable sketches; never infer physical success.

python3 tools/build_library.py /path/to/data-only-project/extracted.json
"""
import copy
import hashlib
import html
import json
import math
import pathlib
import sys
from collections import Counter
from integration_status import status_for
from capability_requirements import from_source

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMIT = (ROOT/'library/source-commit.txt').read_text().strip()
SCHEMA = 'gunman-rush-level-sketch/v1'
OUT = ROOT/'library/modules'
THUMBS = ROOT/'library/thumbnails'
OUT.mkdir(parents=True, exist_ok=True)
THUMBS.mkdir(parents=True, exist_ok=True)
NAMES = {
 'boss_approach':'Boss 前厅','challenge_ferry_ascent':'摆渡上升挑战','challenge_long_gap':'长距离跨越','challenge_recoil_climb':'反冲攀升',
 'descending_switchback':'下降折返','macro_chain':'连续动作链','micro_board':'微型落脚台','micro_drop':'微型落差','micro_step':'微型台阶',
 'moving_transfer':'移动换乘','recoil_shaft':'反冲竖井','route_junction':'路线枢纽','safe_hub':'安全枢纽','saw_gate':'锯轮关口',
 'spike_gap':'尖刺缺口','square_loop':'方形回环','stepped_crossing':'阶梯横渡','timed_gallery':'时机关廊','windchime_trial':'风铃试炼',
 'plains_bell_ferry_control':'风铃控制摆渡','plains_bellstrider_arena':'鸣铃巡游机战场','plains_boss_arena':'平原 Boss 战场',
 'plains_braided_meadow':'交织草甸','plains_bramble_causeway':'荆棘堤道','plains_bramble_ridge':'荆棘山脊','plains_door_landing':'门前落点',
 'plains_ferry_channel':'摆渡水道','plains_ferry_gears':'摆渡与齿轮','plains_ferry_one':'单段摆渡','plains_ferry_two':'双段摆渡',
 'plains_fork_paths':'分岔路径','plains_fork_rest':'分岔休整','plains_gear_brook':'齿轮溪流','plains_gear_glade':'齿轮林隙','plains_gear_hop':'齿轮小跳',
 'plains_high_perches':'高处落脚点','plains_long_meadow':'长草甸','plains_low_arch':'低矮拱顶','plains_meadow_gap':'草甸缺口',
 'plains_micro_landing':'微型落地点','plains_micro_rise':'微型上升','plains_micro_stool':'微型踏台','plains_patrol_meadow':'巡逻草甸',
 'plains_perch_double':'双重高台','plains_perch_rise':'高台上升','plains_recoil_chasm':'反冲深沟','plains_recoil_chasm_wide':'宽反冲深沟',
 'plains_recoil_double':'双段反冲','plains_recoil_span':'反冲横渡','plains_recoil_step':'反冲台阶','plains_recovery_bridge':'恢复桥',
 'plains_remote_bell':'远程风铃','plains_remote_sequence':'远程双铃顺序','plains_skip_stones':'跳石','plains_split_terrace':'分流台地',
 'plains_switchback':'平原折返','plains_terraces':'交错台地','plains_thorn_bridge':'荆棘桥','plains_thorn_cells':'刺格安全落点',
 'plains_thorn_hop':'荆棘小跳','plains_thorn_slalom':'荆棘穿梭','plains_thorn_steps':'荆棘台阶','plains_thorn_wall':'刺墙翻越',
 'plains_twin_gears':'双齿轮节奏','plains_valley':'草谷','plains_wind_spire':'风中尖塔','plains_windchime_ferry':'风铃摆渡',
 'plains_windchime_lesson':'风铃教学','plains_windchime_rush':'风铃限时冲关','plains_windchime_sequence':'风铃顺序挑战',
 'plains_windchime_timed':'限时风铃','plains_windchime_well':'风铃反冲井',
 'root_meadow':'宽根草甸','mushroom_fork':'蘑菇分岔','low_root_tunnel':'低根隧道','root_basin_return':'根盆地回返',
 'side_fruit_crossing':'侧果横渡','double_fruit_s':'双果 S 线','double_window':'双窗树腹','canopy_detour':'树冠绕路',
 'thorn_side_passage':'刺面侧通道','backbranch_turn':'背枝折返','crown_hook_relay':'树冠钩索接力','deep_root_switchback':'深根折返',
 'backlook_fruit_cache':'回望果实宝藏','borrow_pod_crossing':'借活果横渡','thorn_l_root_turn':'荆棘 L 根转弯',
 'thorn_7_root_fold':'荆棘 7 型回折','thorn_z_root_switchback':'荆棘 Z 根折返','forked_bough_hh':'双钩分叉高枝',
 'side_root_rh':'反冲侧根接钩','rooted_double_window':'实体树干双窗','descending_borer_elbow':'向下钻根弯道',
 'fallen_arch_canopy':'倒木拱顶树冠','thorn_side_outlet':'刺面侧出口','l_hollow_reward_loop':'L 树腹奖励回环',
 'z_hollow_inner_cache':'Z 树腹内侧宝藏','seven_bough_reveal':'7 型高枝回望','z_descending_return':'Z 型下降回返',
 'arch_four':'拱根四动作','bridge_five':'桥根五动作','recoil_hook':'反冲 → 钩索','recoil_hook_recoil':'反冲 → 钩索 → 反冲',
 'hook_hook':'双钩连续腾空','height_then_precision':'先登高，再精确落地','read_ride_release':'观察、乘坐、离开',
 'hollow_floorless_canopy':'无上层地板树腹','shared_hollow_floorless_upper':'共享上层空心树腹','hollow_horizontal_borer_cavity':'横向钻根空腔',
 'root_arch_hook_recoil':'拱根钩索反冲','side_hook_thorn_mouth':'侧钩刺口','hollow_spiral':'树腹螺旋','backbranch_HR':'背枝钩索反冲','thorn_mouth':'荆棘树口',
 'precision_to_transfer':'精确落点接换乘','climb_change_height':'攀升与高度变化','resource_then_rhythm':'资源与节奏','short_long_rise':'短跳、长跳、上升',
}
ACTION = {'walk':'行走','jump_gap':'跳过缺口','jump_rise':'起跳上升','drop_through':'下落穿过','drop':'下落',
          'H':'钩索弹起','HANG':'钩索悬挂','R':'射击反冲','wait':'等待','land':'落地','jump':'起跳'}
ROUTE = {'main':'主路线','returning':'返回路线','recovery':'失误回收','outer':'外侧路线','reward':'奖励路线',
         'lower_bypass':'下方绕行','main_to_exit':'主路到出口','inner_reward':'内侧奖励','reward_return':'奖励后返回',
         'retry':'重试路线','failure_to_return':'失败后返回','approach':'接近路线','cache_return':'宝藏返回',
         'main_to_far':'主路到远端','near_west_return':'近端向西返回'}
LATCHES = json.loads((ROOT/'library/source/config/plains_shot_latches.json').read_text())['modules']
EXTRACTED = json.loads(pathlib.Path(sys.argv[1]).read_text())
RESOURCES = {r['id']: r for r in EXTRACTED if r['kind']=='resource'}
CATALOG = []

def name(identifier):
    return NAMES.get(identifier, identifier.replace('_',' '))

def base(row,title,category):
    d={'schema':SCHEMA,'id':'reference-'+row['id'],'title':title,'description':'','constraints':'原始布局已保留，位置与尺寸可修改；动作路线是设计指引，需在真实游戏中验证。',
       'canvas':{'width':1600,'height':900,'units':'world_units_reference','positionPrecision':'approximate'},'objects':[],
       'updatedAt':'2026-10-22T00:00:00.000Z',
       'source':{'repository':'zhipijun1996/gunman-rush','commit':COMMIT,'path':row['path'],'moduleId':row['id'],
                 'kind':row['kind'],'category':category,'original':row['data'],
                 'method':row.get('method'),'arguments':row.get('arguments',[])}}
    return d

def add(d,kind,x,y,w,h,**extra):
    obj={'id':f'{d["id"]}/o{len(d["objects"])}','type':kind,'x':x,'y':y,'w':w,'h':h,'rotation':0,'label':'','note':'',**extra}
    d['objects'].append(obj)
    return obj

def add_route(d,points,label='主路线',source='main',**extra):
    # Collapse repeated consecutive nodes while preserving the last action annotation.
    clean=[]
    for p in points:
        if clean and abs(clean[-1]['x']-p['x'])<.01 and abs(clean[-1]['y']-p['y'])<.01:
            if p.get('action'): clean[-1]['action']=p['action']
        else: clean.append(p)
    if len(clean)<2: return
    xs=[p['x'] for p in clean];ys=[p['y'] for p in clean]
    return add(d,'route',min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys),points=clean,duration=max(4,len(clean)*.6),mode='once',label=label,sourceRoute=source,**extra)

def convert_resource(row,offset=(0,0),prefix='',phase=0):
    raw=copy.deepcopy(row['data']);title=name(row['id']);category='平原模块' if row['id'].startswith('plains_') else '基础 / 历史模块'
    d=base(row,title,category);ox,oy=offset
    for i,r in enumerate(raw['platforms']):
        add(d,'platform' if i in raw['one_way_platform_indices'] else 'terrain',r[0]+ox,r[1]+oy,r[2],r[3],sourceIndex=i)
    dangers=[(r,'danger_bounds') for r in raw['danger_bounds']]
    for thorn in raw['surface_thorns']:
        p=raw['platforms'][thorn['platform_index']];start=thorn['start_offset'];length=thorn['length'];depth=thorn['depth'];face=thorn['face']
        r=[p[0]+start,p[1]-depth,length,depth] if face==0 else [p[0]-depth,p[1]+start,depth,length] if face==1 else [p[0]+p[2],p[1]+start,depth,length] if face==2 else [p[0]+start,p[1]+p[3],length,depth]
        dangers.append((r,thorn))
    seen=set()
    for r,meta in dangers:
        if tuple(r) in seen:continue
        seen.add(tuple(r));kind='hazard';rotation=0
        if isinstance(meta,dict):
            face=meta['face'];kind='spike' if face in (0,3) else 'wallSpike';rotation=180 if face in (1,3) else 0
        else:
            for p in raw['platforms']:
                if r[0]<p[0]+p[2] and r[0]+r[2]>p[0]:
                    if abs(r[1]+r[3]-p[1])<.01:kind='spike';break
                    if abs(r[1]-p[1]-p[3])<.01:kind='spike';rotation=180;break
                if r[1]<p[1]+p[3] and r[1]+r[3]>p[1]:
                    if abs(r[0]+r[2]-p[0])<.01:kind='wallSpike';rotation=180;break
                    if abs(r[0]-p[0]-p[2])<.01:kind='wallSpike';break
        add(d,kind,r[0]+ox,r[1]+oy,r[2],r[3],rotation=rotation,note='原始危险区域' if kind=='hazard' else '依附实体的刺面',sourceHazard=meta)
    for saw in raw['saws']:
        origin=saw['origin'];travel=saw['travel'];r=saw['radius'];ph=(saw['initial_phase']+phase)%1
        o=add(d,'gear',ox+origin[0]+travel[0]*math.sin(2*math.pi*ph)-r,oy+origin[1]+travel[1]*math.sin(2*math.pi*ph)-r,r*2,r*2,sourceId=saw['source_id'])
        if any(travel):
            points=[{'x':ox+origin[0]-travel[0],'y':oy+origin[1]-travel[1]},{'x':ox+origin[0]+travel[0],'y':oy+origin[1]+travel[1]}]
            track=add(d,'trackLine',points[0]['x'],points[0]['y'],abs(travel[0]*2),abs(travel[1]*2),points=points,duration=saw['period'],mode='sine',initialPhase=ph)
            o['trackId']=track['id']
    for ferry in raw['ferries']:
        start=ferry['start'];finish=ferry['finish'];size=ferry['size'];duration=ferry['travel_duration'];dwell=ferry['dwell_duration'];ph=(ferry['initial_phase']+phase)%1
        t=ph*2*(duration+dwell)
        f=0 if t<dwell else (t-dwell)/duration if t<dwell+duration else 1 if t<2*dwell+duration else 1-(t-2*dwell-duration)/duration
        x=ox+start[0]+(finish[0]-start[0])*f;y=oy+start[1]+(finish[1]-start[1])*f
        o=add(d,'platform',x-size[0]/2,y-size[1]/2,*size,sourceId=ferry['platform_id'],note='移动平台')
        points=[{'x':ox+start[0],'y':oy+start[1]},{'x':ox+finish[0],'y':oy+finish[1]}]
        track=add(d,'trackLine',points[0]['x'],points[0]['y'],abs(finish[0]-start[0]),abs(finish[1]-start[1]),points=points,duration=duration,dwell=dwell,initialPhase=ph,mode='pingpong')
        o['trackId']=track['id']
    port_points=set()
    for kind,ports in [('entry',[raw['entry_port']]+raw['entry_ports']),('exit',[raw['exit_port']]+raw['exit_ports'])]:
        for p in ports:
            key=(kind,tuple(p['position']))
            if key in port_points:continue
            port_points.add(key);x,y=p['position'];add(d,kind,ox+x-15,oy+y-35,30,53,label=('入口' if kind=='entry' else '出口')+(' · '+p['port_id'] if len(ports)>1 else ''),sourcePort=p)
    for i,p in enumerate(raw['anchors']):add(d,'anchor',ox+p[0]-4,oy+p[1]-4,8,8,sourceAnchorIndex=i)
    if raw['main_route']:
        add_route(d,[{'x':ox+raw['anchors'][i][0],'y':oy+raw['anchors'][i][1],'action':'入口' if n==0 else '原始路线锚点'} for n,i in enumerate(raw['main_route'])],note='连接原模块显式 main_route 锚点，不是输入回放')
    for n,route in enumerate(raw['branch_routes']):
        add_route(d,[{'x':ox+raw['anchors'][i][0],'y':oy+raw['anchors'][i][1],'action':'支路锚点'} for i in route],f'支路 {n+1}',f'branch_{n}',note='原始 branch_routes 锚点连接')
    if row['id'] in LATCHES:
        latch=LATCHES[row['id']];g=latch['gate'];gate=add(d,'gate',ox+g[0],oy+g[1],g[2],g[3],label='机关门',note=latch['prompt'])
        x,y=latch['bell'];bell=add(d,'bell',ox+x-15,oy+y-20,30,40,label='风铃',targetId=gate['id'],note=latch['prompt'])
        if latch.get('actuator_id'):
            carrier=next((o for o in d['objects'] if o.get('sourceId')==latch['actuator_id']),None)
            if carrier:bell['targetId']=carrier['id']
        seq=latch.get('sequence_offset',[0,0])
        if any(seq):
            second=add(d,'bell',ox+x+seq[0]-15,oy+y+seq[1]-20,30,40,label='风铃 2',targetId=gate['id'],note=latch['prompt'])
            if latch.get('sequence_gate'):
                sg=latch['sequence_gate'];first_gate=add(d,'gate',ox+sg[0],oy+sg[1],sg[2],sg[3],label='顺序门 1');bell['targetId']=first_gate['id']
    d['description']=f'原项目「{title}」。平台压力 {raw["platform_pressure"]}/3，时机压力 {raw["timing_pressure"]}/3；最低跳跃 {raw["min_jumps"]}，最低空中射击 {raw["min_air_shots"]}。'
    if not raw['main_route']:d['description']+='浅绿小点是原始安全锚点；源模块未记录完整动作顺序，可自行补画人物路线。'
    if 'arena' in row['id']:d['description']+='这里只保留模块地形；Boss / 敌人由关卡消费者另外装配。'
    return d

def step_points(steps,spawn):
    points=[{'x':spawn[0],'y':spawn[1],'action':'入口'}]
    for step in steps:
        label=ACTION.get(step.get('kind'),step.get('kind',step.get('action','动作')))
        for p in ([step['takeoff']] if 'takeoff' in step else [])+step.get('path',[])+([step['landing']] if 'landing' in step else []):
            points.append({'x':p[0],'y':p[1],'action':label if p==step.get('landing') else ''})
    return points

def convert_forest(row):
    raw=row['data'];localid=raw.get('id',row['id']);title=name(localid)
    if 'forest_exploration_fallen_trunk' in row['id']:title='倒木上下两面'
    if 'forest_exploration_fruit_crossing' in row['id']:title='固定果反向背枝'
    if 'forest_hollow_trunk_geometry' in row['id']:title={'deep_zeroR':'双窗树腹 · 深返回','shallow':'双窗树腹 · 浅返回','cavity':'树腹空腔','cavity_elbow':'树腹折角','aircatch':'树腹空中接钩'}.get(row['id'].split('__')[-1],title)
    if row.get('arguments') and isinstance(row['arguments'][-1],int):title+=f' · 变体 {row["arguments"][-1]+1}'
    category='森林场所 / v18' if 'forest_exploration_places' in row['id'] or 'forest_exploration_fallen_trunk' in row['id'] or 'forest_exploration_fruit_crossing' in row['id'] else '森林探索模块' if 'forest_exploration_modules' in row['id'] or 'forest_playful_module_variants' in row['id'] else '森林动作 / 历史候选'
    d=base(row,title,category)
    support_map={}
    for platform in raw.get('platforms',[]):
        r=platform['rect'];o=add(d,'platform' if platform.get('one_way') else 'terrain',*r,sourceId=platform['id'],note=platform.get('scene_kind',''))
        support_map[platform['id']]=o['id']
    for anchor in raw.get('hook_anchors',[]):
        x,y=anchor['position'];add(d,'hookHang' if anchor.get('hang_enabled') else 'hookBounce',x-15,y-15,30,30,sourceId=anchor['id'],note=anchor.get('fruit_role',''))
    faces={s['danger_index']:s for s in raw.get('danger_surfaces',[])}
    for i,r in enumerate(raw.get('dangers',[])):
        surface=faces.get(i);face=surface.get('face','up') if surface else None
        kind=('wallSpike' if face in ('left','right') else 'spike') if face else 'hazard'
        add(d,kind,*r,rotation=180 if face in ('down','left') else 0,sourceDangerIndex=i,note='原始危险面',hostId=support_map.get(surface.get('host_support_id')) if surface else None)
    spawn=raw.get('spawn',[0,0]);goal=raw.get('goal',spawn)
    add(d,'entry',spawn[0]-15,spawn[1]-35,30,53,label='入口')
    seen={tuple(spawn)}
    for key,port in raw.get('ports',{}).items():
        p=port['position']
        if tuple(p) in seen:continue
        seen.add(tuple(p));add(d,'exit',p[0]-12,p[1]-28,24,46,label={'cache':'奖励口','failure':'失败回收','return':'返回口','outer':'外侧口','crown':'高枝口','exit':'出口','entry':'入口'}.get(key,key),note=port.get('role',''),sourcePort=port)
    if tuple(goal) not in seen:add(d,'exit',goal[0]-15,goal[1]-35,30,53,label='目标出口')
    routes=raw.get('routes',{})
    for key,route in routes.items():
        steps=route if isinstance(route,list) else route.get('steps',[])
        route_spawn=spawn
        if isinstance(route,dict) and route.get('from_port') in raw.get('ports',{}):route_spawn=raw['ports'][route['from_port']]['position']
        elif steps and steps[0].get('takeoff'):route_spawn=steps[0]['takeoff']
        elif key!='main' and steps and steps[0].get('landing'):route_spawn=steps[0]['landing']
        points=step_points(steps,route_spawn)
        if len(points)<2 and isinstance(route,dict):points=[{'x':p[0],'y':p[1],'action':''} for p in route.get('path',[])]
        add_route(d,points,ROUTE.get(key,key),key,note='由原模块 steps / path 转换，保留原始动作意图')
    if not routes and raw.get('steps'):
        add_route(d,step_points(raw['steps'],spawn),note='原始 steps，仅作为动作示意')
    if not any(o['type']=='route' for o in d['objects']) and raw.get('action_program'):
        anchors={a['id']:a['position'] for a in raw.get('hook_anchors',[])};points=[{'x':spawn[0],'y':spawn[1],'action':'起跳'}]
        program=raw['action_program']
        for i,action in enumerate(program):
            label=ACTION.get(action.get('action'),action.get('action','动作'))
            if action.get('anchor') in anchors:p=anchors[action['anchor']]
            else:
                # A recoil has no sampled position. Interpolate for illustration,
                # retaining the source action and explicitly marking this trajectory.
                f=(i+1)/(len(program)+1);p=[spawn[0]+(goal[0]-spawn[0])*f,spawn[1]+(goal[1]-spawn[1])*f]
            points.append({'x':p[0],'y':p[1],'action':label+((' '+str(action['direction'])) if action.get('direction') else '')})
        points.append({'x':goal[0],'y':goal[1],'action':'落地'})
        add_route(d,points,note='按原 action_program 标出动作；无采样位置的反冲点仅作示意',trajectory='schematic_from_action_program')
    if raw.get('reward_position'):
        x,y=raw['reward_position'];add(d,'reward',x-18,y-30,36,30,label='可选奖励',note=str(raw.get('risk_reward',{})))
    for enemy in raw.get('ecology_slots',raw.get('enemies',[])):
        if 'position' not in enemy:continue
        x,y=enemy['position'];add(d,'enemy',x-18,y-32,36,36,label=enemy.get('behavior_id','敌人'),sourceId=enemy.get('id'),note=enemy.get('role',''))
    # Mushroom forks are named for their structure; do not invent a bounce body
    # unless the source actually supplies one.
    d['description']=raw.get('identity',raw.get('geometry_intent','森林代码模块原始几何参考。'))
    if isinstance(d['description'],dict):d['description']=json.dumps(d['description'],ensure_ascii=False)
    d['description']+=' 切换下方路线菜单，可查看不同出口与返回路径。'
    if raw.get('chain_contract',{}).get('continuous_airborne'):d['constraints']+=' 原动作链要求连续腾空，中途不能添加落脚点。'
    d['source']['admission']=raw.get('admission',{'production_pool':raw.get('production_pool',False),'native_verified':raw.get('native_verified',False)})
    return d

def normalize_canvas(d):
    points=[]
    for o in d['objects']:
        points.extend([(o['x'],o['y']),(o['x']+o['w'],o['y']+o['h'])]);points.extend((p['x'],p['y']) for p in o.get('points',[]))
    left=min([p[0] for p in points],default=0);top=min([p[1] for p in points],default=0)
    dx=80-left;dy=80-top
    for o in d['objects']:
        o['x']+=dx;o['y']+=dy
        for p in o.get('points',[]):p['x']+=dx;p['y']+=dy
        if o.get('control'):o['control']['x']+=dx;o['control']['y']+=dy
    d['source']['editorTranslation']=[dx,dy]
    d['canvas']['width']=max(400,math.ceil(max([p[0] for p in points],default=0)+dx+80))
    d['canvas']['height']=max(300,math.ceil(max([p[1] for p in points],default=0)+dy+80))

def thumbnail(d):
    shapes=[]
    for o in d['objects']:
        t=o['type'];x=o['x'];y=o['y'];w=o['w'];h=o['h']
        if t in ('route','trackLine','trackArc','anchor','note'):continue
        if t=='gear':shapes.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{w/2}" fill="#dfad93" stroke="#bd775d" stroke-width="3"/>')
        elif t in ('hookHang','hookBounce'):shapes.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{w/2}" fill="none" stroke="#ac975a" stroke-width="5"/>')
        else:
            color={'terrain':'#bdc8a6','platform':'#c6b490','spike':'#d58e77','wallSpike':'#d58e77','hazard':'#e7c5b6','bell':'#d5b96e','gate':'#b9ac8a','entry':'#82a07b','exit':'#b9a669','reward':'#dfc57e','enemy':'#a79ab2'}.get(t,'#bbc3a7')
            shapes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" rx="2"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {d["canvas"]["width"]} {d["canvas"]["height"]}"><rect width="100%" height="100%" fill="#f3f5e9"/>{"".join(shapes)}</svg>'

def write(d):
    normalize_canvas(d);identifier=d['source']['moduleId'];file=f'library/modules/{identifier}.json';thumb=f'library/thumbnails/{identifier}.svg'
    old_category=d['source']['category']
    d['source']['collection']=old_category
    d['source']['category']='工坊' if d['source']['kind']=='foundry' else '森林' if d['source']['kind']=='forest' else '平原' if identifier.startswith('plains_') else '通用'
    d['source']['integration']=status_for(identifier,COMMIT)
    requirements,evidence=from_source(d['source'],RESOURCES)
    d['source']['capabilityRequirements']=requirements
    d['source']['capabilityEvidence']=evidence
    d['capabilityRequirements']=copy.deepcopy(requirements)
    d['difficulty']={'version':1,'scale':'gunman-rush/module-difficulty/v1','score':None,'note':''}
    d['source']['difficulty']=copy.deepcopy(d['difficulty'])
    encoded=json.dumps(d,ensure_ascii=False,separators=(',',':'))
    (ROOT/file).write_text(encoded);(ROOT/thumb).write_text(thumbnail(d))
    kinds=Counter(o['type'] for o in d['objects'])
    tags=[{'gear':'齿轮 锯轮','spike':'地刺','wallSpike':'墙刺','bell':'风铃','platform':'平台','hookBounce':'钩索 弹起','hookHang':'钩索 悬挂','route':'动作 路线','enemy':'怪物','reward':'奖励'}.get(k,k) for k in kinds]
    CATALOG.append({'id':identifier,'title':d['title'],'category':d['source']['category'],'collection':old_category,'integration':d['source']['integration'],'capabilityRequirements':requirements,'difficulty':d['difficulty'],'file':'./'+file,'thumbnail':'./'+thumb,'objectCount':len(d['objects']),'tags':tags,'contentSha256':hashlib.sha256(encoded.encode()).hexdigest()})

for row in EXTRACTED:write(convert_resource(row) if row['kind']=='resource' else convert_forest(row))
batch=json.loads((ROOT/'library/source/resources/foundry/batch.json').read_text())
for category,manifests in [('工坊组合片段',[a['manifest'] for a in batch['accepted']]),('工坊连续路线',batch['itineraries'])]:
    for n,manifest in enumerate(manifests):
        identifier='foundry__'+manifest['id'];title=name(manifest.get('template_id','')) if manifest.get('template_id') else f'连续路线 {n+1:02d}'
        title+=' · '+{'base':'基础','double_jump':'二跳','air_chain':'空中链'}.get(manifest['capability_profile'],manifest['capability_profile'])
        if 'variant' in manifest:title+=f' · V{manifest["variant"]+1} P{manifest["phase_index"]}'
        row={'id':identifier,'path':'resources/foundry/batch.json','kind':'foundry','data':manifest}
        d=base(row,title,category)
        for i,node in enumerate(manifest['nodes']):
            part=convert_resource(RESOURCES[node['module_id']],node['offset'],phase=node['phase_index']*.25)
            mapping={o['id']:f'{d["id"]}/part{i}/{j}' for j,o in enumerate(part['objects'])}
            for o in part['objects']:
                o['id']=mapping[o['id']]
                for key in ('trackId','targetId'):
                    if o.get(key):o[key]=mapping[o[key]]
                # Internal module ports are retained as small seam markers.
                if o['type'] in ('entry','exit') and not (i==0 and o['type']=='entry' or i==len(manifest['nodes'])-1 and o['type']=='exit'):
                    o['x']+=o['w']/2-4;o['y']+=35-4;o.update(type='anchor',w=8,h=8,label='')
                d['objects'].append(o)
        d['description']='按原工坊 Manifest 的实际模块偏移和相位组合。回放验证配置：'+manifest['capability_profile']+'。这份编辑器草图不运行原输入回放。'
        d['source']['originalValidation']='Original batch contains native replay evidence; no new physics validation is claimed by this editor.'
        write(d)

coverage={'sourceCommit':COMMIT,'schema':1,'counts':dict(Counter(m['category'] for m in CATALOG)),
          'integrationCounts':dict(Counter(m['integration']['usage'] for m in CATALOG)),
          'total':len(CATALOG),'resourceModules':len(RESOURCES),'forestFactoryResults':sum(r['kind']=='forest' for r in EXTRACTED),
          'foundryPhrases':len(batch['accepted']),'foundryRoutes':len(batch['itineraries']),
          'scope':'All 72 authored .tres module resources; all finite standalone geometry factories listed in extract_modules.gd, including 51 forest results/variants; every accepted Foundry phrase and itinerary in the pinned batch.',
          'limits':['Does not enumerate infinitely many seeded whole maps or their generated inline connectors.','Standalone module geometry does not include enemies/Bosses placed by a full-stage encounter consumer.','Godot data factories are evaluated; no gameplay/physics acceptance is inferred.','Proposed catalogue entries with no build implementation are not fabricated.','Historical alternatives and current candidates are categorized; library inclusion does not mean production admission.']}
(ROOT/'library/catalog.json').write_text(json.dumps({'schema':2,'sourceCommit':COMMIT,'sourceRepository':'zhipijun1996/gunman-rush','modules':CATALOG},ensure_ascii=False,separators=(',',':')))
(ROOT/'library/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
print(json.dumps(coverage,ensure_ascii=False,indent=2))
