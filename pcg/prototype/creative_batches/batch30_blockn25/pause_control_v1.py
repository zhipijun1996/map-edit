import copy,json,math
from pathlib import Path
from . import cell_probe_v1 as source
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 c=copy.deepcopy(source.cases()[0]);c.update(id='b31-n25-original-linear-pause-control-v1',spawn=[448,546],max_frames=300,cell_pause_probe=True)
 c['moving_platforms']=[dict(platform_id='base-deck',start=[448,576],finish=[1088,576],size=[160,24],travel_duration=3.8,dwell_duration=.2,initial_phase=0)]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn25-original-pause-v1',extra_sources=[Path(__file__),HERE/'pause-control-protocol-v1.json',Path(source.__file__),*source.SOURCE_DEPENDENCIES],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run([c],'original-component-pause-control'):
  fs=r['frames'];steps=[dict(frame=b['frame'],delta=math.dist(a['moving_platforms'][0]['position'],b['moving_platforms'][0]['position']))for a,b in zip(fs,fs[1:])];row=dict(id=c['id'],evidence=ev,max_step=max(steps,key=lambda v:v['delta']),ordinary_expected_max_step=640/3.8/60,around_pause=[dict(frame=f['frame'],clock=f['module_clock'],position=f['moving_platforms'][0]['position'],actor=[f['x'],f['y']])for f in fs[116:124]],pause_receipts=r['n25']['pause_receipts'],source_original_body_and_definition=True,cell_qualification='Notapprovedbythiscontrol');rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
