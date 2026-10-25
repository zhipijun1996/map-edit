"""Continuous original-state return/recovery fixtures; never a Map generator."""
import argparse,copy,json
from .rules import candidates,cmd,ground,wait_x,settle
from .engine import ROOT,WorkshopEngine
from .evaluate import instantiate
from .experiments import write
from ..factory.core.quality import digest

def arrival(base):
    # Do not leave the old controller's persistent settle enabled at a junction.
    # Continue actual movement until the declared port, stop, and really land.
    x=base['exit_port'][0]
    return copy.deepcopy(base['control_plan'][:-1])+[wait_x(x-3),cmd('axis',value=0),ground(),cmd('wait',20)]

def fixtures():
    out=[]
    for variant in range(2):
        c=candidates('thorn-slot',variant)[0];left=c['platforms'][1][0]
        c['control_plan']=arrival(c)+[cmd('axis',value=-1),wait_x(left+40,-1),cmd('jump'),cmd('jump_release',6),cmd('shoot',10,direction=[.9886859966642595,.15]),settle(80,6)]
        c.update(id=c['id']+'-roundtrip',goal=[55,416,50,8],transition_kind='thorn-roundtrip',max_frames=1000)
        out.append(c)
        c=candidates('chase-landing',variant)[0]
        c['control_plan']=arrival(c)+[cmd('axis',value=-1),wait_x(575+variant*35,-1),ground(),wait_x(470+variant*10,-1),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,direction=[.9886859966642595,.15]),settle(80,6)]
        c.update(id=c['id']+'-roundtrip',goal=[55,416,50,8],transition_kind='carrier-roundtrip',max_frames=1200)
        out.append(c)
        c=candidates('timed-cache',variant)[0];gate_x=c['latches'][0]['gate'][0]
        c['control_plan']=arrival(c)+[cmd('wait',90),cmd('axis',value=-1),wait_x(gate_x+60,-1),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),cmd('wait',6),cmd('axis',value=-1),wait_x(290,-1),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',4,direction=[.5,.8660254037844386]),cmd('axis',9,value=-1),settle(80,6)]
        c.update(id=c['id']+'-delayed-return',goal=[55,416,50,8],transition_kind='timed-delayed-return',max_frames=1400)
        out.append(c)
        c=candidates('one-shot-two-routes',variant)[1];high=c['exit_port'][:];low=c['ports'][1]['position']
        c['control_plan']=arrival(c)+[cmd('axis',value=1),wait_x(high[0]+100),settle(low[0])]
        c.update(id=c['id']+'-rejoin',goal=[low[0]-25,low[1]-4,50,8],transition_kind='fork-high-rejoin',max_frames=1000)
        out.append(c)
    return out

def check(c,r):
    frames=r.get('frames',[]);kind=c['transition_kind'];reasons=[]
    if not r['ok']or r.get('hp')!=5:reasons.append(r['reason'])
    if r.get('returns'):reasons.append('unexpected_return_or_teleport')
    if r.get('workshop',{}).get('coins',0)!=c['reward_sites'][0]['amount']:reasons.append('reward_lost_or_not_claimed')
    visited=any(f['grounded']and abs(f['x']-c['exit_port'][0])<30 and abs(f['y']-c['exit_port'][1])<1 for f in frames)
    if not visited:reasons.append('did_not_actually_visit_outbound_port')
    causal={}
    if kind=='timed-delayed-return':
        states=[(f,next((b for b in f.get('plains',{}).get('bells',[])if b['id']=='short-bell'),{}))for f in frames]
        closed=[f['frame']for f,b in states if b.get('open_count')==1 and not b.get('open',True)and f['x']>c['latches'][0]['gate'][0]+36]
        reopened=[f['frame']for f,b in states if closed and f['frame']>closed[0]and b.get('open_count',0)>=2]
        causal=dict(actual_closed_inside=bool(closed),actual_reopened_after_close=bool(reopened))
        if not closed or not reopened:reasons.append('actual_close_reopen_not_demonstrated')
    if kind=='fork-high-rejoin':
        take=max((f['frame']for f in frames if f['grounded']and abs(f['y']-c['exit_port'][1])<1),default=-1)
        shots_after=[f['frame']for f in frames if f['frame']>take and any(e['type']=='shot'for e in f.get('accepted',[]))]
        causal=dict(reward_route_shots=r.get('shots'),shots_after_high_port=shots_after,changed_relation='outbound ascend using recoil; rejoin descend without another shot')
        if shots_after:reasons.append('rejoin_not_a_distinct_drop_relation')
    return dict(ok=not reasons,reasons=reasons,causal=causal,visited_outbound_port=visited)

def run(name,holdout=False,noise_calibration=False,families=None):
    engine=WorkshopEngine(ROOT/'results'/name);bases=[c for c in fixtures()if not families or c['family']in families];cs=[]
    for c in bases:
        cs.append(c)
        if holdout or noise_calibration:
            for i in range(12):
                v=instantiate(c,261025940 if holdout else 26102501,'mild',i);v['transition_kind']=c['transition_kind'];cs.append(v)
    write(engine.out/'protocol.json',dict(version=2,prior_holdout='workshop-transitions-holdout-v1 failed 17/104; never relabeled as pass',scope='continuous same actor/resources/mechanisms/reward ledger; no scene reset between legs',holdout=holdout,seed=261025940 if holdout else 26102501,calibration_revisions_maximum=4,maximum_cases=len(cs),whole_map=False))
    write(engine.out/'cases.json',dict(cases=cs));rows=[]
    for c,r,e in engine.run(cs,'transition-holdout'if holdout else'transition-calibration'):
        p=check(c,r);row=dict(id=c['id'],ok=p['ok'],check=p,reason=r['reason'],evidence=e,last=[r['frames'][-1][k]for k in ['x','y']]if r.get('frames')else None)
        rows.append(row);write(engine.out/'rows.json',rows)
        print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(all_passed=all(r['ok']for r in rows),rows=rows,production_admitted=False,whole_map=False))
    return engine.out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--holdout',action='store_true');p.add_argument('--noise-calibration',action='store_true');p.add_argument('--families',nargs='+');a=p.parse_args();run(a.name,a.holdout,a.noise_calibration,a.families)
