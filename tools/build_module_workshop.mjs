// An index of existing documents/evidence, never another candidate library or physics validator.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {validateGenerationContract} from '../module-contract.js';
import {renderContractSvg} from '../module-contract-render.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=v=>createHash('sha256').update(v).digest('hex');
const write=(p,d)=>{const s=typeof d==='string'?d:JSON.stringify(d,null,2)+'\n';const full=path.join(root,p);if(fs.existsSync(full)&&fs.readFileSync(full,'utf8')===s)return;fs.mkdirSync(path.dirname(full),{recursive:true});fs.writeFileSync(full,s);};
const out='generation/module-workshop',snapshotFile=out+'/implementation-snapshot.json';
const href=(ref,p)=>`https://github.com/zhipijun1996/map-edit/blob/${ref}/${p.replace(/^\.\//,'')}`;
const rawHref=(ref,p)=>`https://raw.githubusercontent.com/zhipijun1996/map-edit/${ref}/${p.replace(/^\.\//,'')}`;
function project(doc){
 const check=validateGenerationContract(doc);if(!check.versionMatches)throw Error('stale Module content version '+doc.id);
 const c=doc.generationContract;if(c.version!==2)throw Error('Foundation v2 is required');
 return {foundation:c.foundation,ports:c.ports.map(({id,position,face,surface,permission,initialPermissionConditions})=>({id,position,face,surface,permission,initialPermissionConditions})),
  routes:c.routes.map(r=>({id:r.id,from:r.from,to:r.to,role:r.role,capabilityRequirements:r.capabilityRequirements,requiredAbilities:r.requiredAbilities??[],transferStatus:r.transfer?.status??'UNKNOWN'})),
  relations:c.relations,capabilityRequirements:doc.capabilityRequirements,foundationCheck:'PASS',mapReady:false};
}
function projectResult(row,ref){
  const {result,document:doc,resultReference}=row,declaredStatus=result.status??result.localTechnicalQualification??'UNKNOWN';
  let interfaceData=null,structuralError=null,diagram=null;
  if(doc){try{interfaceData=project(doc);}catch(e){structuralError=e.message;}
   diagram=`images/implementation-${row.reviewId}-${result.module.sha256.slice(0,12)}.svg`;
   write(out+'/'+diagram,renderContractSvg(doc,{review:true}));
  }
  const videos=[...(result.videos??[]),...(result.video?[result.video]:[])].filter(v=>v.movie?.path).map(v=>({url:rawHref(ref,v.movie.path),comparison:v.comparison??result.videoStrictComparison??'UNKNOWN'}));
  return {reviewId:row.reviewId,moduleId:result.moduleId,designVersion:result.designVersion,implementationVersion:result.implementationVersion??null,declaredStatus,
   resultReference,resultUrl:href(ref,resultReference.path),moduleReference:result.module??null,moduleUrl:result.module?href(ref,result.module.path):null,
   downloadUrl:result.module?rawHref(ref,result.module.path):null,diagram,interface:interfaceData,structuralError,
   nativePlayable:result.nativePlayable?.passed===true||result.nativePlayable?.verification?.passed===true||result.nativePlayable?.result?.passed===true,playableUrl:result.nativePlayable?.manifest?href(ref,result.nativePlayable.manifest.path):null,
   videos,scope:result.scope??{orientation:'identity',mirror:'UNKNOWN',closureConfigurations:'UNKNOWN',fullMap:'UNKNOWN'},
   humanPlaytest:result.humanPlaytest??'UNKNOWN',productionApproval:false};
}
if(process.argv.includes('--import-snapshot')){
 const input=JSON.parse(fs.readFileSync(process.argv[process.argv.indexOf('--import-snapshot')+1],'utf8'));
 if(!/^[a-f0-9]{40}$/.test(input.ref))throw Error('immutable source commit required');
 const rows=input.rows.map(row=>{
  return projectResult(row,input.ref);
 });
 write(snapshotFile,{schema:'pcg/module-workshop-implementation-projection/v1',repository:input.repository,ref:input.ref,pullRequest:input.pullRequest,merged:input.merged,
  indices:input.indices??[],source:'Existing read-only implementation receipts; no evidence rerun, promotion, or production approval',rows});
}
const queue=read('generation/manual-review/queue.json'),handoff=read('feedback/manual-review/implementation-handoff-v1.json');
const sourceCatalog=read('modules/catalog.json'),original=new Map(sourceCatalog.modules.map(m=>[m.id,m]));
const snapshot=fs.existsSync(path.join(root,snapshotFile))?read(snapshotFile):{rows:[]};
const implementations=new Map(snapshot.rows.map(r=>[r.reviewId,r]));
const ideas=read('feedback/module-workshop/ideas-v1.json');
const rows=handoff.rows.map(h=>{
 const idea=ideas.rows.find(r=>r.id===h.moduleId);
 if(idea?.implementationResult){
  const reference=idea.implementationResult,raw=fs.readFileSync(path.join(root,reference.path));if(hash(raw)!==reference.sha256)throw Error('implementation result changed');
  const result=JSON.parse(raw),moduleRaw=result.module?fs.readFileSync(path.join(root,result.module.path)):null;
  if(moduleRaw&&hash(moduleRaw)!==result.module.sha256)throw Error('implementation Module SHA changed');
  implementations.set(h.reviewId,projectResult({reviewId:h.reviewId,result,resultReference:reference,document:moduleRaw?JSON.parse(moduleRaw):null},'main'));
 }
 const q=queue.rows.find(r=>r.reviewId===h.reviewId)??(idea?.humanApproval==='KEEP'?{receivedDecision:'KEEP',contentVersion:idea.design.version,title:idea.title,summary:idea.verbatim,category:'新创意'}:null);if(!q||q.receivedDecision!=='KEEP'||q.contentVersion!==h.designVersion)throw Error('approval does not bind '+h.reviewId);
 const bytes=fs.readFileSync(path.join(root,h.designFile));if(hash(bytes)!==h.designFileSha256)throw Error('approved snapshot changed '+h.reviewId);
 const doc=JSON.parse(bytes),base=original.get(h.moduleId),impl=implementations.get(h.reviewId);
 const currentDesign=h.designFileKind==='source_module_reference'?doc.generationContract.contentVersion:doc.designVersion;
 if(currentDesign!==h.designVersion)throw Error('handoff design version mismatch');
 let stage='READY_FOR_IMPLEMENTATION',interfaceData=null,diagram=idea?.design?.diagram??'../manual-review/'+q.diagram;
 if(impl){
  if(impl.designVersion!==h.designVersion)stage='NEEDS_ALIGNMENT';
  else if(impl.declaredStatus!=='PASS'||!impl.interface||!impl.nativePlayable)stage='NEEDS_REPAIR';
  else {stage='IMPLEMENTED_CANDIDATE';interfaceData=impl.interface;diagram=impl.diagram;}
 }
 if(stage==='IMPLEMENTED_CANDIDATE'&&base?.contentSha256===impl.moduleReference?.sha256&&base?.contentVersion===impl.implementationVersion){
  const raw=fs.readFileSync(path.join(root,base.file));if(hash(raw)!==base.contentSha256)throw Error('archive source SHA changed');
  interfaceData=project(JSON.parse(raw));stage='ARCHIVED';diagram='../../'+base.thumbnail.replace(/^\.\//,'');
 }
 // An unchanged human-approved reference already in the formal archive is distinct from a new implementation candidate.
 if(h.designFileKind==='source_module_reference'&&base?.contentSha256===h.designFileSha256){interfaceData=project(doc);stage='ARCHIVED';diagram='../../'+base.thumbnail.replace(/^\.\//,'');}
 if(!interfaceData){
  if(doc.schema==='pcg/module-design/v1')interfaceData={foundation:{blockSize:doc.blockSize,widthBlocks:doc.bounds.w/doc.blockSize,heightBlocks:doc.bounds.h/doc.blockSize},ports:doc.ports,routes:doc.intendedRoutes.map(r=>({...r,capabilityRequirements:r.capabilityRequirements??doc.capabilityRequirements??{version:1,status:'unspecified',allOf:[],anyOfGroups:[],note:''}})),relations:[],capabilityRequirements:doc.capabilityRequirements,foundationCheck:'DESIGN_ONLY',mapReady:false};
  else interfaceData=project(doc);
 }
 return {id:h.moduleId,reviewId:h.reviewId,title:q.title,summary:q.summary,category:base?.category??q.category,stage,diagram,...interfaceData,
  designVersion:h.designVersion,designFile:h.designFile,designFileSha256:h.designFileSha256,designUrl:href('main',h.designFile),
  reviewUrl:idea?'#ideas':`../manual-review/?batch=${queue.batches.find(b=>b.reviewIds.includes(h.reviewId)).id}#r${h.reviewId}`,
  implementation:impl??null,archiveUrl:stage==='ARCHIVED'?'../../'+base.file.replace(/^\.\//,''):null,
  productionApproval:false,humanPlaytest:impl?.humanPlaytest??'UNKNOWN'};
});
for(const idea of ideas.rows){
 if(idea.design){const raw=fs.readFileSync(path.join(root,idea.design.file));if(hash(raw)!==idea.design.sha256)throw Error('idea design SHA changed');if(JSON.parse(raw).designVersion!==idea.design.version)throw Error('idea version mismatch');}
 if(!['IDEA','DESIGN_REVIEW','READY_FOR_IMPLEMENTATION','DISCARDED'].includes(idea.stage))throw Error('Unsupported idea stage');
 if(idea.stage==='READY_FOR_IMPLEMENTATION'){const r=handoff.rows.find(r=>r.moduleId===idea.id);if(!r||r.designVersion!==idea.design.version||idea.humanApproval!=='KEEP')throw Error('Approved idea lacks exact handoff');const raw=fs.readFileSync(path.join(root,idea.decisionReceipt.path));if(hash(raw)!==idea.decisionReceipt.sha256)throw Error('human receipt changed');const receipt=JSON.parse(raw);if(receipt.decision!=='KEEP'||receipt.designVersion!==idea.design.version||receipt.sourceType!=='human_feedback')throw Error('human approval mismatch');}
}
const counts=Object.fromEntries(['ARCHIVED','IMPLEMENTED_CANDIDATE','READY_FOR_IMPLEMENTATION','NEEDS_REPAIR','NEEDS_ALIGNMENT'].map(s=>[s,rows.filter(r=>r.stage===s).length]));
const sources={catalogSha256:hash(fs.readFileSync(path.join(root,'modules/catalog.json'))),handoffRevision:handoff.revision,
 implementationCommit:snapshot.ref??null,implementationPullRequest:snapshot.pullRequest??null,implementationMerged:snapshot.merged??false,
 reportedTechnicalPass:snapshot.rows.filter(r=>r.declaredStatus==='PASS').length};
write(out+'/data.json',{schema:'pcg/module-workshop-view/v1',counts,sources,modules:rows,ideas:ideas.rows,
 policy:{productionApproval:false,designOnlyIsNotImplementation:true,archiveRequiresExistingValidatedModule:true,localDraftsAreNotRepositoryReceipts:true}});
console.log(JSON.stringify({counts,approvedDesigns:rows.length,newIdeas:ideas.rows.length,sourceCommit:snapshot.ref??null,physicsRun:false}));
