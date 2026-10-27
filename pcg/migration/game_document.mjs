// Exact source dictionaries enter the existing output adapter; no physics claim.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {moduleDocument} from '../../tools/export-module-contracts.mjs';
import {contentVersion,validateGenerationContract,sha256,canonical,unknownState} from '../../module-contract.js';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const player=path.join(repo,'pcg/prototype/godot/scenes/player/player.tscn');
const sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const results=[];
if(process.argv[2]==='--finalize-list'){
 for(const file of JSON.parse(fs.readFileSync(process.argv[3]))){try{
  const doc=JSON.parse(fs.readFileSync(file)),c=doc.generationContract,b=c.space.bounds;
  c.version=2;c.foundation={version:'1.0',blockSize:128,widthBlocks:b.w/128,heightBlocks:b.h/128};
  c.closures=[];c.mirror={status:'UNKNOWN',validationIds:[]};
  for(const p of c.ports){const g=p.grid??{};p.stagingPosition=g.stagingPosition??p.position;delete p.grid;
   p.face=({'-1,0':'LEFT','1,0':'RIGHT','0,-1':'TOP','0,1':'BOTTOM'})[p.normal.join(',')];
   const obj=doc.objects.find(o=>o.id===p.support?.objectId);p.surface=obj?.type==='platform'?'ONE_WAY_PLATFORM':obj?'ROCK':'AIR';
   p.permission='INOUT';p.permissionStatus='declared_pending_boundary_probe';
  }
  c.relations=c.ports.flatMap(a=>c.ports.map(b=>({from:a.id,to:b.id,status:c.routes.some(r=>r.from===a.id&&r.to===b.id)?'path':'UNKNOWN',routeIds:c.routes.filter(r=>r.from===a.id&&r.to===b.id).map(r=>r.id),conditions:'UNKNOWN'})));
  const cases=JSON.parse(fs.readFileSync(path.join(path.dirname(file),'cases.json'))).cases;c.validations=[];
  for(const r of c.routes){r.requiredAbilities=cases[0].capabilities;r.actionTags=[];r.durationSeconds='UNKNOWN';r.resourceProfile={status:'UNKNOWN'};r.initialConditions={status:'UNKNOWN'};
   const a=c.ports.find(p=>p.id===r.from),b=c.ports.find(p=>p.id===r.to);r.localDisplacementBlocks=b.position.map((v,i)=>(v-a.position[i])/128);
   r.validationIds=['migration-'+r.id];c.validations.push({id:'migration-'+r.id,kind:'physics',contentVersion:c.contentVersion,routeId:r.id,from:r.from,to:r.to,result:'UNKNOWN',capabilityConfiguration:{available:cases[0].capabilities,equipment:'UNKNOWN'},entryState:unknownState(),method:'pending_original_game_migration_physics',coverage:{status:'NOT_RUN'},failures:[],unverified:['not_yet_run'],artifacts:[]});
  }
  const physical=doc.objects.filter(o=>!['entry','exit','anchor','route','note','trackLine','trackArc'].includes(o.type));
  c.composition.cells=physical.map(o=>({id:o.id,contentVersion:'sha256:'+sha256(canonical(o)),objectIds:[o.id]}));
  c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;for(const v of c.validations)v.contentVersion=c.contentVersion;
  fs.writeFileSync(file,JSON.stringify(doc,null,2)+'\n');results.push({file,...validateGenerationContract(doc)});
 }catch(error){results.push({file,wellFormed:false,conflict:String(error)});}}
 console.log(JSON.stringify(results));process.exit(0);
}
for(const {row,case:original,folder}of JSON.parse(fs.readFileSync(process.argv[2])).rows){
 try{
  const raw=structuredClone(original);delete raw.ports;
  const doc=moduleDocument({case:raw,result:'UNKNOWN',geometryDefinitions:{player:{size:[24,36],source:{path:path.relative(repo,player),sha256:sha(player)}},bell:{size:[28,34]},enemies:{}},generationMetadata:{producer:'pcg/migration/game_adapter.py'},sourceRun:'UNKNOWN',sourceCases:{path:folder+'/cases.json',sha256:sha(path.join(repo,folder,'cases.json'))},binding:'UNKNOWN'},row.sourceCommit);
  doc.title=row.title;const integration=doc.source.integration;doc.source={integration,repository:'zhipijun1996/gunman-rush',commit:row.sourceCommit,path:row.sourcePath,moduleId:row.id,kind:row.kind,original:row.data,method:row.method,arguments:row.arguments};
  doc.description='原游戏精确来源迁移候选；原接口、机关和调参保留，尚未取得新地基物理认证。';
  const c=doc.generationContract,id=doc.id;
  const skeleton=structuredClone(c.ports[0]);
  doc.objects=doc.objects.filter(o=>!['entry','exit'].includes(o.type));
  c.ports=original.ports.map(p=>{
    const out=structuredClone(skeleton);out.id=p.id;out.objectId=id+'/port-'+p.id;out.position=p.position;out.normal=p.normal;
    out.support=Number.isInteger(p.support_index)?{objectId:id+'/platform-'+p.support_index,face:'top',status:'source_derived'}:'UNKNOWN';
    out.seamIds=[p.id+'-seam'];out.routeRoles=[];out.sourceRoles=p.sourceRoles;out.sourcePort=p.sourcePort??{};
    doc.objects.push({id:out.objectId,type:p.sourceRoles.includes('entry')?'entry':'exit',x:p.position[0]-12,y:p.position[1]-18,w:24,h:36,rotation:0,label:p.id,note:'原角色身体站位；外边接口等待实际适配'});return out;
  });
  const route=c.routes[0],spec=original.route_spec;route.from=spec.from_port;route.to=spec.to_port;
  c.relations=c.ports.flatMap(a=>c.ports.filter(b=>b.id!==a.id).map(b=>({from:a.id,to:b.id,status:'UNKNOWN',routeIds:a.id===route.from&&b.id===route.to?[route.id]:[],conditions:'UNKNOWN'})));
  c.space.seams=c.ports.map(p=>({id:p.id+'-seam',portId:p.id,region:'UNKNOWN',status:'UNKNOWN',allowedOverlap:[]}));
  for(const p of c.ports)p.routeRoles=[...(p.id===route.from?['main:entry']:[]),...(p.id===route.to?['main:exit']:[])];
  for(const unlock of c.unlocks){unlock.before.from=route.from;unlock.before.to=route.to;unlock.after.from=route.from;unlock.after.to=route.to;}
  c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;
  validateGenerationContract(doc);
  const file=path.join(repo,folder,'module.mapnote.json');fs.writeFileSync(file,JSON.stringify(doc,null,2)+'\n');
  results.push({id:row.id,status:'decoded_unverified',document:path.relative(repo,file),documentSha256:sha(file)});
 }catch(error){results.push({id:row.id,status:'document_error',conflict:String(error)});}
}
console.log(JSON.stringify(results));
