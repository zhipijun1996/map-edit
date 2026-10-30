"""Read-only correction of observer types and capture-stage clock attribution.

Original additional-fixture failures and raw bytes remain immutable.
"""
import copy
import gzip
import json
import math
from pcg.migration import core, physics
from .new_ideas_v1 import OUT

def load(root, evidence):
    case = core.read(root/'physics'/(evidence['batch']+'.input.json'))['cases'][evidence['index']]
    raw = json.loads(gzip.decompress((root/evidence['output']).read_bytes()))['results'][evidence['index']]
    return case, raw

def position(platform, clock):
    points = platform['loop_points']
    lengths = [math.dist(a,b) for a,b in zip(points,points[1:])]
    distance = ((clock/platform['loop_period'] + platform['initial_phase']) % 1) * sum(lengths)
    for i, length in enumerate(lengths):
        if distance <= length or i == len(lengths)-1:
            t=distance/length
            return [a+(b-a)*t for a,b in zip(points[i],points[i+1])]
        distance -= length

def main():
    results=[]
    for name in ['enemies-2','enemies-3','orbit']:
        version = 'v2' if name == 'orbit' else 'v1'
        root=core.REPO/('pcg/results/approved-ideas-'+name+'-extra-recovery-'+version)
        old=core.read(root/'extra-checks.json')
        for item in old['rows']:
            c,r=load(root,item['evidence'])
            check=copy.deepcopy(item['check'])
            if item['fixture']['kind']=='full-port-selfloop':
                stable=len({f['actor_epoch']for f in r['frames']})==1 and not r['returns']
                check.update(sameActorAndWorld=stable)
                check['passed'] = bool(r['ok'] and r['hp']==5 and stable and check['sequence']==['outside','inside','outside'] and all(v['aperture']for v in check['crossing']) and all(b['module_clock']>a['module_clock']for a,b in zip(r['frames'],r['frames'][1:])))
                assert check['passed']
            elif name=='orbit':
                errors=[];relative=[]
                for f in r['frames']:
                    actual=f['idea_loops'][0]['position']
                    # Native free-running carrier is positioned before Module.clock
                    # increments for this captured frame. Bell-controlled carriers
                    # use their own motion_clock and need no such attribution.
                    expected=position(c['moving_platforms'][0],f['module_clock']-1/60)
                    errors.append(math.dist(actual,expected))
                    relative.append([f['x']-actual[0],f['y']-actual[1]])
                variation=max(math.dist(a,relative[0])for a in relative)
                check.update(maximumPoseError=max(errors), nativePoseClock='captured module_clock minus one original fixed physics tick, free-running only', elapsedClock=r['frames'][-1]['module_clock']-r['frames'][0]['module_clock'], maximumCarryOffsetVariation=variation, noIntermediateReset=not r['returns'])
                check['passed']=bool(max(errors)<.002 and variation<.1 and check['elapsedClock']>=8 and r['hp']==5 and not r['returns'] and all(f['support_id']=='carrier'for f in r['frames']))
                assert check['passed'], check
            else:
                assert check['realDeathObserved'] and check['staysDead'] and check['actorEpochs']==[1] and not check['worldReturns']
            results.append(dict(name=name,fixture=item['fixture'],check=check,originalCheck=item['check'],rawEvidence=item['evidence'],source=physics.artifact(root/'extra-checks.json')))
    core.write(OUT/'extra-fixtures-reanalyzed.json',dict(passed=True, simulationTrials=0, originalRawUnchanged=True, noNewHoldout=True, rows=results))
    print('EXTRA_FIXTURES_READONLY_PASS',len(results))
if __name__=='__main__':main()
