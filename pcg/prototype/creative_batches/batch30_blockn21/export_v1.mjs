// Existing sequence object mapping on the canonical multi-route Block exporter.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {contentVersion,canonical,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
execFileSync(process.execPath,[path.join(here,'../batch30_runtime/export_block_v1.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
const bindingPaths=['pcg/prototype/creative_batches/batch30_blockn21/export_v1.mjs','pcg/prototype/creative_batches/plains50_new_relations/sequence_runner_v1.gd','pcg/prototype/creative_batches/plains50_new_relations/sequence_main_v1.gd'];
const bindings=bindingPaths.map(p=>({path:p,sha256:createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex')}));
for(const item of manifest.modules){
 const file=path.join(out,item.file),doc=JSON.parse(fs.readFileSync(file)),gc=doc.generationContract;
 const raw=bundle.rows.find(r=>(r.case.layout_uid??r.case.factory_id)===doc.id.replace(/^generated-/,'' )).case;
 for(const [i,spec]of raw.latches.entries()){
  if(!spec.sequence_offset)continue;
  const bell=doc.objects.find(o=>o.id===doc.id+'/bell-'+i),gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i),point=[spec.bell[0]+spec.sequence_offset[0],spec.bell[1]+spec.sequence_offset[1]],r=spec.sequence_gate;
  const second={id:doc.id+'/sequence-bell-'+i,type:'bell',x:point[0]-14,y:point[1]-17,w:28,h:34,rotation:0,label:'第二铃：补完东门',sourceId:spec.id+'/second',targetId:gate.id,note:'原ShotLatch第二receiver，只在sequence_step=1时接受真实弹丸；最终开门后layer0，计时分支不会恢复此body',mechanics:{service:'ShotLatch',sequenceOrdinal:2,expectedSequenceStep:1,sharesHealthWith:bell.id,finalCollisionLayer:0,timerRestoresSecondBody:false}};
  const first={id:doc.id+'/sequence-gate-'+i,type:'gate',x:r[0],y:r[1],w:r[2],h:r[3],rotation:0,label:'首铃永久撤去庭院隔断',sourceId:spec.id+'/sequence-gate',note:'原sequence_gate_rect，不是最终门；step1持久退碰撞',mechanics:{service:'ShotLatch.restore_sequence_gate',removedAtSequenceStep:1,permanentProgress:true}};
  bell.mechanics={service:'ShotLatch',sequenceOrdinal:1,expectedSequenceStep:0,commitsSequenceStep:1,targetId:first.id};
  gate.mechanics={service:'ShotLatch',kind:'permanent_sequence_final_gate',requiresReceiver:second.id,requiresSequenceStep:1,openSeconds:spec.open_seconds,doesNotResetSequenceProgress:true};
  for(const o of [second,first]){doc.objects.push(o);gc.space.occupancy.objectIds.push(o.id);gc.composition.cells.push({id:o.id,objectIds:[o.id],contentVersion:'sha256:'+sha256(canonical(o))});}
  const u=gc.unlocks.find(u=>u.trigger.objectId===bell.id);
  if(!u)throw Error('Original sequence final unlock missing');
  u.trigger={objectId:second.id,condition:'eligible original player projectile while sequence_step=1 and final gate not already open'};
  u.changes={objectId:gate.id,collision:'disabled permanently',secondReceiverCollisionLayer:0,sequenceStepRemains:1};
  u.before={from:'A',to:'C',status:'UNKNOWN',conditions:[{field:'mechanisms.'+spec.id+'.sequence_step',op:'eq',value:1}]};
  u.after={from:'A',to:'C',status:'UNKNOWN',conditions:[{field:'mechanisms.'+spec.id+'.is_open',op:'eq',value:true}]};u.affectedRouteIds=['A-to-C'];
  for(const target of ['B','C'])gc.unlocks.push({id:spec.id+'/stage1/'+target,trigger:{objectId:bell.id,condition:'eligible original player projectile while sequence_step=0'},changes:{objectId:first.id,collision:'disabled permanently',sequenceStep:1},before:{from:'A',to:target,status:'UNKNOWN',conditions:[{field:'mechanisms.'+spec.id+'.sequence_step',op:'eq',value:0}]},after:{from:'A',to:target,status:'UNKNOWN',conditions:[{field:'mechanisms.'+spec.id+'.sequence_step',op:'eq',value:1}]},affectedRouteIds:['A-to-'+target]});
 }
 for(const cell of gc.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 gc.generation.source.sequenceAdapter={originalCell:'pcg/prototype/godot/scripts/world/shot_latch.gd',originalInstall:'pcg/prototype/creative_batches/plains50_new_relations/sequence_runner_v1.gd',sourceBinding:'exact bytes in physics source_snapshot',secondReceiverAfterOpen:'layer0; no timer restore claim',actualMapConsumer:'UNKNOWN'};
 gc.generation.source.exportSourceFiles.push(...bindings);
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateDocument(doc);const result=validateGenerationContract(doc);if(!result.versionMatches)throw Error('N21 semantic version mismatch');
 fs.writeFileSync(file,JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
for(const b of bindings){const dst=path.join(out,'export-source',b.path);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(path.join(repo,b.path),dst);}
