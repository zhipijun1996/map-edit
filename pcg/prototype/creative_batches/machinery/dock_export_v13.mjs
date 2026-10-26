// Extend the canonical adapter with the real isolated dock Cell, retaining all objects.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {contentVersion,canonical,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const [source,out]=process.argv.slice(2);
const base=fileURLToPath(new URL('../../workshop/export.mjs',import.meta.url));
const child=spawnSync(process.execPath,[base,source,out],{stdio:'inherit'});if(child.status!==0)process.exit(child.status??1);
const bundle=JSON.parse(fs.readFileSync(source));const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const row of manifest.modules){
 const file=path.join(out,row.file),doc=JSON.parse(fs.readFileSync(file)),raw=bundle.rows.find(r=>r.case.family===row.family).case,c=doc.generationContract;
 doc.source.path='pcg/prototype/creative_batches/machinery/production_v14.py';
 for(const [i,spec]of raw.latches.entries()){
  if(!spec.carrier_dock)continue;
  const sensor=doc.objects.find(o=>o.id===doc.id+'/bell-'+i),gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i),r=spec.carrier_dock.rect;
  Object.assign(sensor,{type:'switch',x:r[0],y:r[1],w:r[2],h:r[3],label:'载台实体Dock',note:'原生Area2D只感应指定ModuleMovingPlatform实体；不是可射击铃',mechanics:{service:'CarrierDockLatch',platformId:spec.carrier_dock.platform_id,sensor:'native Area2D body_entered/body_exited',source:spec.carrier_dock}});
  gate.mechanics={kind:'carrier_occupancy_gate',holdWhileOccupied:true,closeDelaySeconds:spec.open_seconds,safeClose:'original ShotLatch anti-pinch close'};
  const unlock=c.unlocks.find(u=>u.trigger.objectId===sensor.id);if(unlock){unlock.trigger.condition='specified real carrier body overlaps native Area2D';unlock.changes={objectId:gate.id,openWhile:'real moving body occupies sensor',afterRelease:'original delayed anti-pinch close'};}
 }
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.generation.source.isolatedCell={runner:'pcg/prototype/creative_batches/machinery/dock_runner_v11.gd',cell:'pcg/prototype/creative_batches/machinery/dock_latch_v11.gd',binding:'pcg/prototype/creative_batches/machinery/dock_binding_v11.gd',identity:'exact bytes in physics source_binding/source_snapshot'};
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;c.validations.forEach(v=>v.contentVersion=c.contentVersion);c.staticChecks.contentVersion=c.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);fs.writeFileSync(file,JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));row.contentVersion=c.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
