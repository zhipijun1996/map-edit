"""Canonical Module objects are the geometry source consumed by direct assembly."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha


def export_reload(modules,out):
 out=Path(out).resolve();source=out/'source.json';project=REPO/'pcg/prototype/godot'
 bell=re.search(r'bell_rectangle.size = Vector2\(([^,]+), ([^)]+)\)',(project/'scripts/world/shot_latch.gd').read_text())
 definitions={'player':{'size':[24,36],'source':{'path':'pcg/prototype/godot/scenes/player/player.tscn','sha256':file_sha(project/'scenes/player/player.tscn')}},
 'bell':{'size':list(map(float,bell.groups())),'source':{'path':'pcg/prototype/godot/scripts/world/shot_latch.gd','sha256':file_sha(project/'scripts/world/shot_latch.gd')}},'enemies':{}}
 write(source,{'modules':modules});bundle=dict(modules=modules,sourcePath=str(source.relative_to(REPO)),sourceSha=file_sha(source),
  generatorSha=file_sha(REPO/'pcg/prototype/plains/room_modules.py'),sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),geometryDefinitions=definitions)
 write(out/'bundle.json',bundle)
 subprocess.run(['node',str(Path(__file__).with_name('export_modules.mjs')),str(out/'bundle.json'),str(out/'documents')],check=True,cwd=REPO)
 return reload_catalog(out)


def reload_catalog(out):
 out=Path(out).resolve()
 modules=json.loads((out/'source.json').read_text())['modules']
 manifest=json.loads((out/'documents/manifest.json').read_text());result=[]
 # Reuse the same schema/content-version gate for a persisted catalog.
 subprocess.run(['node',str(Path(__file__).with_name('verify_catalog.mjs')),str(out/'documents/manifest.json')],check=True,cwd=REPO)
 for entry,module in zip(manifest['modules'],modules):
  doc_path=out/'documents'/entry['file'];doc=json.loads(doc_path.read_text());by={o['id']:o for o in doc['objects']}
  if file_sha(doc_path)!=entry['sha256']:raise ValueError('canonical_module_file_drift')
  m=copy.deepcopy(module);case=m['case']
  static=sorted((o for o in doc['objects']if isinstance(o.get('sourceIndex'),int)),key=lambda o:o['sourceIndex'])
  loaded=[[o['x'],o['y'],o['w'],o['h']]for o in static]
  if loaded!=case['platforms']:raise ValueError('canonical_static_source_mismatch')
  case['platforms']=loaded;case['one_way_platform_indices']=[o['sourceIndex']for o in static if o['type']=='platform']
  case['saws']=[];case['moving_platforms']=[];case['latches']=[];m['boundary_gates']=[]
  for o in doc['objects']:
   track=by.get(o.get('trackId'))
   if o['type']=='gear':
    a,b=track['points'];case['saws'].append(dict(source_id=o['sourceId'],origin=[(a['x']+b['x'])/2,(a['y']+b['y'])/2],travel=[(b['x']-a['x'])/2,(b['y']-a['y'])/2],radius=o['w']/2,period=track['duration'],initial_phase=track['initialPhase']))
   elif o['type']=='platform'and track:
    a,b=track['points'];case['moving_platforms'].append(dict(platform_id=o['sourceId'],start=[a['x'],a['y']],finish=[b['x'],b['y']],size=[o['w'],o['h']],travel_duration=track['duration'],dwell_duration=track['dwell'],initial_phase=track['initialPhase']))
   elif o['type']=='bell':
    gate=by[o['targetId']];case['latches'].append(dict(id=o['sourceId'],bell=[o['x']+o['w']/2,o['y']+o['h']/2],gate=[gate[k]for k in ['x','y','w','h']],open_seconds=gate['mechanics']['openSeconds'],prompt=next(v['prompt']for v in module['case']['latches']if v['id']==o['sourceId'])))
   elif o['type']=='gate'and o.get('mechanics',{}).get('kind')=='boundary_gate':
    v=o['mechanics'];m['boundary_gates'].append(dict(id=o['sourceId'],edge_id=v['edgeId'],bounds=[o[k]for k in ['x','y','w','h']],direction=v['direction'],switch=v['switch'],one_way=v['oneWay'],owner_module=v['owner'],source='module-generated boundary gate',from_module=v['from'],to_module=v['to']))
  for kind in ['platforms','one_way_platform_indices','saws','moving_platforms','latches']:
   if case[kind]!=module['case'][kind]:raise ValueError('canonical_physical_payload_mismatch/'+m['id']+'/'+kind)
  if m['boundary_gates']!=module['boundary_gates']:raise ValueError('canonical_module_gate_mismatch')
  m['content_version']=entry['contentVersion'];m['canonical_document']={'path':str(doc_path.relative_to(REPO)),'sha256':entry['sha256'],'id':doc['id'],'contentVersion':entry['contentVersion']}
  result.append(m)
 return result
