"""Read-only capture-stage clock correction for the real original bell fixture."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import math
from pcg.migration import core, physics
from .new_ideas_v1 import OUT
from .reanalyze_ideas_extras_v1 import load, position

def main():
    root=core.REPO/'pcg/results/approved-ideas-orbit-toggle-cell-v1'
    item=core.read(root/'toggle-checks.json')['rows'][0]
    case,raw=load(root,item['evidence'])
    errors=[]
    for frame in raw['frames']:
        platform=frame['idea_loops'][0]
        clock=platform['clock']-(1/60 if platform['running'] else 0)
        errors.append(math.dist(platform['position'],position(case['moving_platforms'][0],clock)))
    check={**item['check'], 'originalCheck':item['check'], 'maximumPoseError':max(errors), 'clockAttribution':'Native controlled platform positions before its motion_clock increment; subtract one fixed tick only when running.', 'rawChanged':False}
    check['passed']=check['pausedClockDelta']==0 and max(errors)<.002 and [e['running']for e in check['toggles']]==[True,False,True,False] and check['hp']==5 and not check['worldReturns']
    assert check['passed']
    core.write(OUT/'loop-toggle-reanalyzed.json',dict(passed=True,check=check,rawEvidence=item['evidence'],source=physics.artifact(root/'toggle-checks.json'),observer=physics.artifact(__file__),simulationTrials=0))
if __name__=='__main__':main()
