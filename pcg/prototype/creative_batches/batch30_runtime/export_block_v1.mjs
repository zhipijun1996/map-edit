// Bind real staging witnesses to the upstream Block128 boundary interface.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {canonical,contentVersion,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
const policy=JSON.parse(fs.readFileSync(path.join(repo,'pcg/map_directed/block_grid/plains-policy.json')));
const ownSources=['module-block-grid.js','pcg/prototype/creative_batches/batch30_runtime/export_block_v1.mjs'];
const bindings=ownSources.map(p=>({path:p,sha256:createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex')}));
const mounted=bundle.rows.some(r=>(r.case.latches??[]).some(l=>l.carrier_mount));
const parent=path.join(here,mounted?'export_mounted_v1.mjs':'export_v1.mjs');
execFileSync(process.execPath,[parent,source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const item of manifest.modules){
 const doc=JSON.parse(fs.readFileSync(path.join(out,item.file))),gc=doc.generationContract;
 const rows=bundle.rows.filter(r=>(r.case.layout_uid??r.case.factory_id)===doc.id.replace(/^generated-/,''));
 const raw=rows[0].case,grid=raw.block_grid;
 if(!grid||grid.size!==policy.block_size||!raw.block_ports)throw Error('needs_design: current Map Block contract required');
 if(rows.some(r=>canonical(r.case.block_grid)!==canonical(grid)||canonical(r.case.block_ports)!==canonical(raw.block_ports)))throw Error('Routes must share the same Block world and interface');
 gc.space.blockGrid=structuredClone(grid);
 for(const p of gc.ports){
  const binding=raw.block_ports[p.id],actual=raw.ports.find(q=>q.id===p.id);
  if(!binding||canonical(binding.grid?.stagingPosition)!==canonical(actual?.position))throw Error('Unbound real staging checkpoint: '+p.id);
  const marker=doc.objects.find(o=>o.id===p.objectId);
  p.position=[...binding.position];p.normal=[...binding.normal];p.grid=structuredClone(binding.grid);
  p.crossing_offset=binding.crossing_offset??[0,14];
  p.connection={status:'declared',region:binding.aperture?{x:binding.aperture[0],y:binding.aperture[1],w:binding.aperture[2],h:binding.aperture[3]}:'UNKNOWN'};
  p.orientationSource='Upstream Block boundary normal; actual staging and boundary crossing remain distinct.';
  marker.x=p.position[0]-marker.w/2;marker.y=p.position[1]-marker.h/2;
 }
 for(const [i,latch]of(raw.latches??[]).entries()){
  if(!latch.ferry_id)continue;
  const gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i);
  gate.mechanics={...gate.mechanics,ferryId:latch.ferry_id};
  // Original bind_motion disables this constructor placeholder; it is not
  // a physical door or a remote occupied Block in the resulting module.
  gate.type='note';gate.note='原 bind_motion 已禁用的构造占位；真实输出是控制移动平台，不是远处碰撞门。';
  (gc.generation.parameters.disabledCarrierGateNotes??=[]).push(gate.id);
 }
 const size=grid.size,xs=grid.cells.map(c=>c[0]),ys=grid.cells.map(c=>c[1]);
 gc.space.physicalBoundsBeforeBlockOwnership=gc.space.bounds;
 gc.space.bounds={x:grid.origin[0]+Math.min(...xs)*size,y:grid.origin[1]+Math.min(...ys)*size,w:(Math.max(...xs)-Math.min(...xs)+1)*size,h:(Math.max(...ys)-Math.min(...ys)+1)*size};
 gc.space.boundsCoverage='Connected upstream Block ownership; actual objects, full known motion and sampled body sweeps independently retained. Unknown behaviour is not certified.';
 doc.canvas.width=gc.space.bounds.w;doc.canvas.height=gc.space.bounds.h;
 for(const cell of gc.composition.cells){const objects=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(objects.length===1?objects[0]:objects));}
 for(const v of gc.validations){
  const row=rows.find(r=>(r.case.route_spec?.id??'main')===v.routeId);
  v.coverage.stagingDirectionEvidence={from:raw.block_ports[gc.routes.find(r=>r.id===v.routeId).from].grid.stagingPosition,to:raw.block_ports[gc.routes.find(r=>r.id===v.routeId).to].grid.stagingPosition,caseSha256:row?.case.module_sha256??'UNKNOWN'};
  v.coverage.blockBoundaryCrossing='UNKNOWN unless independently bound continuous crossing fixture is supplied';
 }
 gc.generation.source.blockContractUpstream='a685faebdb7596b0808538ab9ef299d6455d2320';
 gc.generation.source.exportSourceFiles.push(...bindings);
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;
 for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateGenerationContract(doc);
 fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;item.blockSize=size;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
for(const b of bindings){const bytes=fs.readFileSync(path.join(repo,b.path));if(createHash('sha256').update(bytes).digest('hex')!==b.sha256)throw Error('Frozen export source changed');const dst=path.join(out,'export-source',b.path);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.writeFileSync(dst,bytes);}
console.log(JSON.stringify({exported:manifest.modules.length,blockSize:policy.block_size,out}));
