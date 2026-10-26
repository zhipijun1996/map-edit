import fs from 'node:fs';import path from 'node:path';import {execFileSync}from'node:child_process';
import {contentVersion,canonical,sha256,validateGenerationContract}from'../../../../module-contract.js';
import {validateDocument}from'../../../../model.js';import {renderContractSvg}from'../../../../module-contract-render.js';
const [bundlePath,out]=process.argv.slice(2),base=out+'-base',bundle=JSON.parse(fs.readFileSync(bundlePath));
execFileSync('node',[path.resolve('pcg/prototype/workshop/export.mjs'),bundlePath,base],{stdio:'inherit'});
if(fs.existsSync(out))throw Error('immutable_export_exists');fs.mkdirSync(out,{recursive:true});const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json')));
for(const item of manifest.modules){
 const doc=JSON.parse(fs.readFileSync(path.join(base,item.file))),c=doc.generationContract;
 const raw=bundle.rows.find(r=>'generated-'+r.case.factory_id===doc.id).case;
 for(const [i,l]of raw.latches.entries()){
  const trigger=doc.objects.find(o=>o.id===doc.id+'/bell-'+i),gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i);
  if(l.occupancy){
   const[x,y,w,h]=l.occupancy.rect;Object.assign(trigger,{type:'switch',x,y,w,h,label:'存活敌体感应区',note:'真实Area2D仅认活EnemyActor；原弹丸接收器禁用',mechanics:{service:'OccupancyLatch v1',mode:l.occupancy.mode,sensorRect:l.occupancy.rect,originalBellBody:{position:l.bell,collisionLayer:0},source:'pcg/prototype/creative_batches/occupancy/occupancy_latch_v1.gd'}});
   gate.mechanics={kind:'occupancy_gate',condition:l.occupancy.mode,releaseGraceSeconds:l.open_seconds,clockAndAntiPinch:'original ShotLatch unchanged'};
   c.unlocks[i].trigger={objectId:trigger.id,condition:'actual live EnemyActor overlaps original Godot Area2D'};
   c.unlocks[i].changes={objectId:gate.id,collision:'disabled while qualifying body occupies sensor, original safe closing after release'};
  }
  if(l.attack_relay){
   const enemyIndex=raw.enemies.findIndex(e=>e.id===l.attack_relay.enemy_id),enemyId=doc.id+'/enemy-'+enemyIndex;
   Object.assign(trigger,{type:'switch',label:'敌人攻击继电器',note:'真实EnemyAttackBehavior进入attack时驱动；不是可射击风铃',mechanics:{service:'AttackRelayLatch v1',enemyObjectId:enemyId,onNativeState:'attack',originalBellBody:{position:l.bell,collisionLayer:0},source:'pcg/prototype/creative_batches/enemy_world/attack_relay_v1.gd'}});
   gate.mechanics={kind:'enemy_attack_relay_gate',enemyObjectId:enemyId,onNativeState:'attack',openSeconds:l.open_seconds,clockAndAntiPinch:'original ShotLatch unchanged'};
   c.unlocks[i].trigger={objectId:enemyId,condition:'original EnemyAttackBehavior state_changed attack; native projectile firing remains active'};
   c.unlocks[i].changes={objectId:gate.id,collision:'disabled for original timer after actual enemy attack commitment'};
  }
 }
 for(const[i,e]of raw.enemies.entries())if(e.variant_definition){
  const enemy=doc.objects.find(o=>o.id===doc.id+'/enemy-'+i);enemy.mechanics={kind:'derived_real_EnemyDefinition',originalDefinition:'res://resources/enemies/plains_charger.tres',derivedDefinition:e.variant_definition,definitionSource:'pcg/prototype/creative_batches/enemy_world/guard_charger_v1.tres',sourceSha256:e.variant_tres_sha256,overrides:{stable_id:'enemy_world_guard_charger_v1',definition_version:1,patrol_speed:0},health:'original patrol_health.tres 3HP unchanged',behavior:'original EnemyAttackBehavior/EnemyMotor/EnemyActor; original telegraph, charge, recovery, accepted-hit knockback',nativeResourceShaCheckedEveryCase:true};
 }
 doc.source.path=raw.generation_rule.source_path;
 c.generation.source.enemyWorldCells=raw.world_cell_sources??'UNKNOWN';
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;c.staticChecks.contentVersion=c.contentVersion;for(const v of c.validations)v.contentVersion=c.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);item.contentVersion=c.contentVersion;
 fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));
}fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
