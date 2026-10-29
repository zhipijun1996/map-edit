"""Migration experiments on the existing Godot Harness and quality policy.

Interior replay, local seam traversal, and continuous route exit are different
claims. An exterior witness has an explicitly declared neighboring test floor;
that floor is never copied into the Module or added at runtime by a Map.
"""
import copy
import gzip
import importlib
import json
import os
import types
from pathlib import Path

from . import core, causal_observer, causal_observer_v2, causal_observer_v3, pool_protocols, holdout_guard, region_outcomes
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.factory.core.quality import digest, module_hash
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

PROTOCOL = core.STATE/'protocol.json'
FULL_PROTOCOL = core.STATE/'protocol-full-v2.json'


def author_for(case):
    """Resolve the original causal checker, including pre-registration recipes.

    Older library rows predate registration_source. Their persisted source path
    or stable rule namespace selects the existing checker; no generic weakened
    purpose test is substituted for an unavailable author.
    """
    rule = case.get('generation_rule', {})
    path = rule.get('registration_source') or rule.get('source_path') or case.get('rule_source_path')
    rid, family = rule.get('id', ''), case.get('family', '')
    if not path:
        exact = {
            'gate-brake-return': 'pcg/prototype/workshop/macro.py',
            'bell_lift': 'pcg/prototype/plains/evaluation.py',
            'one-shot-two-routes': 'pcg/prototype/workshop/evaluate.py',
            'sightline-backtrack': 'pcg/prototype/creative_batches/resource_routes/recipes-v7.py',
            'trapdoor-commit': 'pcg/prototype/creative_batches/resource_routes/recipes-v7.py',
            'ordered-target-transaction': 'pcg/prototype/creative_batches/resource_routes/ordered-target-v2.py',
            'low-ray-recoil-return': 'pcg/prototype/creative_batches/plains50_resources/lowray_v2.py',
            'moving-ray-window': 'pcg/prototype/creative_batches/resource_routes/moving-ray-v1.py',
            'carrier-dual-service': 'pcg/prototype/creative_batches/machinery/production_v14.py',
            'evacuate-rejoin': 'pcg/prototype/creative_batches/machinery/production_v9.py',
            'carrier-rendezvous': 'pcg/prototype/creative_batches/machinery/production_v3.py',
            'saw-pursuit': 'pcg/prototype/creative_batches/machinery/production_v3.py',
        }
        if rid.startswith('plains50-ports/'):
            path = 'pcg/prototype/creative_batches/plains50_ports/recipes_v2.py'
        elif rid.startswith('creative/jump-wall/'):
            version = max(2, rule.get('version', 1))
            path = f'pcg/prototype/creative_batches/jump_wall/production-v{version}.py'
        elif rid.startswith('creative/grapple/'):
            path = 'pcg/prototype/creative_batches/grapple/delivery_v1.py'
        elif rid.startswith('plains50-new/'):
            leaf = {'brake-gate-catch':'production_v1', 'prepared-air-sequence':'production_sequence_v1',
                    'adverse-refund-reversal':'production_resources_v1', 'refill-short-gate':'production_resources_v1'}.get(family)
            if leaf: path = 'pcg/prototype/creative_batches/plains50_new_relations/'+leaf+'.py'
        elif family in exact:
            path = exact[family]
        elif rid.startswith('workshop/production/'):
            path = 'pcg/prototype/workshop/production_recipes.py'
        elif rid.startswith('workshop/'):
            path = 'pcg/prototype/workshop/evaluate.py'
    if not path:
        raise ValueError('missing_original_purpose_source:'+rid+'/'+family)
    path = Path(path)
    if path.is_absolute():path = path.relative_to(core.REPO)
    module = importlib.import_module(path.as_posix().removesuffix('.py').replace('/', '.'))
    if not callable(getattr(module, 'purpose', None)):
        # Some immutable adaptation files deliberately reuse their predecessor's
        # checker without exporting it. Resolve that documented predecessor.
        if path.as_posix().endswith('plains50_machinery/recipes_v2.py'):
            return importlib.import_module('pcg.prototype.creative_batches.plains50_machinery.recipes_v1')
        raise ValueError('original_source_has_no_causal_checker:'+str(path))
    return module


def author_sources(authors, runner=None):
    """Freeze imported causal helpers too; physics remains the existing runtime."""
    paths, seen = set(), set()
    def visit(module):
        if id(module) in seen:return
        seen.add(id(module))
        source = getattr(module, '__file__', None)
        if not source or not Path(source).resolve().is_relative_to(core.REPO/'pcg'):return
        paths.add(Path(source).resolve())
        for dependency in getattr(module, 'SOURCE_DEPENDENCIES', []):paths.add(Path(dependency).resolve())
        for value in vars(module).values():
            if isinstance(value, types.ModuleType):visit(value)
            elif callable(value):
                owner = __import__('sys').modules.get(getattr(value, '__module__', ''))
                if owner is not None and owner is not module:visit(owner)
    for author in authors:visit(author)
    def gd(path):
        import re
        path = Path(path).resolve()
        if path in paths or not path.is_file():return
        paths.add(path)
        for ref in re.findall(r'(?:extends\s+|preload\()"([^"\n]+)"', path.read_text()):
            target = core.REPO/'pcg/prototype/godot'/ref[6:] if ref.startswith('res://') else Path(ref) if ref.startswith('/') else path.parent/ref
            if target.suffix == '.gd':gd(target)
    if runner:gd(runner)
    return sorted(paths)


def runner_for(case, author):
    from pcg.prototype.dynamic.simulator import PROJECT
    for name in ('RUNNER_SCRIPT', 'RUNNER', 'ADAPTER'):
        value = getattr(author, name, None)
        if isinstance(value, (str, Path)) and str(value).endswith('.gd') and Path(value).is_file():return Path(value)
    callback = getattr(author, 'runner', None)
    if callable(callback):return Path(callback(case.get('production_recipe', case.get('family'))))
    if case.get('capabilities') != ['move','jump','shot_recoil']:
        return core.REPO/'pcg/prototype/creative_batches/grapple/runner_v3.gd'
    if any(l.get('paired_gate') for l in case.get('latches', [])):
        return core.REPO/'pcg/prototype/creative_batches/batch30_cell/runner_v3.gd'
    if case.get('family') == 'carrier-dual-service':
        return core.REPO/'pcg/prototype/creative_batches/machinery/dock_runner_v11.gd'
    if any(l.get('sequence_offset') for l in case.get('latches', [])):
        return core.REPO/'pcg/prototype/creative_batches/resource_routes/runner-v1.gd'
    family = case.get('family')
    if family == 'enemy-sensor-hold':return core.REPO/'pcg/prototype/creative_batches/occupancy/runner_v1.gd'
    if family == 'enemy-attack-relay':return core.REPO/'pcg/prototype/creative_batches/enemy_world/attack_runner_v1.gd'
    if family in ('enemy-clear-sightline','enemy-displace-landing'):return core.REPO/'pcg/prototype/creative_batches/enemy_world/runner_v1.gd'
    if case.get('family') in ('enemy-sensor-hold','enemy-attack-relay','enemy-displace-landing'):
        # Their exact source files generally export RUNNER_SCRIPT. Never guess
        # the ordinary runtime when a special world binding was requested.
        for name in ('RUNNER_PATH', 'RUNNER_V3'):
            value = getattr(author, name, None)
            if value and Path(value).is_file():return Path(value)
    return core.REPO/'pcg/prototype/workshop/runner.gd'


def deduplicate_snapshot(out):
    """Content-address immutable source copies; retain every original path."""
    pool = core.REPO/'.cache/migration/frozen-sources'
    pool.mkdir(parents=True, exist_ok=True)
    for path in (Path(out)/'source_snapshot').rglob('*'):
        if not path.is_file():continue
        target = pool/core.sha(path)
        if not target.exists():
            try:os.link(path, target)
            except FileExistsError:pass
        if path.stat().st_ino != target.stat().st_ino:
            temporary = path.with_name(path.name+'.dedup')
            os.link(target, temporary); temporary.replace(path)


def _engine(folder, name, protocol_path):
    folder = Path(folder).resolve(); core.safe_id(name)
    cases_file = folder/'physics-input-cases.json'
    if not cases_file.exists():cases_file=folder/'cases.json'
    cases = core.read(cases_file)['cases']
    authors = [author_for(case) for case in cases]
    runners = [runner_for(case, author) for case, author in zip(cases, authors)]
    if len(set(map(str, runners))) != 1:raise ValueError('mixed_runtime_sources')
    sources = [Path(__file__), Path(core.__file__), Path(causal_observer.__file__), Path(causal_observer_v2.__file__), Path(causal_observer_v3.__file__), Path(region_outcomes.__file__), Path(__file__).with_name('review_counter_scope_v1.py'), Path(__file__).with_name('review_counter_scope_v2.py'), Path(__file__).with_name('review_counter_scope_v3.py'), Path(__file__).with_name('review_counter_scope_v4.py'), Path(__file__).with_name('review_counter_scope_v5.py'), Path(__file__).with_name('review_counter_scope_v6.py'), Path(__file__).with_name('review_counter_scope_v7.py'), Path(__file__).with_name('review_counter_scope_v8.py'), Path(__file__).with_name('review_counter_scope_v9.py'), Path(__file__).with_name('review_counter_scope_v11.py'), Path(__file__).with_name('review_boundary_observer_v1.py'), Path(__file__).with_name('review_boundary_repair_v5.py'), Path(__file__).with_name('review_boundary_repair_v6.py'), Path(__file__).with_name('review_boundary_repair_v7.py'), Path(__file__).with_name('ideas_boundary_v1.py'), Path(__file__).with_name('revision053_boundary_v1.py'), Path(__file__).with_name('revision058_boundary_v1.py'), Path(__file__).with_name('revision059_boundary_v1.py'), Path(__file__).with_name('revision059_top_boundary_v1.py'), Path(__file__).with_name('revision059_top_observer_v1.py'), Path(__file__).with_name('review_counter_scope_v12.py'), Path(__file__).with_name('review_counter_scope_v13.py'), Path(__file__).with_name('revision058_top_observer_v1.py'), Path(__file__).with_name('revision058_top_observer_v2.py'), Path(__file__).with_name('revision058_protocol_completion_v1.py'), Path(__file__).with_name('revision058_protocol_completion_v2.py'), Path(__file__).with_name('review_oneway_fixture_v2.py'), Path(__file__).with_name('review_oneway_fixture_v3.py'), Path(__file__).with_name('review_oneway_fixture_v1.py'), Path(__file__).with_name('air_interfaces_v1.py'), protocol_path, *pool_protocols.source_dependencies(folder, protocol_path), *author_sources(authors, runners[0])]
    engine = WorkshopEngine(core.REPO/'pcg/results'/name, batch_size=24,
        extra_sources=sources, runner_script=runners[0])
    deduplicate_snapshot(engine.out)
    return engine, cases, authors


def _recording(case, raw):
    value = copy.deepcopy(case)
    value['recorded_frames'] = [dict(frame=f['frame'], axis=f['axis'], requested=f['requested']) for f in raw['frames']]
    return value


def run_clean(folder, name):
    """Real canonical replay and interfaces; diagnostic only, never admission."""
    folder = Path(folder).resolve(); doc = core.read(folder/'module.mapnote.json')
    engine, cases, authors = _engine(folder, name, FULL_PROTOCOL)
    rows, replay, baselines = [], [], {}
    bases = [fresh(case, 'preflight') for case in cases]
    for index, (case, raw, evidence) in enumerate(engine.run(bases, 'canonical-preflight')):
        check = checked_purpose(authors[index], case, raw)
        rows.append(dict(routeId=cases[index]['route_spec']['id'],check=check,evidence=evidence))
        if check['ok']:
            replay.append(_recording(cases[index],raw))
            baselines[cases[index]['route_spec']['id']]=raw
    probes, preparation_error = [], None
    try:probe_cases = seam_cases(cases[0],doc)+[continuous_exit(case,doc)for case in cases]+[continuous_entry(case,doc)for case in cases]
    except ValueError as error:probe_cases=[];preparation_error=str(error)
    for case, raw, evidence in engine.run(probe_cases, 'preflight-boundaries'):
        probes.append(dict(id=case['id'],check=crossing(case,raw),evidence=evidence))
    counters=_run_counters(engine,cases,authors,'preflight-cheap-counters',baselines)
    core.write(engine.out/'counterexamples.json',counters)
    result=dict(schema='pcg/migration-clean-preflight/v1',contentVersion=doc['generationContract']['contentVersion'],
        passed=all(row['check']['ok'] for row in rows)and all(row['check']['passed']for row in probes)and preparation_error is None and not any(c['adjudication']['invalidates_design']for c in counters),
        counters=counters, routes=rows,probes=probes,preparationError=preparation_error,actualAttempts=engine.sim.cases,
        protocol=artifact(FULL_PROTOCOL),technicalAdmission=False)
    core.write(engine.out/'clean-preflight.json',result)
    if len(replay)==len(cases):core.write(engine.out/'replay-cases.json',dict(cases=replay))
    return result


def fresh(case, label):
    value = copy.deepcopy(case)
    for key in ('recorded_frames', 'factory_evidence', 'module_sha256', 'factory_id', 'noise'):
        value.pop(key, None)
    value['id'] += '-migration-' + label
    value['module_sha256'] = module_hash(value)
    return value


def exterior_floor(case, port):
    from .revision053_boundary_v1 import neighbor as revision_neighbor
    existing=revision_neighbor(case,port)
    if existing is not None:return existing
    support_index = next(p['support_index'] for p in case['ports'] if p['id'] == port['id'])
    source = case['platforms'][support_index]
    x, y = port['position']; nx, ny = port['normal']
    if nx:
        rect = [x-128 if nx < 0 else x, source[1], 128, min(source[3], 64)]
    else:
        if port.get('surface') != 'ONE_WAY_PLATFORM':
            raise ValueError('vertical_fixture_requires_real_one_way_surface:'+port['id'])
        # An explicit adjacent Module owns this witness deck. There is no new
        # support inside the tested Module and no runtime seam auto-repair.
        from .ideas_boundary_v1 import applies as idea_top
        rect = [x-48, y-(96 if idea_top(case,port)else 32) if ny < 0 else y+40, 96, 12]
    new_index = len(case['platforms']); case['platforms'].append(rect)
    if not nx or support_index in case.get('one_way_platform_indices', []):
        case.setdefault('one_way_platform_indices', []).append(new_index)
    return dict(portId=port['id'], floor=rect, source='explicit_test_neighbor',
                copiedIntoModule=False)


def _vertical_inner_dock(case, port):
    from .revision059_top_boundary_v1 import applies as hq_top
    if hq_top(case,port):return list(port['stagingPosition'])
    from .revision058_boundary_v1 import applies as revision_top
    if revision_top(case,port):return list(port['stagingPosition'])
    from .ideas_boundary_v1 import applies as idea_top
    if idea_top(case,port):return list(port['stagingPosition'])
    x, y = port['position']; ny = port['normal'][1]
    eligible = [r for r in case['platforms'] if r[0]+12 <= x <= r[0]+r[2]-12
                and ((r[1]-18 >= y+20) if ny < 0 else (r[1]-18 <= y-20))]
    if not eligible:raise ValueError('vertical_port_has_no_full_body_interior_dock:'+port['id'])
    floor = min(eligible, key=lambda r:abs(r[1]-18-y))
    return [x, floor[1]-18]


def seam_cases(case, doc):
    fixtures = []
    for port in doc['generationContract']['ports']:
        if port.get('surface')=='AIR':
            from .air_interfaces_v1 import local_cases
            fixtures.extend(local_cases(case,port));continue
        nx, ny = port['normal']; bx, by = port['position']
        permission = port.get('permission','INOUT')
        directions = (['ingress'] if permission=='INPUT' else ['egress'] if permission=='OUTPUT' else ['ingress','egress'])
        for direction in directions:
            for offset in (-2, 0, 2):
                value = fresh(case, f"{port['id']}-{direction}-{offset}")
                inner = _vertical_inner_dock(value, port) if ny else None
                neighbor = exterior_floor(value, port)
                if nx:
                    y = port['stagingPosition'][1]
                    outside, inside = bx+nx*48, bx-nx*48
                    start, target = (outside, inside) if direction == 'ingress' else (inside, outside)
                    value['spawn'] = [start, y+offset]
                    from .review_oneway_fixture_v1 import repair as repair_oneway_start
                    repair_oneway_start(value,port,offset)
                    from .review_oneway_fixture_v2 import repair as repair_final_oneway_start
                    repair_final_oneway_start(value,port,offset)
                    from .revision058_boundary_v1 import side_start
                    side_start(value,port,offset)
                    from .review_oneway_fixture_v3 import repair as revision_oneway_start
                    revision_oneway_start(value,port,offset)
                    value['goal'] = [target-9, y-5, 18, 10]
                    value['control_plan'] = [dict(op='settle', trigger=dict(after=0), target_x=target, deadband=3)]
                else:
                    outer = [bx, neighbor['floor'][1]-18]
                    start,target = (outer,inner) if direction=='ingress' else (inner,outer)
                    value['spawn']=[start[0]+offset,start[1]]
                    value['goal']=[target[0]-9,target[1]-5,18,10]
                    downward=target[1]>start[1]
                    value['control_plan']=[dict(op='settle',trigger=dict(after=0),target_x=bx,deadband=2),
                        dict(op='drop_through' if downward else 'jump',trigger=dict(after=1))]
                    if not downward:value['control_plan'].append(dict(op='jump_release',trigger=dict(after=24)))
                value['max_frames'] = 240 if ny else 180
                value['migration_probe'] = dict(kind='local_boundary', portId=port['id'],
                    direction=direction, boundary=port['position'], normal=port['normal'],
                    neighbor=neighbor, body=[24,36])
                from .ideas_boundary_v1 import applies as idea_top,local as idea_local
                if idea_top(value,port):idea_local(value,port,direction,doc,offset)
                from .revision053_boundary_v1 import local as revision_local
                revision_local(value,port,direction,doc,offset)
                from .revision059_top_boundary_v1 import local as hq_local
                hq_local(value,port,direction,doc,offset)
                from .revision058_boundary_v1 import local as new_local
                new_local(value,port,direction,doc,offset)
                value['module_sha256'] = module_hash(value)
                fixtures.append(value)
    return fixtures



def _original_pickups_satisfied(case,raw):
    required=set(case.get('required_original_pickups',[]))
    if not required:return True
    state=raw.get('original_pickups',{})
    pickups={p.get('id'):p for p in state.get('pickups',[])if p.get('claimed')is True}
    accepted={e.get('id'):e for e in state.get('events',[])if e.get('type')=='original_pickup_interaction'and e.get('accepted')is True}
    if not required<=set(pickups) or not required<=set(accepted):return False
    totals={'coins':0,'notes':0}
    for identifier in required:
        pickup,event=pickups[identifier],accepted[identifier]
        key={'coin':'coins','note':'notes'}.get(pickup.get('kind'))
        if key:
            amount=pickup.get('amount',1)
            if event.get(key,0)<amount:return False
            totals[key]+=amount
    return all(state.get(key,0)>=amount for key,amount in totals.items())

def crossing(case, raw):
    from .review_boundary_observer_v1 import observe
    probe = case['migration_probe']; bx, by = probe['boundary']; nx, ny = probe['normal']
    frames = raw.get('frames', [])
    # Entire rectangle must pass the boundary; a center crossing is insufficient.
    distances = [(f['x']-bx)*nx+(f['y']-by)*ny for f in frames]
    half_normal = 12 if nx else 18
    inward = any(distance <= -half_normal for distance in distances)
    outward = any(distance >= half_normal for distance in distances)
    aperture = case.get('block_ports', {}).get(probe['portId'], {}).get('aperture')
    if not isinstance(aperture, list) or len(aperture) != 4:
        return dict(passed=False, reason='explicit_port_aperture_missing')
    tangent_low, tangent_high = (aperture[1], aperture[1]+aperture[3]) if nx else (aperture[0], aperture[0]+aperture[2])
    half_tangent = 18 if nx else 12
    tangent_key = 'y' if nx else 'x'
    crossing_segments = []
    violations = []
    for index, (a, b) in enumerate(zip(frames, frames[1:])):
        if min(distances[index:index+2]) > half_normal or max(distances[index:index+2]) < -half_normal:
            continue
        crossing_segments.append(b['frame'])
        if min(a[tangent_key], b[tangent_key])-half_tangent < tangent_low-.05 or max(a[tangent_key], b[tangent_key])+half_tangent > tangent_high+.05:
            violations.append(b['frame'])
    ordered = bool(distances and ((distances[0] >= half_normal and distances[-1] <= -half_normal)
                   if probe['direction'] == 'ingress' else (distances[0] <= -half_normal and distances[-1] >= half_normal)))
    healthy = raw.get('hp') == 5 and not raw.get('plains', {}).get('player_damage')
    no_reset = not raw.get('returns')
    outcome=True
    if probe['kind']=='continuous_exit':
        required=set(case.get('required_rewards',case.get('route_spec',{}).get('required_rewards',[])))
        claimed={event['id']for event in raw.get('workshop',{}).get('events',[])
                 if event.get('type')=='chest_claim'and event.get('accepted')}
        outcome=required<=claimed and raw.get('workshop',{}).get('coins',0)>=case.get('expected_reward',0)and _original_pickups_satisfied(case,raw)and region_outcomes.satisfied(case,raw)
    observation=observe(case,raw)
    if observation is None:
        from .revision059_top_observer_v1 import observe as observe_hq_top
        hq_observation=observe_hq_top(case,raw)
        if hq_observation:observation=hq_observation
        from .revision058_top_observer_v2 import observe as observe_top
        if observation is None:observation=observe_top(case,raw)
    stable=bool(raw.get('ok')) or bool(observation and observation['stableExit'])
    result=dict(passed=bool(stable and healthy and no_reset and inward and outward and ordered and crossing_segments and not violations and outcome),
                stableExit=stable, bodyPassedBothSides=inward and outward,
                requiredWorldOutcomeSatisfied=outcome,
                aperture=aperture, apertureViolationFrames=violations,
                actualCrossingFrames=crossing_segments, directionOrdered=ordered,
                healthy=healthy, noReset=no_reset, samples=len(frames),
                minimumSignedDistance=min(distances, default=None),
                maximumSignedDistance=max(distances, default=None),
                neighbor=probe['neighbor'])
    if observation:result['observationReanalysis']=observation
    return result


def continuous_exit(case, doc):
    from .revision059_top_boundary_v1 import exit as hq_exit
    special=hq_exit(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    from .revision058_boundary_v1 import exit as new_exit
    special=new_exit(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    from .revision053_boundary_v1 import exit as revision_exit
    special=revision_exit(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    from .ideas_boundary_v1 import exit as idea_exit
    special=idea_exit(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    value = fresh(case, 'continuous-exit')
    route = case['route_spec']
    port = next(p for p in doc['generationContract']['ports'] if p['id'] == route['to_port'])
    if port.get('surface')=='AIR':
        from .air_interfaces_v1 import exit
        return exit(case,port)
    neighbor = exterior_floor(value, port)
    settle_indices = [i for i, command in enumerate(value['control_plan']) if command['op'] == 'settle']
    if not settle_indices:
        raise ValueError('continuous_exit_needs_explicit_terminal_settle')
    if port['normal'][0]:
        target = port['position'][0]+port['normal'][0]*48
        origin=next(p for p in doc['generationContract']['ports']if p['id']==route['from_port'])
        earned_reward_dock=case.get('approved_first30',{}).get('reviewId')=='17'and route['to_port']=='C'
        approved_drop_dock=case.get('approved_implementation',{}).get('reviewId')=='125' and route['from_port']in('fork_up','C') and route['to_port']in('entry','fork_right')
        if case.get('approved_implementation'):
            # Preserve the complete authored landing, waits and terminal dock.
            # Retargeting it can skip a descent or leave an old goal unreachable.
            value['control_plan'] += [dict(op='wait',trigger=dict(after=6,state='grounded',timeout=240)),dict(op='settle',trigger=dict(after=0),target_x=target,deadband=2)]
        elif (origin.get('surface')=='AIR' and abs(case['spawn'][0]-case['exit_port'][0])<64) or earned_reward_dock or approved_drop_dock:
            # First complete the authored downward landing. Retargeting the
            # only settle while still in the sky crosses the side aperture high.
            value['control_plan'] += [dict(op='wait',trigger=dict(after=6,state='grounded',timeout=240)),dict(op='wait',trigger=dict(after=6)),dict(op='settle',trigger=dict(after=0),target_x=target,deadband=2)] if earned_reward_dock else [dict(op='wait',trigger=dict(after=6,state='grounded',timeout=240)),dict(op='settle',trigger=dict(after=0),target_x=target,deadband=2)]
        else:value['control_plan'][settle_indices[-1]]['target_x'] = target
        value['goal'] = [target-9, port['stagingPosition'][1]-5, 18, 10]
    else:
        # Finish the original reward/core landing before moving to the new
        # vertical dock. Persistent settle is explicitly retargeted, not assumed
        # to be cancelled by an axis command.
        old_target=value['control_plan'][settle_indices[-1]]['target_x']
        sign='gte' if old_target>=case['spawn'][0] else 'lte'
        value['control_plan'] += [dict(op='wait',trigger=dict(state='grounded',
            dynamic=dict(kind='actor_x',direction=sign,value=old_target-3 if sign=='gte' else old_target+3),timeout=240)),
            dict(op='settle',trigger=dict(after=6),target_x=port['position'][0],deadband=2),
            dict(op='wait',trigger=dict(after=24,state='grounded',timeout=240))]
        if port['normal'][1]>0:
            value['control_plan'].append(dict(op='drop_through',trigger=dict(after=1)))
        else:
            adaptation=next((p for p in case.get('migration_adaptation',{}).get('portAdaptations',[])
                             if p['portId']==port['id']),{})
            jumps=max(1,len(adaptation.get('connectorPlatforms',[])))+1
            for _ in range(jumps):
                value['control_plan'] += [dict(op='jump',trigger=dict(after=6)),
                    dict(op='jump_release',trigger=dict(after=24)),
                    dict(op='wait',trigger=dict(after=6,state='grounded',timeout=180))]
        target=[port['position'][0],neighbor['floor'][1]-18]
        value['goal']=[target[0]-9,target[1]-5,18,10]
    value['max_frames'] += 600 if port['normal'][1] else 180
    if case.get('approved_implementation'):
        value['max_frames']=min(3600,value['max_frames'])
    value['migration_probe'] = dict(kind='continuous_exit', portId=port['id'],
        direction='egress', boundary=port['position'], normal=port['normal'],
        neighbor=neighbor, body=[24,36], noIntermediateReset=True,
        originalRouteId=route['id'])
    value['module_sha256'] = module_hash(value)
    return value



def continuous_entry(case, doc):
    from .revision059_top_boundary_v1 import entry as hq_entry
    special=hq_entry(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    from .revision059_boundary_v1 import entry as repair_entry
    repair=repair_entry(case,doc,__import__(__name__,fromlist=['unused']))
    if repair is not None:return repair
    from .revision058_boundary_v1 import entry as new_entry
    special=new_entry(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    """Approach the actual canonical start from an explicit adjacent Module.

    This measures entry docking only. It never resets an actor mid-fixture or
    claims the separately replayed interior starts with identical world phase.
    """
    from .ideas_boundary_v1 import entry as idea_entry
    special=idea_entry(case,doc,__import__(__name__,fromlist=['unused']))
    if special is not None:return special
    value=fresh(case,'continuous-entry')
    port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['from_port'])
    if port.get('surface')=='AIR':
        from .air_interfaces_v1 import entry
        return entry(case,port)
    neighbor=exterior_floor(value,port)
    target=case['spawn'];nx,ny=port['normal']
    if nx:
        value['spawn']=[port['position'][0]+nx*48,port['stagingPosition'][1]]
        value['control_plan']=[dict(op='settle',trigger=dict(after=0),target_x=target[0],deadband=2)]
    else:
        value['spawn']=[port['position'][0],neighbor['floor'][1]-18]
        value['control_plan']=[dict(op='settle',trigger=dict(after=0),target_x=target[0],deadband=2),
            dict(op='drop_through'if ny<0 else'jump',trigger=dict(after=1))]
        if ny>0:value['control_plan'].append(dict(op='jump_release',trigger=dict(after=24)))
    value['goal']=[target[0]-9,target[1]-5,18,10]
    value['max_frames']=360
    value['migration_probe']=dict(kind='continuous_entry',portId=port['id'],direction='ingress',
        boundary=port['position'],normal=port['normal'],neighbor=neighbor,body=[24,36],
        noIntermediateReset=True,originalRouteId=case['route_spec']['id'],
        scope='boundary to canonical starting dock; interior continuation phase not asserted')
    # Entrance docking must not inherit the original route's AIR exit goal.
    if case.get('approved_first30') and any(p['id']==case['route_spec']['to_port'] and p.get('surface')=='AIR' for p in doc['generationContract']['ports']):
        value['route_spec']=dict(case['route_spec'],to_port=case['route_spec']['from_port'])
    value['module_sha256']=module_hash(value)
    return value


def counter_cases(case):
    """Fixed low-cost searches after geometry edits; not random gameplay labels."""
    target=case['goal'][0]+case['goal'][2]/2
    definitions=[('walk-direct',[dict(op='settle',trigger=dict(after=0),target_x=target,deadband=3)])]
    sign=1 if target>=case['spawn'][0]else-1
    definitions.append(('ordinary-jump',[dict(op='axis',trigger=dict(after=0),value=sign),
        dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=20)),
        dict(op='settle',trigger=dict(after=0),target_x=target,deadband=3)]))
    shots=[i for i,c in enumerate(case['control_plan'])if c['op']=='shoot']
    jumps=[i for i,c in enumerate(case['control_plan'])if c['op']=='jump']
    for label,indices in [('omit-all-shots',shots),('omit-first-shot',shots[:1]),('omit-first-jump',jumps[:1])]:
        if not indices:continue
        plan=copy.deepcopy(case['control_plan'])
        for index in indices:
            # Preserve real waiting/trigger timing, omit only the requested action.
            plan[index]['op']='wait'
            for key in ('direction','aim_target','aim_cell'):plan[index].pop(key,None)
        definitions.append((label,plan))
    for latch in case.get('latches',[])[:2]:
        plan=[dict(op='shoot',trigger=dict(after=0),aim_cell=dict(kind='bell',id=latch['id'])),
              dict(op='wait',trigger=dict(after=24))]+copy.deepcopy(case['control_plan'])
        definitions.append(('ground-preopen-'+str(latch['id']),plan))
    native_actions=case.get('actions',[])
    native_shots=[i for i,a in enumerate(native_actions)if a.get('type')in('shoot_release','shoot')]
    native_jumps=[i for i,a in enumerate(native_actions)if a.get('type')=='jump']
    for label,indices in [('native-omit-all-shots',native_shots),('native-omit-first-shot',native_shots[:1]),('native-omit-first-jump',native_jumps[:1])]:
        if indices:
            kept=[copy.deepcopy(a)for i,a in enumerate(native_actions)if i not in indices]
            definitions.append((label,copy.deepcopy(case['control_plan']),kept))
    result=[]
    for definition in definitions[:8]:
        label,plan=definition[:2]
        native_timeline=definition[2:]

        # Omission policies can be as long as an already valid canonical policy.
        # The actual registered runner validates its DSL budget (Foundry: 384).
        value=fresh(case,'counter-'+label);value['control_plan']=plan
        if native_actions:
            if native_timeline:value['actions']=native_timeline[0]
            else:
                value.pop('actions',None);value.pop('axes',None)
        value['migration_counter']=dict(kind=label,originalRouteId=case['route_spec']['id'],
            search='fixed low-cost geometry adaptation checks; finite, not impossibility proof')
        if native_timeline:value['migration_counter']['keepNativeTimeline']=True
        value['module_sha256']=module_hash(value);result.append(value)
    return result


def _same_outcome(case,raw):
    required=set(case.get('required_rewards',case.get('route_spec',{}).get('required_rewards',[])))
    claimed={e['id']for e in raw.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
    okay=bool(raw.get('ok')and raw.get('hp')==5 and not raw.get('plains',{}).get('player_damage')and not raw.get('returns')
        and required<=claimed and raw.get('workshop',{}).get('coins',0)>=case.get('expected_reward',0)and _original_pickups_satisfied(case,raw)and region_outcomes.satisfied(case,raw))
    park=case.get('required_carrier_park')
    if park:
        final=raw.get('frames',[{}])[-1]
        platform=next((p for p in final.get('moving_platforms',[])if p['id']==park['id']),None)
        state=next((p for p in raw.get('workshop',{}).get('carriers',[])if p['id']==park['id']),None)
        okay=okay and bool(platform and state and state['running']==park['running']and park['x_range'][0]<=platform['position'][0]<=park['x_range'][1])
    if case.get('purpose_kind')=='persistent_death':
        okay=okay and any(e.get('dead')for e in raw.get('plains',{}).get('enemies',[]))
    return dict(ok=okay,required_reward_ids=sorted(required),claimed_reward_ids=sorted(claimed))


def _counter_judgment(case,raw,author,baseline=None):
    from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification
    check=causal_observer.correct(case,raw,checked_purpose(author,case,raw))
    if case.get('family')in('gate-brake-return','trapdoor-commit')and any(r in check.get('reasons',[])for r in('airborne_same_shot_gate_missing','self_support_removal_missing')):
        try:assertion_source=causal_observer_v2._assertion_source(author)
        except (AttributeError,TypeError,ValueError):assertion_source='UNKNOWN'
        check=causal_observer_v2.correct(case,raw,check,assertion_source=assertion_source)
        check=causal_observer_v3.correct(case,raw,check,assertion_source=assertion_source)
    outcome=_same_outcome(case,raw)
    judgment=counter_classification(case,raw,check,outcome,baseline=baseline)
    from .review_counter_scope_v1 import classify
    judgment=classify(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v2 import classify as reviewed_exterior
    judgment=reviewed_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v3 import classify as sky_exterior
    judgment=sky_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v4 import classify as paid_jump_exterior
    judgment=paid_jump_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v5 import classify as rejected_exterior
    judgment=rejected_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v6 import classify as compact_bell_exterior
    judgment=compact_bell_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v7 import classify as low_return_exterior
    judgment=low_return_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v8 import classify as approved040_exterior
    judgment=approved040_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v9 import classify as new_ideas_exterior
    judgment=new_ideas_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v11 import classify as revised196_exterior
    judgment=revised196_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v12 import classify as new_exterior
    judgment=new_exterior(case,raw,check,outcome,judgment,baseline)
    from .review_counter_scope_v13 import classify as approved_hq_exterior
    judgment=approved_hq_exterior(case,raw,check,outcome,judgment,baseline)
    return dict(causalCheck=check,externalOutcome=outcome,adjudication=judgment)


def _run_counters(engine,cases,authors,stage,baselines=None):
    expanded=[];author_by_id={}
    for case,author in zip(cases,authors):
        for candidate in counter_cases(case):expanded.append(candidate);author_by_id[candidate['id']]=author
    result=[]
    for case,raw,evidence in engine.run(expanded,stage):
        result.append(dict(id=case['id'],probe=case['migration_counter'],
            **_counter_judgment(case,raw,author_by_id[case['id']],(baselines or {}).get(case['route_spec']['id'])),evidence=evidence))
    return result

def artifact(path):
    return dict(path=core.relative(path), sha256=core.sha(path))


def run(folder, name, protocol_path=None):
    folder = Path(folder).resolve(); doc = core.read(folder/'module.mapnote.json')
    protocol_path = pool_protocols.runtime_protocol(folder, protocol_path, new_run=True)
    holdout_guard.check(folder,protocol_path=protocol_path)
    pool_protocols.assert_unstarted(folder,protocol_path)
    protocol = core.read(protocol_path)
    if doc['generationContract']['version'] != 2:
        raise ValueError('migration_requires_v2')
    engine, cases, authors = _engine(folder, name, protocol_path)
    run_path = engine.out
    core.write(run_path/'protocol.json', protocol)
    core.write(run_path/'input-binding.json', dict(module=artifact(folder/'module.mapnote.json'),
        cases=artifact(folder/'physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else folder/'cases.json'), contentVersion=doc['generationContract']['contentVersion'],
        internalGeometryChanged=any(bool(c.get('migration_adaptation'))for c in cases), testOnlyNeighborNeverExported=True))
    route_reports, baselines = [], {}
    for index, (case, author) in enumerate(zip(cases, authors)):
        base = fresh(case, 'interior')
        check = lambda c, r: checked_purpose(author, c, r)
        calibration = evaluate(engine, [base], protocol['calibrationSeed']+index*1009,
                               12, 'migration-calibration', purpose_fn=check)[0]
        core.write(run_path/f'calibration-{index}.json', calibration)
        if calibration.get('witness'):baselines[case['route_spec']['id']]=calibration['witness']['result']
        if calibration['quality_gate']['status'] != 'awaiting_human_review':
            route_reports.append(dict(routeId=case['route_spec']['id'], passed=False,
                calibration=artifact(run_path/f'calibration-{index}.json'), holdout='NOT_RUN'))
            continue
        # Fixed canonical geometry/program; selection happens before holdout.
        core.write(run_path/f'selection-{index}.json', dict(case_sha256=module_hash(base),
            calibrationSha256=core.sha(run_path/f'calibration-{index}.json'),
            holdoutSeed=protocol['holdoutSeed']+index*1009, revisions=0))
        pool_protocols.reserve_holdout(folder,protocol_path,name)
        holdout = evaluate(engine, [base], protocol['holdoutSeed']+index*1009,
                           12, 'migration-holdout', purpose_fn=check)[0]
        core.write(run_path/f'holdout-{index}.json', holdout)
        route_reports.append(dict(routeId=case['route_spec']['id'],
            passed=holdout['quality_gate']['status'] == 'awaiting_human_review',
            calibration=artifact(run_path/f'calibration-{index}.json'),
            holdout=artifact(run_path/f'holdout-{index}.json')))
    extended = protocol.get('schema')=='pcg/module-migration-protocol/v2'
    probes = seam_cases(cases[0], doc)+[continuous_exit(case, doc) for case in cases]
    if extended:probes += [continuous_entry(case,doc)for case in cases]
    probe_reports = []
    for case, raw, evidence in engine.run(probes, 'boundary-and-continuous-exit'):
        probe_reports.append(dict(id=case['id'], probe=case['migration_probe'],
            check=crossing(case, raw), evidence=evidence))
    core.write(run_path/'boundary-probes.json', probe_reports)
    counters=_run_counters(engine,cases,authors,'cheap-adaptation-counters',baselines)if extended else []
    if extended:core.write(run_path/'counterexamples.json',counters)
    report = dict(schema='pcg/foundation-migration-physics/v1',
        contentVersion=doc['generationContract']['contentVersion'],
        passed=all(r['passed'] for r in route_reports) and all(p['check']['passed'] for p in probe_reports)and not any(c['adjudication']['invalidates_design']for c in counters),
        routes=route_reports, probes=artifact(run_path/'boundary-probes.json'),
        actualAttempts=engine.sim.cases, sourceBinding=artifact(run_path/'source_binding.json'),
        batches=artifact(run_path/'batches.json'), protocol=artifact(run_path/'protocol.json'),
        unknown=['unsearched port pairs', 'closure combinations', 'mirror', 'arbitrary entry states', 'full Map'],
        humanReview='UNKNOWN', productionAdmitted=False)
    if extended:report['counterexamples']=artifact(run_path/'counterexamples.json')
    pool_binding=pool_protocols.report_binding(folder,protocol_path,name)
    if pool_binding is not None:report['holdoutPool']=pool_binding
    core.write(run_path/'migration-physics.json', report)
    if engine.sim.cases > protocol['maximumAttemptsPerModule']:
        raise ValueError('predeclared_migration_budget_exceeded')
    return report


def verify_report(folder, proof):
    """Re-derive admission from original raw bytes, not report booleans."""
    core.verify_artifacts([proof])
    report_path = core.resolve_artifact(proof['path']); run_path = report_path.parent
    report = core.read(report_path)
    if report.get('protocolCompletion'):
        from .revision058_protocol_completion_v2 import validate_lineage as validate_completion
        validate_completion(report,report_path)
    lineage_report=report
    if report.get('metadataCorrection'):
        from .review_metadata_bindings_v1 import validate_lineage as validate_metadata
        lineage_report=validate_metadata(report,report_path)
    if lineage_report.get('boundaryRepair'):
        if lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v8':
            from .review_boundary_repair_v8 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v7':
            from .review_boundary_repair_v7 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v6':
            from .review_boundary_repair_v6 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v5':
            from .review_boundary_repair_v5 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v4':
            from .review_boundary_repair_v4 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v3':
            from .review_boundary_repair_v3 import validate_lineage
        elif lineage_report['boundaryRepair']['schema']=='pcg/review-boundary-fixture-repair/v2':
            from .review_boundary_repair_v2 import validate_lineage
        else:
            from .review_boundary_repair_v1 import validate_lineage
        validate_lineage(lineage_report,report_path)
    doc = core.read(Path(folder)/'module.mapnote.json')
    if report['schema'] != 'pcg/foundation-migration-physics/v1' or report['contentVersion'] != doc['generationContract']['contentVersion']:
        raise ValueError('physics_report_bound_to_another_version')
    core.verify_artifacts([report[key] for key in ('sourceBinding','batches','protocol','probes')])
    protocol = core.read(core.resolve_artifact(report['protocol']['path']))
    pool_protocols.evidence_protocol(folder,protocol,report=report,report_path=report_path)
    if report.get('offlineAnalysis'):
        from .offline_reanalysis import validate_lineage
        validate_lineage(report,report_path)
    binding = core.read(core.resolve_artifact(report['sourceBinding']['path']))
    input_binding = core.read(run_path/'input-binding.json')
    physics_cases_path = Path(folder)/'physics-input-cases.json'
    if not physics_cases_path.exists(): physics_cases_path = Path(folder)/'cases.json'
    if input_binding['contentVersion'] != lineage_report['contentVersion'] or input_binding['cases']['sha256'] != core.sha(physics_cases_path):
        raise ValueError('physics_input_not_bound_to_current_module')
    canonical_cases = core.read(physics_cases_path)['cases']
    playback_cases = core.read(Path(folder)/'cases.json')['cases']
    def without_recording(value):
        value = copy.deepcopy(value)
        value.pop('recorded_frames', None)
        return value
    if [without_recording(case) for case in canonical_cases] != [without_recording(case) for case in playback_cases]:
        raise ValueError('playback_and_validated_program_differ')
    if len(canonical_cases) != len(report['routes']):
        raise ValueError('canonical_route_count_changed')
    for rel, expected in binding['source_files'].items():
        frozen = run_path/'source_snapshot'/rel
        if not frozen.is_file() or core.sha(frozen) != expected:
            raise ValueError('frozen_source_missing_or_changed:' + rel)
    batches = core.read(core.resolve_artifact(report['batches']['path']))
    lookup = {}; by_id = {}; count = 0
    for batch in batches:
        compressed = run_path/batch['gzip_path']
        if core.sha(compressed) != batch['gzip_sha256']:
            raise ValueError('physics_compressed_bytes_changed')
        with gzip.open(compressed, 'rb') as stream:
            data = stream.read()
        import hashlib
        if hashlib.sha256(data).hexdigest() != batch['raw_output_sha256']:
            raise ValueError('physics_raw_bytes_changed')
        execution = core.read(run_path/batch['execution'])
        input_path = run_path/'physics'/(batch['batch']+'.input.json')
        if execution['exit_code'] or core.sha(input_path) != execution['input_sha256']:
            raise ValueError('physics_execution_input_mismatch')
        inputs = core.read(input_path)['cases']; results = json.loads(data)['results']
        if [c['id'] for c in inputs] != [r['id'] for r in results] or len(results) != batch['cases']:
            raise ValueError('physics_case_identity_mismatch')
        for index, (case, raw) in enumerate(zip(inputs, results)):
            lookup[(batch['batch'], index)] = (case, raw)
            by_id[case['id']] = (case, raw)
        count += len(inputs)
    if count != report['actualAttempts'] or count > protocol['maximumAttemptsPerModule']:
        raise ValueError('physics_attempt_count_mismatch')
    from pcg.prototype.factory.core.quality import gate
    from pcg.prototype.workshop.evaluate import instantiate
    counter_baselines={}
    for route_index, route in enumerate(report['routes']):
        if not isinstance(route['holdout'], dict):
            raise ValueError('independent_holdout_not_run')
        for stage in ('calibration', 'holdout'):
            core.verify_artifacts([route[stage]])
            evaluation = core.read(core.resolve_artifact(route[stage]['path']))
            base = evaluation['case']
            if module_hash(base) != module_hash(fresh(canonical_cases[route_index], 'interior')):
                raise ValueError('validation_used_another_canonical_program')
            author = author_for(base)
            for source in [Path(author.__file__), *getattr(author, 'SOURCE_DEPENDENCIES', [])]:
                source = Path(source).resolve()
                rel = source.relative_to(core.REPO/'pcg').as_posix()
                if binding['source_files'].get(rel) != core.sha(source):
                    raise ValueError('causal_validator_drift:' + rel)
            dynamic = bool(base.get('moving_platforms') or base.get('enemies') or base.get('saws'))
            seed = protocol[stage+'Seed']+route_index*1009
            stats = {}
            for level in ('clean', 'mild', 'moderate'):
                rows = [row for row in evaluation['rows'] if row['level'] == level]
                needed = 12 if level != 'clean' or dynamic else 1
                if {row['trial'] for row in rows} != set(range(needed)) or len(rows) != needed:
                    raise ValueError('insufficient_or_duplicate_validation_trials')
                good = 0
                for row in rows:
                    case, raw = lookup[(row['evidence']['batch'], row['evidence']['index'])]
                    expected = instantiate(base, seed, level, row['trial'])
                    if module_hash(case) != module_hash(expected):
                        raise ValueError('validation_seed_or_input_changed')
                    author = author_for(case)
                    check = checked_purpose(author, case, raw)
                    good += bool(check['ok'])
                    if stage=='calibration'and level=='clean'and check['ok']and route['routeId']not in counter_baselines:
                        counter_baselines[route['routeId']]=raw
                stats[level] = dict(trials=len(rows), purpose_valid=good)
            if gate(stats, False, dynamic)['status'] != 'awaiting_human_review':
                raise ValueError('original_quality_gate_failed:' + route['routeId']+'/'+stage)
    probes = core.read(core.resolve_artifact(report['probes']['path']))
    cases = canonical_cases
    expected_probes = seam_cases(cases[0], doc)+[continuous_exit(case, doc) for case in cases]
    if protocol.get('schema')=='pcg/module-migration-protocol/v2'or report.get('protocolCompletion'):
        expected_probes += [continuous_entry(case,doc)for case in cases]
    if {p['id'] for p in probes} != {case['id'] for case in expected_probes} or len(probes) != len(expected_probes):
        raise ValueError('boundary_or_continuous_exit_coverage_missing')
    for expected in expected_probes:
        case, raw = by_id[expected['id']]
        if module_hash(case) != module_hash(expected) or not crossing(case, raw)['passed']:
            raise ValueError('actual_boundary_probe_failed:' + expected['id'])
    if protocol.get('schema')=='pcg/module-migration-protocol/v2'or report.get('protocolCompletion'):
        if 'counterexamples'not in report:raise ValueError('adaptation_counter_search_missing')
        core.verify_artifacts([report['counterexamples']])
        counters=core.read(core.resolve_artifact(report['counterexamples']['path']))
        expected_counters=[counter for case in cases for counter in counter_cases(case)]
        if {c['id']for c in counters}!={c['id']for c in expected_counters}or len(counters)!=len(expected_counters):
            raise ValueError('adaptation_counter_coverage_missing')
        for expected in expected_counters:
            case,raw=by_id[expected['id']]
            if module_hash(case)!=module_hash(expected):raise ValueError('adaptation_counter_input_changed')
            judgment=_counter_judgment(case,raw,author_for(case),counter_baselines.get(case['route_spec']['id']))
            if judgment['adjudication']['invalidates_design']:raise ValueError('actual_adapted_cheap_bypass:'+expected['id'])
    if {r['routeId'] for r in report['routes']} != {r['id'] for r in doc['generationContract']['routes']}:
        raise ValueError('route_validation_coverage_missing')
    return report


def _verification_identity(folder, proof):
    """Hash immutable inputs before reusing a deep raw-analysis result.

    This deliberately hashes bytes, never only mtimes or report pass flags. The
    cache accelerates decompression and repeated causal analysis, not integrity
    checks. It is local disposable acceleration, not a candidate/evidence store.
    """
    core.verify_artifacts([proof])
    report_path = core.resolve_artifact(proof['path'])
    report = core.read(report_path)
    doc = core.read(Path(folder)/'module.mapnote.json')
    files = {p.relative_to(report_path.parent).as_posix(): core.sha(p)
             for p in report_path.parent.rglob('*') if p.is_file()}
    input_path = Path(folder)/'physics-input-cases.json'
    if not input_path.exists():input_path=Path(folder)/'cases.json'
    cases = core.read(input_path)['cases']
    playback = copy.deepcopy(core.read(Path(folder)/'cases.json')['cases'])
    for case in playback:case.pop('recorded_frames', None)
    live_sources = {}
    for case in cases:
        author = author_for(case)
        for source in [Path(author.__file__), *getattr(author,'SOURCE_DEPENDENCIES',[])]:
            live_sources[str(source)] = core.sha(source)
    return digest(dict(schema='pcg/deep-physics-verification-cache/v1',
        verifier=core.sha(Path(__file__)), causalObserver=core.sha(Path(causal_observer.__file__)),
        causalObserverV2=core.sha(Path(causal_observer_v2.__file__)), causalObserverV3=core.sha(Path(causal_observer_v3.__file__)), poolProtocolSource=core.sha(Path(pool_protocols.__file__)),
        holdoutGuardSource=core.sha(Path(holdout_guard.__file__)), regionOutcomeSource=core.sha(Path(region_outcomes.__file__)),
        reviewCounterScope=core.sha(Path(__file__).with_name('review_counter_scope_v1.py')),
        reviewCounterScopeV2=core.sha(Path(__file__).with_name('review_counter_scope_v2.py')),
        reviewCounterScopeV3=core.sha(Path(__file__).with_name('review_counter_scope_v3.py')),
        reviewCounterScopeV4=core.sha(Path(__file__).with_name('review_counter_scope_v4.py')),
        reviewCounterScopeV5=core.sha(Path(__file__).with_name('review_counter_scope_v5.py')),
        reviewCounterScopeV6=core.sha(Path(__file__).with_name('review_counter_scope_v6.py')),
        reviewCounterScopeV7=core.sha(Path(__file__).with_name('review_counter_scope_v7.py')),
        reviewCounterScopeV9=core.sha(Path(__file__).with_name('review_counter_scope_v9.py')),
        reviewCounterScopeV8=core.sha(Path(__file__).with_name('review_counter_scope_v8.py')),
        revision058TopObserver=core.sha(Path(__file__).with_name('revision058_top_observer_v2.py')),
        revision058Completion=core.sha(Path(__file__).with_name('revision058_protocol_completion_v2.py')),
        reviewBoundaryObserverV1=core.sha(Path(__file__).with_name('review_boundary_observer_v1.py')),
        onewayFixtureV1=core.sha(Path(__file__).with_name('review_oneway_fixture_v1.py')),
        ideasBoundaryV1=core.sha(Path(__file__).with_name('ideas_boundary_v1.py')),
        onewayFixtureV2=core.sha(Path(__file__).with_name('review_oneway_fixture_v2.py')),
        reviewBoundaryRepairV5=core.sha(Path(__file__).with_name('review_boundary_repair_v5.py')),
        metadataBindingCorrection=core.sha(Path(__file__).with_name('review_metadata_bindings_v1.py')),
        boundaryLineage={v:core.sha(Path(__file__).with_name('review_boundary_repair_'+v+'.py'))for v in ('v1','v2','v3','v4','v5','v6','v7')},
        airInterfaces=core.sha(Path(__file__).with_name('air_interfaces_v1.py')),
        registeredPool=pool_protocols.cache_identity(folder,core.read(core.resolve_artifact(report['protocol']['path'])),report)if report.get('protocol')else None,
        report=proof, runFiles=files,
        protocolV1=core.sha(PROTOCOL), protocolV2=core.sha(FULL_PROTOCOL),
        currentVersion=doc['generationContract']['contentVersion'],
        routes=doc['generationContract']['routes'], ports=doc['generationContract']['ports'],
        physicsInput=core.sha(input_path),playbackProgram=playback,causalSources=live_sources))


_verify_report_uncached = verify_report


def verify_report(folder, proof, *, deep=False):
    key = _verification_identity(folder, proof)
    cache = core.REPO/'.cache/migration/deep-verification'/(key+'.json')
    if not deep and cache.exists():
        receipt = core.read(cache)
        if receipt.get('identity') == key and receipt.get('deepVerified') is True:
            return core.read(core.resolve_artifact(proof['path']))
    report = _verify_report_uncached(folder, proof)
    core.write(cache,dict(identity=key,deepVerified=True,report=proof,
        scope='Hash-identical raw inputs, frozen sources and canonical program; no new experiment or certificate.'))
    return report
