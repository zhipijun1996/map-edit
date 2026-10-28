// Mounted receiver metadata over the frozen original and paired-gate adapters.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {canonical,contentVersion,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
const ownPath='pcg/prototype/creative_batches/batch30_runtime/export_mounted_v1.mjs';
const bytes=fs.readFileSync(path.join(repo,ownPath)),ownSha=createHash('sha256').update(bytes).digest('hex');
execFileSync(process.execPath,[path.join(here,'export_v1.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const item of manifest.modules){
 const doc=JSON.parse(fs.readFileSync(path.join(out,item.file))),gc=doc.generationContract;
 const row=bundle.rows.find(r=>(r.case.layout_uid??r.case.factory_id)===doc.id.replace(/^generated-/,''));
 for(const [i,l]of(row.case.latches??[]).entries()){
  if(!l.carrier_mount)continue;
  const carrier=doc.objects.find(o=>o.sourceId===l.carrier_mount),bell=doc.objects.find(o=>o.id===doc.id+'/bell-'+i);
  if(!carrier||!bell)throw Error('Mounted receiver requires its real exported carrier');
  const moving=row.case.moving_platforms.find(p=>p.platform_id===l.carrier_mount);
  const offset=[l.bell[0]-(carrier.x+carrier.w/2),l.bell[1]-(carrier.y+carrier.h/2)];
  bell.hostId=carrier.id;bell.mechanics={...bell.mechanics,kind:'carrier_mounted_original_receiver',hostId:carrier.id,localReceiverOffset:offset,
   attachment:'Original ShotLatch is reparented to original carrier with global transform preserved; receiver body and aim target move together',sourceField:'carrier_mount'};
  const xs=[moving.start[0]+offset[0],moving.finish[0]+offset[0]],ys=[moving.start[1]+offset[1],moving.finish[1]+offset[1]];
  gc.space.dynamicEnvelopes.push({objectId:bell.id,region:{x:Math.min(...xs)-bell.w/2,y:Math.min(...ys)-bell.h/2,w:Math.max(...xs)-Math.min(...xs)+bell.w,h:Math.max(...ys)-Math.min(...ys)+bell.h},status:'source_derived',coverage:'Full original carrier path plus fixed mounted receiver offset; original projectile collision body moves with receiver'});
 }
 for(const cell of gc.composition.cells){const objects=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(objects.length===1?objects[0]:objects));}
 gc.generation.source.exportSourceFiles.push({path:ownPath,sha256:ownSha});
 for(const v of gc.validations){const match=bundle.rows.find(r=>(r.case.route_spec?.id??'main')===v.routeId&&(r.case.layout_uid??r.case.factory_id)===row.case.layout_uid);v.coverage.mountedReceiverWitness=match?.result?.workshop?.mounted_bells??'UNKNOWN';}
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;
 for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);
 fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
const dest=path.join(out,'export-source',ownPath);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,bytes);
console.log(JSON.stringify({exported:manifest.modules.length,out,mountedReceiverAdapter:true}));
