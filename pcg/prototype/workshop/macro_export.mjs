// Local recipe adapter, reusing the existing Module/Macro contract and renderer.
import fs from 'node:fs';
import path from 'node:path';
import {validateDocument} from '../../../model.js';
import {contentVersion,validateGenerationContract,unknownState,assemblyInterface,sha256} from '../../../module-contract.js';
import {renderContractSvg} from '../../../module-contract-render.js';
const read=p=>JSON.parse(fs.readFileSync(p)),clone=v=>structuredClone(v);
function resolvedCheck(doc,children){
 const resolve=(id,v)=>children.find(d=>d.id===id&&d.generationContract.contentVersion===v);
 validateDocument(doc);const result=validateGenerationContract(doc,{resolve});
 if(!result.versionMatches)throw Error('stale_macro_version');return {result,resolve};
}
if(process.argv[2]==='--verify'){
 const doc=read(process.argv[3]),children=process.argv.slice(4).map(read);
 console.log(JSON.stringify(resolvedCheck(doc,children).result));process.exit(0);
}
const [bundleFile,rawDir,outDir]=process.argv.slice(2),bundle=read(bundleFile),rawManifest=read(path.join(rawDir,'manifest.json'));
if(fs.existsSync(outDir))throw Error('immutable_macro_export_directory_exists');fs.mkdirSync(outDir,{recursive:true});
const docs=rawManifest.modules.map(m=>({item:m,doc:read(path.join(rawDir,m.file))})),manifest=[];
for(const row of docs.filter(r=>r.item.family!=='gate-brake-return')){
 for(const ext of ['.mapnote.json','.svg'])fs.copyFileSync(path.join(rawDir,row.doc.id+ext),path.join(outDir,row.doc.id+ext));
 manifest.push({...row.item,kind:'module'});
}
for(const variant of [0,1]){
 const relevant=bundle.rows.filter(r=>r.case.rule_parameters.variant===variant),macroRows=relevant.filter(r=>r.case.family==='gate-brake-return');
 const base=docs.find(d=>d.doc.id==='generated-'+macroRows[0].case.layout_uid).doc,doc=clone(base),c=doc.generationContract;
 const children=['gate','brake'].map(name=>{
  const r=relevant.find(r=>r.case.family==='gate-brake-return-'+name);
  return docs.find(d=>d.doc.id==='generated-'+r.case.layout_uid).doc;
 });
 const parts=children.map((child,i)=>({id:i?'brake':'gate',moduleId:child.id,contentVersion:child.generationContract.contentVersion,transform:{translation:[0,0],scale:[1,1],rotation:0,mirrorX:false,status:'UNKNOWN'}}));
 const owned=children.flatMap((child,i)=>child.objects.map(raw=>{
  const o=clone(raw),prefix=id=>parts[i].id+'/'+id;o.id=prefix(o.id);
  for(const k of ['trackId','targetId','hostId'])if(o[k])o[k]=prefix(o[k]);return o;
 }));
 // Keep the whole-world recorded paths. Component markers and paths are also
 // retained because canonical composition resolves EVERY versioned child object.
 doc.objects=[...owned,...base.objects.filter(o=>o.type==='route')];
 c.kind='macro';doc.title='门后双宝箱 · 连续返回 Macro / '+variant;
 doc.description='穿短门取箱，在岩沿外反冲刹入第二箱，再经下岸岩阶回到入口。程序回放候选；本版人工观感待评。';
 doc.source.path='pcg/prototype/workshop/macro.py';doc.source.method='bounded_local_macro_recipe_with_continuous_original_state';
 const mapping={A:[0,'A'],C:[0,'C'],B:[1,'B']};
 for(const p of c.ports){const [i,id]=mapping[p.id],cp=children[i].generationContract.ports.find(p=>p.id===id);p.objectId=parts[i].id+'/'+cp.objectId;p.support=clone(cp.support);if(p.support!=='UNKNOWN')p.support.objectId=parts[i].id+'/'+p.support.objectId;}
 const loop=bundle.continuousRows.find(r=>r.case.rule_parameters.variant===variant);
 if(!loop?.macroPurpose?.ok)throw Error('continuous_macro_excursion_missing');
 const gateSource=macroRows.find(r=>r.case.route_spec.id==='outbound'),returnSource=macroRows.find(r=>r.case.route_spec.id==='return');
 function crossing(row,x,direction){
  const frames=row.result.frames;for(let i=1;i<frames.length;i++){
   const a=frames[i-1],b=frames[i];if(a.grounded&&b.grounded&&(direction>0?a.x<x&&b.x>=x:a.x>x&&b.x<=x))return {before:a,after:b};
  }throw Error('actual_supported_seam_crossing_missing '+x);
 }
 const joint=600+40*variant,lower=joint-120;
 const links=[{id:'upper-contact',from:{instanceId:'gate',portId:'C'},to:{instanceId:'brake',portId:'D'},status:'connected',transfer:{status:'observed_only',requires:unknownState(),ensures:unknownState(),snapshot:crossing(gateSource,joint,1)},validationIds:['recorded-outbound'],geometry:{contactX:joint,addedSolidArea:0,coverage:'exact abutting colliders and selected supported crossing; general state transfer UNKNOWN'}},
 {id:'lower-contact',from:{instanceId:'brake',portId:'E'},to:{instanceId:'gate',portId:'R'},status:'connected',transfer:{status:'observed_only',requires:unknownState(),ensures:unknownState(),snapshot:crossing(returnSource,lower,-1)},validationIds:['recorded-return'],geometry:{contactX:lower,addedSolidArea:0,coverage:'exact abutting colliders and selected supported crossing; no automatic recovery'}}];
 c.composition={components:parts,connections:links,exports:c.ports.map(p=>({portId:p.id,source:{instanceId:parts[mapping[p.id][0]].id,portId:mapping[p.id][1]}})),cells:[]};
 const step=(instanceId,routeId)=>({kind:'component_route',instanceId,routeId}),link=id=>({kind:'connection',id});
 const steps={outbound:[step('gate','gate'),link('upper-contact'),step('brake','brake')],cache:[step('gate','gate')],descent:[link('upper-contact'),step('brake','brake')],return:[step('brake','drop'),link('lower-contact'),step('gate','climb')]};
 for(const r of c.routes){r.steps=steps[r.id];r.transfer={status:'observed_only',requires:unknownState(),ensures:unknownState()};}
 c.routes.find(r=>r.id==='outbound').return={status:'yes',routeId:'return',conditions:{coverage:'selected continuous A-C-B-A excursion with same actor/resources/clock/wallet',sourceCaseSha256:loop.case.module_sha256,universalStates:'UNKNOWN'}};
 c.space.occupancy.objectIds=doc.objects.filter(o=>!['entry','exit','route'].includes(o.type)).map(o=>o.id);
 c.space.occupancy.coverage='exact union of two versioned component geometries; zero synthetic connector terrain';
 c.space.actionClearance.coverage='whole Macro recorded router body sweeps; component passes were not substituted for joined physics';
 for(const u of c.unlocks){const original=children[0].generationContract.unlocks.find(x=>x.id===u.id);u.trigger.objectId='gate/'+original.trigger.objectId;u.changes.objectId='gate/'+original.changes.objectId;}
 c.generation.source.componentDocuments=children.map(child=>({id:child.id,contentVersion:child.generationContract.contentVersion,path:path.join(outDir,child.id+'.mapnote.json'),sha256:sha256(fs.readFileSync(path.join(outDir,child.id+'.mapnote.json'),'utf8'))}));
 c.generation.source.continuousExcursion={caseId:loop.case.id,moduleSha256:loop.case.module_sha256,artifacts:loop.artifacts,check:loop.macroPurpose,run:loop.sourceRun};
 c.generation.parameters.recipe={id:'workshop/macro/gate-brake-return',version:1,variant,kind:'macro',addedFamilyCount:0,syntheticConnectorArea:0};
 c.generation.parameters.interfaceSpecification=bundle.specifications[variant];
 for(const v of c.validations){v.method='actual_godot_whole_local_macro_router_replay';v.coverage.macroScope='two physically joined components, exact identity placement; not a region or whole Map';v.coverage.componentPassInheritance=false;v.coverage.wholeMap=false;v.coverage.causal=macroRows.find(r=>r.case.route_spec.id===v.routeId).macroPurpose;}
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;for(const v of c.validations)v.contentVersion=c.contentVersion;c.staticChecks.contentVersion=c.contentVersion;
 c.staticChecks.method='canonical contract + resolved exact child versions/objects/ports + contiguous internal route steps';
 const check=resolvedCheck(doc,children),file=doc.id+'.mapnote.json';
 fs.writeFileSync(path.join(outDir,file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(outDir,doc.id+'.svg'),renderContractSvg(doc));
 manifest.push({id:doc.id,file,contentVersion:c.contentVersion,kind:'macro',family:'gate-brake-return',variant,portCount:3,internalConnections:2,syntheticConnectorArea:0,productionAdmitted:false,assembly:c.routes.map(r=>assemblyInterface(doc,{routeId:r.id,resolve:check.resolve}))});
}
fs.writeFileSync(path.join(outDir,'manifest.json'),JSON.stringify({schema:'pcg/workshop-macro-delivery/v1',modules:manifest,productionAdmitted:false},null,2));
console.log(JSON.stringify({components:4,macros:2,out:outDir}));
