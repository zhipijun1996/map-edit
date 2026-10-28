"""Exact approved-design observers, delegating unchanged gameplay assertions.

The N08 anchor correction measures the approved moved A dock; all other legacy
assertions remain active. New N06 downward routes have no invented recoil rule.
"""
from pathlib import Path
import copy
from pcg.migration import physics

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DEPENDENCIES = [Path(__file__)]


def purpose(case, raw):
    spec = case['approved_implementation']
    original = __import__(spec['originalAuthor'].removesuffix('.py').replace('/', '.'), fromlist=['purpose'])
    if spec['reviewId'] == '01' and case['route_spec']['to_port'] in ('A', 'D'):
        reasons = []
        if not raw.get('ok'):
            reasons.append(raw.get('reason', 'not_stable'))
        if raw.get('hp') != 5 or raw.get('plains', {}).get('player_damage'):
            reasons.append('player_harm')
        if raw.get('returns'):
            reasons.append('world_reset')
        if any(raw.get(k, 0) for k in ('air_jumps', 'wall_jumps', 'grapples')):
            reasons.append('forbidden_ability')
        result = dict(ok=not reasons, reasons=reasons, causal={}, behavior={k:raw.get(k) for k in ('shots','jumps','ticks')})
    else:
        result = original.purpose(case, raw)
    result = copy.deepcopy(result)
    if spec['reviewId'] == '02':
        # Original N08 hard-coded A=(24,718). The approved crop moves its
        # physical dock to (152,718), without changing the 12-frame criterion.
        from pcg.prototype.creative_batches.batch30_blockn08.rules_v1 import visits
        if case['route_spec']['from_port'] == 'B' or case.get('fixture_kind') == 'same-world-A-B-A':
            dock = next(p['position'] for p in case['ports'] if p['id'] == 'A')
            after = result['causal']['B_first_stable'] if case.get('fixture_kind') == 'same-world-A-B-A' else -1
            observed = visits(raw.get('frames', []), *dock, after)
            result['causal']['legacy_A_anchor_result'] = dict(reasons=result['reasons'][:], frames=result['causal']['A_return_stable_frames'])
            result['causal']['approved_A_anchor'] = dict(position=dock, stable_frames=len(observed), required_frames=12)
            if len(observed) >= 12:
                result['reasons'] = [r for r in result['reasons'] if r != 'actual_A_return_stable_missing']
    rectangle = spec['rectangle']
    outside = [f['frame'] for f in raw.get('frames', [])
               if f['x']-12 < rectangle['x']-.05 or f['x']+12 > rectangle['x']+rectangle['w']+.05
               or f['y']-18 < rectangle['y']-.05 or f['y']+18 > rectangle['y']+rectangle['h']+.05]
    if outside:
        result['reasons'].append('actual_body_outside_approved_rectangle')
    result['causal']['approved_rectangle_outside_frames'] = outside
    result['ok'] = not result['reasons']
    return result


def original_sources(cases):
    authors = [__import__(c['approved_implementation']['originalAuthor'].removesuffix('.py').replace('/', '.'), fromlist=['purpose']) for c in cases]
    return physics.author_sources(authors)
