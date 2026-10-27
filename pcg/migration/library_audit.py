"""Full finite library audit; reads sources, never edits content or archives.

python3 -m pcg.migration.library_audit
A matching fingerprint is a review candidate, never an equivalence certificate.
"""
from __future__ import annotations
import argparse, collections, copy, datetime, gzip, hashlib, json, re
from pathlib import Path
from . import core, game_adapter
from pcg.prototype.factory.core.quality import digest

POINTS={'position','spawn','entry_port','exit_port','stagingPosition','bell','return_access','aim_target','start','finish','origin','takeoff','landing','reward_position','goal_position','targetPosition'}
RECTS={'rect','bounds','world_bounds','goal','gate','paired_gate','sequence_gate','region','sensorRect','inactiveGate'}
RECT_ARRAYS={'platforms','hazards','danger_bounds','dangers'}
POINT_ARRAYS={'anchors','path','points'}
VECTORS={'direction','normal','directions','travel','size','offset','sequence_offset','crossing_offset','localReceiverOffset','translation','scale','velocity','normal_velocity','real_velocity'}
DISPLAY={'label','note','title','description','prompt','name','color','link_color'}
CASE_FIELDS=('capabilities','platforms','one_way_platform_indices','one_way_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','reward_sites','shop_sites','original_pickups','original_tuning_profile','spawn','entry_port','exit_port','goal','world_bounds','control_plan','actions','axes','route_spec','required_rewards','expected_reward','required_original_pickups','challenge_requirements','max_frames','settle_frames','warmup_frames','schedule_mode','relay_support_id','initial_state','resource_state','decoder_pending_behavior','source_components')
RAW_IGNORE={'id','module_id','seed','hash','basis','engine','scope','title','name','identity','fingerprint','template_id','variant','phase_index'}
RAW_CACHE={}


def _number(v):
    if isinstance(v,float):
        v=round(v,8)
        if v.is_integer():return int(v)
    return v


def normalize(value,origin=(0,0),key='',ids=None,skip_display=True):
    """Translate typed world points/rectangles, never directions or lengths."""
    ids=ids or {}
    if isinstance(value,str):
        if value in ids:return ids[value]
        return re.sub(r'generated-[a-f0-9]{64}', 'module',value)
    if isinstance(value,dict):
        result={k:normalize(v,origin,k,ids,skip_display)for k,v in value.items()if not(skip_display and k in DISPLAY)}
        if key not in VECTORS and all(isinstance(value.get(k),(int,float))and not isinstance(value[k],bool)for k in ('x','y')):
            result['x']=_number(value['x']-origin[0]);result['y']=_number(value['y']-origin[1])
        if value.get('kind')=='actor_x' and isinstance(value.get('value'),(int,float)):result['value']=_number(value['value']-origin[0])
        if isinstance(value.get('face'),int)and value['face']in range(4):result['face']=['top','left','right','bottom'][value['face']]
        return result
    if isinstance(value,list):
        numeric=all(isinstance(v,(int,float))and not isinstance(v,bool)for v in value)
        if key in RECTS and len(value)==4 and numeric:return [_number(value[0]-origin[0]),_number(value[1]-origin[1]),*map(_number,value[2:])]
        if key in POINTS and len(value)==2 and numeric:return [_number(value[0]-origin[0]),_number(value[1]-origin[1])]
        if key in RECT_ARRAYS:return [normalize(v,origin,'rect',ids,skip_display)for v in value]
        if key in POINT_ARRAYS:return [normalize(v,origin,'position',ids,skip_display)for v in value]
        return [normalize(v,origin,key,ids,skip_display)for v in value]
    if key=='target_x'and isinstance(value,(int,float)):return _number(value-origin[0])
    if key=='target_y'and isinstance(value,(int,float)):return _number(value-origin[1])
    return _number(value)


def _ids(doc,cases):
    mapping={doc['id']:'MODULE'}
    for i,obj in enumerate(doc['objects']):mapping[obj['id']]='O'+str(i)
    for family,prefix,field in [('latches','L','id'),('enemies','E','id'),('moving_platforms','M','platform_id'),('saws','S','source_id'),('thorns','T','surface_id'),('reward_sites','W','id'),('original_pickups','N','id')]:
        for i,spec in enumerate(cases[0].get(family,[])):
            if spec.get(field):mapping.setdefault(spec[field],prefix+str(i))
    ports=sorted(doc['generationContract']['ports'],key=lambda p:(p['position'],p['normal'],p.get('surface','UNKNOWN'),p.get('permission','UNKNOWN')))
    for i,p in enumerate(ports):mapping[p['id']]='P'+str(i)
    for i,r in enumerate(doc['generationContract']['routes']):mapping[r['id']]='R'+str(i)
    return mapping,ports


def _profile(source,cases):
    value=cases[0].get('original_tuning_profile')
    if value:return value
    raw=source.get('data',{})if source else{}
    profile_id=raw.get('capability_profile')
    if not profile_id:return None
    config=core.read(core.REPO/'pcg/prototype/godot/config/foundry_capabilities.json')
    profile=next((p for p in config['profiles']if p['id']==profile_id),None)
    defaults=core.read(core.REPO/'pcg/prototype/godot/config/player_tuning.json')
    if profile:
        return dict(id=profile_id,overrides=profile['overrides'],abilities=profile['abilities'],effectiveTuning={k:profile['overrides'].get(k,defaults[k])for k in ('max_jumps','max_air_shots')})
    return dict(id=profile_id,status='UNKNOWN_ORIGINAL_PROFILE')


def semantic_payload(doc,cases,source=None):
    gc=doc['generationContract'];b=gc['space']['bounds'];origin=(b['x'],b['y'])
    ids,ports=_ids(doc,cases)
    port_fields=('id','position','normal','face','surface','permission','connection','support','stagingPosition','preconditions','motion','cornerRelocations')
    normalized_ports=[normalize({k:p.get(k,'UNKNOWN')for k in port_fields},origin,ids=ids)for p in ports]
    known={(r['from'],r['to']):r for r in gc['relations']}
    matrix=[]
    for a in ports:
        for z in ports:
            relation=known.get((a['id'],z['id']),dict(from_=a['id'],to=z['id'],status='UNKNOWN',routeIds=[],conditions='UNKNOWN'))
            matrix.append(normalize(dict(fromPort=a['id'],toPort=z['id'],status=relation['status'],routeIds=relation.get('routeIds',[]),conditions=relation.get('conditions','UNKNOWN')),origin,ids=ids))
    routes=[]
    for r in gc['routes']:
        routes.append(normalize({k:v for k,v in r.items()if k not in ('validationIds','availability','pathObjectId','durationSeconds')},origin,ids=ids))
    programs=[normalize({k:c[k]for k in CASE_FIELDS if k in c},origin,ids=ids)for c in cases]
    original_behavior=None
    if source:
        raw={k:v for k,v in source['data'].items()if k not in RAW_IGNORE}
        # The original source dictionary keeps its own coordinate system; its
        # positions are normalized independently, not mistaken for edited Cells.
        source_rects=source['data'].get('platforms',[])
        source_rects=[v.get('rect')if isinstance(v,dict)else v for v in source_rects]
        source_rects=[v for v in source_rects if isinstance(v,list)and len(v)==4]
        raw_origin=(min(v[0]for v in source_rects),min(v[1]for v in source_rects))if source_rects else(0,0)
        original_behavior=normalize(raw,raw_origin,ids=ids)
    source_info=gc.get('generation',{}).get('source',{})
    return dict(kind=gc['kind'],rectangle=normalize(b,origin,'bounds'),actorBody=gc['space']['actorBody'],
        objects=normalize([o for o in doc['objects']if o['type']not in ('route','note','entry','exit','anchor')],origin,ids=ids),
        ports=normalized_ports,relations=matrix,routes=routes,programs=programs,portConfigurations=normalize(gc.get('portConfigurations',[]),origin,ids=ids),closures=normalize([{k:v for k,v in row.items()if k!='validationIds'}for row in gc.get('closures',[])],origin,ids=ids),mirror=normalize({k:v for k,v in gc.get('mirror',{}).items()if k!='validationIds'},origin,ids=ids),
        capabilityRequirements=doc.get('capabilityRequirements'),nativeProfile=_profile(source,cases),originalSourceBehavior=original_behavior,
        physicsSource=dict(commit=source_info.get('physicsSourceCommit','UNKNOWN'),manifest=source_info.get('sourceManifestSha256','UNKNOWN')))


def geometry_key(cases):
    c=cases[0];platforms=c['platforms'];origin=(min(p[0]for p in platforms),min(p[1]for p in platforms))
    return digest(normalize({k:c.get(k,[])for k in ('platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','moving_platforms','saws','hooks')},origin))


def relation_key(cases,source=None):
    c=cases[0];latches=c.get('latches',[])
    switches=sorted({next((k for k in ('paired_gate','carrier_dock','occupancy','attack_relay','sequence_offset','carrier_mount','ferry_id')if k in l),'ordinary_gate')for l in latches})
    ops=collections.Counter(command['op']for command in c.get('control_plan',[])if command['op']not in ('wait','axis','settle'))
    return digest(dict(capabilities=sorted(c.get('capabilities',[])),nativeProfile=_profile(source,cases),switchRelations=switches,enemy=bool(c.get('enemies')),hooks=sorted({h.get('kind')for h in c.get('hooks',[])}),hostedHazards=bool(c.get('thorns')),movingPlatforms=bool(c.get('moving_platforms')),saws=bool(c.get('saws')),actions=ops,routeCount=len(cases)))


def _raw_observation(path,index,expected_id,expected_sha=None):
    key=(str(path),index,expected_id,expected_sha)
    if key in RAW_CACHE:return RAW_CACHE[key]
    packed=path.read_bytes();unpacked=gzip.decompress(packed)
    packed_sha=hashlib.sha256(packed).hexdigest();raw_sha=hashlib.sha256(unpacked).hexdigest()
    if expected_sha and expected_sha not in (packed_sha,raw_sha):raise ValueError('original_raw_sha_changed')
    raw=json.loads(unpacked)['results'][index]
    if raw['id']!=expected_id:raise ValueError('original_raw_case_identity_mismatch')
    counts=collections.Counter(f.get('support_id')for f in raw.get('frames',[])if f.get('grounded'))
    result=dict(supportFrames=dict(counts),frameCount=len(raw.get('frames',[])),evidence=dict(path=core.relative(path),sha256=packed_sha,rawOutputSha256=raw_sha,index=index),source='original_raw_output')
    RAW_CACHE[key]=result
    return result


def _observations(folder,doc,cases,current):
    counts=collections.Counter();evidence=[];limitations=[]
    if current:
        index=folder/'load-evidence/index.json'
        if not index.exists():return counts,[],['current_native_load_evidence_missing']
        entries=core.read(index).get('executions',[])
        for execution in entries:
            row=execution.get('artifacts',{}).get('receipt')
            if not row:limitations.append('current_receipt_reference_missing');continue
            path=folder/row['path']
            if not path.is_file()or core.sha(path)!=row['sha256']:limitations.append('current_receipt_bytes_changed');continue
            receipt=core.read(path)
            counts.update(f.get('support_id')for f in receipt.get('frames',[])if f.get('grounded'))
            evidence.append(dict(path=core.relative(path),sha256=row['sha256'],source='current_native_execution'))
    else:
        run=doc['generationContract'].get('generation',{}).get('source',{}).get('run')
        for case in cases:
            e=case.get('factory_evidence',{})
            if not run or not e.get('output'):limitations.append('original_canonical_raw_reference_missing:'+case['id']);continue
            path=core.resolve_artifact(run+'/'+e['output'])
            try:
                observed=_raw_observation(path,e['index'],case['id'],e.get('raw_output_sha256'))
                counts.update(observed['supportFrames']);evidence.append(observed['evidence'])
            except (OSError,ValueError,KeyError,IndexError)as error:limitations.append(str(error)+':'+case['id'])
    return counts,evidence,limitations


def platform_audit(folder,doc,cases,source=None,current=False):
    platforms=cases[0]['platforms'];one_way=set(cases[0].get('one_way_platform_indices',cases[0].get('one_way_indices',[])));walls=set(cases[0].get('wall_platform_indices',[]))
    observed,evidence,limitations=_observations(folder,doc,cases,current)
    objects={o['id']:o for o in doc['objects']};rows=[]
    physical_width=max(p[0]+p[2]for p in platforms)-min(p[0]for p in platforms)
    for i,rect in enumerate(platforms):
        x,y,w,h=rect;roles=set();declared=set()
        for case in cases:
            for port in case.get('ports',[]):
                if port.get('support_index')==i:roles.add('port_support:'+port['id'])
            for thorn in case.get('thorns',[]):
                if thorn.get('platform_index')==i:roles.add('hazard_host:'+thorn['surface_id'])
            for key in ('spawn','entry_port','exit_port'):
                point=case.get(key)
                if point and x-1e-5<=point[0]<=x+w+1e-5 and abs(point[1]+18-y)<2:roles.add('runtime_dock:'+key)
            for site in case.get('reward_sites',[]):
                point=site['position']
                if x<=point[0]<=x+w and abs(point[1]+18-y)<3:roles.add('chest_claim_support:'+site['id'])
            for actor in case.get('enemies',[]):
                obj=next((o for o in doc['objects']if o['type']=='enemy'and o.get('sourceId')==actor['id']),None)
                height=obj['h']/2 if obj else 16
                if x<=actor['position'][0]<=x+w and abs(actor['position'][1]+height-y)<3:roles.add('enemy_spawn_support:'+actor['id'])
        for port in doc['generationContract']['ports']:
            support=port.get('support');host=objects.get(support.get('objectId'))if isinstance(support,dict)else None
            if host and all(abs(rect[n]-host[k])<1e-5 for n,k in enumerate(('x','y','w','h'))):roles.add('contract_port_support:'+port['id'])
        for route in doc['generationContract']['routes']:
            path=objects.get(route.get('pathObjectId'),{})
            for point in path.get('points',[]):
                if x<=point['x']<=x+w and abs(point['y']+18-y)<36:
                    declared.add('declared_route_support:'+route['id'])
                    if route.get('role')in ('return','recovery','shortcut'):declared.add('conditional_route_support:'+route['role'])
        frames=observed.get('Platform'+str(i),0)
        if frames:roles.add('observed_native_support'if current else'observed_original_support')
        if i in one_way:roles.add('one_way_collision')
        if i in walls:roles.add('wall_climb_surface')
        if len(platforms)>1 and y>=max(p[1]for j,p in enumerate(platforms)if j!=i)-1:
            if w>=physical_width*.5:declared.add('potential_fall_recovery_surface_unverified')
        contained=[];coincident=[];compatible=[]
        for j,(a,b,c,d)in enumerate(platforms):
            if i==j:continue
            if a<=x and b<=y and a+c>=x+w and b+d>=y+h:
                contained.append(j)
                if rect==platforms[j]:coincident.append(j)
                if (i in one_way)==(j in one_way)and(i in walls)==(j in walls):compatible.append(j)
        rows.append(dict(index=i,rect=rect,oneWay=i in one_way,wallClimbable=i in walls,roles=sorted(roles),declaredOrPotentialRoles=sorted(declared),observedSupportFrames=frames,
            containedBy=contained,coincidentWith=coincident,sameCollisionFlagsContainedBy=compatible,wideSlabReview=w>=physical_width*.8 and h>=128,
            decision='retain',review='overlap_requires_real_collision_and_route_equivalence_proof'if contained else'nonvisited_is_not_redundancy_proof'if not roles else'identified_role'))
    return dict(platforms=rows,evidence=evidence,limitations=sorted(set(limitations)),automaticRemovals=0)


def _read_inputs(folder):
    doc=core.read(folder/'module.mapnote.json');case_file=folder/('cases.json'if(folder/'cases.json').exists()else'case.json')
    raw=core.read(case_file);cases=raw['cases']if isinstance(raw,dict)and'cases'in raw else raw if isinstance(raw,list)else[raw]
    return doc,cases,case_file


def _row(key,folder,layer,source=None):
    doc,cases,case_file=_read_inputs(folder);payload=semantic_payload(doc,cases,source)
    record=core.read(folder/'record.json')if(folder/'record.json').exists()else{}
    gc=doc['generationContract'];ports=gc['ports']
    actual_profile=_profile(source,cases)
    return dict(key=key,layer=layer,sourceKind=source.get('kind')if source else'repository_generated',sourcePath=core.relative(folder),title=doc['title'],contentVersion=gc['contentVersion'],
        documentSha256=core.sha(folder/'module.mapnote.json'),casesSha256=core.sha(case_file),sourceMetadataSha256=core.sha(folder/'source.json')if source and (folder/'source.json').exists()else None,sourceMetadataSemanticDigest=digest(source)if source else None,
        stableTemplateId=record.get('specification',{}).get('id')or record.get('id')or doc['id'],kind=gc['kind'],portCount=len(ports),directedMatrixSlots=len(ports)**2,
        unknownDirectedRelations=sum(r['status']=='UNKNOWN'for r in payload['relations']),unknownPortPermissions=sum(p.get('permission')in(None,'UNKNOWN')for p in ports),nativeProfile=actual_profile,
        fullSemanticFingerprint=digest(payload),geometryClueFingerprint=geometry_key(cases),relationshipClueFingerprint=relation_key(cases,source),
        familyLabel=cases[0].get('family','UNKNOWN'),platformAudit=platform_audit(folder,doc,cases,source,current=layer=='current'),
        certification='existing_technical_metadata_not_revalidated_by_this_audit'if layer=='current'else'historical_or_unverified_source',decision='retain',status='inspected')


def _groups(rows,field,scope):
    groups=collections.defaultdict(list)
    for r in rows:
        if r.get('status')=='inspected':groups[r[field]].append(r['key'])
    return [dict(fingerprint=k,members=v,status=scope,automaticMerge=False)for k,v in sorted(groups.items())if len(v)>1]


def run(output=None):
    generated=core.read(core.STATE/'inventory-generated-v1.json')['versions'];original_game=game_adapter.source_entries()
    current_paths=sorted(core.ACTIVE.glob('*/module.mapnote.json'));rows=[];sources=[]
    for entry in generated:
        version=entry['contentVersion'].split(':',1)[1];key='generated:'+version
        path=core.resolve_artifact('pcg/map_directed/library/candidates/'+version+'/module.mapnote.json')
        if not path.exists():
            matches=list(core.RECYCLE.glob('*/'+version+'/module.mapnote.json'))
            if len(matches)==1:path=matches[0]
        sources.append((key,path.parent,'source_generated',None))
    for source in original_game:
        name=core.safe_id('game-'+re.sub(r'[^a-z0-9_-]+','-',source['id'].lower()).replace('__','-').replace('_','-'))
        path=core.resolve_artifact('pcg/migration/game-sources/'+name+'/module.mapnote.json')
        sources.append(('game:'+source['id'],path.parent,'source_game',source))
    for key,folder,layer,source in sources:
        try:rows.append(_row(key,folder,layer,source))
        except Exception as error:rows.append(dict(key=key,layer=layer,status='audit_error',error=str(error),decision='retain'))
    for path in current_paths:
        source=None
        try:
            meta=core.read(path.parent/'migration.json')
            if meta.get('sourceType')=='original_game':source=core.read(core.resolve_artifact(meta['sourcePath']+'/source.json'))
            rows.append(_row('current:'+path.parent.name,path.parent,'current',source))
        except Exception as error:rows.append(dict(key='current:'+path.parent.name,layer='current',status='audit_error',error=str(error),decision='retain'))
    source_rows=[r for r in rows if r['layer']!='current'];current=[r for r in rows if r['layer']=='current'];good=[r for r in rows if r['status']=='inspected']
    kinds=collections.Counter(s['kind']for s in original_game);foundry=[s for s in original_game if s['kind']=='foundry'];forest=[s for s in original_game if s['kind']=='forest']
    exact=_groups(source_rows,'fullSemanticFingerprint','semantic_match_pending_current_certificate_equivalence_proof')
    exact_current=_groups(current,'fullSemanticFingerprint','current_semantic_match_pending_deep_certificate_equivalence_proof')
    shapes=_groups(source_rows,'geometryClueFingerprint','geometry_clue_only_compare_interfaces_profiles_mechanisms_and_routes')
    relationships=_groups(source_rows,'relationshipClueFingerprint','relationship_retrieval_clue_not_independent_family_count')
    profiles=collections.Counter((r.get('nativeProfile')or{}).get('id','default_or_not_applicable')for r in source_rows if r['status']=='inspected')
    profile_splits=[]
    by_key={r['key']:r for r in good}
    for group in shapes:
        variants={json.dumps(by_key[k]['nativeProfile'],sort_keys=True)for k in group['members']}
        if len(variants)>1:profile_splits.append(dict(members=group['members'],reason='Same geometric shell has different original actor resource/capability profiles; preserve distinct requirements.',profiles=[json.loads(v)for v in sorted(variants)]))
    aliases=[];alias_path=core.ACTIVE/'aliases.json'
    if alias_path.exists():
        from . import deduplicate
        for key,entry in core.read(alias_path).get('aliases',{}).items():
            try:
                resolved=deduplicate.resolve(key)
                aliases.append(dict(id=key,primaryId=resolved['primaryId'],portMapping=entry['portMapping'],proof=entry['proof'],status='actual_exact_duplicate_merged_and_reloaded'))
            except Exception as error:aliases.append(dict(id=key,status='alias_verification_failed',error=str(error)))
    for group in exact:
        declared={by_key[k]['stableTemplateId']for k in group['members']}
        resolved=[a for a in aliases if a.get('status')=='actual_exact_duplicate_merged_and_reloaded'and a['id']in declared and a['primaryId']in declared]
        if resolved:group.update(status='source_pair_resolved_in_current_archive_by_verified_alias',currentAliasProofs=[a['proof']for a in resolved])
    errors=[r for r in rows if r['status']!='inspected']
    platform_rows=[p for r in good for p in r['platformAudit']['platforms']]
    report=dict(schema='pcg/whole-library-audit/v2',createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='READ_ONLY_SOURCE_AND_CURRENT_LIBRARY',
        sourceInventory=dict(expected=311,generatedVersions=len(generated),originalGameReferences=len(original_game),inspected=sum(r['status']=='inspected'for r in source_rows),errors=sum(r['status']!='inspected'for r in source_rows),complete=len(source_rows)==311 and all(r['status']=='inspected'for r in source_rows)),
        counts=dict(sourceRows=len(source_rows),currentModulesSnapshot=len(current),currentInspected=sum(r['status']=='inspected'for r in current),generatedStableTemplateIds=len({r['stableTemplateId']for r in source_rows if r['layer']=='source_generated'and r['status']=='inspected'}),
            originalGameKinds=dict(kinds),authoredResourceDefinitions=kinds['resource'],forestRegisteredOutputReferences=kinds['forest'],forestGeneratorSourceFiles=len({s['sourcePath']for s in forest}),forestGeneratorEntryPoints=len({(s['sourcePath'],s['method'])for s in forest}),
            foundryBasePhraseTemplates=len({s['data']['template_id']for s in foundry if s['data'].get('template_id')}),foundryPhraseSamples=sum(bool(s['data'].get('template_id'))for s in foundry),foundryItinerarySamples=sum(not s['data'].get('template_id')for s in foundry),originalActorProfiles=dict(profiles),
            sourceSemanticMatchGroups=len(exact),verifiedPersistentAliases=sum(a['status']=='actual_exact_duplicate_merged_and_reloaded'for a in aliases),currentSemanticMatchGroups=len(exact_current),sourceGeometryClueGroups=len(shapes),profileSeparatedGeometryGroups=len(profile_splits),
            sourcePlatforms=sum(len(r['platformAudit']['platforms'])for r in source_rows if r['status']=='inspected'),sourceRowsWithVerifiedOriginalRaw=sum(bool(r['platformAudit']['evidence'])for r in source_rows if r['status']=='inspected'),currentPlatforms=sum(len(r['platformAudit']['platforms'])for r in current if r['status']=='inspected'),
            containedColliderFlags=sum(bool(p['containedBy'])for p in platform_rows),coincidentColliderFlags=sum(bool(p['coincidentWith'])for p in platform_rows),automaticMerges=0,automaticPlatformRemovals=0,newGodotCases=0),
        normalization=dict(translation='Typed world point/rectangle fields only; dimensions/directions/travel/relative offsets remain unchanged.',
            exact='Actual geometry, complete N×N interface matrix with UNKNOWN retained, permissions, routes, resource/ability requirements, real mechanism parameters and control program. Identity/title/seed/decoration never create families.',
            limitations=['Conservative fingerprints are not complete graph-isomorphism or gameplay equivalence proofs.','Source/controller differences and UNKNOWN permissions are retained; matching incomplete metadata never grants a certificate.','A nominally unvisited platform can support recovery, projectiles, enemies, ports or alternative strategies.','Matching geometry under distinct Foundry profiles is explicitly separated.','Different frozen control programs may be alternative strategies of one geometry; they never establish a new gameplay family by themselves.']),
        persistentAliases=aliases,exactSemanticReviewGroups=exact,currentExactSemanticReviewGroups=exact_current,geometryReviewGroups=shapes,profileSeparatedGeometryGroups=profile_splits,relationshipRetrievalGroups=relationships,
        mergePolicy='No automatic archive. A complete equivalence record through the existing migration equivalence gate and current actual certificates is required before merging.',
        rows=rows,errors=errors,sourceCompiler=dict(path=core.relative(Path(__file__)),sha256=core.sha(__file__)))
    output=Path(output or core.STATE/'whole-library-audit-v2.json');core.write(output,report)
    lines=['# 全库重复与平台审计','',f"来源覆盖：{report['sourceInventory']['inspected']}/311；当前归档快照：{len(current)} 个。",'',
        '134 个本仓库历史版本；原游戏177个登记引用包含72个资源定义、51个森林输出、36个 Foundry 短语样品及18个组合行程。样品、版本和生成器入口不计作独立玩法家族。','',
        f"完整语义匹配待证组：来源 {len(exact)}，当前库 {len(exact_current)}。几何相似组 {len(shapes)}，其中 {len(profile_splits)} 组明确包含不同能力/弹药档案。",'',
        f"来源平台 {report['counts']['sourcePlatforms']}；当前版本平台 {report['counts']['currentPlatforms']}。包含标记 {report['counts']['containedColliderFlags']}、重合标记 {report['counts']['coincidentColliderFlags']}（两层分别记录，不相加作为模板数量）。",'',
        f"已从持久化别名重新验证的实际归并：{report['counts']['verifiedPersistentAliases']} 个。审计程序本身不执行归并、删除平台或新增物理实验；其他匹配项仍待等价证明。未踩到的平台不视作冗余。",'',
        '逐项依据、完整矩阵与能力条件的指纹、平台支撑/危险宿主/端口/奖励/条件恢复角色及原始证据引用见同名 JSON。']
    if errors:lines+=['','审计错误：']+[f"- {r['key']}: {r['error']}"for r in errors]
    output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    return dict(sourceInventory=report['sourceInventory'],counts=report['counts'],output=core.relative(output))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out');args=parser.parse_args();print(json.dumps(run(args.out),ensure_ascii=False))
