import fs from 'node:fs';import path from 'node:path';import {execFileSync}from'node:child_process';
import {contentVersion,canonical,sha256,validateGenerationContract}from'../../../../module-contract.js';
import {validateDocument}from'../../../../model.js';import {renderContractSvg}from'../../../../module-contract-render.js';
const [bundlePath,out]=process.argv.slice(2),base=out+'-base',bundle=JSON.parse(fs.readFileSync(bundlePath));
execFileSync('node',[path.resolve('pcg/prototype/workshop/export.mjs'),bundlePath,base],{stdio:'inherit'});
if(fs.existsSync(out))throw Error('immutable_export_exists');fs.mkdirSync(out,{recursive:true});const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json')));
for(const item of manifest.modules){
 const doc=JSON.parse(fs.readFileSync(path.join(base,item.file))),c=doc.generationContract;
 const raw=bundle.rows.find(r=>'generated-'+r.case.factory_id===doc.id).case;
 for(const [i,l]of raw.latches.entries())if(l.occupancy){
  const sensor=doc.objects.find(o=>o.id===doc.id+'/bell-'+i),gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i),[x,y,w,h]=l.occupancy.rect;
  Object.assign(sensor,{type:'switch',x,y,w,h,label:l.occupancy.mode==='enemy_alive'?'活体感应区':'身体占位区',note:'真实Area2D占位；原ShotLatch弹丸接收器禁用，不是可射击风铃',mechanics:{service:'isolated OccupancyLatch v1',mode:l.occupancy.mode,originalBellBody:{position:l.bell,collisionLayer:0},sensorRect:l.occupancy.rect,source:'pcg/prototype/creative_batches/occupancy/occupancy_latch_v1.gd'}});
  gate.mechanics={kind:'occupancy_gate',condition:l.occupancy.mode,releaseGraceSeconds:l.open_seconds,clockAndAntiPinch:'original ShotLatch, unchanged'};
  c.unlocks[i].trigger={objectId:sensor.id,condition:'actual Area2D overlap by '+l.occupancy.mode+'; terminal enemy does not energize gate'};
  c.unlocks[i].changes={objectId:gate.id,collision:'disabled while qualifying body occupies sensor; original timed safe close after release'};
 }
 doc.source.path='pcg/prototype/creative_batches/occupancy/production_v2.py';
 c.generation.source.isolatedCell={service:'OccupancyLatch v1',implementation:'pcg/prototype/creative_batches/occupancy/occupancy_latch_v1.gd',physics:'original Godot bodies and Area2D; original ShotLatch anti-pinch/clock; original EnemyActor health and knockback'};
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;c.staticChecks.contentVersion=c.contentVersion;for(const v of c.validations)v.contentVersion=c.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);item.contentVersion=c.contentVersion;
 fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));
}fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
