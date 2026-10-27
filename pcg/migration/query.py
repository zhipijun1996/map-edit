"""Static retrieval of certified current content and whole Port configurations.

This selector reads durable, offline-verified artifacts. It never edits geometry,
composes untested corner options, or simulates a player's changing resources.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from . import core
from . import corners


HOLDS = {'design_hold', 'human_design_hold', 'rejected', 'pacing_held', 'withdrawn_review'}


def _physical_port_groups(ports, connected):
    """A boundary-face anchor is one connection even under source aliases."""
    groups = defaultdict(list)
    for port in ports:
        if port['id'] in connected:
            groups[(tuple(port['position']), port['face'])].append(port['id'])
    return [dict(position=list(position), face=face, logicalNames=names)
            for (position, face), names in groups.items()]


def _native_profile(gc):
    """Read the exact frozen initial profile; no live resource propagation.

    Older v2/v3 content has no requirement. Native packages also bind their
    canonical profile in generation parameters, so that binding cannot be
    bypassed merely by omitting the convenience requiredNativeProfile field.
    """
    declared = gc.get('requiredNativeProfile')
    stored = gc.get('generation', {}).get('parameters', {}).get('original_tuning_profile')
    if declared is None and stored is None:
        return None, None
    profile = declared if declared is not None else stored
    if declared is not None and stored is not None and declared != stored:
        return profile, 'native_profile_declaration_mismatch'
    if (not isinstance(profile, dict) or not isinstance(profile.get('id'), str)
            or not profile['id'] or profile['id'] == 'UNKNOWN'
            or not isinstance(profile.get('overrides'), dict)
            or not isinstance(profile.get('abilities'), list)
            or not all(isinstance(v, str) and v != 'UNKNOWN' for v in profile['abilities'])):
        return profile, 'required_native_profile_not_fully_declared'
    tuning = profile.get('effectiveTuning')
    if not isinstance(tuning, dict) or any(type(tuning.get(key)) is not int or tuning[key] < 0
                                          for key in ('max_jumps', 'max_air_shots')):
        return profile, 'required_native_profile_effective_tuning_unknown'
    return profile, None


def _ability_set(value):
    if not isinstance(value, list) or not all(isinstance(v, str) and v and v != 'UNKNOWN' for v in value):
        return None
    return tuple(sorted(set(value)))


def _bound_ability_sets(variant):
    """Actual canonical input configurations, grouped by their tested route."""
    if '_bound_ability_sets' in variant: return variant['_bound_ability_sets']
    inputs = variant['folder']/'physics-input-cases.json'
    if not inputs.is_file(): inputs = variant['folder']/'cases.json'
    if not inputs.is_file(): return {}
    payload = core.read(inputs)
    cases = payload.get('cases') if isinstance(payload, dict) else payload
    if not isinstance(cases, list): return {}
    actual_by_route = {}
    for case in cases:
        actual = _ability_set(case.get('capabilities'))
        if actual is None: continue
        actual_by_route.setdefault(case.get('route_spec', {}).get('id', 'main'), set()).add(actual)
    variant['_bound_ability_sets'] = actual_by_route
    return actual_by_route


def _current_physics_validations(gc):
    return [validation for validation in gc.get('validations', [])
            if validation.get('kind') == 'physics' and validation.get('result') == 'pass'
            and validation.get('contentVersion') == gc['contentVersion'] and validation.get('artifacts')]


def _tested_initial_abilities(variant, *, require_metadata_agreement=False):
    """Truthful bound configurations; one-way claims also require agreement.

    Ordinary route lookup reads the actual input configuration even if an old
    evidence display field omitted an ability. One-way permission additionally
    requires the declaration to agree with those same current, bound inputs.
    """
    gc = variant['document']['generationContract']
    actual_by_route = _bound_ability_sets(variant)
    configurations = set()
    for validation in _current_physics_validations(gc):
        actual = actual_by_route.get(validation.get('routeId'), set())
        if not require_metadata_agreement:
            configurations.update(actual)
            continue
        configuration = validation.get('capabilityConfiguration', {})
        if not isinstance(configuration, dict): continue
        available = _ability_set(configuration.get('available'))
        if available is None or available not in actual:
            continue
        configurations.add(available)
    return [list(configuration) for configuration in sorted(configurations)]


def _required_tested_abilities(variant, routes):
    actual = _bound_ability_sets(variant)
    return sorted({ability for route in routes for configuration in actual.get(route['id'], set())
                   for ability in configuration})


def _variants(entry, folder, doc, verified, requested_configuration):
    """Each alternative is an independently certified *whole* configuration."""
    base = dict(id='base', document=doc, folder=folder, file=entry['file'],
                scene=f"modules/{entry['id']}/module.tscn", verified=verified, receipt=None)
    if requested_configuration == 'base':
        return [base]
    variants = [base]
    for artifact in corners.verified_receipts(entry['id'], core.sha(folder/'module.mapnote.json'),
                                             doc['generationContract']['contentVersion']):
        # verified_receipts re-derives actual physics, retired-opening closure,
        # package equality and native playback, rather than accepting booleans.
        core.verify_artifacts([artifact])
        receipt_path = core.resolve_artifact(artifact['path'])
        receipt = core.read(receipt_path)
        configuration_id = receipt['configurationId']
        if configuration_id == 'base' or any(v['id'] == configuration_id for v in variants):
            raise ValueError('duplicate_or_reserved_port_configuration_id:'+configuration_id)
        target = core.resolve_artifact(receipt['configuration']['path'])
        core.verify_artifacts([receipt['configuration']])
        target_doc = core.read(target)
        if target_doc['generationContract']['contentVersion'] != receipt['configuration']['contentVersion']:
            raise ValueError('selected_configuration_content_version_changed:'+configuration_id)
        variants.append(dict(id=configuration_id, document=target_doc, folder=target.parent,
            file='./'+receipt['configuration']['path'].removeprefix('./'),
            scene=receipt['configuration']['path'].removeprefix('./').rsplit('/', 1)[0]+'/module.tscn',
            # A corner certificate does not certify unrelated mirror/closure
            # combinations or unrestricted Map integration for the alternative.
            verified=dict(mapReady=False, certifiedClosureProfiles=[], certifiedMirror=False),
            receipt=artifact))
    return variants


def _reasons(specification, entry, variant, available, unsupported, allow_scoped):
    gc = variant['document']['generationContract']; verified = variant['verified']
    requested = specification.get('relations', []); limits = specification.get('space', {})
    reasons = []
    required_profile, profile_error = _native_profile(gc)
    if profile_error:
        reasons.append(profile_error)
    elif required_profile is not None:
        initial_profile = specification.get('initial_profile')
        if initial_profile is None:
            reasons.append('initial_profile_required:'+required_profile['id'])
        elif initial_profile != required_profile['id']:
            reasons.append('initial_profile_mismatch:'+initial_profile+'!='+required_profile['id'])
        if not set(required_profile['abilities']) <= available:
            reasons.append('initial_profile_abilities_unavailable:'+required_profile['id'])
    tested_initial = _tested_initial_abilities(variant, require_metadata_agreement=True)
    initial_permissions_known = sorted(available) in tested_initial
    for port in gc['ports']:
        if 'initialPermissionConditions' not in port: continue
        condition = port['initialPermissionConditions']
        exact = _ability_set(condition.get('availableAbilitiesExact')) if isinstance(condition, dict) else None
        if exact is None or list(exact) != sorted(available) or list(exact) not in tested_initial:
            initial_permissions_known = False
            break
    if ((any(port.get('permission') in ('INPUT', 'OUTPUT') for port in gc['ports'])
            or any('initialPermissionConditions' in port for port in gc['ports']))
            and not initial_permissions_known):
        reasons.append('initial_permission_ability_configuration_not_certified')
    if entry.get('humanReview') in HOLDS:
        reasons.append('human_design_hold_excluded_from_eligible_lookup')
    meta_path = variant['folder']/'migration.json'
    if meta_path.is_file() and core.read(meta_path).get('humanReview') in HOLDS:
        reasons.append('human_design_hold_excluded_from_eligible_lookup')
    if unsupported: reasons.append('unsupported_requirement_fields:'+','.join(unsupported))
    if limits.get('block_size', gc['foundation']['blockSize']) != gc['foundation']['blockSize']:
        reasons.append('block_size_mismatch')
    if specification.get('required_family'):
        actual_family = core.read(variant['folder']/'cases.json')['cases'][0].get('family')
        if actual_family != specification['required_family']: reasons.append('required_family_mismatch')
    if not allow_scoped and not verified.get('mapReady', False):
        reasons.append('unrestricted_Map_integration_not_certified')
    bounds = gc['space']['bounds']
    if bounds['w'] > limits.get('max_width', float('inf')) or bounds['h'] > limits.get('max_height', float('inf')):
        reasons.append('rectangle_exceeds_requested_size')
    by_port = {port['id']: port for port in gc['ports']}
    pairs = []
    for relation in requested:
        start = relation.get('from_port', relation.get('from'))
        end = relation.get('to_port', relation.get('to'))
        actual = next((r for r in gc['relations'] if r['from'] == start and r['to'] == end), None)
        if not actual or actual['status'] != 'path':
            reasons.append('unverified_requested_pair:'+str(start)+'->'+str(end))
        else:
            pairs.extend(actual['routeIds'])
        if start in by_port and end in by_port and (by_port[start].get('permission') == 'OUTPUT'
                                                   or by_port[end].get('permission') == 'INPUT'):
            reasons.append('requested_pair_violates_initial_port_permissions:'+str(start)+'->'+str(end))
    routes = [r for r in gc['routes'] if not requested or r['id'] in pairs]
    if not routes or any(not set(r['requiredAbilities']) <= available for r in routes):
        reasons.append('required_tested_abilities_unavailable')
    actual_configurations = _bound_ability_sets(variant)
    for route in routes:
        actual = actual_configurations.get(route['id'], set())
        if not actual:
            reasons.append('actual_route_ability_configuration_unknown:'+route['id'])
        elif any(not set(configuration) <= available for configuration in actual):
            reasons.append('actual_tested_route_abilities_unavailable:'+route['id'])
    connected = specification.get('connected_ports', list(by_port))
    requested_ports = specification.get('ports', {})
    physical_groups = _physical_port_groups(gc['ports'], connected)
    for group in physical_groups:
        if len(group['logicalNames']) > 1:
            reasons.append('coincident_logical_ports_need_alias_normalization:'+','.join(group['logicalNames']))
    if set(requested_ports)-{'count', 'required_normals'}:
        reasons.append('unsupported_port_constraints')
    if requested_ports.get('count', len(physical_groups)) != len(physical_groups):
        reasons.append('requested_physical_port_count_mismatch:'+str(requested_ports['count'])+'!='+str(len(physical_groups)))
    if 'required_normals' in requested_ports:
        normals = [tuple(p['normal']) for p in gc['ports'] if p['id'] in connected]
        if Counter(normals) != Counter(map(tuple, requested_ports['required_normals'])):
            reasons.append('requested_port_normal_multiset_mismatch')
    closed = set(by_port)-set(connected)
    if not set(connected) <= set(by_port): reasons.append('unknown_requested_port')
    if any(r['from'] not in connected or r['to'] not in connected for r in routes):
        reasons.append('requested_route_uses_unconnected_port')
    if closed and not any(set(profile['closedPorts']) == closed
            and profile['id'] in verified.get('certifiedClosureProfiles', [])
            and {r['id'] for r in routes} <= set(profile['routeIds']) for profile in gc['closures']):
        reasons.append('requested_partial_connection_closure_not_certified')
    if specification.get('mirror_x') and not verified.get('certifiedMirror', False):
        reasons.append('mirror_not_certified')
    return list(dict.fromkeys(reasons)), routes


def find(specification, *, allow_scoped=False):
    """Select base/whole certified profiles using static Module requirements.

    ``port_configuration_id`` may select one exact receipt ID, or ``base``.
    If omitted, normal/size/route constraints filter the base and all separately
    verified alternatives. ``contentVersion`` in each match is the *selected*
    version; ``baseContentVersion`` identifies its persistent base template.
    ``initial_profile`` is an exact frozen native profile ID, never a partial
    tuning object or a statement about resources consumed along a route.
    INPUT/OUTPUT Port permissions additionally require an exact currently tested
    available-ability set; adding a capability can invalidate a one-way claim.
    Route ability requirements conservatively include actual bound input
    capabilities, because an evidence witness with extra abilities does not
    certify a smaller configuration, regardless of a minimum-ability label.
    Port counts refer to distinct boundary-face anchors. Selecting coincident
    logical names as separate connections fails closed until alias semantics
    are explicitly normalized and rebound; an editor grouping is not a proof.
    """
    catalog = core.read(core.ACTIVE/'catalog.json')
    invalid = []
    if not isinstance(specification, dict):
        invalid.append({'field': 'request', 'reason': 'explicit specification object required'})
        specification = {}
    space = specification.get('space', {})
    if not isinstance(space, dict):
        invalid.append({'field': 'space', 'reason': 'known rectangle constraints required'}); space = {}
    for key in ('max_width', 'max_height', 'block_size'):
        if key in space and (not isinstance(space[key], (int, float)) or isinstance(space[key], bool)
                or not math.isfinite(space[key]) or space[key] <= 0):
            invalid.append({'field': 'space.'+key, 'reason': 'positive known numeric limit required; UNKNOWN is unresolved'})
    caps = specification.get('capabilities', {})
    abilities = specification.get('abilities', caps.get('allOf', []) if isinstance(caps, dict) else None)
    if not isinstance(abilities, list) or not all(isinstance(v, str) and v != 'UNKNOWN' for v in abilities):
        invalid.append({'field': 'abilities', 'reason': 'known ability list required'})
    relations = specification.get('relations', [])
    if not isinstance(relations, list) or any(not isinstance(r, dict) or not all(
            isinstance(r.get(k, r.get(a)), str) and r.get(k, r.get(a)) != 'UNKNOWN'
            for k, a in [('from_port', 'from'), ('to_port', 'to')]) for r in relations):
        invalid.append({'field': 'relations', 'reason': 'explicit directed Port IDs required'})
    ports = specification.get('ports', {})
    if not isinstance(ports, dict):
        invalid.append({'field': 'ports', 'reason': 'explicit Port constraints required'})
    elif 'count' in ports and (type(ports['count']) is not int or ports['count'] < 1):
        invalid.append({'field': 'ports.count', 'reason': 'positive known count required'})
    elif 'required_normals' in ports and (not isinstance(ports['required_normals'], list) or any(
            not isinstance(n, list) or any(type(v) not in (int, float) for v in n)
            or n not in ([-1, 0], [1, 0], [0, -1], [0, 1])
            for n in ports['required_normals'])):
        invalid.append({'field': 'ports.required_normals', 'reason': 'known cardinal normal vectors required'})
    if 'connected_ports' in specification and (not isinstance(specification['connected_ports'], list)
            or not all(isinstance(v, str) and v != 'UNKNOWN' for v in specification['connected_ports'])
            or len(set(specification['connected_ports'])) != len(specification['connected_ports'])):
        invalid.append({'field': 'connected_ports', 'reason': 'unique explicit Port ID subset required'})
    if 'mirror_x' in specification and type(specification['mirror_x']) is not bool:
        invalid.append({'field': 'mirror_x', 'reason': 'known orientation required'})
    selection = specification.get('port_configuration_id')
    if 'port_configuration_id' in specification and (not isinstance(selection, str) or not selection or selection == 'UNKNOWN'):
        invalid.append({'field': 'port_configuration_id', 'reason': 'known configuration ID or base required'})
    if 'initial_profile' in specification and (not isinstance(specification['initial_profile'], str)
            or not specification['initial_profile'] or specification['initial_profile'] == 'UNKNOWN'):
        invalid.append({'field': 'initial_profile', 'reason': 'exact known original native profile ID required; tuning objects and UNKNOWN are unresolved'})
    if invalid:
        return dict(status='unsatisfied', matches=[], conflicts=invalid,
            searched={'currentTemplates': len(catalog['modules']), 'source': 'persistent modules/catalog.json', 'additionalGeneration': False},
            negotiable=['provide explicit known constraints', 'perform offline adaptation for the unresolved requirement'])
    available = set(abilities)
    matches = []; conflicts = []; configuration_count = alternatives = 0
    unsupported = sorted(set(specification)-{'schema', 'id', 'abilities', 'capabilities', 'space',
        'relations', 'connected_ports', 'mirror_x', 'ports', 'required_family', 'port_configuration_id', 'initial_profile'})
    unsupported += ['space.'+key for key in space if key not in ('max_width', 'max_height', 'block_size')]
    for entry in catalog['modules']:
        folder = core.ACTIVE/entry['id']
        verified = core.validate(folder, require_certified=True)
        document_path = folder/'module.mapnote.json'
        doc = core.read(document_path); gc = doc['generationContract']
        if gc['contentVersion'] != entry['contentVersion'] or core.sha(document_path) != entry['contentSha256']:
            raise ValueError('current_catalog_module_identity_changed:'+entry['id'])
        # A design hold cannot become eligible through a different orientation.
        meta_path = folder/'migration.json'
        held = entry.get('humanReview') in HOLDS or (meta_path.is_file()
            and core.read(meta_path).get('humanReview') in HOLDS)
        if held:
            conflicts.append(dict(moduleId=entry['id'], portConfigurationId='base',
                                  reasons=['human_design_hold_excluded_from_eligible_lookup']))
            continue
        variants = _variants(entry, folder, doc, verified, selection)
        configuration_count += len(variants); alternatives += len(variants)-1
        selected = [variant for variant in variants if selection is None or variant['id'] == selection]
        if not selected:
            conflicts.append(dict(moduleId=entry['id'], portConfigurationId=selection,
                reasons=['port_configuration_not_certified_or_unknown:'+selection]))
        for variant in selected:
            reasons, routes = _reasons(specification, entry, variant, available, unsupported, allow_scoped)
            if reasons:
                conflict = dict(moduleId=entry['id'], portConfigurationId=variant['id'], reasons=reasons)
                groups = _physical_port_groups(variant['document']['generationContract']['ports'],
                    specification.get('connected_ports', [p['id'] for p in variant['document']['generationContract']['ports']]))
                aliases = [group for group in groups if len(group['logicalNames']) > 1]
                if aliases:
                    conflict.update(physicalPortCount=len(groups), coincidentPortGroups=aliases)
                conflicts.append(conflict)
            else:
                gc = variant['document']['generationContract']
                matches.append(dict(id=entry['id'], baseModuleId=entry['id'], baseContentVersion=entry['contentVersion'],
                    portConfigurationId=variant['id'], contentVersion=gc['contentVersion'],
                    file=variant['file'], scene=variant['scene'],
                    ports=[{**{key: port[key] for key in ('id', 'position', 'normal', 'face', 'surface', 'permission')},
                            **({'initialPermissionConditions': port['initialPermissionConditions']}
                               if 'initialPermissionConditions' in port else {})}
                           for port in gc['ports']],
                    certifiedRoutes=[r['id'] for r in routes], humanReview=entry['humanReview'],
                    requiredNativeProfile=_native_profile(gc)[0],
                    requiredTestedAbilities=_required_tested_abilities(variant, routes),
                    testedInitialAbilityConfigurations=_tested_initial_abilities(variant),
                    configurationReceipt=variant['receipt'],
                    scope='finite_module_integration' if allow_scoped else 'Map', unresolved=entry['unresolved']))
    return dict(status='matched' if matches else 'unsatisfied', matches=matches, conflicts=conflicts,
        searched=dict(currentTemplates=len(catalog['modules']), portConfigurations=configuration_count,
            certifiedAlternatives=alternatives, source='persistent modules/catalog.json',
            additionalGeneration=False, onlinePlayerStateSimulation=False),
        negotiable=[] if matches else ['choose a certified direction/connection profile',
            'enlarge the rectangle budget', 'perform offline certification for the missing feature'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('specification'); parser.add_argument('--allow-scoped', action='store_true'); args = parser.parse_args()
    print(json.dumps(find(core.read(args.specification), allow_scoped=args.allow_scoped), ensure_ascii=False, indent=2))
