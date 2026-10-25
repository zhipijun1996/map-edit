"""Miss a moving landing, recover on authored ground, then retry continuously."""
import argparse,copy,json
from .rules import candidates,cmd,ground,wait_x
from .engine import ROOT,WorkshopEngine
from .experiments import write
from .evaluate import instantiate

def cases():
    out=[]
    for v in range(2):
        c=candidates('chase-landing',v)[0];retry=copy.deepcopy(c['control_plan'])
        c['control_plan']=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',10,direction=[-1,0]),wait_x(500),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=-1),wait_x(450,-1),cmd('axis',value=0),ground(),cmd('jump'),cmd('jump_release',20),cmd('shoot',4,direction=[.6,.8]),cmd('axis',9,value=-1),wait_x(340,-1),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[1,0]),wait_x(80,-1),cmd('axis',value=0),ground(),cmd('wait',20)]+retry
        c.update(id=c['id']+'-miss-recover-retry',max_frames=1600)
        out.append(c)
    return out

def run(name,noise=False,holdout=False):
    engine=WorkshopEngine(ROOT/'results'/name);cs=[]
    for c in cases():
        cs.append(c)
        if noise or holdout:
            for i in range(12):cs.append(instantiate(c,261025941 if holdout else 26102501,'mild',i))
    write(engine.out/'protocol.json',dict(calibration=not holdout,holdout_seed=261025941 if holdout else None,maximum_calibration_revisions=4,no_world_reset=True))
    write(engine.out/'cases.json',dict(cases=cs));rows=[]
    for c,r,e in engine.run(cs,'recovery-calibration'):
        frames=r.get('frames',[]);bottom=any(f['grounded']and abs(f['y']-632)<1 for f in frames)
        revisit=[f['frame']for f in frames if f['grounded']and abs(f['x']-80)<12 and abs(f['y']-420)<1 and f['frame']>100]
        first_start=next((e['frame']for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'),None)
        row=dict(id=c['id'],ok=r['ok']and bottom and bool(revisit)and first_start is not None and first_start>revisit[0]and not r.get('returns'),
            safe_bottom_visited=bottom,entry_revisited=bool(revisit),first_carrier_start=first_start,reason=r['reason'],evidence=e)
        rows.append(row);print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(all_passed=all(r['ok']for r in rows),rows=rows,scope='same actor and world; deliberately wrong first shot misses carrier; authored safe ground; no teleport/resource writes'))
    return engine.out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--noise-calibration',action='store_true');p.add_argument('--holdout',action='store_true');a=p.parse_args();run(a.name,a.noise_calibration,a.holdout)
