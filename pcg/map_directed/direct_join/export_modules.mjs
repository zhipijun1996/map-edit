import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {moduleDocument} from '../../../tools/export-module-contracts.mjs';
import {validateDocument} from '../../../model.js';
import {UNKNOWN,unknownState,contentVersion,validateGenerationContract,sha256,canonical} from '../../../module-contract.js';
import {renderContractSvg} from '../../../module-contract-render.js';
const sha=data=>createHash('sha256').update(data).digest('hex');
const input=JSON.parse(fs.readFileSync(process.argv[2]));const out=process.argv[3];
fs.mkdirSync(out,{recursive:true});const entries=[];
for(const module of input.modules){
 const raw=structuredClone(module.case);raw.factory_id='direct-'+module.id;
 const row={case:raw,result:UNKNOWN,inputCase:UNKNOWN,protocol:UNKNOWN,binding:UNKNOWN,artifacts:[],sourceRun:UNKNOWN,
 sourceCases:{path:input.sourcePath,sha256:input.sourceSha},statistics:UNKNOWN,trialRows:[],
 generationMetadata:{producer:'pcg/prototype/plains/room_modules.py',seed:{status:'not_used',value:null,reason:'Deterministic demand materialization'},parameters:{request:module.spec.id,producerSha256:input.generatorSha,rawPayloadVersion:module.content_version}},
 geometryDefinitions:input.geometryDefinitions};
 const doc=moduleDocument(row,input.sourceCommit),gc=doc.generationContract,id=doc.id;
 doc.title='直接拼接 · '+module.id;doc.description='独立Module完整几何；Map只作刚性摆放，接缝无填充。当前为隔离实验候选，通用状态关系未知。';
 doc.objects=doc.objects.filter(o=>!['entry','exit','route'].includes(o.type));gc.routes=[];gc.validations=[];
 for(const [i,raw]of module.case.latches.entries()){
  doc.objects.find(o=>o.id===id+'/gate-'+i).mechanics={kind:'shot_latch',openSeconds:raw.open_seconds};
  doc.objects.find(o=>o.id===id+'/bell-'+i).sourceId=raw.id;
 }
 for(const [i,gate]of module.boundary_gates.entries()){
  const [x,y,w,h]=gate.bounds;
  doc.objects.push({id:id+'/boundary-gate-'+i,type:'gate',x,y,w,h,rotation:0,label:gate.edge_id,note:'Module输出的状态门',sourceId:gate.id,
   mechanics:{kind:'boundary_gate',edgeId:gate.edge_id,direction:gate.direction,switch:gate.switch,oneWay:gate.one_way,owner:module.id,from:gate.from_module,to:gate.to_module}});
 }
 gc.ports=Object.values(module.ports).map((p,i)=>{
  const marker={id:id+'/port-'+p.id,type:i===0?'entry':'exit',x:p.position[0]-12,y:p.position[1]-18,w:24,h:36,rotation:0,label:p.id,note:'接触面上的角色中心点'};
  doc.objects.push(marker);
  return {id:p.id,objectId:marker.id,position:p.position,normal:p.normal,
   connection:{status:'source_derived',region:{x:p.aperture[0],y:p.aperture[1],w:p.aperture[2],h:p.aperture[3]}},
   support:{objectId:id+'/platform-'+p.dock.support_indices[0],face:'top',status:'source_derived'},
   motion:{ingress:{directions:UNKNOWN,modes:UNKNOWN},egress:{directions:UNKNOWN,modes:UNKNOWN}},
   preconditions:{ingress:unknownState(),egress:unknownState()},seamIds:['seam-'+p.id],routeRoles:[]};
 });
 gc.relations=gc.ports.flatMap(a=>gc.ports.filter(b=>b.id!==a.id).map(b=>({from:a.id,to:b.id,status:UNKNOWN,routeIds:[],conditions:UNKNOWN,note:'Actual whole-map instance evidence is separate; no universal independent relation inferred'})));
 gc.space.seams=Object.values(module.ports).map(p=>({id:'seam-'+p.id,portId:p.id,region:{x:p.aperture[0],y:p.aperture[1],w:p.aperture[2],h:p.aperture[3]},status:'source_derived',allowedOverlap:p.kind==='vertical'?['exact_shared_landing','actor_body']:['actor_body','touching_floor_faces']}));
 gc.space.occupancy.objectIds=doc.objects.filter(o=>!['entry','exit','route'].includes(o.type)).map(o=>o.id);
 gc.space.actionClearance.regions=[];gc.space.actionClearance.coverage=UNKNOWN;
 gc.unlocks=[];
 gc.generation.parameters.moduleSourceVersion=module.content_version;
 gc.generation.parameters.policyBinding={sha256:sha(JSON.stringify({out:module.center_to_port,in:module.port_to_center})),scope:'A policy is a calibration candidate, not inferred physics'};
 const extents=[...doc.objects.map(o=>({x:o.x,y:o.y,w:Math.max(.000001,o.w),h:Math.max(.000001,o.h)})),...gc.space.dynamicEnvelopes.filter(e=>e.region!==UNKNOWN).map(e=>e.region)];
 const bx=Math.min(...extents.map(r=>r.x)),by=Math.min(...extents.map(r=>r.y));
 gc.space.bounds={x:bx,y:by,w:Math.max(...extents.map(r=>r.x+r.w))-bx,h:Math.max(...extents.map(r=>r.y+r.h))-by};
 doc.canvas.width=gc.space.bounds.w;doc.canvas.height=gc.space.bounds.h;
 gc.composition.cells=doc.objects.filter(o=>!['entry','exit','route'].includes(o.type)).map(o=>({id:o.id,contentVersion:'sha256:'+sha256(canonical(o)),objectIds:[o.id]}));
 gc.contentVersion=contentVersion(doc);gc.visualization={path:id+'.svg',contentVersion:gc.contentVersion};
 gc.staticChecks={result:'pass',contentVersion:gc.contentVersion,method:'existing Module schema + exact object payload + explicit contact ports',scope:'Structure/source only; actual joining physics recorded against the complete Map instance'};
 validateDocument(doc);validateGenerationContract(doc);
 const file=id+'.mapnote.json';fs.writeFileSync(path.join(out,file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,id+'.svg'),renderContractSvg(doc));
 entries.push({nodeId:module.id,id,contentVersion:gc.contentVersion,file,sha256:sha(fs.readFileSync(path.join(out,file))),rawPayloadVersion:module.content_version,physics:'UNKNOWN until explicit instance validation',productionAdmitted:false});
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({schema:'pcg/direct-module-catalog/v1',modules:entries,scope:'Canonical existing Module outputs; no global terrain source and no generic assembly admission'},null,2));
console.log(JSON.stringify({modules:entries.length,canonical:true}));
