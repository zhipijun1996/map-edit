// Thin, isolated metadata adapter after the original canonical exporter.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {canonical,contentVersion,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
const groups=new Map();
for(const row of bundle.rows){const k=row.case.layout_uid;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(row);}
for(const rows of groups.values()){
 const rewards=canonical(rows[0].case.reward_sites);
 if(rows.some(r=>canonical(r.case.reward_sites)!==rewards))throw Error('different shared reward world');
}
execFileSync(process.execPath,[path.join(repo,'pcg/prototype/workshop/export.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const item of manifest.modules){
 const doc=JSON.parse(fs.readFileSync(path.join(out,item.file))),gc=doc.generationContract;
 const rows=groups.get(doc.id.replace(/^generated-/,''));if(!rows)throw Error('missing layout rows');
 doc.source.path='pcg/prototype/creative_batches/plains50_ports/recipes_v2.py';
 doc.description='平原三/四端口分叉候选；同一真实几何、奖励与机关初态；有向见证不自动授权接缝或任意进入状态。';
 gc.staticChecks.scope=`${gc.ports.length} actual supported ports; all ${gc.ports.length*(gc.ports.length-1)} ordered relations; shared rewards and physical initial state; original schema.`;
 gc.generation.source.portRecipeAdapter='pcg/prototype/creative_batches/plains50_ports/export_v1.mjs';
 for(const p of gc.ports){
  // Normals describe intended interfaces only. All experiments start supported
  // and stop on support; incoming momentum has not been verified.
  p.motion={ingress:{directions:'UNKNOWN',modes:['supported_original_spawn']},egress:{directions:'UNKNOWN',modes:['supported_stable_observation']}};
  p.orientationSource='design interface normal; actual incoming/outgoing velocity set UNKNOWN until seam test';
 }
 for(const route of gc.routes){
  const row=rows.find(r=>r.case.route_spec.id===route.id);if(!row)throw Error('missing exact route');
  route.resourcePressure.rewardGrant=row.result?.workshop?.coins??'UNKNOWN';
  route.resourcePressure.note='Actual reward total from original transactions; shared scene includes all reward sites. No resource reset between via ports.';
  route.onward.note='Only listed route and via-port sequence were replayed continuously; any other return, entry state or seam remains UNKNOWN.';
  route.availability='authored initial scene and tested supported source port only';
 }
 for(const v of gc.validations){const row=rows.find(r=>r.case.route_spec.id===v.routeId);v.coverage.returnStateChaining=Boolean(row?.case.route_spec.via_ports?.length);v.coverage.sourcePortSceneReset=true;v.coverage.noResetWithinViaSequence=true;}
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;
 for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);
 fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
console.log(JSON.stringify({exported:manifest.modules.length,out}));
