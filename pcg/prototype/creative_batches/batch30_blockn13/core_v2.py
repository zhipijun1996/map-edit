"""Minimal existing dock/mount composition, first real relative-support controls."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
HERE=Path(__file__).parent
def candidate(k):
 c=base('N13-relative-stop-v2-'+str(k));c['capabilities']=['move','jump','shot_recoil'];c['platforms']=[[0,608,192,96],[1408,480,256,96],[96,928,1472,40],[384,800,128,32],[224,672,128,32]]
 c['moving_platforms']=[dict(platform_id='parking-deck',start=[320,618],finish=[1120,618],size=[320,20],travel_duration=2.5,dwell_duration=.2,initial_phase=0)]
 c['latches']=[dict(id='deck-control',bell=[520,538],gate=[0,0,10,10],open_seconds=0,ferry_id='parking-deck',carrier_mount='parking-deck'),dict(id='dock-gate',bell=[1224,560],gate=[1344,128,24,800],open_seconds=.18,carrier_dock=dict(platform_id='parking-deck',rect=[1208,598,32,40]))]
 c['spawn']=[24,590];c['entry_port']=[24,590];c['exit_port']=[1640,462]
 p=[cmd('axis',value=1),wait_x(304),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='deck-control')),cmd('wait',8),wait_x(501)]
 if k:p +=[cmd('axis',value=1),cmd('wait',[0,30,50][k]),cmd('axis',value=0)]
 p +=[wait_x([924,1085,1193][k]),cmd('shoot',aim_target=[1288,538]),cmd('wait',90)]
 c.update(control_plan=p,goal=[900,560,400,80],max_frames=450,trace_all=True,control=k,validation_fixture=dict(kind='actualAboarding_and_relative_stop_timeline',marker_exit=[1640,462],actual_goal='parking-region',no_module_enrollment=True))
 return c
def observed(c,r):
 fs=r.get('frames',[]);toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'];stop=next((e for e in toggles if not e['running']),None)
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];shot=shots[1]if len(shots)>1 else None
 window=[f for f in fs if shot and shot['frame']-3<=f['frame']<=shot['frame']+60]
 timeline=[dict(frame=f['frame'],x=f['x'],y=f['y'],grounded=f['grounded'],support=f.get('support_id'),carrier=f.get('n13',{}).get('carriers'),shot_charges=f.get('shot_charges'))for f in window]
 return dict(actual_stop=stop,actual_toggles=toggles,shot_positions=[dict(frame=f['frame'],x=f['x'],y=f['y'],grounded=f['grounded'])for f in shots],support_after_stop=sum(f.get('support_id')=='parking-deck'for f in window if stop and f['frame']>stop['frame']),dock_events=[e for e in r.get('plains',{}).get('events',[])if e['type']=='dock_occupied'],timeline=timeline,hp=r.get('hp'),ticks=r.get('ticks'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 syntax=check([HERE/'runner_v1.gd'])
 if syntax['status']!='syntax_checked':write(out/'preflight.json',syntax);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 deps=[Path(__file__),HERE/'runner_v1.gd',HERE/'protocol-v1.json',HERE/'protocol-v2.json',HERE/'idea-source-v1.json',*[HERE.parent/'machinery'/n for n in ['dock_runner_v11.gd','dock_binding_v11.gd','dock_latch_v11.gd']],HERE.parent/'batch30_d05/mount_v1.gd']
 e=WorkshopEngine(out,extra_sources=deps,runner_script=HERE/'runner_v1.gd');write(out/'preflight.json',syntax);rows=[]
 for c,r,ev in e.run([candidate(k)for k in [0,1,2]],'front-mid-rear-timelines'):
  q=observed(c,r);rows.append(dict(case=c,observed=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','ticks']}));write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],actual=rows[-1]['actual'],stop=q['actual_stop'],support_after_stop=q['support_after_stop'],shots=q['shot_positions'],dock=q['dock_events'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,new_modules=0,scope='realexistingCellscompositiontimelines; noModulequalification'))
if __name__=='__main__':main()
