"""Solve a gate budget from actual calibration projectile/body timings."""
import argparse,json,math
from .engine import ROOT
from .experiments import write
from ..factory.core.engine import file_sha

def solve(source='workshop-calibration-noise-v2'):
    path=ROOT/'results'/source/'evaluations.json';entries=json.loads(path.read_text());rows=[]
    for e in entries:
        if e['case']['family']!='timed-cache':continue
        measured=[r['purpose']['causal']for r in e['rows']if r['purpose']['ok']]
        flight=[m['projectile_flight_ticks']for m in measured];cross=[m['hit_to_body_clear_ticks']for m in measured]
        # Six simulation ticks (0.10 s) of operating margin, then round upwards
        # to 0.05 s. Timer starts on actual projectile commit, not shot release.
        ticks=math.ceil((max(cross)+6)/3)*3
        rows.append(dict(interface=e['case']['id'],measured_policies=len(measured),projectile_flight_ticks=[min(flight),max(flight)],
            hit_to_full_24x36_body_clear_ticks=[min(cross),max(cross)],margin_ticks=6,round_up_ticks=3,solved_open_seconds=ticks/60,
            source=str(path.relative_to(ROOT)),source_sha256=file_sha(path),safety_close='unchanged original ShotLatch; not used as timing margin',scope='calibration samples only, not all possible policies'))
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();write(ROOT/'results'/a.out,dict(schema='pcg/gate-window-solution/v1',rows=solve()))
