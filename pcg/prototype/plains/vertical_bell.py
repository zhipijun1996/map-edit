"""Compact vertical recoil/bell challenge from original Godot motion probes."""
import argparse,copy,json
from pathlib import Path
from .engine import ROOT,PlainsEngine
from .synthesis import probe,command,shot_events,crossing
from .evaluation import purpose

def run(name):
 out=ROOT/'results'/name
 if out.exists():raise ValueError('immutable_vertical_bell_run_exists')
 engine=PlainsEngine(out,4)
 probes=[]
 for hold in [8,12]:
  for shot in [18,26]:
   c=probe('bell_lift',len(probes),hold,shot,[0,1]);c['control_plan'][0]['value']=0;probes.append(c)
 protocol={'method':'same original synthesis probe/actual crossing; compact vertical materializer','budget':{'motion_probes':4,'calibration_candidates':4},'selected_policy_before_probe':'hold8/shot18, no alternate candidate if nominal fails','requested_rise':180,'max_width':256,'max_height':320,'new_physics_pass_inherited':False,'repair':'place bell before measured takeoff-floor ray occlusion, keep nominal hold8/shot18'}
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2))
 candidates=[]
 for c,r,e in engine.run(probes,'vertical-probes'):
  events=shot_events(r);cross=crossing(r,240)
  if not events or not cross:continue
  v=copy.deepcopy(c);v.update(id=c['id']+'-vertical-180',trace_all=False,max_frames=600,
    platforms=[[-16,438,224,32],[16,258,192,16]],one_way_platform_indices=[1],
    goal=[124,216,32,32],exit_port=[140,240],world_bounds=[-64,48,400,512])
  s=events[0];bell=[s['muzzle'][i]+s['direction'][i]*24 for i in range(2)]
  v['latches']=[dict(id='vertical_bell',bell=bell,gate=[112,158,16,100],open_seconds=1.6,prompt='RECOIL UP / CACHE')]
  v['control_plan'] += [command('settle',6,target_x=140,deadband=4)]
  v['synthesis']={'method':'actual vertical crossing at180; no invented movement equation','probe_evidence':e,'nominal_selected_before_physics':len(candidates)==0}
  candidates.append(v)
 (out/'candidates.json').write_text(json.dumps({'cases':candidates},indent=2));rows=[]
 for c,r,e in engine.run(candidates,'vertical-calibration'):
  rows.append({'case':c,'ok':r['ok'],'reason':r['reason'],'purpose':purpose(c,r),'evidence':e})
 (out/'summary.json').write_text(json.dumps({'rows':rows},ensure_ascii=False,indent=2));print([(r['case']['id'],r['ok'],r['reason'],r['purpose'])for r in rows],flush=True)
 if rows and rows[0]['ok']and rows[0]['purpose']['ok']:(out/'selected.json').write_text(json.dumps(rows[0],ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
