"""Lower every room and edge of a preserved R2 map into real navigation Cells.

This is an unvalidated navigation candidate, not a completed challenge library.
Boundary terrain only separates spaces. Landing supports and optional original
thorn Cells are authored explicitly for demand ports and actual pilot testing.
No old Module physical evidence is inherited or silently upgraded.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re

from .paths import cell_path, waypoints

REPO = Path(__file__).resolve().parents[3]


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def _body_size():
    path = REPO / 'pcg/prototype/godot/scenes/player/player.tscn'
    text = path.read_text()
    found = re.search(r'size = Vector2\(([^,]+), ([^)]+)\)', text)
    if not found:
        raise ValueError('cannot_read_actual_player_body')
    return [float(v) for v in found.groups()]


def _intervals(values):
    values = sorted(set(values))
    if not values:
        return []
    out = []; start = end = values[0]
    for value in values[1:]:
        if value == end + 1:
            end = value
        else:
            out.append((start, end)); start = end = value
    out.append((start, end))
    return out


def _shell(free, width, height, thickness):
    bands = defaultdict(list)
    for x, y in sorted(free):
        for side, dx, dy in [('top', 0, -1), ('bottom', 0, 1), ('left', -1, 0), ('right', 1, 0)]:
            if (x + dx, y + dy) not in free:
                bands[(side, y if dx == 0 else x)].append(x if dx == 0 else y)
    result = []; bottom_owner = {}
    for (side, fixed), values in sorted(bands.items()):
        for low, high in _intervals(values):
            if side in ('top', 'bottom'):
                rect = [low * width, fixed * height + (height - thickness if side == 'bottom' else 0),
                        (high - low + 1) * width, thickness]
            else:
                rect = [fixed * width + (width - thickness if side == 'right' else 0),
                        low * height, thickness, (high - low + 1) * height]
            index = len(result); result.append(rect)
            if side == 'bottom':
                for x in range(low, high + 1):
                    bottom_owner[(x, fixed)] = index
    return result, bottom_owner


def _gate(edge, cells, room_cells, width, height, platforms, thorns, body_half_height):
    if edge['switch'] is None and edge['bidirectional']:
        return None
    # Interior corridor cell faces are real openings between shell boundaries.
    options = [(a, b) for a, b in zip(cells, cells[1:]) if a not in room_cells and b not in room_cells]
    if not options:
        raise ValueError('no_internal_corridor_aperture_for_gate/' + edge['id'])
    def overlap(a, b):
        return a[0] < b[0] + b[2] - 1e-6 and b[0] < a[0] + a[2] - 1e-6 and a[1] < b[1] + b[3] - 1e-6 and b[1] < a[1] + a[3] - 1e-6
    hazards = []
    for thorn in thorns:
        host = platforms[thorn['platform_index']]
        hazards.append([host[0] + thorn['start_offset'], host[1] - thorn['depth'], thorn['length'], thorn['depth']])
    chosen = None
    for a, b in sorted(options, key=lambda p: abs(options.index(p) - (len(options) - 1) / 2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx:
            rectangle = [max(a[0], b[0]) * width - 5, a[1] * height + 8, 10, height - 16]
        else:
            rectangle = [a[0] * width + 8, max(a[1], b[1]) * height - body_half_height - 5, width - 16, 10]
        if not any(overlap(rectangle, p) for p in platforms + hazards):
            chosen = (a, b, rectangle, dx, dy); break
    if chosen is None:
        raise ValueError('gate_aperture_overlaps_support_or_hazard/' + edge['id'])
    a, b, rectangle, dx, dy = chosen
    x, y, w, h = rectangle
    return {'id': 'gate/' + edge['id'], 'edge_id': edge['id'], 'from': edge['from'], 'to': edge['to'],
            'x': x, 'y': y, 'w': w, 'h': h, 'direction': [dx, dy],
            'bounds': [x, y, w, h],
            'switch': edge['switch'], 'one_way': not edge['bidirectional'],
            'mechanism_status': 'proposed_actual_gate_consumer_required',
            'semantic_note': 'Direction gate; not assumed to be a gravity drop.'}


def compile_map(region='plains', seed='0', scale=(96, 128), static_gap_hazards=False, source_path=None):
    width, height = scale
    if (width, height) != (96, 128):
        raise ValueError('first_navigation_template_requires_96x128_world_units')
    source_path = Path(source_path or REPO / 'experiments/l4-mapgen/results/region-network-v2/runs.json')
    raw = source_path.read_bytes(); data = json.loads(raw)
    selected = next((r for r in data['runs'] if r['region'] == region and str(r['seed']) == str(seed)), None)
    if selected is None or not selected['layout'].get('ok'):
        raise ValueError('missing_successful_source_layout')
    graph = copy.deepcopy(selected['exploration_graph']); layout = selected['layout']
    if region != 'plains' or str(seed) != '0' or len(graph['nodes']) != 27 or len(graph['edges']) != 39:
        raise ValueError('first_consumer_is_frozen_full_plains_seed0_not_a_general_generator')
    body_width, body_height = _body_size()
    if body_width != 24 or body_height != 36:
        raise ValueError('navigation_template_body_requires_recalibration')
    room = {r['node']: {tuple(c) for c in r['cells']} for r in layout['rooms']}
    all_room_cells = set().union(*room.values())
    centers = {}
    for key, cells in room.items():
        cx = sum(x for x, y in cells) / len(cells); cy = sum(y for x, y in cells) / len(cells)
        centers[key] = min(cells, key=lambda p: ((p[0] - cx) ** 2 + (p[1] - cy) ** 2, p))
    routes = {}; port_cells = defaultdict(dict); normals = defaultdict(dict)
    needed = set(centers.values()); free = set(all_room_cells)
    for corridor in layout['corridors']:
        if len(corridor['edges']) != 1:
            raise ValueError('parallel_edge_geometry_requires_explicit_adapter')
        edge_id = corridor['edges'][0]
        edge = next(e for e in graph['edges'] if e['id'] == edge_id)
        points = [tuple(p) for p in corridor['points']]
        from_port, to_port = corridor['from_port'], corridor['to_port']
        if corridor['from'] != edge['from']:
            points.reverse(); from_port, to_port = to_port, from_port
        routes[edge_id] = points; free.update(points); needed.update(points)
        for node, point, port in [(edge['from'], points[0], from_port), (edge['to'], points[-1], to_port)]:
            if point not in room[node]:
                raise ValueError('source_port_not_in_room')
            port_cells[node][edge_id] = point; normals[node][edge_id] = port['direction'][:]
            needed.update(cell_path(centers[node], point, room[node]))
    shell, bottom_owner = _shell(free, width, height, 8)
    platforms = shell[:]; one_way = []; lower = {}; upper = {}; support_cells = {}
    pad_thickness = 8
    port_support_cells = {cell for ports in port_cells.values() for cell in ports.values()}
    def target(cell, surface_offset, suffix):
        x, y = cell; surface = y * height + surface_offset
        # Preserve body-wide landing margin after real corner-wall contact.
        # e30 reverse missed the 32wu receiver by <2wu after a head contact;
        # this is a new geometry version and needs complete route revalidation.
        pad_width = 80 if cell in port_support_cells else 48
        index = len(platforms)
        platforms.append([x * width + (width - pad_width) / 2, surface, pad_width, pad_thickness])
        one_way.append(index); support_cells[index] = list(cell)
        return {'id': 'landing/%s/%s/%s' % (x, y, suffix),
                'position': [x * width + width / 2, surface - body_height / 2],
                'region': [x * width + width / 2 - 12, surface - body_height / 2 - 5, 24, 10],
                'support_indices': [index], 'support_width': pad_width, 'grounded': True,
                'validation_status': 'unverified_new_generated_support'}
    for cell in sorted(needed):
        lower[cell] = target(cell, 96, 'lower')
        if (cell[0], cell[1] - 1) in needed:
            upper[cell] = target(cell, 32, 'upper')
    thorns = []
    if static_gap_hazards:
        corridor_only = free - all_room_cells
        for cell in sorted(corridor_only):
            if cell not in bottom_owner:
                continue
            host_index = bottom_owner[cell]; host = platforms[host_index]
            for ordinal, (offset, length) in enumerate([(8, 24), (64, 24)]):
                thorns.append({'surface_id': 'gap-pressure/%s/%s/%s' % (*cell, ordinal),
                               'platform_index': host_index, 'face': 'top',
                               'start_offset': cell[0] * width + offset - host[0],
                               'length': length, 'depth': 12, 'damage': 1, 'contact_interval': .7})
    nodes = {}
    for node in graph['nodes']:
        key = node['id']; ports = {}; outbound = {}; inbound = {}
        for edge_id, cell in sorted(port_cells[key].items()):
            # Corner rooms can expose two different physical apertures from
            # one landing. Give horizontal apertures separate stable docking
            # positions on the explicitly widened support, not duplicate IDs
            # at one position pretending to be extra physical connections.
            dock = copy.deepcopy(lower[cell])
            dock['position'][0] += normals[key][edge_id][0] * 24
            dock['region'][0] = dock['position'][0] - 8
            dock['region'][2] = 16
            cx, cy = cell; nx, ny = normals[key][edge_id]
            aperture = ([cx * width - 5 + (width if nx > 0 else 0), cy * height + 8, 10, height - 16]
                        if nx else [cx * width + 8, cy * height - 5 + (height if ny > 0 else 0), width - 16, 10])
            ports[edge_id] = {'id': key + '/' + edge_id, 'edge_id': edge_id,
                'position': dock['position'][:], 'normal': normals[key][edge_id], 'aperture_region': aperture,
                'target': dock, 'support_indices': lower[cell]['support_indices'][:],
                'status': 'demand_generated_candidate_not_existing_verified_port'}
            path = cell_path(centers[key], cell, room[key])
            outbound[edge_id] = waypoints(path, lower, upper) + [{'kind': 'walk', 'target': copy.deepcopy(dock)}]
            inbound[edge_id] = [{'kind': 'walk', 'target': copy.deepcopy(dock)}] + waypoints(path[::-1], lower, upper)
        nodes[key] = {'id': key, 'role': node['role'], 'label': node.get('label', key),
                      'center': copy.deepcopy(lower[centers[key]]), 'ports': ports,
                      'center_to_port': outbound, 'port_to_center': inbound,
                      'grants': node.get('grants', []), 'opens': node.get('opens', []),
                      'reward': node.get('reward', 0), 'room_cells': [list(p) for p in sorted(room[key])],
                      'macro_kind': 'demand_generated_landing_junction', 'physics_status': 'unverified'}
    edges = {}; gates = []
    def dock_endpoint(waypoint, dock):
        allowed = waypoint['target'].get('allowed_transit_support_indices')
        waypoint['target'] = copy.deepcopy(dock)
        if allowed:
            waypoint['target']['allowed_transit_support_indices'] = allowed[:]
    for edge in graph['edges']:
        key = edge['id']; points = routes[key]
        gate = _gate(edge, points, all_room_cells, width, height, platforms, thorns, body_height / 2)
        if gate:
            gates.append(gate)
        forward = waypoints(points, lower, upper)
        dock_endpoint(forward[0], nodes[edge['from']]['ports'][key]['target'])
        dock_endpoint(forward[-1], nodes[edge['to']]['ports'][key]['target'])
        reverse = waypoints(points[::-1], lower, upper) if edge['bidirectional'] else []
        if reverse:
            dock_endpoint(reverse[0], nodes[edge['to']]['ports'][key]['target'])
            dock_endpoint(reverse[-1], nodes[edge['from']]['ports'][key]['target'])
        edges[key] = {**copy.deepcopy(edge), 'from_port': nodes[edge['from']]['ports'][key]['id'],
            'to_port': nodes[edge['to']]['ports'][key]['id'],
            'forward_waypoints': forward,
            'reverse_waypoints': reverse,
            'gate_ids': [gate['id']] if gate else [],
            'planning_cells': [list(p) for p in points],
            'macro_kind': 'navigation_cell_chain_pending_action_module_enrichment',
            'physics_status': 'unverified'}
    xs = [r[0] for r in platforms] + [r[0] + r[2] for r in platforms]
    ys = [r[1] for r in platforms] + [r[1] + r[3] for r in platforms]
    bounds = [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]
    spawn = nodes[graph['entry']]['center']['position'][:]
    goal = nodes[graph['goal']]['center']['region'][:]
    case = {'id': 'r2-full-plains-seed0-navigation', 'family': 'r2_full_navigation_candidate',
            'capabilities': ['move', 'jump', 'shot_recoil'], 'platforms': platforms,
            'one_way_platform_indices': one_way, 'wall_platform_indices': [],
            'spawn': spawn, 'entry_port': spawn[:],
            'exit_port': nodes[graph['goal']]['center']['position'][:],
            'goal': goal, 'world_bounds': bounds, 'control_plan': [], 'max_frames': 3600,
            'trace_all': False, 'hazards': [], 'thorns': thorns, 'saws': [],
            'moving_platforms': [], 'hooks': [], 'latches': [], 'enemies': [],
            'ports': [], 'content_status': 'navigation_candidate_only_not_final_module_quality'}
    counts = Counter(w['kind'] for e in edges.values() for w in e['forward_waypoints'])
    coverage = {'source_nodes': len(graph['nodes']), 'realized_node_candidates': len(nodes),
                'source_edges': len(graph['edges']), 'realized_edge_candidates': len(edges),
                'missing_nodes': sorted(set(n['id'] for n in graph['nodes']) - nodes.keys()),
                'missing_edges': sorted(set(e['id'] for e in graph['edges']) - edges.keys()),
                'junction_macros': len(nodes), 'edge_macros': len(edges),
                'distinct_existing_challenge_modules_inserted': 0,
                'navigation_waypoint_kinds': dict(counts), 'declared_port_positions': sum(len(n['ports']) for n in nodes.values()),
                'new_support_cells': len(one_way), 'boundary_shell_rectangles': len(shell),
                'static_gap_hazards': bool(static_gap_hazards),
                'independent_physics': 'unverified', 'action_necessity': 'unverified',
                'content_quality': 'navigation scaffold; must not be promoted as finished full-map content'}
    source = {'path': str(source_path), 'file_sha256': hashlib.sha256(raw).hexdigest(),
              'map_id': selected['id'], 'map_digest': selected.get('deterministic_digest'),
              'graph_sha256': _digest(graph), 'scale': list(scale), 'body_size': [body_width, body_height],
              'compiler_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return {'case': case, 'nodes': nodes, 'edges': edges, 'coverage': coverage,
            'gate_specs': gates, 'source': source, 'exploration_graph': graph,
            'support_cells': support_cells, 'lower_targets': {str(k): v for k, v in lower.items()},
            'status': 'unverified_navigation_candidate'}
