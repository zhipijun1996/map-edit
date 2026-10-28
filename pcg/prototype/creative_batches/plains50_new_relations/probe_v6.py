"""New preparation/commitment proposal after ground-detour control budget ended."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import timed,cmd
HERE=Path(__file__).parent

def prepared_gate(v=0):
 c=timed(v);c['id']=f'p50-prepared-gate-{v}';c['family']='prepared-air-sequence'
 l=c['latches'][0];second=l['bell'];l['bell']=[80,300];l['sequence_offset']=[second[0]-80,second[1]-300];l.pop('return_access',None)
 p=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell')),cmd('wait',after=18)]+copy.deepcopy(c['control_plan']);p[7]['aim_cell']['receiver']='second';c['control_plan']=p
 c['rule_parameters']=dict(c['rule_parameters'],relationship='prepare first sequence target on ground, read armed state, then airborne second target opens short door while recoil crosses',original_cell='ShotLatch.sequence_offset; no new Cell',sequence_bells=[l['bell'],second]);c['rule_source_path']='pcg/prototype/creative_batches/plains50_new_relations/production_sequence_v1.py';return c
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v6';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'sequence_runner_v1.gd'],runner_script=HERE/'sequence_runner_v1.gd');rows=[]
 for c,r,ev in e.run([prepared_gate(v)for v in [0,1]],'prepared-air-sequence'):
  fs=r.get('frames',[]);row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),accepted=[dict(frame=f['frame'],x=f['x'],y=f['y'],events=f['accepted'])for f in fs if f.get('accepted')],last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
