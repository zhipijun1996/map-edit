"""Canonical Module objects are the geometry source consumed by direct assembly."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha


def export_reload(modules,out,producer='pcg/prototype/plains/room_modules.py'):
 out=Path(out).resolve();source=out/'source.json';project=REPO/'pcg/prototype/godot'
 bell=re.search(r'bell_rectangle.size = Vector2\(([^,]+), ([^)]+)\)',(project/'scripts/world/shot_latch.gd').read_text())
 definitions={'player':{'size':[24,36],'source':{'path':'pcg/prototype/godot/scenes/player/player.tscn','sha256':file_sha(project/'scenes/player/player.tscn')}},
 'bell':{'size':list(map(float,bell.groups())),'source':{'path':'pcg/prototype/godot/scripts/world/shot_latch.gd','sha256':file_sha(project/'scripts/world/shot_latch.gd')}},'enemies':{}}
 for name in {e['definition']for m in modules for e in m['case'].get('enemies',[])}:
  path=project/'resources/enemies'/str(name+'.tres')
  size=re.search(r'collision_size = Vector2\(([^,]+), ([^)]+)\)',path.read_text())
  if not size:raise ValueError('enemy_collision_definition_missing/'+name)
  definitions['enemies'][name]={'size':list(map(float,size.groups())),'source':{'path':str(path.relative_to(REPO)),'sha256':file_sha(path)}}
 write(source,{'modules':modules});bundle=dict(modules=modules,sourcePath=str(source.relative_to(REPO)),sourceSha=file_sha(source),
  generatorSha=file_sha(REPO/producer),producer=producer,sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),geometryDefinitions=definitions)
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
  if doc['generationContract']['generation']['parameters'].get('runtimeActors',[])!=case.get('boss_encounters',[]):raise ValueError('canonical_runtime_actor_payload_mismatch')
  if m.get('block_grid'):
   gc=doc['generationContract']
   if gc['space'].get('blockGrid')!=m['block_grid']:raise ValueError('canonical_block_grid_mismatch')
   clear=[[r[k]for k in ['x','y','w','h']]for r in gc['space']['actionClearance']['regions']]
   if clear!=m['action_clearance']:raise ValueError('canonical_block_action_space_mismatch')
   for key,p in m['ports'].items():
    actual=next(v for v in gc['ports']if v['id']==key)
    if actual['position']!=p['position']or actual['normal']!=p['normal']or actual.get('grid')!={**p['grid'],'stagingPosition':p['dock']['position']}:raise ValueError('canonical_grid_port_mismatch')
  static=sorted((o for o in doc['objects']if isinstance(o.get('sourceIndex'),int)),key=lambda o:o['sourceIndex'])
  loaded=[[o['x'],o['y'],o['w'],o['h']]for o in static]
  if loaded!=case['platforms']:raise ValueError('canonical_static_source_mismatch')
  case['platforms']=loaded;case['one_way_platform_indices']=[o['sourceIndex']for o in static if o['type']=='platform']
  # Hazard faces are part of the canonical physical payload, not annotations.
  for i,thorn in enumerate(case.get('thorns',[])):
   obj=by[doc['id']+'/thorn-'+str(i)]
   if obj['hostId']!=doc['id']+'/platform-'+str(thorn['platform_index']) or obj['sourceId']!=thorn['surface_id']:
    raise ValueError('canonical_thorn_host_or_identity_mismatch')
   p=loaded[thorn['platform_index']];face=thorn['face'];offset=thorn['start_offset'];depth=thorn['depth'];length=thorn['length']
   rect={'top':[p[0]+offset,p[1]-depth,length,depth],'bottom':[p[0]+offset,p[1]+p[3],length,depth],
     'left':[p[0]-depth,p[1]+offset,depth,length],'right':[p[0]+p[2],p[1]+offset,depth,length]}[face]
   if [obj[k]for k in ['x','y','w','h']]!=rect:raise ValueError('canonical_thorn_geometry_mismatch')
  case['saws']=[];case['moving_platforms']=[];case['latches']=[];case['enemies']=[];m['boundary_gates']=[]
  if 'reward_sites' in case:case['reward_sites']=[];case['shop_sites']=[]
  for o in doc['objects']:
   track=by.get(o.get('trackId'))
   if o['type']=='gear':
    a,b=track['points'];case['saws'].append(dict(source_id=o['sourceId'],origin=[(a['x']+b['x'])/2,(a['y']+b['y'])/2],travel=[(b['x']-a['x'])/2,(b['y']-a['y'])/2],radius=o['w']/2,period=track['duration'],initial_phase=track['initialPhase']))
    if o.get('mechanics',{}).get('sourceFields'):
     source=copy.deepcopy(o['mechanics']['sourceFields']);source.update(case['saws'][-1]);case['saws'][-1]=source
   elif o['type']=='platform'and track:
    a,b=track['points'];case['moving_platforms'].append(dict(platform_id=o['sourceId'],start=[a['x'],a['y']],finish=[b['x'],b['y']],size=[o['w'],o['h']],travel_duration=track['duration'],dwell_duration=track['dwell'],initial_phase=track['initialPhase']))
   elif o['type']=='bell':
    gate=by[o['targetId']];case['latches'].append(dict(id=o['sourceId'],bell=[o['x']+o['w']/2,o['y']+o['h']/2],gate=[gate[k]for k in ['x','y','w','h']],open_seconds=gate['mechanics']['openSeconds'],prompt=next(v.get('prompt','')for v in module['case']['latches']if v['id']==o['sourceId'])))
    if gate['mechanics'].get('startsFerry'):case['latches'][-1]['starts_ferry']=gate['mechanics']['startsFerry']
    if gate['mechanics'].get('ferryId'):case['latches'][-1]['ferry_id']=gate['mechanics']['ferryId']
    if gate['mechanics'].get('returnAccess'):case['latches'][-1]['return_access']=gate['mechanics']['returnAccess']
    if gate['mechanics'].get('sourceFields'):
     raw=copy.deepcopy(gate['mechanics']['sourceFields'])
     for name in ['id','bell','gate','open_seconds']:raw[name]=case['latches'][-1][name]
     case['latches'][-1]=raw
   elif o['type']=='enemy':
    enemy=dict(id=o['sourceId'],definition=o['definition'],position=[o['x']+o['w']/2,o['y']+o['h']/2])
    if o.get('mechanics',{}).get('initialIdleCooldown') is not None:enemy['initial_idle_cooldown']=o['mechanics']['initialIdleCooldown']
    case['enemies'].append(enemy)
   elif o['type']=='reward'and o.get('mechanics',{}).get('kind')in ['chest','merchant']:
    case['reward_sites'if o['mechanics']['kind']=='chest'else'shop_sites'].append(copy.deepcopy(o['mechanics']['source']))
   elif o['type']=='gate'and o.get('mechanics',{}).get('kind')=='boundary_gate':
    v=o['mechanics'];gate=copy.deepcopy(v.get('sourceFields',{}));gate.update(id=o['sourceId'],edge_id=v['edgeId'],bounds=[o[k]for k in ['x','y','w','h']],direction=v['direction'],switch=v['switch'],one_way=v['oneWay'],owner_module=v['owner'],from_module=v['from'],to_module=v['to']);gate.setdefault('source','module-generated boundary gate');m['boundary_gates'].append(gate)
  for kind in ['platforms','one_way_platform_indices','saws','moving_platforms','latches','enemies']+(['reward_sites','shop_sites']if 'reward_sites'in module['case']else[]):
   if case[kind]!=module['case'][kind]:raise ValueError('canonical_physical_payload_mismatch/'+m['id']+'/'+kind)
  if m['boundary_gates']!=module['boundary_gates']:raise ValueError('canonical_module_gate_mismatch')
  m['content_version']=entry['contentVersion'];m['canonical_document']={'path':str(doc_path.relative_to(REPO)),'sha256':entry['sha256'],'id':doc['id'],'contentVersion':entry['contentVersion']}
  result.append(m)
 return result
