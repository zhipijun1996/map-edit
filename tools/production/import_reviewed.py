"""One-time consolidation from exact reviewed implementations into modules/."""
import copy,hashlib,json,os,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from module_pipeline import library as lib
from module_pipeline.bindings import recipe_for,evaluate,META,equal
from module_pipeline.vendor import Vendor
from inventory import discover
BASE='9b712fe814ef228b368c0eb9adf660e39de29e37'
def history(path):return dict(commit=BASE,path=str(path),uri='git+https://github.com/zhipijun1996/map-edit@'+BASE+':'+str(path))
def actual_cases(folder):
 p=folder/'physics-input-cases.json'
 if not p.exists():p=folder/'cases.json'
 return lib.read(p)['cases']if p.exists()else[]
def main():
 root=lib.ROOT;stage=root/'build/module-source-import';assert not stage.exists();stage.mkdir(parents=True);vendor=Vendor();inventory=discover();counts={};all_ids={r['id']for r in inventory['rows']};origin=[]
 for row in inventory['rows']:
  identifier=row['id'];lib.safe_id(identifier);folder=stage/identifier;folder.mkdir();source=root/row['module'];original=lib.read(source);result=lib.read(root/row['receipt']);native=root/row['native'];data=lib.read(native/'compiled-content.json');design=lib.read(root/row['approvedDesign']);cases=actual_cases(source.parent)
  ref=result.get('module')or result.get('sourceModule');assert lib.sha(source)==ref['sha256'],identifier
  adjustments=[]
  if row['reviewId']=='157':
   auth=root/'feedback/manual-review/implementation-results/157-upper-block-v1/authorization/request.json';assert'1block'in lib.read(auth)['verbatim'];adjustments.append(dict(reason='Previously explicitly approved top +1Block; old drawing bounds were not synchronized.',receipt=history(auth.relative_to(root))));row['state']='verified_scoped'
  if row['reviewId']=='174':
   auth=root/'feedback/manual-review/implementation-results/clarified-three-v1/authorization/request.json';assert'174修改不是rock'in lib.read(auth)['verbatim'];adjustments.append(dict(reason='Previously explicitly approved non-ROCK exit; actual safe support is ONE_WAY_PLATFORM.',receipt=history(auth.relative_to(root))));row['state']='verified_scoped'
  assert row['state']=='verified_scoped',row
  recipe=recipe_for(original,data);doc=copy.deepcopy(original);old_id=doc['id'];doc['id']=identifier
  for key in ['baselineObjects','baselineDifficulty','baselineCapabilityRequirements']:doc.pop(key,None)
  for obj in doc['objects']:
   obj.pop('designMotionStatus',None)
   if obj.get('mechanics',{}).get('status','').startswith(('DESIGN_','PROPOSED_')):obj['mechanics']['status']='implemented_native'
  doc['source']=dict(repository='zhipijun1996/map-edit',commit=BASE,path=f'modules/{identifier}/module.mapnote.json',moduleId=identifier,kind=original.get('source',{}).get('kind','reviewed'),category=original.get('source',{}).get('category','森林'if'forest'in identifier else'平原'),integration=dict(isIntegrated=False,reason='Current reviewed source; runtime delivery is separate from production game approval.'))
  doc['intent']=dict(operation='modify_existing',notes='Authoritative current Module. Edit objects and declared native bindings here; generated files are not another source library.')
  g=doc['generationContract'];g['generation']=dict(parameters=dict(runtimeBindings=recipe),source=dict(kind='current_module_source',record=f'modules/{identifier}/record.json'),migration=dict(moduleId=identifier,status='current_source'))
  g['validations']=[]
  for transform in g['space']['transforms']:transform.update(status='UNKNOWN',validationIds=[])
  g['mirror'].update(status='UNKNOWN',validationIds=[])
  for r in g['routes']:r['validationIds']=[]
  for p in g['ports']:
   for v in p.get('cornerRelocations',{}).values():
    if v.get('applicable'):v.update(allowed='UNKNOWN',profileId=None,reason='Not inherited across current-source normalization; only explicit delivery configurations are allowed.')
  for name in ['closures','portConfigurations']:g[name]=[]
  lib.write(folder/'module.mapnote.json',doc);lib.node('refresh',folder/'module.mapnote.json');doc=lib.read(folder/'module.mapnote.json')
  expected={k:v for k,v in data.items()if k not in META};assert equal(evaluate(recipe,doc),expected),identifier
  loader_ref=(native/'module.tscn').read_text().split('path="')[1].split('"')[0];loader=vendor.add(native/loader_ref)
  proofpath=row.get('qualification');q=lib.read(root/proofpath)if proofpath else{};proof=q.get('report')or result.get('qualificationReport');report=lib.read(root/proof['path'])if isinstance(proof,dict)and(root/proof['path']).exists()else None
  verified_routes=[r['routeId']for r in report.get('routes',[])if r.get('passed')]if report else[r['id']for r in g['routes']]
  route_caps={c['route_spec']['id']:c.get('capabilities',[])for c in cases};signature=lib.digest(expected)
  record=dict(schema=lib.SCHEMA,id=identifier,title=doc['title'],reviewId=row['reviewId'],region=doc['source']['category'],lifecycle='retained',review=dict(decision='KEEP',implementationApproval='approved',designVersion=row['approvedVersion'],priorExplicitAdjustments=adjustments),source={},aliases=[old_id]if old_id!=identifier and old_id not in all_ids else[],qualification=dict(status='verified_scoped',physicalSignature=signature,routeIds=verified_routes,availableAbilitiesByRoute=route_caps,originalReportSha256=proof.get('sha256')if isinstance(proof,dict)else None,scope='Original exact native Cells and scoped route qualification; only metadata/ID/source-location normalized. Native physical payload equality is checked before installation.'),runtime=dict(loader='runtime/module_runtime/'+loader,deliveryStatus='pending_portable_validation',hostProfile='gunman-rush-native-12f6cb0',configurations=[dict(id='original-all-ports',orientation='identity',mirrorX=False,connectedPortIds=[p['id']for p in g['ports']],relocations=[],closures=[],routeIds=verified_routes)],unsupported=dict(mirror='UNKNOWN',relocations='UNKNOWN',closures='UNKNOWN')),history=dict(originalDocument=history(row['module'])|dict(sha256=lib.sha(source),contentVersion=original['generationContract']['contentVersion']),implementationReceipt=history(row['receipt'])|dict(sha256=lib.sha(root/row['receipt'])),design=history(row['approvedDesign'])),gaps=[])
  lib.write(folder/'record.json',record)
  # Offline input policies remain with this one source, never in a delivery.
  if cases:
   lib.write(folder/'validation/cases.json',dict(cases=cases));lib.write(folder/'validation/origin.json',dict(sourceIdentity=lib.read(source.parent/'migration.json')if(source.parent/'migration.json').exists()else{},sourceContentVersion=original['generationContract']['contentVersion'],sourceDocumentSha256=lib.sha(source)))
  lib.compile_module(folder);record=lib.read(folder/'record.json');assert record['runtime']['physicalSignature']==signature
  origin.append(dict(id=identifier,source=history(row['module']),oldContentVersion=original['generationContract']['contentVersion'],newContentVersion=record['source']['contentVersion'],physicalSignature=signature,nativePayloadUnchanged=True));print('IMPORTED_REVIEWED',identifier,flush=True)
 ideas=lib.read(root/'feedback/module-workshop/ideas-v1.json')
 for idea in ideas['rows']:
  if idea['stage']=='DISCARDED'or idea['humanApproval']=='KEEP':continue
  identifier=idea['id'];folder=stage/identifier;folder.mkdir();design=lib.read(root/idea['design']['file']);lib.write(folder/'design.json',design)
  # Keep the existing diagram as an immutable generated preview during intake.
  old=root/'generation/module-workshop'/idea['design']['diagram'];svg=old.with_suffix('.svg');shutil.copy2(svg,folder/'thumbnail.svg')
  lib.write(folder/'record.json',dict(schema=lib.SCHEMA,id=identifier,title=idea['title'],reviewId=design['reviewId'],region='平原',lifecycle='development',review=dict(decision='PENDING',implementationApproval='not_implemented',designVersion=design['designVersion']),source=dict(kind='design',file='design.json',sha256=lib.sha(folder/'design.json'),contentVersion=design['designVersion']),qualification=dict(status='not_implemented'),runtime=dict(deliveryStatus='not_implemented'),history=dict(design=history(idea['design']['file'])),gaps=['Await current design review and missing Cell implementations; not a runtime Module.']))
 old_catalog=lib.read(root/'modules/catalog.json');old_ids={r['id']for r in old_catalog['modules']};retired=0
 for entry in old_catalog['modules']:
  if entry['id']in all_ids:continue
  identifier=entry['id'];folder=stage/identifier;folder.mkdir();lib.write(folder/'record.json',dict(schema=lib.SCHEMA,id=identifier,title=entry['title'],lifecycle='withdrawn',review=dict(decision='NOT_IN_CURRENT_REVIEW_SET'),source=None,runtime=dict(deliveryStatus='withdrawn'),withdrawal=dict(reason='Historical template outside the latest human-reviewed collection; removed under the current cleanup instruction.',replacement=None),history=dict(previousSource=history(entry['file'].removeprefix('./')))));retired+=1
 discarded=[]
 for q in lib.read(root/'generation/manual-review/queue.json')['rows']:
  if q.get('receivedDecision')=='DISCARD':discarded.append(dict(id=q['moduleId'],title=q['title'],reviewId=q['reviewId'],version=q.get('receivedDecisionVersion',q.get('contentVersion'))))
 for idea in ideas['rows']:
  if idea['stage']=='DISCARDED':discarded.append(dict(id=idea['id'],title=idea['title'],reviewId=idea['id'],version=idea.get('design',{}).get('version')))
 for item in discarded:
  if item['id']in all_ids:raise ValueError('retained_and_discarded_identity_conflict:'+item['id'])
  folder=stage/item['id'];folder.mkdir(exist_ok=True)
  lib.write(folder/'record.json',dict(schema=lib.SCHEMA,id=item['id'],title=item['title'],reviewId=item['reviewId'],lifecycle='withdrawn',review=dict(decision='DISCARD',designVersion=item['version']),source=None,runtime=dict(deliveryStatus='withdrawn'),withdrawal=dict(reason='explicit_human_discard',replacement=None),history=dict(review=history('generation/manual-review/queue.json'))))
 retired=sum(lib.read(p)['lifecycle']=='withdrawn'for p in stage.glob('*/record.json'))
 vendor.save();lib.write(root/'build/module-source-import-receipt.json',dict(schema='map-edit/source-consolidation/v1',retainedImplemented=len(origin),developmentDesigns=3,withdrawnHistorical=retired,oldCurrentReplaced=len(old_ids&all_ids),sourceCommit=BASE,rows=origin,staging=str(stage.relative_to(root)),installed=False));print('IMPORT_STAGED',len(origin),3,retired,flush=True)
if __name__=='__main__':main()
