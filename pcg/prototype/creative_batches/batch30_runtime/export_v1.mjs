// Extend original canonical exports with the complementary-gate Cell only.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {canonical,contentVersion,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';

const here=path.dirname(fileURLToPath(import.meta.url)), repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2), bundle=JSON.parse(fs.readFileSync(source));
const outputSources=['model.js','capabilities.js','difficulty.js','module-contract.js','module-contract-render.js','tools/export-module-contracts.mjs','pcg/prototype/workshop/export.mjs','pcg/prototype/creative_batches/batch30_runtime/export_v1.mjs'].map(p=>({path:p,sha256:createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex')}));
const grouped=new Map();
for(const row of bundle.rows){
  const key=row.case.layout_uid??row.case.factory_id;
  if(!grouped.has(key))grouped.set(key,[]);
  grouped.get(key).push(row);
}
for(const rows of grouped.values()){
  if(rows.some(r=>canonical(r.case.reward_sites)!==canonical(rows[0].case.reward_sites)))throw Error('Different reward worlds cannot share a Module');
}
execFileSync(process.execPath,[path.join(repo,'pcg/prototype/workshop/export.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const item of manifest.modules){
  const doc=JSON.parse(fs.readFileSync(path.join(out,item.file))), gc=doc.generationContract;
  const rows=grouped.get(doc.id.replace(/^generated-/,'')), raw=rows[0].case;
  doc.source.path=raw.generation_rule?.source_path??'UNKNOWN';
  doc.description='平原动作内容候选：核心动作/世界后果、技术覆盖、人工观感分别记录；未验方向与Map状态保持UNKNOWN。';
  gc.generation.source.batchAdapter='pcg/prototype/creative_batches/batch30_runtime/export_v1.mjs';
  gc.generation.source.exportSourceFiles=outputSources;
  for(const [index,spec]of(raw.latches??[]).entries()){
    if(!spec.paired_gate)continue;
    const bell=doc.objects.find(o=>o.id===doc.id+'/bell-'+index), first=doc.objects.find(o=>o.id===doc.id+'/gate-'+index);
    const [x,y,w,h]=spec.paired_gate;
    const second={id:doc.id+'/paired-gate-'+index,type:'gate',x,y,w,h,rotation:0,label:spec.id+' / B',note:'与A门互斥的真实第二碰撞门，非装饰',sourceId:spec.id+'/B'};
    const mechanism={kind:'complementary_gates',initialOpen:spec.initial_open??'A',gateA:first.id,gateB:second.id,
      invariant:'exactly_one_open',switch:'eligible original projectile atomically swaps complementary collision states',
      antiPinch:'reject entire switch while the closing gate overlaps the player or another real character body',
      resourcePolicy:'original projectile, recoil, cooldown and hit recovery unchanged; no scripted resource writes'};
    first.mechanics={...mechanism,member:'A'};second.mechanics={...mechanism,member:'B'};
    bell.mechanics=mechanism;bell.targetIds=[first.id,second.id];
    doc.objects.push(second);gc.space.occupancy.objectIds.push(second.id);
    gc.composition.cells.push({id:second.id,contentVersion:'sha256:'+sha256(canonical(second)),objectIds:[second.id]});
    gc.unlocks[index].changes={objectIds:[first.id,second.id],mechanism,automaticClose:false,
      note:'A repeated switch, not a permanent unlock or one-way proof'};
    for(const phase of ['before','after']){
      gc.unlocks[index][phase].from=gc.routes[0].from;gc.unlocks[index][phase].to=gc.routes[0].to;
      gc.unlocks[index][phase].status='UNKNOWN';delete gc.unlocks[index][phase].routeId;
      gc.unlocks[index][phase].conditions=[{field:'mechanisms.'+spec.id+'.open_a',op:'eq',value:phase==='before'?(spec.initial_open??'A')==='A':(spec.initial_open??'A')!=='A'}];
    }
    gc.space.dynamicEnvelopes.push({objectId:second.id,region:{x,y,w,h},status:'source_derived',coverage:'fixed collision area; open/closed state is complementary to gate A'});
  }
  for(const cell of gc.composition.cells){
    const objects=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));
    cell.contentVersion='sha256:'+sha256(canonical(objects.length===1?objects[0]:objects));
  }
  for(const route of gc.routes){
    const row=rows.find(r=>(r.case.route_spec?.id??'main')===route.id);
    route.resourcePressure.rewardGrant=row?.result?.workshop?.coins??'UNKNOWN';
    route.resourcePressure.note='Actual original reward transactions and sampled movement/resource costs; variants do not transfer approval.';
    route.onward.note='Only this local route and declared continuous visits were witnessed; arbitrary return, placement and seams remain UNKNOWN.';
  }
  for(const validation of gc.validations){
    const row=rows.find(r=>(r.case.route_spec?.id??'main')===validation.routeId);
    validation.coverage.noWorldResetWithinProgram=true;
    validation.coverage.complementaryGateWitness=row?.result?.workshop?.paired_gates??'not applicable';
    if(validation.observedExit&&typeof validation.observedExit==='object')validation.observedExit.batchMechanisms=row?.result?.workshop??'UNKNOWN';
  }
  const geometry=doc.objects.filter(o=>!o.points), b=gc.space.bounds;
  const x=Math.min(b.x,...geometry.map(o=>o.x)), y=Math.min(b.y,...geometry.map(o=>o.y));
  gc.space.bounds={x,y,w:Math.max(b.x+b.w,...geometry.map(o=>o.x+o.w))-x,h:Math.max(b.y+b.h,...geometry.map(o=>o.y+o.h))-y};
  doc.canvas.width=gc.space.bounds.w;doc.canvas.height=gc.space.bounds.h;
  gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;
  for(const v of gc.validations)v.contentVersion=gc.contentVersion;
  validateDocument(doc);validateGenerationContract(doc);
  fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));
  fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
for(const binding of outputSources){
  const bytes=fs.readFileSync(path.join(repo,binding.path));
  if(createHash('sha256').update(bytes).digest('hex')!==binding.sha256)throw Error('Output source changed while exporting');
  const destination=path.join(out,'export-source',binding.path);fs.mkdirSync(path.dirname(destination),{recursive:true});fs.writeFileSync(destination,bytes);
}
console.log(JSON.stringify({exported:manifest.modules.length,out}));
