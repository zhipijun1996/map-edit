"""Paths over the landing supports actually emitted by the full-map compiler."""
from collections import deque
import copy


def cell_path(start, goal, allowed):
    start, goal = tuple(start), tuple(goal)
    if start not in allowed or goal not in allowed:
        raise ValueError('path_endpoint_has_no_reserved_room_space')
    queue = deque([start]); previous = {start: None}
    while queue:
        here = queue.popleft()
        if here == goal:
            result = []
            while here is not None:
                result.append(here); here = previous[here]
            return result[::-1]
        for dx, dy in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            other = (here[0] + dx, here[1] + dy)
            if other in allowed and other not in previous:
                previous[other] = here; queue.append(other)
    raise ValueError('room_support_topology_disconnected')


def waypoints(cells, lower, upper):
    """Keep real stable endpoints; upward 128wu cells use a measured 64wu step.

    Downward targets are the next full-cell landing. A pilot may have to request
    drop_through again if it lands on the intermediate support first.
    """
    cells = [tuple(p) for p in cells]
    if not cells:
        raise ValueError('empty_navigation_path')
    result = [{'kind': 'walk', 'target': copy.deepcopy(lower[cells[0]])}]
    for a, b in zip(cells, cells[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if abs(dx) + abs(dy) != 1:
            raise ValueError('nonadjacent_support_navigation')
        if dy < 0:
            if a not in upper:
                raise ValueError('missing_real_intermediate_ascent_support')
            result.append({'kind': 'jump', 'target': copy.deepcopy(upper[a])})
            result.append({'kind': 'jump', 'target': copy.deepcopy(lower[b])})
        elif dx and b in upper and upper[b].get('support_width', 0) >= 80:
            # e27 can intercept the wide upper Dock, but e15 proves a forced
            # diagonal ascent to that upper Dock is not generally feasible.
            # Keep the exact lower destination. Only this specific real upper
            # support may be used transiently by the bounded input pilot.
            target = copy.deepcopy(lower[b])
            target['allowed_transit_support_indices'] = upper[b]['support_indices'][:]
            result.append({'kind': 'jump', 'target': target, 'hold_ticks': 4,
                           'routing_reason': 'exact_lower_target_with_explicit_wide_upper_transit'})
        else:
            leg = {'kind': 'drop' if dy > 0 else 'jump', 'target': copy.deepcopy(lower[b])}
            if dx:
                # The 128wu passage has only 52wu of head clearance above the
                # standing actor. A full-hold jump hits its corner wall before
                # entering the next cell (actual e33/e34 pressure failures).
                # Release through the original jump ability; never move actor.
                leg['hold_ticks'] = 4
            result.append(leg)
    return result


def join_waypoints(*sections):
    result = []
    for section in sections:
        for waypoint in section:
            if result and waypoint.get('kind') == 'walk' and waypoint['target']['position'] == result[-1]['target']['position'] and waypoint.get('assembly_phase')==result[-1].get('assembly_phase'):
                continue
            result.append(copy.deepcopy(waypoint))
    return result
