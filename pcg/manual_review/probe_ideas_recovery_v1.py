"""Additional preregistered same-world loops, enemy persistence and loop Cell trials.

These fixtures do not change a frozen Module, nominal control or holdout result.
"""
import copy
import math
import sys
from pcg.migration import core, physics
from .new_ideas_v1 import rows, label, OUT
from .finalize_ideas_v1 import folder_for
from .prepare_review045_v1 import at, end, axis
from pcg.prototype.workshop.rules import cmd


def build_loop(case, doc):
    c = physics.fresh(case, 'full-port-selfloop-v1')
    port = next(p for p in doc['generationContract']['ports'] if p['id'] == 'A')
    neighbor = physics.exterior_floor(c, port)
    x, y = port['stagingPosition']
    outside = [x, neighbor['floor'][1] - 18]
    c['spawn'] = outside
    c['control_plan'] = [axis(0), cmd('jump'), cmd('jump_release', 24)] + at(x, y) + copy.deepcopy(case['control_plan']) + [cmd('drop_through', 1)] + end(*outside)
    c['goal'] = [outside[0]-9, outside[1]-5, 18, 10]
    c['max_frames'] = 1600
    c['extra_fixture'] = dict(kind='full-port-selfloop', boundary=port['position'], neighbor=neighbor, body=[24, 36], order='outside-inside-outside', noIntermediateReset=True)
    return c


def build_depletion(case, doc):
    c = physics.fresh(case, 'persistent-enemy-depletion-v1')
    port = next(p for p in doc['generationContract']['ports'] if p['id'] == 'A')
    neighbor = physics.exterior_floor(c, port)
    x, y = port['stagingPosition']
    outside = [x, neighbor['floor'][1]-18]
    shoot = dict(op='shoot', direction=[-1,-1], aim_cell=dict(kind='enemy', id='enemy-1'), trigger=dict(after=40, state='grounded', timeout=300))
    c['control_plan'] = []
    for _ in range(3):
        c['control_plan'] += [copy.deepcopy(shoot)] + at(x, y)
    c['control_plan'] += [cmd('wait', 60), cmd('drop_through', 1)] + at(*outside) + [cmd('jump'), cmd('jump_release', 24)] + at(x, y) + copy.deepcopy(case['control_plan'])
    c['max_frames'] = 3200
    c['extra_fixture'] = dict(kind='persistent-enemy-depletion', neighbor=neighbor, noIntermediateReset=True, expected='real ground shots kill enemy-1; retreat/reenter preserves death; frozen ascent then cannot use that dead target', doesNotProveNoAlternativeRoute=True)
    return c


def observe_loop(c, r):
    boundary = c['extra_fixture']['boundary'][1]
    sequence = []
    crossing = []
    for f in [r['entry_snapshot']] + r['frames']:
        state = 'outside' if f['y']-18 >= boundary+.05 else 'inside' if f['y']+18 <= boundary-.05 else 'crossing'
        if state != 'crossing' and (not sequence or sequence[-1] != state):
            sequence.append(state)
        if state == 'crossing':
            crossing.append(dict(frame=f['frame'], aperture=abs(f['x']-192)+12 <= 32.05))
    clocks = [f['module_clock'] for f in r['frames']]
    stable = len({f['actor_epoch'] for f in r['frames']}) == 1 and r['returns'] == 0
    passed = r['ok'] and r['hp'] == 5 and stable and sequence == ['outside','inside','outside'] and all(v['aperture'] for v in crossing) and all(b > a for a,b in zip(clocks, clocks[1:]))
    return dict(passed=passed, sequence=sequence, crossing=crossing, sameActorAndWorld=stable, realJumps=r['jumps'], hp=r['hp'], reason=r['reason'])


def run(row):
    f = folder_for(row)
    eng, cases, _ = physics._engine(f, 'approved-ideas-'+label(row)+'-extra-recovery-v1', physics.FULL_PROTOCOL)
    doc = core.read(f/'module.mapnote.json')
    probes = []
    if label(row) != 'orbit':
        retry = next(c for c in cases if c['route_spec']['id'] == 'A-to-A-retry')
        ascent = next(c for c in cases if c['route_spec']['id'] == 'A-to-B')
        probes = [build_loop(retry, doc), build_depletion(ascent, doc)]
    else:
        for phase in [0, .25, .5, .75]:
            c = physics.fresh(cases[0], 'loop-cell-phase-'+str(phase))
            moving = c['moving_platforms'][0]
            moving['initial_phase'] = phase
            # This is an isolated Cell fixture: no bell, always running.
            c['latches'] = []
            p = moving['loop_points'][round(phase*16)]
            c['spawn'] = [p[0], p[1]-26]
            c['entry_port'] = list(c['spawn'])
            c['goal'] = [-5000, -5000, 1, 1]
            c['control_plan'] = [axis(0), cmd('wait', 485)]
            c['max_frames'] = 490
            c['extra_fixture'] = dict(kind='closed-loop-cell', initialPhase=phase, durationPeriods=2, doesNotQualifyPortRoute=True)
            probes.append(c)
    results = []
    for c, r, evidence in eng.run(probes, 'preregistered-additional-fixture'):
        kind = c['extra_fixture']['kind']
        if kind == 'full-port-selfloop':
            check = observe_loop(c, r)
        elif kind == 'persistent-enemy-depletion':
            enemies = [fr['plains']['enemies'][0] for fr in r['frames']]
            dead_at = next((i for i,e in enumerate(enemies) if e['dead']), None)
            check = dict(realDeathObserved=dead_at is not None, staysDead=dead_at is not None and all(e['dead'] and e['hp']==0 for e in enemies[dead_at:]), actorEpochs=sorted({fr['actor_epoch'] for fr in r['frames']}), worldReturns=r['returns'], hp=r['hp'], originalAscentCompleted=r['ok'], reason=r['reason'], alternativeRoute='UNKNOWN', respawnAdded=False)
        else:
            poses = [v for fr in r['frames'] for v in fr.get('idea_loops', [])]
            check = dict(maximumPoseError=max(v['expected_error'] for v in poses), maximumRotation=max(abs(v['rotation']) for v in poses), frames=len(r['frames']), actualSupportFrames=sum(fr['support_id']=='carrier' for fr in r['frames']), hp=r['hp'], clocks=[poses[0]['clock'], poses[-1]['clock']], noIntermediateReset=r['returns']==0)
            check['passed'] = check['maximumPoseError'] < .002 and check['maximumRotation'] == 0 and check['frames'] >= 480 and check['hp'] == 5
        results.append(dict(caseId=c['id'], fixture=c['extra_fixture'], check=check, evidence=evidence))
        print(label(row), kind, check, flush=True)
    core.write(eng.out/'extra-checks.json', dict(rows=results, simulationTrials=len(probes), independentHoldout=False, frozenControlsUnchanged=True))

if __name__ == '__main__':
    for row in rows():
        if label(row) in sys.argv[1:]:
            run(row)
