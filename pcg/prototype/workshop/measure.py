"""Small real-motion probes, retained as calibration and never holdout."""
import argparse,json,math
from .engine import WorkshopEngine,ROOT
from ..plains.synthesis import command as cmd,CAPS

def base(name):
    return dict(id=name,family=name,capabilities=CAPS[:],platforms=[[-160,438,400,100]],
        spawn=[80,420],entry_port=[80,420],exit_port=[120,420],goal=[100000,0,100,100],
        world_bounds=[-1200,-1000,4000,2400],one_way_platform_indices=[],hazards=[],thorns=[],
        saws=[],moving_platforms=[],hooks=[],latches=[],enemies=[],reward_sites=[],
        max_frames=130,trace_all=True)

def probes():
    out=[]
    for hold,shot,dy in [(8,12,0),(8,16,.15),(12,20,.25),(12,24,.35),(12,24,.5),(12,24,.7)]:
        c=base(f'edge-{hold}-{shot}-{dy}')
        c['control_plan']=[cmd('axis',value=1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=205),timeout=100)),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot-hold,direction=[-math.sqrt(1-dy*dy),dy])];out.append(c)
    for hold,shot,dy in [(6,12,0),(8,16,0),(8,20,.1),(12,24,.15),(8,18,.866),(12,24,.866)]:
        c=base(f'motion-{hold}-{shot}-{dy}');c['control_plan']=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot-hold,direction=[-math.sqrt(1-dy*dy),dy])];out.append(c)
    for shot in [18,26,34]:
        c=base(f'brake-{shot}');c['platforms'][0]=[-160,180,400,100];c['spawn']=[180,162];c['entry_port']=c['spawn'][:];c['exit_port']=[120,162]
        c['control_plan']=[cmd('axis',value=1),cmd('shoot',shot,direction=[1,1]),cmd('axis',value=0)];out.append(c)
    return out

def run(name):
    out=ROOT/'results'/name;engine=WorkshopEngine(out);rows=[]
    for c,r,e in engine.run(probes(),'measure'):
        rows.append(dict(case=c,result=r,evidence=e))
        print(c['id'],r['reason'],[(f['frame'],round(f['x'],1),round(f['y'],1),round(f['vx'],1),round(f['vy'],1))for f in r.get('frames',[])[::10]],flush=True)
    (out/'measured.json').write_text(json.dumps(rows))
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
