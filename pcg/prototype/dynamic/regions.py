"""Region-driven proposal constraints; never grants abilities or certifies physics.

An authored profile is distinct from the current actor's available capabilities.
All transformed geometry must be replayed by the real Godot V3 worker.
"""
from __future__ import annotations
import copy,hashlib,json,math,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'prototype/composable'))
from contracts import Registry,ContractError,RULE_BY_ID

IMPLEMENTED_MECHANISMS=frozenset(('static_terrain','one_way','wall_climb_surface','grapple_anchor','thorns','moving_platform','moving_saw'))
AUTHORED_KEYS=frozenset(('schema','version','id','status','name','description','mechanisms','capabilities','traversal','geometry','transform','generator_families','motifs'))
class RegionSpecError(ValueError):pass
class RegionTransformError(RegionSpecError):pass

def _sha(data):return hashlib.sha256(data).hexdigest()
def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def _number(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def _strings(value,path):
    if not isinstance(value,list) or any(not isinstance(x,str) or not x for x in value) or len(value)!=len(set(value)):raise RegionSpecError(path+': expected unique nonempty string IDs')
    return value
def _range(value,path):
    if not isinstance(value,list) or len(value)!=2 or not all(_number(x) and x>0 for x in value) or value[0]>value[1]:raise RegionSpecError(path+': invalid positive range')
    return value
def _keys(value,allowed,path):
    if not isinstance(value,dict) or set(value)-set(allowed):raise RegionSpecError(path+': unknown fields or invalid object')
def _index(value,count):return int(value) if _number(value) and value==int(value) and 0<=value<count else None
def _rect(value):return isinstance(value,list) and len(value)==4 and all(_number(x) for x in value) and value[2]>0 and value[3]>0

def actor_body():
    """Read the actual protected player rectangle, not a second tuning default."""
    path=ROOT/'prototype/godot/scenes/player/player.tscn';text=path.read_text()
    node=re.search(r'\[node name="CollisionShape2D"[^\n]*\]\s*shape = SubResource\("([^"]+)"\)',text)
    if not node:raise RegionSpecError('unmodelled_player_collision_node')
    shape=re.search(r'\[sub_resource type="RectangleShape2D" id="'+re.escape(node[1])+r'"\]\s*size = Vector2\(([^,]+),\s*([^\)]+)\)',text)
    if not shape:raise RegionSpecError('unmodelled_player_collision_shape')
    values=[float(shape[1])/2,float(shape[2])/2]
    if not all(math.isfinite(x) and x>0 for x in values):raise RegionSpecError('invalid_player_collision_shape')
    return values,_sha(path.read_bytes())

def validate_region_spec(authored,availablecaps,*,runtime=True):
    _keys(authored,AUTHORED_KEYS,'region')
    spec=copy.deepcopy(authored)
    if spec.get('schema')!='pcg/region-spec/v1':raise RegionSpecError('unsupported_region_schema')
    if not isinstance(spec.get('version'),int) or isinstance(spec['version'],bool) or spec['version']<1:raise RegionSpecError('invalid_region_version')
    if not re.fullmatch('[a-z][a-z0-9_]{0,63}',str(spec.get('id',''))):raise RegionSpecError('invalid_region_id')
    if spec.get('status')not in ('research_only','proposed'):raise RegionSpecError('region_status_requires_explicit_research_or_proposed')
    try:available=Registry().resolve(list(availablecaps))
    except (ContractError,TypeError) as e:raise RegionSpecError('available_capabilities/'+str(e)) from e
    mechanisms=spec.get('mechanisms');_keys(mechanisms,('allowed','required','forbidden'),'mechanisms')
    allowed=set(_strings(mechanisms.get('allowed',[]),'mechanisms.allowed'));required=set(_strings(mechanisms.get('required',[]),'mechanisms.required'));forbidden=set(_strings(mechanisms.get('forbidden',[]),'mechanisms.forbidden'))
    if not required<=allowed or allowed&forbidden:raise RegionSpecError('contradictory_mechanism_policy')
    unsupported=sorted((allowed|required)-IMPLEMENTED_MECHANISMS)
    if unsupported and spec['status']!='proposed':raise RegionSpecError('unimplemented_mechanisms:'+','.join(unsupported))
    caps=spec.get('capabilities',{});_keys(caps,('requires','preferred_challenge_capabilities'),'capabilities')
    known=set(Registry().items)
    requires=set(_strings(caps.get('requires',[]),'capabilities.requires'));preferred=set(_strings(caps.get('preferred_challenge_capabilities',[]),'capabilities.preferred_challenge_capabilities'))
    if (requires|preferred)-known:raise RegionSpecError('unregistered_capability_in_region')
    if not requires<=available:raise RegionSpecError('region_missing_available_capabilities:'+','.join(sorted(requires-available)))
    traversal=spec.get('traversal',{});_keys(traversal,('allow_repetition','must_use_all_available','min_actions','max_depth','preferred_actions'),'traversal')
    if traversal.get('must_use_all_available',False)is not False:raise RegionSpecError('region_must_not_require_all_available_capabilities')
    if traversal.get('allow_repetition',True)is not True:raise RegionSpecError('repetition_policy_must_be_explicitly_supported')
    minimum=traversal.get('min_actions',1);depth=traversal.get('max_depth',32)
    if not isinstance(minimum,int) or not isinstance(depth,int) or isinstance(minimum,bool) or isinstance(depth,bool) or not 1<=minimum<=depth<=32:raise RegionSpecError('invalid_region_search_budget')
    actions=_strings(traversal.get('preferred_actions',[]),'traversal.preferred_actions')
    if set(actions)-RULE_BY_ID.keys() and spec['status']!='proposed':raise RegionSpecError('unimplemented_region_action')
    g=spec.get('geometry',{});_keys(g,('direction','min_goal_rise','small_rock','max_contiguous_height','min_vertical_gap','port_support_exceptions'),'geometry')
    if g.get('direction','any')not in ('any','upward','horizontal'):raise RegionSpecError('unsupported_traversal_direction')
    for key in ('min_goal_rise','max_contiguous_height','min_vertical_gap'):
        if key in g and (not _number(g[key]) or g[key]<0):raise RegionSpecError('invalid_geometry/'+key)
    if 'small_rock'in g:
        rock=g['small_rock'];_keys(rock,('width','height'),'geometry.small_rock');_range(rock.get('width'),'small_rock.width');_range(rock.get('height'),'small_rock.height')
    if 'port_support_exceptions'in g:
        exc=g['port_support_exceptions'];_keys(exc,('max_width','max_height'),'geometry.port_support_exceptions')
        if any(not _number(exc.get(k)) or exc[k]<=0 for k in ('max_width','max_height')):raise RegionSpecError('invalid_port_support_exceptions')
    t=spec.get('transform',{});_keys(t,('split_climb_walls','remove_pressure_floor','remove_forbidden_pressure_cells','contact_padding','contact_x_tolerance'),'transform')
    for key in ('split_climb_walls','remove_pressure_floor','remove_forbidden_pressure_cells'):
        if key in t and not isinstance(t[key],bool):raise RegionSpecError('invalid_transform_flag/'+key)
    for key in ('contact_padding','contact_x_tolerance'):
        if key in t and (not _number(t[key]) or t[key]<0):raise RegionSpecError('invalid_transform_guard/'+key)
    _strings(spec.get('generator_families',[]),'generator_families');_strings(spec.get('motifs',[]),'motifs')
    if runtime and (spec['status']=='proposed' or unsupported):raise RegionSpecError('runtime_region_rejected:'+spec['status']+'/unimplemented='+','.join(unsupported))
    spec['profile_sha256']=_sha(_canonical(authored));spec['available_capabilities']=sorted(available)
    spec['unimplemented_mechanisms']=unsupported;spec['runtime_eligible']=spec['status']=='research_only' and not unsupported
    spec['approval_scope']='research proposal only; no formal region/Bible or human acceptance'
    return spec

def prepare_regions(specpath,availablecaps,*,runtime=True):
    path=Path(specpath);raw=path.read_bytes()
    try:authored=json.loads(raw)
    except (ValueError,UnicodeError) as e:raise RegionSpecError('invalid_region_json') from e
    spec=validate_region_spec(authored,availablecaps,runtime=runtime)
    spec['source_sha256']=_sha(raw);spec['source_path']=str(path)
    return spec

def _prepared(spec):
    if not isinstance(spec,dict) or not spec.get('runtime_eligible'):raise RegionSpecError('runtime_region_not_prepared_or_proposed')
    authored={k:v for k,v in spec.items() if k in AUTHORED_KEYS}
    if _sha(_canonical(authored))!=spec.get('profile_sha256'):raise RegionSpecError('region_profile_mutated_since_prepare')

def filter_families(spec,families=None):
    _prepared(spec);allowed=spec.get('generator_families',[])
    return list(allowed) if families is None else [family for family in families if family in allowed]

def _goal(case):
    goal=case.get('goal')
    if not _rect(goal):raise RegionSpecError('invalid_candidate_goal')
    return [goal[0]+goal[2]/2,goal[1]+goal[3]/2]

def _port_support(rect,case,half,exceptions):
    if not exceptions or rect[2]>exceptions['max_width'] or rect[3]>exceptions['max_height']:return False
    ports=[case.get('spawn'),_goal(case)]
    return any(isinstance(p,list) and len(p)==2 and all(_number(v) for v in p) and rect[0]+half[0]<=p[0]<=rect[0]+rect[2]-half[0] and abs(p[1]+half[1]-rect[1])<=2 for p in ports)

def _used_capabilities(case):
    ids=set();mapping={'ground_jump':('jump',),'air_jump':('jump','double_jump'),'wall_jump':('wall_climb',),'anchor_jump':('jump','grapple'),'hook_hang':('grapple',),'hook_bounce':('grapple',),'recoil':('shot_recoil',)}
    for action in case.get('word',[]):ids.update(mapping.get(action,()))
    return sorted(ids)

def _mechanisms(case):
    fields={'platforms':'static_terrain','one_way_platform_indices':'one_way','wall_platform_indices':'wall_climb_surface','hooks':'grapple_anchor','thorns':'thorns','moving_platforms':'moving_platform','saws':'moving_saw','bounce_mushrooms':'bounce_mushroom','spore_currents':'spore_current'}
    return {mechanism for key,mechanism in fields.items() if case.get(key)}|({'one_way'} if case.get('one_way_indices') else set())

def check_candidate(case,spec):
    """Return auditable proposal violations; [] never means physically feasible."""
    _prepared(spec);issues=[]
    def add(code,path,**details):issues.append(dict(code=code,path=path,**details))
    try:declared=Registry().resolve(case.get('capabilities'))
    except (ContractError,TypeError) as e:add('invalid_capabilities','capabilities',detail=str(e));declared=frozenset()
    available=set(spec['available_capabilities'])
    if declared-available:add('unavailable_capabilities','capabilities',ids=sorted(declared-available))
    used=set(_used_capabilities(case))
    if used-declared:add('action_uses_undeclared_capability','word',ids=sorted(used-declared))
    present=_mechanisms(case);policy=spec['mechanisms'];allowed=set(policy.get('allowed',[]));required=set(policy.get('required',[]))
    if present-IMPLEMENTED_MECHANISMS:add('unimplemented_candidate_mechanism','mechanisms',ids=sorted(present-IMPLEMENTED_MECHANISMS))
    if present-allowed:add('region_forbidden_mechanism','mechanisms',ids=sorted(present-allowed))
    if required-present:add('required_mechanism_missing','mechanisms',ids=sorted(required-present))
    if case.get('hazards'):add('unhosted_legacy_hazard_envelope','hazards')
    claims=case.get('mechanisms',[])
    if claims:
        if not isinstance(claims,list) or any(not isinstance(v,str) for v in claims):add('invalid_mechanism_claim','mechanisms')
        elif set(claims)-present:add('claimed_mechanism_has_no_consumer','mechanisms',ids=sorted(set(claims)-present))
    platforms=case.get('platforms',[])
    if not isinstance(platforms,list):add('invalid_platforms','platforms');return issues
    half,_=actor_body();g=spec.get('geometry',{});rock=g.get('small_rock');exceptions=g.get('port_support_exceptions')
    try:goal=_goal(case)
    except RegionSpecError:add('invalid_goal','goal');return issues
    spawn=case.get('spawn')
    if not isinstance(spawn,list) or len(spawn)!=2 or not all(_number(v) for v in spawn):add('invalid_spawn','spawn');return issues
    rise=spawn[1]-goal[1]
    if 'min_goal_rise'in g and rise<g['min_goal_rise']:add('insufficient_goal_rise','goal',rise=rise,minimum=g['min_goal_rise'])
    if g.get('direction')=='upward' and rise<=0:add('region_requires_upward_route','goal',rise=rise)
    if g.get('direction')=='horizontal' and abs(goal[0]-spawn[0])<abs(rise):add('region_requires_horizontal_route','goal',horizontal_displacement=abs(goal[0]-spawn[0]),vertical_displacement=abs(rise))
    for i,p in enumerate(platforms):
        if not _rect(p):add('invalid_platform_rect',f'platforms/{i}');continue
        if rock and not _port_support(p,case,half,exceptions):
            if not rock['width'][0]<=p[2]<=rock['width'][1]:add('rock_width_out_of_range',f'platforms/{i}',width=p[2],allowed=rock['width'])
            if not rock['height'][0]<=p[3]<=rock['height'][1]:add('rock_height_out_of_range',f'platforms/{i}',height=p[3],allowed=rock['height'])
    walls=[]
    for raw in case.get('wall_platform_indices',[]):
        index=_index(raw,len(platforms))
        if index is None:add('invalid_wall_index','wall_platform_indices',value=raw)
        elif _rect(platforms[index]):walls.append((index,platforms[index]))
    # Reject a tall wall relabelled as touching short rectangles.
    parent=list(range(len(walls)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,(ia,p) in enumerate(walls):
        for b,(ib,q) in enumerate(walls[a+1:],a+1):
            if min(p[0]+p[2],q[0]+q[2])-max(p[0],q[0])<=.001:continue
            gap=max(p[1],q[1])-min(p[1]+p[3],q[1]+q[3])
            if gap<=.001:parent[find(a)]=find(b)
            elif gap<g.get('min_vertical_gap',0):add('wall_rocks_not_separated',f'platforms/{ia},{ib}',gap=gap,minimum=g['min_vertical_gap'])
    groups={}
    for i,(index,p) in enumerate(walls):groups.setdefault(find(i),[]).append((index,p))
    limit=g.get('max_contiguous_height')
    if limit is not None:
        for group in groups.values():
            height=max(p[1]+p[3] for _,p in group)-min(p[1] for _,p in group)
            if height>limit:add('contiguous_wall_too_tall','wall_platform_indices',height=height,maximum=limit,indices=[i for i,_ in group])
    for i,t in enumerate(case.get('thorns',[])):
        if not isinstance(t,dict) or _index(t.get('platform_index'),len(platforms)) is None:add('invalid_thorn_host',f'thorns/{i}')
    return issues

def transform_candidate(case,reference_frames,spec):
    """Convert trace-supported long climb faces into separate real rock Cells.

    No trajectory/player/resource is moved. Removed/replaced geometry invalidates
    every old receipt. The return value still requires check_candidate and Godot.
    """
    _prepared(spec);c=copy.deepcopy(case);platforms=c.get('platforms',[])
    if not isinstance(platforms,list) or any(not _rect(p) for p in platforms):raise RegionTransformError('invalid_platforms')
    g=spec.get('geometry',{});t=spec.get('transform',{});half,body_hash=actor_body()
    oldwalls={_index(v,len(platforms)) for v in c.get('wall_platform_indices',[])}
    if None in oldwalls:raise RegionTransformError('invalid_wall_index')
    removals=set();removal_operations={}
    if t.get('remove_pressure_floor'):
        for thorn in c.get('thorns',[]):
            if thorn.get('surface_id',thorn.get('source_id'))=='pressure_floor':
                index=_index(thorn.get('platform_index'),len(platforms))
                if index is None:raise RegionTransformError('invalid_pressure_floor_host')
                if _port_support(platforms[index],c,half,dict(max_width=float('inf'),max_height=float('inf'))):raise RegionTransformError('pressure_floor_is_actual_port_support')
                removals.add(index);removal_operations[index]='remove_pressure_floor_host'
    if t.get('remove_forbidden_pressure_cells') and 'thorns'not in spec['mechanisms'].get('allowed',[]):
        # Only the exact current pressure_surfaces() Cell signature is eligible.
        # A generic pressure name never authorizes deleting useful/unknown terrain.
        one_way=set(c.get('one_way_platform_indices',[]))|set(c.get('one_way_indices',[]))
        thorns=c.get('thorns',[])
        for thorn in thorns:
            source=thorn.get('surface_id',thorn.get('source_id',''))
            if not isinstance(source,str) or not re.fullmatch(r'flight_pressure_[1-9][0-9]*',source):continue
            index=_index(thorn.get('platform_index'),len(platforms))
            if index is None:raise RegionTransformError('invalid_pressure_cell_host')
            p=platforms[index]
            signature=p[2:]==[40,24] and thorn.get('face')in ('top','bottom') and thorn.get('start_offset')==0 and thorn.get('length')==40 and thorn.get('depth')==20
            if not signature:raise RegionTransformError('unrecognized_generated_pressure_cell/'+str(index))
            shared=[x for x in thorns if _index(x.get('platform_index'),len(platforms))==index]
            if len(shared)!=1 or index in oldwalls or index in one_way:raise RegionTransformError('pressure_cell_has_nonpressure_role/'+str(index))
            if _port_support(p,c,half,dict(max_width=float('inf'),max_height=float('inf'))):raise RegionTransformError('pressure_cell_is_actual_port_support/'+str(index))
            if any(isinstance(f,dict) and f.get('grounded') and _number(f.get('x')) and _number(f.get('y')) and p[0]-half[0]<f['x']<p[0]+p[2]+half[0] and abs(f['y']+half[1]-p[1])<=2 for f in reference_frames):raise RegionTransformError('pressure_cell_has_observed_support_role/'+str(index))
            removals.add(index);removal_operations[index]='remove_forbidden_generated_pressure_cell'
    built=[];mapping={};newwalls=[];replaced=set();changes=[]
    for index,p in enumerate(platforms):
        if index in removals:mapping[index]=[];changes.append(dict(operation=removal_operations[index],old_index=index));continue
        patches=[p]
        if index in oldwalls and t.get('split_climb_walls') and p[3]>g.get('small_rock',{}).get('height',[0,float('inf')])[1]:
            rock=g.get('small_rock')
            if not rock or not rock['width'][0]<=p[2]<=rock['width'][1]:raise RegionTransformError('climb_wall_width_cannot_be_preserved')
            padding=t.get('contact_padding',0);tolerance=t.get('contact_x_tolerance',0);intervals=[]
            for f in reference_frames:
                if not isinstance(f,dict) or not all(_number(f.get(k)) for k in ('x','y')):raise RegionTransformError('invalid_reference_frame')
                state=f.get('traversal_state','free');accepted=f.get('accepted',[])
                if not isinstance(accepted,list) or any(not isinstance(e,dict) for e in accepted):raise RegionTransformError('invalid_reference_accepted_events')
                contact=state in ('wall_attach','wall_kick') or any(e.get('type')=='wall_jump' or (e.get('type')=='traversal' and e.get('state')=='wall_kick') for e in accepted)
                near=min(abs(f['x']-(p[0]-half[0])),abs(f['x']-(p[0]+p[2]+half[0])))<=tolerance
                if contact and near and p[1]-half[1]<=f['y']<=p[1]+p[3]+half[1]:intervals.append([max(p[1],f['y']-half[1]-padding),min(p[1]+p[3],f['y']+half[1]+padding)])
            if not intervals:raise RegionTransformError('no_reference_wall_contacts/'+str(index))
            merged=[];gap=g.get('min_vertical_gap',0)
            for lo,hi in sorted(intervals):
                if merged and lo<=merged[-1][1]+gap:merged[-1][1]=max(merged[-1][1],hi)
                else:merged.append([lo,hi])
            patches=[]
            for lo,hi in merged:
                height=max(rock['height'][0],hi-lo)
                if height>rock['height'][1]:raise RegionTransformError('protected_contact_band_exceeds_rock_height/'+str(index))
                center=(lo+hi)/2;patches.append([p[0],center-height/2,p[2],height])
            replaced.add(index);changes.append(dict(operation='split_climb_wall',old_index=index,rocks=len(patches)))
        mapping[index]=[]
        for patch in patches:
            mapped=len(built);built.append(patch);mapping[index].append(mapped)
            if index in oldwalls:newwalls.append(mapped)
    c['platforms']=built;c['wall_platform_indices']=newwalls
    for key in ('one_way_platform_indices','one_way_indices'):
        if key in c:
            output=[]
            for raw in c[key]:
                i=_index(raw,len(platforms))
                if i is None:raise RegionTransformError('invalid_one_way_index')
                output.extend(mapping[i])
            c[key]=output
    thorns=[]
    for thorn in c.get('thorns',[]):
        i=_index(thorn.get('platform_index'),len(platforms))
        if i is None:raise RegionTransformError('invalid_thorn_host')
        if i in removals or i in replaced:
            changes.append(dict(operation='remove_old_host_thorn',surface_id=thorn.get('surface_id',thorn.get('source_id','')),old_index=i));continue
        thorn['platform_index']=mapping[i][0];thorns.append(thorn)
    c['thorns']=thorns
    c['id']=str(c.get('id','candidate'))+'-region-'+spec['id']+'-'+spec['profile_sha256'][:8]
    c['region_profile']=dict(schema='pcg/region-binding/v1',id=spec['id'],version=spec['version'],profile_sha256=spec['profile_sha256'],status=spec['status'],available_capabilities=spec['available_capabilities'],declared_challenge_used_subset=_used_capabilities(c),used_subset_scope='Intended action word; not proven minimum ability requirements',body_shape_source_sha256=body_hash,transformations=changes,old_to_new_platform_indices={str(i):v for i,v in mapping.items()},validation_status='requires_real_physics_revalidation',formal_region_approval=False)
    c['region_profile']['proposal_violations']=check_candidate(c,spec)
    return c
