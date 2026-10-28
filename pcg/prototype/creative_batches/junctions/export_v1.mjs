// Bind local junction intent after the original Module/physics exporter.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {canonical,contentVersion,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';

const here=path.dirname(fileURLToPath(import.meta.url)), repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2), bundle=JSON.parse(fs.readFileSync(source));
const groups=new Map();
const physicalKeys=['capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports','reward_sites'];
for(const row of bundle.rows){
  const key=row.case.layout_uid;
  if(!key)throw Error('junction layout identity required');
  if(!groups.has(key))groups.set(key,[]);
  groups.get(key).push(row);
}
for(const rows of groups.values()){
  const signature=row=>canonical(Object.fromEntries(physicalKeys.map(k=>[k,row.case[k]??[]])));
  if(rows.some(r=>signature(r)!==signature(rows[0])))throw Error('junction routes do not share one physical world');
}
execFileSync(process.execPath,[path.join(repo,'pcg/prototype/workshop/export.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const item of manifest.modules){
  const doc=JSON.parse(fs.readFileSync(path.join(out,item.file))), gc=doc.generationContract;
  const rows=groups.get(doc.id.replace(/^generated-/,'')), raw=rows[0].case;
  doc.source.path=raw.generation_rule.source_path;
  doc.description='平原空间选择节点：不同继续开口共享同一真实世界；只授权已列出的局部路线见证，人工观感与整图集成待验证。';
  gc.generation.source.junctionAdapter='pcg/prototype/creative_batches/junctions/export_v1.mjs';
  gc.generation.parameters.junction={role:raw.map_specification.objective.junction_role??'UNKNOWN',ideaIds:raw.idea_ids,
    semanticScope:'local choice, not regional topology',humanApproval:'UNKNOWN'};
  for(const port of gc.ports){
    port.motion={ingress:{directions:'UNKNOWN',modes:['supported_original_spawn']},egress:{directions:'UNKNOWN',modes:['supported_stable_observation']}};
    port.orientationSource='authored external opening normal; incoming/outgoing seam motion remains UNKNOWN';
  }
  for(const route of gc.routes){
    const row=rows.find(r=>r.case.route_spec.id===route.id);
    route.resourcePressure.rewardGrant=row.result.workshop?.coins??'UNKNOWN';
    route.resourcePressure.note='No mandatory reward transaction; static routes may walk, jump or recoil. No resource writes or resets within a route.';
    route.availability='authored supported source port and exact shared initial world';
    route.onward.note='Only listed local route and declared via sequence validated. Other directions, arbitrary ingress and Map composition remain UNKNOWN.';
  }
  for(const validation of gc.validations){
    const row=rows.find(r=>r.case.route_spec.id===validation.routeId);
    validation.coverage.noResetWithinViaSequence=true;
    validation.coverage.returnStateChaining=Boolean(row.case.route_spec.via_ports?.length);
    validation.coverage.sourcePortSceneReset=true;
  }
  gc.contentVersion=contentVersion(doc); gc.visualization.contentVersion=gc.contentVersion;
  gc.staticChecks.contentVersion=gc.contentVersion;
  for(const v of gc.validations)v.contentVersion=gc.contentVersion;
  validateDocument(doc); validateGenerationContract(doc);
  fs.writeFileSync(path.join(out,item.file),JSON.stringify(doc,null,2));
  fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));
  item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
console.log(JSON.stringify({exported:manifest.modules.length,out}));
