// Metadata repair wrapper: original Block/mounted/Dock adapters own geometry.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {contentVersion,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const [source,out]=process.argv.slice(2);
execFileSync(process.execPath,[path.join(here,'../batch30_blockn13/export_v1.mjs'),source,out],{cwd:repo});
const receiptPath=path.join(here,'probe-receipt-v1.json');
const receipt=JSON.parse(fs.readFileSync(receiptPath));
if(receipt.status!=='screened_requires_original_full')throw Error('N13 repair has not completed frozen screen');
const bindingPaths=['api_v1.py','rules_v1.py','export_v1.mjs','protocol-v1.json','probe-receipt-v1.json','control-selection-v1.json'].map(p=>path.relative(repo,path.join(here,p)));
const sha=p=>createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex');
const bindings=bindingPaths.map(p=>({path:p,sha256:sha(p)}));
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const row of manifest.modules){
 const file=path.join(out,row.file),doc=JSON.parse(fs.readFileSync(file)),gc=doc.generationContract;
 doc.source.path='pcg/prototype/creative_batches/batch30_blockn13_repair/rules_v1.py';
 gc.generation.source.outerControlRepair={id:'B31-N13-repair',priorFailure:receipt.prior_failed_scope,sourceReceipt:path.relative(repo,receiptPath),priorCases:51,newProbeCases:receipt.actual_new_probe_cases,worldGeometryChanged:false,originalPhysicsUnchanged:true};
 gc.generation.source.exportSourceFiles.push(...bindings);
 gc.generation.parameters.N13StrategyScope='Parking is optional for outbound: fast no-stop is a legitimate alternative. Nominal parking must retain actual deck support and keep real Dock gate held at B. Separate same-world return evidence grants no fresh B-to-A or arbitrary return.';
 gc.generation.source.sameWorldReturnSupplement={...receipt.continuous_return,standardModuleRoute:false,originalRegularCertification:'UNKNOWN',freshBtoA:'UNKNOWN',wholeMap:'UNKNOWN'};
 gc.contentVersion=contentVersion(doc);gc.visualization.contentVersion=gc.contentVersion;gc.staticChecks.contentVersion=gc.contentVersion;
 for(const v of gc.validations)v.contentVersion=gc.contentVersion;
 validateDocument(doc);const result=validateGenerationContract(doc);if(!result.versionMatches)throw Error('N13 repair semantic version mismatch');
 fs.writeFileSync(file,JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));row.contentVersion=gc.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
for(const b of bindings){const src=path.join(repo,b.path);if(sha(b.path)!==b.sha256)throw Error('N13 export source changed');const dst=path.join(out,'export-source',b.path);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(src,dst);}
