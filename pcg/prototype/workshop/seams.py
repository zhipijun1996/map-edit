"""Port collision/continuity specimens for B, not Module placement or Mapgen.

Split an already-authored receiver at its port; union geometry is identical.
This tests a collider seam, not generic production assembly admission.
"""
import argparse,copy,json
from .rules import candidates,cmd,ground,wait_x,settle
from .transitions import arrival
from .engine import ROOT,WorkshopEngine
from .experiments import write
from .evaluate import instantiate
from ..factory.core.quality import digest

def specimens():
    out=[]
    for v in range(2):
        c=candidates('thorn-slot',v)[0];p=c['platforms'][1];split=c['exit_port'][0];old=p[:]
        c['platforms'][1]=[p[0],p[1],split-p[0],p[3]]
        c['platforms'].append([split,p[1],p[0]+p[2]-split,p[3]])
        c['control_plan']=arrival(c)+[cmd('axis',value=1),wait_x(split+45),cmd('axis',value=0),ground(),cmd('wait',20),cmd('axis',value=-1),wait_x(old[0]+40,-1),cmd('jump'),cmd('jump_release',6),cmd('shoot',10,direction=[.9886859966642595,.15]),settle(80,6)]
        # Original Definition requires the complete port body on one collider.
        # Place its fixture marker on the right slab, still cross the real seam.
        c['exit_port']=[split+40,c['exit_port'][1]]
        c.update(id='thorn-port-seam-'+str(v),goal=[55,416,50,8],max_frames=1200,seam_specimen=dict(x=split,original_receiver=old,split_indices=[1,len(c['platforms'])-1],added_solid_area=0,synthetic_connector=False,coverage='concrete collider split, not two-Module Map assembly',contentVersion='sha256:'+digest(c['platforms'])))
        out.append(c)
    return out

def run(name):
    engine=WorkshopEngine(ROOT/'results'/name);cs=[]
    for base in specimens():
        cs.append(base)
        for i in range(12):cs.append(instantiate(base,261025939,'mild',i))
    write(engine.out/'cases.json',dict(cases=cs));rows=[]
    for c,r,e in engine.run(cs,'seam-holdout'):
        sx=c['seam_specimen']['x'];frames=r.get('frames',[])
        forward=any(a['x']<sx<=b['x']and b['grounded']for a,b in zip(frames,frames[1:]))
        backward=any(a['x']>sx>=b['x']and b['grounded']for a,b in zip(frames,frames[1:]))
        row=dict(id=c['id'],ok=r['ok']and forward and backward and not r.get('returns'),forward=forward,backward=backward,evidence=e,reason=r['reason'])
        rows.append(row);print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(all_passed=all(r['ok']for r in rows),rows=rows,scope='original receiver split only; no added terrain/resources/teleport; exact specimen, not arbitrary Module seam'))
    return engine.out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
