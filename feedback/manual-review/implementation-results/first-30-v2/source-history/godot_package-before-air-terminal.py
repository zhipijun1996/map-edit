"""Offline data compiler. Never imports a recipe, generator, or physics search.

Mapnote objects own content; canonical cases supply frozen playback/entry data.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, re, shutil, subprocess, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).with_name('runtime')
PROJECT = ROOT/'pcg/prototype/godot'
VERSION = 'foundation-data-runtime/v2'
LEGACY_VERSION = 'foundation-data-runtime/v1'
EXTENDED_VERSION = 'foundation-data-runtime/v3'

class PackageError(ValueError):
    def __init__(self, code, details):
        self.code, self.details = code, details
        super().__init__(f'{code}: {details}')

_SHA_CACHE={}
def sha(path):
    # A batch repeatedly binds the same 870 immutable runtime files. Cache only
    # a digest, keyed by kernel file identity/change timestamps, never a pass.
    # ctime detects same-size edits even when a caller restores mtime.
    path=Path(path).resolve();before=path.stat()
    signature=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
    previous=_SHA_CACHE.get(path)
    if previous and previous[0]==signature:return previous[1]
    with path.open('rb')as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    after=path.stat()
    final=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    if final!=signature:raise ValueError('package_source_changed_while_hashing:'+str(path))
    if len(_SHA_CACHE)>=16384:_SHA_CACHE.clear()
    _SHA_CACHE[path]=(signature,digest)
    return digest
def _json(path): return json.loads(Path(path).read_text())
def _write(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def _rect(o): return [o[k] for k in ('x','y','w','h')]
def _center(o): return [o['x']+o['w']/2, o['y']+o['h']/2]
def _fail(code, **details): raise PackageError(code, details)
def _equal(actual, expected, field, case_id=None):
    def same(a,b):
        if isinstance(a,(float,int))and not isinstance(a,bool)and isinstance(b,(float,int))and not isinstance(b,bool):return abs(a-b)<=1e-7
        if isinstance(a,list)and isinstance(b,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
        if isinstance(a,dict)and isinstance(b,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
        return a==b
    if not same(actual,expected):_fail('geometry_mismatch',field=field,case_id=case_id,objects=actual,canonical=expected)

def bind_case_behavior(doc, cases, *, _extension=False):
    """Preserve formerly unexported behavioral parameters before hashing a sketch.

    Geometry still comes from explicit objects. Only parameters without an
    editable geometry representation are attached, never a second full case.
    Multiple route witnesses must describe the same installed Cells.
    """
    if not _extension:
        from . import godot_package_v5
        if godot_package_v5.required(doc,cases):return godot_package_v5.bind_case_behavior(doc,cases)
        from . import godot_package_v4
        if godot_package_v4.required(doc,cases):return godot_package_v4.bind_case_behavior(doc,cases)
    doc=copy.deepcopy(doc)
    if not cases:return doc
    first=cases[0]
    maps={key:{v.get('id',v.get('source_id',v.get('platform_id'))):v for v in first.get(key,[])}
          for key in ('enemies','saws','latches')}
    for o in doc.get('objects',[]):
        kind=o['type'];source=None;parameters={}
        if kind=='enemy':
            source=maps['enemies'].get(o.get('sourceId'))
            if source:parameters={k:source[k] for k in ('initial_idle_cooldown','variant_definition','variant_tres_sha256')if k in source}
        elif kind=='gear':
            source=maps['saws'].get(o.get('sourceId'))
            if source:
                parameters={k:source[k]for k in ('damage','contact_interval')if k in source}
                if not o.get('trackId'):parameters.update({k:source[k]for k in ('period','initial_phase')if k in source})
        elif kind in ('spike','wallSpike'):
            source=next((v for v in first.get('thorns',[])if v['surface_id']==o.get('sourceId')),None)
            if source:parameters={k:source[k]for k in ('damage','contact_interval')if k in source}
        elif kind in ('bell','switch'):
            source=maps['latches'].get(o.get('sourceId'))
            if source is None and kind=='bell' and not o.get('sourceId'):
                found=[v for v in first.get('latches',[])if all(abs(a-b)<1e-7 for a,b in zip(_center(o),v['bell']))]
                if len(found)==1:source=found[0];o['sourceId']=source['id']
            if source:
                target=next((v for v in doc['objects']if v['id']==o.get('targetId')),None)
                if target and target['type']=='gate' and not target.get('mechanics'):
                    target['mechanics']=dict(kind='timed_gate',openSeconds=source.get('open_seconds',0))
                if target and target['type']=='gate' and 'openSeconds' not in target.get('mechanics',{}):target.setdefault('mechanics',{})['openSeconds']=source.get('open_seconds',0)
                # Sensor cases retain the native disabled receiver's location.
                if kind=='switch':parameters['disabledReceiverPosition']=source['bell']
                if source.get('ferry_id'):parameters['inactiveGate']=source['gate']
                parameters.update({k:source[k]for k in ('ferry_id','carrier_mount','attack_relay','carrier_dock','occupancy','prompt','kind','link_color','actuator_id')if k in source})
        if parameters:o.setdefault('mechanics',{})['runtimeParameters']=copy.deepcopy(parameters)
    by_id={o['id']:o for o in doc.get('objects',[])}
    for spec in first.get('latches',[]):
        bell=next((o for o in doc['objects']if o['type']=='bell'and o.get('sourceId')==spec['id']),None)
        if bell is None:continue
        if 'sequence_offset'in spec:
            offset=spec['sequence_offset']
            if any(offset):
                second=next((o for o in doc['objects']if o.get('sourceId')==spec['id']+'/second'),None)
                if second is None:
                    at=[bell['x']+bell['w']/2+offset[0],bell['y']+bell['h']/2+offset[1]]
                    doc['objects'].append(dict(id=bell['id']+'/second',type='bell',x=at[0]-14,y=at[1]-17,w=28,h=34,rotation=0,sourceId=spec['id']+'/second',targetId=bell['targetId'],mechanics=dict(service='ShotLatch',sequenceStep=2,sharesHealthWith=bell['id'])))
            else:bell.setdefault('mechanics',{}).setdefault('runtimeParameters',{})['sequence_offset']=[0,0]
        if 'sequence_gate'in spec:
            rect=spec['sequence_gate'];identifier=bell['id']+'/sequence-gate'
            if identifier not in by_id:
                doc['objects'].append(dict(id=identifier,type='gate',x=rect[0],y=rect[1],w=rect[2],h=rect[3],rotation=0,mechanics=dict(kind='original_sequence_gate',ownerBellId=bell['id'])))
            bell.setdefault('mechanics',{})['sequenceGateId']=identifier
    for i,o in enumerate(v for v in doc['objects']if v['type']in ('hookHang','hookBounce')):
        source=first.get('hooks',[])[i]
        if source.get('source_id'):o['sourceId']=source['source_id']
    occupancy=doc.get('generationContract',{}).get('space',{}).get('occupancy')
    if isinstance(occupancy,dict):
        refs=occupancy.setdefault('objectIds',[])
        for o in doc['objects']:
            if o['type']not in ('entry','exit','route','anchor','note','trackLine','trackArc')and o['id']not in refs:refs.append(o['id'])
    return doc


def content_from_objects(doc):
    """Decode the already-authored native Cells; never run a content generator."""
    objects=doc.get('objects')
    if not isinstance(objects,list):_fail('missing_objects')
    by_id={o['id']:o for o in objects}
    if len(by_id)!=len(objects):_fail('duplicate_object_id')
    content={k:[] for k in ('platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','reward_sites')}
    used=set();platforms=[]
    legal={'terrain','platform','bell','switch','gate','reward','route','entry','exit','note','anchor','hazard','spike','wallSpike','gear','trackLine','hookHang','hookBounce','enemy'}
    for o in objects:
        kind=o.get('type')
        if kind not in legal:_fail('unsupported_cell',object_id=o['id'],kind=kind)
        if o.get('rotation',0)!=0 and kind not in ('spike','wallSpike'):_fail('unsupported_rotation',object_id=o['id'])
        if kind in ('terrain','platform')and not o.get('trackId'):
            if not isinstance(o.get('sourceIndex'),int):_fail('missing_platform_index',object_id=o['id'])
            platforms.append(o)
        if kind in ('route','entry','exit','note','anchor'):used.add(o['id'])
        if kind=='note'and o.get('mechanics')and o['mechanics'].get('kind')!='carrier_control':_fail('unsupported_mechanism_note',object_id=o['id'])
    platforms.sort(key=lambda o:o['sourceIndex'])
    if [o['sourceIndex']for o in platforms]!=list(range(len(platforms))):_fail('non_contiguous_platform_indices')
    for o in platforms:
        i=o['sourceIndex'];content['platforms'].append(_rect(o));used.add(o['id'])
        if o['type']=='platform':content['one_way_platform_indices'].append(i)
        if o.get('wallClimbable',False):content['wall_platform_indices'].append(i)
    for o in objects:
        kind=o['type'];m=o.get('mechanics',{});params=copy.deepcopy(m.get('runtimeParameters',{}))
        track=by_id.get(o.get('trackId'))
        if kind=='hazard':content['hazards'].append(_rect(o));used.add(o['id'])
        elif kind in ('spike','wallSpike'):
            host=by_id.get(o.get('hostId'))
            if not host or host not in platforms:_fail('missing_thorn_host',object_id=o['id'])
            # Host contact, rather than display rotation, determines actual face.
            x,y,w,h=_rect(o);px,py,pw,ph=_rect(host);near=lambda a,b:abs(a-b)<1e-5
            if near(y+h,py):face='top';offset=x-px;length=w;depth=h
            elif near(y,py+ph):face='bottom';offset=x-px;length=w;depth=h
            elif near(x+w,px):face='left';offset=y-py;length=h;depth=w
            elif near(x,px+pw):face='right';offset=y-py;length=h;depth=w
            else:_fail('thorn_not_attached',object_id=o['id'])
            thorn=dict(surface_id=o['sourceId'],platform_index=host['sourceIndex'],face=face,start_offset=offset,length=length,depth=depth)
            thorn.update(params);content['thorns'].append(thorn);used.add(o['id'])
        elif kind in ('gear','platform')and (track or kind=='gear'):
            if track is None and kind=='gear':
                if 'period'not in params:_fail('stationary_saw_missing_period',object_id=o['id'])
                x,y=_center(o);track=dict(type='trackLine',points=[dict(x=x,y=y),dict(x=x,y=y)],duration=params.pop('period'),initialPhase=params.pop('initial_phase',0))
            if not track or track['type']!='trackLine' or len(track.get('points',[]))!=2:_fail('unsupported_track',object_id=o['id'])
            a,b=track['points'];ident=o.get('sourceId')
            if not ident:_fail('missing_native_cell_identity',object_id=o['id'])
            if kind=='gear':
                _equal(o['w'],o['h'],o['id']+'/circular_size')
                value=dict(source_id=ident,origin=[(a['x']+b['x'])/2,(a['y']+b['y'])/2],travel=[(b['x']-a['x'])/2,(b['y']-a['y'])/2],radius=o['w']/2,period=track['duration'],initial_phase=track.get('initialPhase',0))
                value.update(params)
                phase=math.sin(2*math.pi*value['initial_phase'])
                _equal(_center(o),[value['origin'][i]+value['travel'][i]*phase for i in range(2)],o['id']+'/initial_position')
                content['saws'].append(value)
            else:
                value=dict(platform_id=ident,start=[a['x'],a['y']],finish=[b['x'],b['y']],size=[o['w'],o['h']],travel_duration=track['duration'],dwell_duration=track.get('dwell',0),initial_phase=track.get('initialPhase',0))
                value.update(params)
                duration=value['travel_duration'];dwell=value['dwell_duration'];at=value['initial_phase']*2*(duration+dwell)
                f=0 if at<dwell else (at-dwell)/duration if at<dwell+duration else 1 if at<2*dwell+duration else 1-(at-2*dwell-duration)/duration
                _equal(_center(o),[value['start'][i]+(value['finish'][i]-value['start'][i])*f for i in range(2)],o['id']+'/initial_position')
                content['moving_platforms'].append(value)
            used.add(o['id'])
            if 'id'in track:used.add(track['id'])
        elif kind in ('hookHang','hookBounce'):
            x,y=_center(o);value=dict(x=x,y=y,kind='hang'if kind=='hookHang'else'bounce')
            if o.get('sourceId'):value['source_id']=o['sourceId']
            content['hooks'].append(value);used.add(o['id'])
        elif kind=='enemy':
            if not o.get('sourceId')or o.get('definition')not in ('plains_sentry','plains_charger','plains_diver'):_fail('unsupported_cell',object_id=o['id'],kind=kind)
            definition=PROJECT/'resources/enemies'/(o['definition']+'.tres')
            size=re.search(r'collision_size = Vector2\(([^,]+), ([^)]+)\)',definition.read_text())
            if not size:_fail('missing_enemy_collision_size',object_id=o['id'])
            _equal([o['w'],o['h']],list(map(float,size.groups())),o['id']+'/body_size')
            value=dict(id=o['sourceId'],definition=o['definition'],position=_center(o))
            if m.get('initialIdleCooldown')is not None:value['initial_idle_cooldown']=m['initialIdleCooldown']
            value.update(params);content['enemies'].append(value);used.add(o['id'])
    for bell in [o for o in objects if o['type']in ('bell','switch') and not o.get('mechanics',{}).get('returnSideOnly')and o.get('mechanics',{}).get('sequenceStep')!=2]:
        target=by_id.get(bell.get('targetId'));bm=bell.get('mechanics',{});params=copy.deepcopy(bm.get('runtimeParameters',{}));ident=bell.get('sourceId')
        if not target:_fail('unsupported_bell_target',object_id=bell['id'])
        if not ident:_fail('missing_bell_source_id',object_id=bell['id'])
        used.add(bell['id'])
        if target['type']=='platform'and target.get('trackId'):
            m={};kind='timed_gate'
            gate=params.pop('inactiveGate',None)
            if gate is None:_fail('missing_inactive_carrier_gate',object_id=bell['id'])
            latch=dict(id=ident,bell=_center(bell),gate=gate,open_seconds=0,ferry_id=target['sourceId'])
        else:
            if target['type']!='gate':_fail('unsupported_bell_target',object_id=bell['id'])
            m=target.get('mechanics',{});kind=m.get('kind')
            if kind not in ('timed_gate','complementary_gates','permanent_sequence_gate','timed_sequence_gate','carrier_occupancy_gate','occupancy_gate','enemy_attack_relay_gate'):_fail('unsupported_gate_kind',object_id=target['id'],kind=kind)
            latch=dict(id=ident,bell=_center(bell),gate=_rect(target),open_seconds=m.get('openSeconds',0));used.add(target['id'])
        if bell['type']=='switch':latch['bell']=params.pop('disabledReceiverPosition',bm.get('originalBellBody',{}).get('position'))
        else:_equal([bell['w'],bell['h']],[28,34],bell['id']+'/hitbox')
        params.pop('inactiveGate',None)
        latch.update(params)
        if bm.get('sequenceGateId'):
            sequence_gate=by_id.get(bm['sequenceGateId'])
            if not sequence_gate or sequence_gate['type']!='gate':_fail('missing_sequence_gate',object_id=bell['id'])
            latch['sequence_gate']=_rect(sequence_gate);used.add(sequence_gate['id'])
        if 'carrier_dock'in latch:_equal(_rect(bell),latch['carrier_dock']['rect'],bell['id']+'/native_sensor_rect')
        if 'occupancy'in latch:
            _equal(_rect(bell),latch['occupancy']['rect'],bell['id']+'/native_sensor_rect')
            _equal(bm.get('mode'),latch['occupancy']['mode'],bell['id']+'/native_sensor_mode')
        if 'attack_relay'in latch:
            actor=by_id.get(bm.get('enemyObjectId'))
            if not actor or actor['type']!='enemy':_fail('missing_attack_relay_actor',object_id=bell['id'])
            _equal(actor.get('sourceId'),latch['attack_relay']['enemy_id'],bell['id']+'/native_enemy')
            _equal(bm.get('onNativeState'),'attack',bell['id']+'/native_state')
        if 'carrier_mount'in latch:
            host=by_id.get(bell.get('hostId'))
            if not host or host.get('sourceId')!=latch['carrier_mount']:_fail('missing_mounted_receiver_host',object_id=bell['id'])
            if 'localReceiverOffset'in bm:_equal([a-b for a,b in zip(_center(bell),_center(host))],bm['localReceiverOffset'],bell['id']+'/mount_offset')
        if kind=='complementary_gates':
            second=by_id.get(m.get('gateB'))
            if not second or second['type']!='gate'or m.get('gateA')!=target['id']:_fail('invalid_pair_binding',object_id=bell['id'])
            for field in ('kind','initialOpen','gateA','gateB'):
                _equal(bm.get(field),m.get(field),bell['id']+'/'+field);_equal(second.get('mechanics',{}).get(field),m.get(field),second['id']+'/'+field)
            _equal(bell.get('targetIds'),[target['id'],second['id']],bell['id']+'/targets')
            if m.get('initialOpen')not in ('A','B'):_fail('invalid_pair_initial_state',object_id=bell['id'])
            latch.update(paired_gate=_rect(second),initial_open=m['initialOpen']);used.add(second['id'])
        returns=[o for o in objects if o['type']=='bell'and o.get('sourceId')==ident+'/return']
        if len(returns)>1:_fail('multiple_return_receivers',latch=ident)
        if returns:
            other=returns[0];_equal(other.get('targetId'),bell.get('targetId'),other['id']+'/target');_equal([other['w'],other['h']],[28,34],other['id']+'/hitbox')
            if not other.get('mechanics',{}).get('returnSideOnly'):_fail('return_receiver_semantics',object_id=other['id'])
            latch['return_access']=_center(other);used.add(other['id'])
        seconds=[o for o in objects if o['type']=='bell'and o.get('sourceId')==ident+'/second']
        if seconds:
            if len(seconds)!=1:_fail('multiple_sequence_receivers',latch=ident)
            second=seconds[0];_equal(second.get('targetId'),bell.get('targetId'),second['id']+'/target')
            latch['sequence_offset']=[a-b for a,b in zip(_center(second),latch['bell'])];used.add(second['id'])
        if kind in ('timed_gate','permanent_sequence_gate','timed_sequence_gate')and 'returnAccess'in m:_equal(m.get('returnAccess'),latch.get('return_access'),target['id']+'/returnAccess')
        content['latches'].append(latch)
    for o in [v for v in objects if v['type']=='reward']:
        m=o.get('mechanics',{});source=m.get('source')
        if m.get('service')!='SimpleRoomReward'or m.get('kind')!='chest'or not isinstance(source,dict):_fail('unsupported_reward',object_id=o['id'])
        _equal([o['w'],o['h']],[36,36],o['id']+'/size');_equal(_center(o),source.get('position'),o['id']+'/position');_equal(m.get('amount'),source.get('amount'),o['id']+'/amount')
        if set(source)!=set(('id','position','region','amount')):_fail('unsupported_reward_fields',object_id=o['id'],fields=sorted(source))
        content['reward_sites'].append(copy.deepcopy(source));used.add(o['id'])
    for o in objects:
        m=o.get('mechanics',{})
        if o['type'] in ('gate','note')and m.get('kind')=='carrier_control'and m.get('collision')=='disabled_by_original_bind_motion':
            candidates=[l for l in content['latches']if l.get('ferry_id')==m.get('carrierId',m.get('ferryId'))]
            if not candidates:_fail('unbound_disabled_gate',object_id=o['id'])
            _equal(_rect(o),candidates[0]['gate'],o['id']+'/inactiveGate');used.add(o['id'])
    unused=set(by_id)-used
    if unused:_fail('unbound_content_objects',objects=sorted(unused))
    return content

def audit_cases(doc, cases, *, require_replay=True, _extension=False):
    if not _extension:
        from . import godot_package_v5
        if godot_package_v5.required(doc,cases):return godot_package_v5.audit_cases(doc,cases,require_replay=require_replay)
        from . import godot_package_v4
        if godot_package_v4.required(doc,cases):return godot_package_v4.audit_cases(doc,cases,require_replay=require_replay)
    content=content_from_objects(doc)
    if not cases: _fail('empty_canonical_cases')
    audited=[]
    for case in cases:
        if require_replay and (not isinstance(case.get('recorded_frames'),list)or not case['recorded_frames']):_fail('missing_frozen_replay',case_id=case.get('id'))
        native_fields={
            'thorns':{'surface_id','platform_index','face','start_offset','length','depth','damage','contact_interval'},
            'saws':{'source_id','origin','travel','radius','period','initial_phase','damage','contact_interval'},
            'moving_platforms':{'platform_id','start','finish','size','travel_duration','dwell_duration','initial_phase'},
            'hooks':{'x','y','kind','source_id'},
            'enemies':{'id','definition','position','initial_idle_cooldown'},
            'latches':{'id','bell','gate','open_seconds','paired_gate','initial_open','return_access','prompt','ferry_id','carrier_mount','sequence_offset','sequence_gate','occupancy','carrier_dock','attack_relay','kind','link_color','actuator_id'}}
        for field,allowed in native_fields.items():
            for spec in case.get(field,[]):
                unknown=set(spec)-allowed
                if unknown:_fail('unsupported_native_behavior',case_id=case.get('id'),field=field,parameters=sorted(unknown))
        for spec in case.get('latches',[]):
            if 'kind'in spec and spec['kind']not in ('safe_lesson','ferry_bell','timed','sequence','remote_sequence','remote','shot_recoil_combo','toggle_ferry'):_fail('unsupported_latch_kind',case_id=case.get('id'),kind=spec['kind'])
            if 'actuator_id'in spec and spec['actuator_id']!=spec.get('ferry_id'):_fail('unbound_latch_actuator',case_id=case.get('id'))
        for field,value in content.items():
            expected=case.get(field,case.get('one_way_indices',[])if field=='one_way_platform_indices'else [])
            if field=='thorns':
                expected=[dict(v,face=['top','left','right','bottom'][v['face']]if isinstance(v.get('face'),int)else v['face'])for v in expected]
            if field=='latches':
                expected=[{k:v for k,v in l.items()if k!='prompt'}for l in expected]
                value=[{k:v for k,v in l.items()if k!='prompt'}for l in value]
                for item in expected+value:item.setdefault('open_seconds',0)
            _equal(value,expected,field,case.get('id'))
        audited.append(dict(case_id=case['id'],recorded_frames=len(case.get('recorded_frames',[])),objects_equal=True))
    return content,dict(schema='pcg/package-object-case-audit/v1',passed=True,cases=audited,objects_are_content_source=True,scope='exact supported Cell geometry and behavior; Port/foundation certification handled separately')

def _dependencies(project, version=VERSION):
    """Pin the installed original runtime without copying its asset tree."""
    paths=set()
    provenance=_json(project/'source_provenance.json')
    records=provenance.get('files',{})
    if isinstance(records,dict):
        for name in records:
            p=project/name
            if not p.is_file():_fail("missing_original_runtime",path=str(p))
            if p.is_file():
                if sha(p)!=records[name]:_fail("runtime_original_changed",path=str(p))
                paths.add(p)
    else:
        for row in records:
            p=project/row.get('path',row.get('file',''))
            if p.is_file():paths.add(p)
    # Exact adapters used by this data consumer, not generation/search scripts.
    paths.update(RUNTIME/name for name in ('module_loader.gd','local_rewards.gd','package_demo.gd'))
    if version==EXTENDED_VERSION:
        paths.update(RUNTIME/name for name in ('module_loader_v3.gd','package_demo_v3.gd'))
        base=ROOT/'pcg/prototype/creative_batches'
        paths.update(base/name for name in ('batch30_d05/mount_v1.gd','occupancy/binding_v1.gd','occupancy/occupancy_latch_v1.gd','machinery/dock_binding_v11.gd','machinery/dock_latch_v11.gd','enemy_world/attack_relay_v1.gd'))
    paths.update([project/'source_provenance.json',project/'project.godot',project/'plains_cells.gd',project/'dynamic_context.gd',project/'capability_adapter.gd',project/'plains_lifecycle.gd',ROOT/'pcg/prototype/workshop/mechanics.gd'])
    pair=ROOT/'pcg/prototype/creative_batches/batch30_cell'
    paths.update(pair/n for n in ('runtime_v3.gd','pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd'))
    rows=[]
    for p in sorted(paths):
        if not p.is_file():_fail('missing_runtime_dependency', path=str(p))
        try:name=p.relative_to(ROOT).as_posix()
        except ValueError:_fail('external_project_not_supported',path=str(project))
        row=dict(path=name,sha256=sha(p))
        if p.is_relative_to(project):row['resourcePath']='res://'+p.relative_to(project).as_posix()
        rows.append(row)
    return rows

def _bundle_rows(dependencies):
    rows=[]
    for dependency in dependencies:
        # Original loader's unchanged relative preload needs this res:// alias.
        alias=dependency['path']=='pcg/prototype/godot/plains_cells.gd'
        if 'resourcePath'not in dependency or alias:
            rows.append(dict(sourcePath=dependency['path'],packagePath='runtime/'+dependency['path'],sha256=dependency['sha256'],sameByteCompiledCopy=True,resourcePathAlias=dependency.get('resourcePath')if alias else None))
    return rows

def _scene_text(stable_id, name, reference):
    return '[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path='+json.dumps(reference)+' id="1"]\n[node name='+json.dumps(stable_id.replace('-','_')+('_demo'if name=='demo'else''))+' type="Node2D"]\nscript = ExtResource("1")\n'

def compile_package(module_path, cases_path, output_dir, *, stable_id=None, project_root=None, _extension=None):
    module_path=Path(module_path).resolve();cases_path=Path(cases_path).resolve();out=Path(output_dir).resolve();project=Path(project_root or PROJECT).resolve()
    if project!=PROJECT:_fail('unsupported_runtime_project',expected=str(PROJECT),actual=str(project))
    doc=_json(module_path);raw=_json(cases_path);cases=raw.get('cases',[])if isinstance(raw,dict)else raw
    if _extension is None:
        from . import review_first30_runtime_v2
        if review_first30_runtime_v2.required(doc,cases):_extension=review_first30_runtime_v2
        from . import review_air_runtime
        if _extension is None and review_air_runtime.required(doc,cases):_extension=review_air_runtime
        from . import godot_package_v4
        from . import godot_package_v5
        if _extension is None and godot_package_v5.required(doc,cases):_extension=godot_package_v5
        elif _extension is None and godot_package_v4.required(doc,cases):_extension=godot_package_v4
    content,audit=(_extension.audit_cases if _extension else audit_cases)(doc,cases)
    stable_id=stable_id or re.sub(r'[^a-zA-Z0-9_-]+','-',str(doc.get('id','module'))).strip('-')
    if not stable_id or '/'in stable_id or '\\'in stable_id:_fail('invalid_stable_id',stable_id=stable_id)
    if out.exists()and any(out.iterdir()):_fail('output_exists',path=str(out))
    version=EXTENDED_VERSION if any(content[k]for k in ('hazards','thorns','saws','moving_platforms','hooks','enemies'))or any(any(k in l for k in ('sequence_offset','occupancy','carrier_dock','attack_relay','kind'))for l in content['latches'])else VERSION
    if _extension:version=_extension.VERSION
    deps=_extension.dependencies(project)if _extension else _dependencies(project,version)
    # Build in a sibling directory; invalid inputs never leave a partial package.
    out.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.package-',dir=out.parent))
    try:
        shutil.copyfile(module_path,stage/'module.mapnote.json');shutil.copyfile(cases_path,stage/'cases.json')
        content.update(schema='pcg/compiled-module-content/v1',source_sha256=sha(module_path),stable_id=stable_id,ports=copy.deepcopy(doc.get('generationContract',{}).get('ports',[])),world_bounds=cases[0].get('world_bounds',[-5000,-5000,15000,15000]),entry_port=cases[0]['entry_port'],exit_port=cases[0]['exit_port'])
        _write(stage/'compiled-content.json',content);_write(stage/'geometry-audit.json',audit)
        bundled=_bundle_rows(deps)
        for row in bundled:
            target=stage/row['packagePath'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['sourcePath'],target)
        for name,script in (_extension.SCENES if _extension else [('module','module_loader_v3.gd'if version==EXTENDED_VERSION else'module_loader.gd'),('demo','package_demo_v3.gd'if version==EXTENDED_VERSION else'package_demo.gd')]):
            (stage/(name+'.tscn')).write_text(_scene_text(stable_id,name,'runtime/pcg/migration/runtime/'+script))
        manifest=dict(schema='pcg/godot-module-package/v1',compiler_version=version,compilerSource=dict(path='pcg/migration/godot_package.py',sha256=sha(__file__)),stable_id=stable_id,source=dict(module_sha256=sha(module_path),cases_sha256=sha(cases_path),objects_are_content_source=True),scene='module.tscn',demo_scene='demo.tscn',data='compiled-content.json',runtimeDependencies=deps,bundledRuntime=bundled,portableLayout=dict(kind='package-local-repository-mirror/v1',root='runtime',independentOfPackageDepth=True,sourceScriptsModified=False),requiredProject='pcg/prototype/godot',resourceInstallation='Install the pinned original res:// runtime and four Harness adapters once. Nine small scripts are byte-identical package-local copies (including one plains_cells relative-path alias); no original game asset tree is copied. Formal game integration remains NOT_RUN.',onlineGeneration=False,physicsReimplemented=False,geometryAudit=audit,gameAdapter=dict(api='bind_player(controller, policy, lifetime, wallet)',status='IMPLEMENTED_NOT_YET_LOADED',player_spawned=False,capabilities_granted=False,resources_reset=False,mirror_x='UNSUPPORTED_UNCERTIFIED',closures='UNSUPPORTED_UNCERTIFIED'),godotLoad=dict(passed=False,status='NOT_RUN'))
        if _extension:_extension.decorate_manifest(manifest,stage)
        manifest['artifacts']={p.relative_to(stage).as_posix():sha(p)for p in sorted(stage.rglob('*'))if p.is_file()}
        _write(stage/'godot-package.json',manifest)
        if out.exists():out.rmdir()
        stage.rename(out)
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True);raise
    return manifest

def _internal(package, name):
    path=(package/name).resolve()
    if not path.is_relative_to(package) or not path.is_file(): _fail('missing_or_external_package_artifact',path=name)
    return path

def verify_package(output_dir, require_loaded=True, *, _extension=None):
    """Recompute bindings and observed results; a metadata passed=True is ignored."""
    package=Path(output_dir).resolve();manifest=_json(_internal(package,'godot-package.json'))
    if _extension is None:
        from . import review_first30_runtime_v2
        if manifest.get('compiler_version')==review_first30_runtime_v2.VERSION:return review_first30_runtime_v2.verify_package(package,require_loaded=require_loaded)
        from . import review_air_runtime
        if manifest.get('compiler_version')==review_air_runtime.VERSION:return review_air_runtime.verify_package(package,require_loaded=require_loaded)
        from . import godot_package_v4
        from . import godot_package_v5
        if manifest.get('compiler_version')==godot_package_v5.VERSION:return godot_package_v5.verify_package(package,require_loaded=require_loaded)
        if manifest.get('compiler_version')==godot_package_v4.VERSION:return godot_package_v4.verify_package(package,require_loaded=require_loaded)
    if manifest.get('schema')!='pcg/godot-module-package/v1' or manifest.get('compiler_version')not in (VERSION,LEGACY_VERSION,EXTENDED_VERSION,*([_extension.VERSION]if _extension else [])):_fail('wrong_package_schema')
    required={'module.mapnote.json','cases.json','compiled-content.json','geometry-audit.json','module.tscn','demo.tscn'}
    if not required<=set(manifest.get('artifacts',{})):_fail('missing_artifact_bindings',missing=sorted(required-set(manifest.get('artifacts',{}))))
    for name,expected in manifest['artifacts'].items():
        if sha(_internal(package,name))!=expected:_fail('changed_package_artifact',path=name)
    for key,name in [('module_sha256','module.mapnote.json'),('cases_sha256','cases.json')]:
        if manifest.get('source',{}).get(key)!=sha(package/name):_fail('changed_package_source',path=name)
    dependencies=manifest.get('runtimeDependencies',[])
    if not dependencies:_fail('missing_runtime_bindings')
    expected_dependencies=_extension.dependencies(PROJECT)if _extension else _dependencies(PROJECT,manifest.get('compiler_version'))
    _equal(dependencies,expected_dependencies,'runtimeDependencies')
    portable=bool(_extension)or manifest.get('compiler_version')in (VERSION,EXTENDED_VERSION)
    if portable:
        expected_bundled=_bundle_rows(dependencies)
        _equal(manifest.get('bundledRuntime'),expected_bundled,'bundledRuntime')
        _equal(manifest.get('portableLayout'),dict(kind='package-local-repository-mirror/v1',root='runtime',independentOfPackageDepth=True,sourceScriptsModified=False),'portableLayout')
        source=manifest.get('compilerSource',{})
        if source.get('path')!='pcg/migration/godot_package.py' or not re.fullmatch(r'[0-9a-f]{64}',source.get('sha256','')):_fail('missing_compiler_source_binding')
        bundled_names={row['packagePath']for row in expected_bundled}
        actual_names={f.relative_to(package).as_posix()for f in (package/'runtime').rglob('*')if f.is_file()}
        _equal(actual_names,bundled_names,'bundled_file_set')
        for row in expected_bundled:
            if row['packagePath']not in manifest['artifacts']or sha(_internal(package,row['packagePath']))!=row['sha256']:_fail('changed_bundled_runtime',path=row['packagePath'])
    for name,script in (_extension.SCENES if _extension else [('module','module_loader_v3.gd'if manifest.get('compiler_version')==EXTENDED_VERSION else'module_loader.gd'),('demo','package_demo_v3.gd'if manifest.get('compiler_version')==EXTENDED_VERSION else'package_demo.gd')]):
        reference='runtime/pcg/migration/runtime/'+script if portable else str(RUNTIME/script)
        _equal((package/(name+'.tscn')).read_text(),_scene_text(manifest['stable_id'],name,reference),'scene/'+name)
    for row in dependencies:
        path=(ROOT/row['path']).resolve()
        if not path.is_relative_to(ROOT)or not path.is_file()or sha(path)!=row['sha256']:_fail('changed_runtime_dependency',path=row['path'])
    doc=_json(package/'module.mapnote.json');raw=_json(package/'cases.json');cases=raw['cases']if isinstance(raw,dict)else raw
    content,audit=(_extension.audit_cases if _extension else audit_cases)(doc,cases);compiled=_json(package/'compiled-content.json')
    for key,value in content.items():_equal(compiled.get(key),value,'compiled/'+key)
    _equal(compiled.get('source_sha256'),sha(package/'module.mapnote.json'),'compiled/source_sha256')
    _equal(compiled.get('ports'),doc.get('generationContract',{}).get('ports',[]),'compiled/ports')
    _equal(compiled.get('stable_id'),manifest.get('stable_id'),'compiled/stable_id')
    _equal(compiled.get('entry_port'),cases[0]['entry_port'],'compiled/entry_port');_equal(compiled.get('exit_port'),cases[0]['exit_port'],'compiled/exit_port')
    _equal(compiled.get('world_bounds'),cases[0].get('world_bounds',[-5000,-5000,15000,15000]),'compiled/world_bounds')
    result=dict(passed=True,compiled=True,loaded=False,stable_id=manifest['stable_id'],runtime_dependencies=len(dependencies),canonical_cases=len(cases),manifest_sha256=sha(package/'godot-package.json'))
    index_path=package/'load-evidence/index.json'
    if not require_loaded:return result
    if not index_path.is_file():_fail('missing_real_load_evidence')
    index=_json(index_path)
    if index.get('schema')!='pcg/godot-package-executions/v1' or index.get('manifest_sha256')!=result['manifest_sha256']:_fail('load_evidence_manifest_mismatch')
    rows=index.get('executions',[])
    if [v.get('case_index')for v in rows]!=list(range(len(cases))):_fail('incomplete_load_coverage')
    observed=[]
    for row,case in zip(rows,cases):
        paths={}
        for name,artifact in row.get('artifacts',{}).items():
            paths[name]=_internal(package,artifact['path'])
            if sha(paths[name])!=artifact['sha256']:_fail('changed_load_evidence',case_id=case['id'],artifact=name)
        if not {'input','command','stdout','receipt','execution'}<=set(paths):_fail('incomplete_execution_evidence',case_id=case['id'])
        inp=_json(paths['input']);command=_json(paths['command']);execution=_json(paths['execution']);receipt=_json(paths['receipt'])
        expected_binding=dict(manifest_sha256=result['manifest_sha256'],module_sha256=sha(package/'module.mapnote.json'),cases_sha256=sha(package/'cases.json'),compiled_sha256=sha(package/'compiled-content.json'),scene_sha256=sha(package/'demo.tscn'))
        for key,value in expected_binding.items():
            if receipt.get('binding',{}).get(key)!=value or inp.get(key)!=value:_fail('execution_input_binding_mismatch',case_id=case['id'],field=key)
        engine=(ROOT/command.get('engine_repo_path','')).resolve()
        if not engine.is_relative_to(ROOT)or not engine.is_file()or sha(engine)!=command.get('engine_sha256') or receipt.get('binding',{}).get('engine_sha256')!=command.get('engine_sha256'):_fail('execution_engine_binding_mismatch',case_id=case['id'])
        argv=command.get('argv',[])
        if command.get('project_repo_path')!=PROJECT.relative_to(ROOT).as_posix()or '--path'not in argv or argv[argv.index('--path')+1]!=str(PROJECT):_fail('execution_project_binding_mismatch',case_id=case['id'])
        if execution.get('returncode')!=0 or execution.get('timed_out') or execution.get('command_sha256')!=sha(paths['command']):_fail('load_execution_failed',case_id=case['id'])
        if '--verify-package'not in argv or '--case'not in argv or argv[argv.index('--case')+1]!=str(row['case_index']) or '--fixed-fps'not in argv or argv[argv.index('--fixed-fps')+1]!='60':_fail('wrong_load_command',case_id=case['id'])
        if receipt.get('mode')!='canonical_replay' or receipt.get('case_id')!=case['id'] or inp.get('case_id')!=case['id']:_fail('wrong_executed_case',case_id=case['id'])
        frames=receipt.get('frames',[]);expected_count=len(case['recorded_frames'])
        if len(frames)!=expected_count or receipt.get('actual_frames')!=expected_count or [v.get('frame')for v in frames]!=list(range(expected_count)):_fail('wrong_execution_frame_count',case_id=case['id'])
        for actual,frozen in zip(frames,case['recorded_frames']):
            if actual.get('requested')!=frozen.get('requested',[])or actual.get('axis')!=frozen.get('axis'):_fail('replay_input_mismatch',case_id=case['id'],frame=actual['frame'])
            if actual.get('hp')!=5:_fail('load_player_harm',case_id=case['id'])
        goal=case['goal']
        def stable(frame):return goal[0]<=frame['x']<goal[0]+goal[2] and goal[1]<=frame['y']<goal[1]+goal[3] and frame.get('grounded') and sum(v*v for v in frame.get('velocity',[1e9,1e9]))<=1
        if len(frames)<6 or not all(stable(f)for f in frames[-6:])or receipt.get('stable_frames',0)<6 or receipt.get('hp')!=5 or receipt.get('damage')or receipt.get('returns'):_fail('load_terminal_not_safe_stable',case_id=case['id'])
        claimed={e['id']for e in receipt.get('package',{}).get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
        if not set(case.get('required_rewards',[]))<=claimed or receipt.get('coins',0)<case.get('expected_reward',0):_fail('load_reward_missing',case_id=case['id'])
        log=paths['stdout'].read_text();events=[json.loads(line.split('GODOT_PACKAGE_LOAD ',1)[1])for line in log.splitlines()if line.startswith('GODOT_PACKAGE_LOAD ')]
        if len(events)!=1 or events[0].get('case_id')!=case['id']or events[0].get('actual_frames')!=expected_count or events[0].get('hp')!=5 or not events[0].get('passed') or 'SCRIPT ERROR:'in log or '\nERROR:'in log:_fail('invalid_native_load_log',case_id=case['id'])
        observed.append(dict(case_id=case['id'],actual_frames=expected_count,hp=5,coins=receipt['coins'],stable_frames=receipt['stable_frames']))
    result.update(loaded=True,observed=observed,evidence=dict(path='load-evidence/index.json',sha256=sha(index_path)),foundation_route_certification=False)
    return result

def run_package_validation(output_dir, *, engine_path=None, project_root=None):
    """Execute every frozen case once; retain failures, no retries or noise search."""
    package=Path(output_dir).resolve();verify_package(package,require_loaded=False)
    engine=Path(engine_path or ROOT/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64').resolve();project=Path(project_root or PROJECT).resolve()
    if project!=PROJECT:_fail('unsupported_runtime_project',expected=str(PROJECT),actual=str(project))
    if not engine.is_relative_to(ROOT)or not engine.is_file():_fail('invalid_engine_path',path=str(engine))
    evidence=package/'load-evidence'
    if evidence.exists():_fail('load_evidence_already_exists',path=str(evidence))
    evidence.mkdir();raw=_json(package/'cases.json');cases=raw['cases']if isinstance(raw,dict)else raw
    index=dict(schema='pcg/godot-package-executions/v1',manifest_sha256=sha(package/'godot-package.json'),executions=[])
    binding=dict(manifest_sha256=index['manifest_sha256'],module_sha256=sha(package/'module.mapnote.json'),cases_sha256=sha(package/'cases.json'),compiled_sha256=sha(package/'compiled-content.json'),scene_sha256=sha(package/'demo.tscn'))
    for i,case in enumerate(cases):
        folder=evidence/f'case-{i}';folder.mkdir();receipt=folder/'receipt.json'
        argv=[str(engine),'--headless','--fixed-fps','60','--path',str(project),str(package/'demo.tscn'),'--','--verify-package','--case',str(i),'--receipt',str(receipt)]
        _write(folder/'input.json',dict(schema='pcg/package-load-input/v1',case_id=case['id'],case_index=i,recorded_frames=len(case['recorded_frames']),**binding))
        _write(folder/'command.json',dict(schema='pcg/package-native-command/v1',argv=argv,engine_repo_path=engine.relative_to(ROOT).as_posix(),engine_sha256=sha(engine),project_repo_path=project.relative_to(ROOT).as_posix()))
        started=time.monotonic();timed_out=False
        with (folder/'stdout.log').open('w')as log:
            try:process=subprocess.run(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=90);returncode=process.returncode
            except subprocess.TimeoutExpired:timed_out=True;returncode=-1
        _write(folder/'execution.json',dict(schema='pcg/package-native-execution/v1',command_sha256=sha(folder/'command.json'),returncode=returncode,timed_out=timed_out,elapsed_seconds=time.monotonic()-started))
        files=dict(input='input.json',command='command.json',stdout='stdout.log',receipt='receipt.json',execution='execution.json')
        row=dict(case_index=i,case_id=case['id'],artifacts={name:dict(path=(folder/file).relative_to(package).as_posix(),sha256=sha(folder/file))for name,file in files.items()if (folder/file).is_file()});index['executions'].append(row);_write(evidence/'index.json',index)
    return verify_package(package,require_loaded=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--module',required=True);p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--stable-id');p.add_argument('--project');a=p.parse_args()
    try:
        result=compile_package(a.module,a.cases,a.out,stable_id=a.stable_id,project_root=a.project);print(json.dumps(dict(ok=True,stable_id=result['stable_id'],out=a.out,geometry_audit=result['geometryAudit']['passed']),ensure_ascii=False))
    except PackageError as e:
        print(json.dumps(dict(ok=False,code=e.code,details=e.details),ensure_ascii=False));raise SystemExit(2)
