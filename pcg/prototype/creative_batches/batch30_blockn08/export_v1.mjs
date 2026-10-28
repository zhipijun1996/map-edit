// Isolated metadata attachment only: original Block exporter owns all geometry.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {canonical,contentVersion,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
const attachmentPath=path.join(here,'loop-attachment-v1.json'),attachment=JSON.parse(fs.readFileSync(attachmentPath));
const fileSha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function bound(ref){const p=path.resolve(repo,ref.path);if(!p.startsWith(repo+path.sep)||fileSha(p)!==ref.sha256)throw Error('Stale N08 loop artifact '+ref.path);return JSON.parse(fs.readFileSync(p));}
const loop=bound(attachment.loop_evidence),frozen=bound(attachment.frozen_loop_source_case).cases[0];bound(attachment.same_reward_comparison);
if(loop.status!=='scoped_regular_pass'||loop.layout_uid!==attachment.layout_uid||loop.actual_start!=='A'||loop.actual_end!=='A'||loop.new_modules!==0)throw Error('N08 requires separate qualified actualA-B-A fixture');
for(const ref of loop.artifacts)bound(ref);
const worldKeys=['platforms','ports','latches','reward_sites','block_grid','block_ports','block_reservations'];
const pick=c=>Object.fromEntries(worldKeys.map(k=>[k,c[k]]));
for(const row of bundle.rows){
 const c=row.case;
 if(c.fixture_kind==='same-world-A-B-A'||c.route_spec.from_port===c.route_spec.to_port)throw Error('Self-loop fixture is never a standard Module route');
 if(c.layout_uid!==loop.layout_uid||canonical(pick(c))!==canonical(pick(frozen)))throw Error('N08 loop geometry/ports/ownership not exact current world');
 const cp=c.control_plan,fp=frozen.control_plan;
 const expected=c.route_spec.id==='reward-outbound'?fp.slice(0,cp.length):c.route_spec.id==='lower-return'?fp.slice(-cp.length):null;
 if(!expected||canonical(cp)!==canonical(expected))throw Error('N08 changed actualdirectionprogram since continuousfixture');
}
const groups=new Map();for(const r of bundle.rows){const k=r.case.layout_uid;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(r);}
for(const rows of groups.values()){
 const f=rows.find(r=>r.case.route_spec.id==='reward-outbound'),b=rows.find(r=>r.case.route_spec.id==='lower-return');
 if(!f||!b||f.case.control_plan.length+b.case.control_plan.length!==frozen.control_plan.length)throw Error('Both original directions and full continuousprogram required');
}
execFileSync(process.execPath,[path.join(repo,'pcg/prototype/creative_batches/batch30_runtime/export_block_v1.mjs'),source,out],{cwd:repo});
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
const bindingPaths=[path.relative(repo,fileURLToPath(import.meta.url)),path.relative(repo,attachmentPath),attachment.loop_evidence.path,attachment.frozen_loop_source_case.path,attachment.same_reward_comparison.path];
const bindings=bindingPaths.map(p=>({path:p,sha256:fileSha(path.join(repo,p))}));
for(const item of manifest.modules){
 const p=path.join(out,item.file),doc=JSON.parse(fs.readFileSync(p)),gc=doc.generationContract;
 gc.generation.source.blockContractUpstream=attachment.source_map_contract;
 gc.generation.source.continuousLoopSidecar={...attachment,loopEvidenceStatus:loop.status,calibration:loop.calibration_stats,held:loop.held_stats,actualCases:loop.actual_cases,standardModuleRoute:false,doesNotGrantArbitraryReturnOrAssembly:true};
 gc.generation.source.exportSourceFiles.push(...bindings);
 gc.generation.parameters.N08ReturnChoice='Lowerbridge is an actualalternate return; oldupperrouteislegitimateandequalactions19framesfasterinexactcomparison. No shortcut/benefit/humanapprovalclaim.';
 for(const v of gc.validations)v.coverage.continuousLoopSupplement={artifact:attachment.loop_evidence,layout_uid:loop.layout_uid,actualPath:['A','B','A'],status:loop.status,separateFromFreshDirection:true,scope:'Samefrozengeometry/program, no boundary/wholeMap/generalstateproof'};
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateDocument(doc);const result=validateGenerationContract(doc);if(!result.versionMatches)throw Error('N08 final semanticversion mismatch');
 fs.writeFileSync(p,JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));item.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
for(const b of bindings){const src=path.join(repo,b.path);if(fileSha(src)!==b.sha256)throw Error('N08 export source changed');const dst=path.join(out,'export-source',b.path);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(src,dst);}
console.log(JSON.stringify({exported:manifest.modules.length,continuousLoopSupplement:'scoped_regular_pass',newLoopModuleCount:0}));
