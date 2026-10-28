// Read-only review material. Reuse the editor's renderer; never qualify or rewrite Modules.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {renderContractSvg} from '../module-contract-render.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'generation/manual-review');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const write=(p,s)=>{if(fs.existsSync(p)&&fs.readFileSync(p,'utf8')===s)return;fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,s);};
const catalog=read('modules/catalog.json');
const previous=fs.existsSync(path.join(out,'queue.json'))?read('generation/manual-review/queue.json'):null;
const old=new Map((previous?.rows??[]).map(r=>[r.moduleId,r]));
const first=read('generation/manual-review/batch-001/batch.json').rows;
const hints=new Map(first.map(r=>[r.moduleId,r]));
const documents=new Map();
let next=Math.max(0,...[...old.values()].map(r=>Number(r.reviewId)))+1;
let rows=catalog.modules.map(entry=>{
 const raw=fs.readFileSync(path.join(root,entry.file));const sourceSha256=sha(raw);
 if(sourceSha256!==entry.contentSha256)throw Error('stale catalog: '+entry.id);
 const doc=JSON.parse(raw),c=doc.generationContract;
 documents.set(entry.id,doc);
 const hint=hints.get(entry.id),unchangedHint=hint?.sourceSha256===sourceSha256;
 const reviewId=old.get(entry.id)?.reviewId??String(next++).padStart(2,'0');
 const hasHooks=doc.objects.some(o=>o.type==='hookBounce'||o.type==='hookHang');
 const diagram=unchangedHint?'batch-001/'+hint.diagram:'diagrams/'+entry.id+'--'+sourceSha256.slice(0,16)+(hasHooks?'--hooks-v1':'')+'.svg';
 if(!unchangedHint)write(path.join(out,diagram),renderContractSvg(doc,{review:true}));
 return {reviewId,moduleId:entry.id,title:unchangedHint?hint.title:entry.title,
 summary:unchangedHint?hint.summary:`${c.foundation.widthBlocks}×${c.foundation.heightBlocks} Block；${c.ports.length} 个逻辑 Port；${c.routes.length} 条归档动作路线。`,
 source:entry.file,sourceSha256,contentVersion:c.contentVersion,diagram,
 portCount:c.ports.length,category:entry.category,technicalStatus:entry.technicalStatus,
 decision:'PENDING',humanFeedback:[]};
}).sort((a,b)=>Number(a.reviewId)-Number(b.reviewId));
// Review revisions overlay the queue only. The certified library and its catalog stay immutable.
const revisionIndex='generation/manual-review/revisions/latest.json';
if(fs.existsSync(path.join(root,revisionIndex))){
 const updates=new Map(read(revisionIndex).rows.map(r=>[r.moduleId,r]));
 rows=rows.map(row=>{
  const revision=updates.get(row.moduleId);if(!revision)return row;
  if(revision.baseSourceSha256!==row.sourceSha256)throw Error('review revision base changed: '+row.moduleId);
  const raw=fs.readFileSync(path.join(root,revision.file));const hash=sha(raw);
  if(hash!==revision.sha256)throw Error('review revision source changed: '+row.moduleId);
  const design=JSON.parse(raw);
  documents.set(row.moduleId,design);
  if(revision.reviewStage==='reference_display'){
   if(hash!==row.sourceSha256||design.generationContract.contentVersion!==row.contentVersion)throw Error('reference display changed content');
   if(sha(fs.readFileSync(path.join(out,revision.diagram)))!==revision.diagramSha256)throw Error('reference display image changed');
   return {...row,title:revision.title??row.title,reviewStage:'reference_display',diagram:revision.diagram,designNotes:revision.notes??[],previousDiagram:revision.beforeDiagram,previousVersion:revision.beforeVersion,summary:revision.summary,reviewRevision:revision.revision,receivedFeedback:revision.verbatim,physicsSummary:revision.physicsSummary,formalLibraryChanged:false};
  }
  if(revision.reviewStage==='design'){
   if(design.schema!=='pcg/module-design/v1'||design.reviewStage!=='design')throw Error('invalid design review schema');
   if(sha(fs.readFileSync(path.join(out,revision.diagram)))!==revision.diagramSha256)throw Error('design diagram hash changed');
   return {...row,title:design.title,source:revision.file,sourceSha256:hash,contentVersion:design.designVersion,designVersion:design.designVersion,reviewStage:'design',designNotes:design.designNotes??[],technicalStatus:'design_only',diagram:revision.diagram,portCount:design.ports.length,previousDiagram:revision.beforeDiagram,previousVersion:revision.beforeVersion,summary:revision.summary,reviewRevision:revision.revision,receivedFeedback:revision.verbatim,physicsSummary:'设计讨论阶段；定稿后统一实现与验证。',formalLibraryChanged:false};
  }
  const doc=design;const diagram='diagrams/'+row.moduleId+'--'+hash.slice(0,16)+'.svg';
  let svg=renderContractSvg(doc,{review:true});
  // Presentation only: preserve actual complementary collision state and visible rewards.
  for(const object of doc.objects){
   const prefix=`<rect x="${object.x}" y="${object.y}" width="${object.w}" height="${object.h}" `;
   if(object.type==='gate'&&object.mechanics?.kind==='complementary_gates'&&object.mechanics.member===object.mechanics.initialOpen){
    const from=prefix+'fill="#8b5cb6" fill-opacity=".85" stroke="#ffffff"';
    svg=svg.replace(from,prefix+'fill="#8b5cb6" fill-opacity=".15" stroke-dasharray="6 4" stroke="#8b5cb6"');
   }
   if(object.type==='reward')svg=svg.replace(prefix+'fill="#888"',prefix+'fill="#d6aa35"');
  }
  svg=svg.replace('绿=主路见证；金=奖励；蓝=回程','线条=新版诊断轨迹（未认证）；金=奖励；蓝=回程');
  for(const route of doc.generationContract.routes)if(route.evidenceStatus==='UNKNOWN'){
   const id=route.id.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
   svg=svg.replace(new RegExp('(<polyline data-route-id="'+id+'"[^>]*stroke-dasharray=")none("[^>]*>)'), '$1'+'8 6'+'$2');
  }
  if(!revision.diagram)write(path.join(out,diagram),svg);
  const displayed=revision.diagram??diagram;
  if(revision.diagram&&sha(fs.readFileSync(path.join(out,displayed)))!==revision.diagramSha256)throw Error('review diagram hash changed: '+row.moduleId);
  return {...row,source:revision.file,sourceSha256:hash,contentVersion:doc.generationContract.contentVersion,diagram:displayed,
   previousDiagram:revision.beforeDiagram??row.diagram,previousVersion:revision.beforeVersion??row.contentVersion,summary:revision.summary,reviewRevision:revision.revision,
   portCount:doc.generationContract.ports.length,receivedFeedback:revision.verbatim,decisionOnPreviousVersion:revision.decisionOnSource,technicalStatus:'revision_draft',
   physicsSummary:revision.physicsSummary,formalLibraryChanged:false};
 });
}
// Chat feedback is authoritative only for the exact reviewed design/reference version.
const decisionsPath='feedback/manual-review/received-design-decisions-v1.json';
if(fs.existsSync(path.join(root,decisionsPath))){
 const receipts=new Map(read(decisionsPath).rows.map(r=>[r.moduleId,r]));
 rows=rows.map(row=>{const receipt=receipts.get(row.moduleId);
  if(!receipt||receipt.version!==row.contentVersion)return row;
  return {...row,receivedDecision:receipt.decision,receivedDecisionVersion:receipt.version,receivedDecisionScope:'design_only',receivedDecisionNote:receipt.verbatim};
 });
}
// Priority affects future review batches, never Module IDs, source versions or opinions.
rows=rows.map(row=>{const doc=documents.get(row.moduleId),objects=doc.visualObjects??doc.objects;
 const hookPointCount=objects.filter(o=>['hookBounce','hookHang'].includes(o.type)).length;
 const usesGrapple=hookPointCount>0||(doc.capabilityRequirements?.allOf??[]).includes('grapple')||(doc.source?.original?.hook_anchors??[]).length>0;
 return {...row,usesGrapple,hookPointCount,reviewPriorityGroup:usesGrapple?'grapple':row.category==='平原'?'plains_without_grapple':'other_without_grapple'};
});
let ordering=null,batches;
const orderPath='generation/manual-review/order-policy.json';
if(fs.existsSync(path.join(root,orderPath))){
 const policy=read(orderPath),byId=new Map(rows.map(r=>[r.reviewId,r]));
 if(policy.schema!=='pcg/manual-review-order-policy/v1')throw Error('invalid review order policy');
 const frozen=new Map(policy.frozenBatches.map(b=>[b.id,b.reviewIds.filter(id=>byId.has(id))]));
 const receivedIds=new Set(fs.existsSync(path.join(root,decisionsPath))?read(decisionsPath).rows.map(r=>r.moduleId):[]);
 if(policy.preserveBatchesWithReceivedFeedback)for(const batch of previous?.batches??[]){
  if(batch.reviewIds.some(id=>receivedIds.has(byId.get(id)?.moduleId)))frozen.set(batch.id,batch.reviewIds.filter(id=>byId.has(id)));
 }
 const frozenIds=new Set();for(const ids of frozen.values())for(const id of ids){if(frozenIds.has(id))throw Error('duplicate frozen review ID');frozenIds.add(id);}
 const rank=new Map(policy.priority.map((name,i)=>[name,i]));
 const pending=rows.filter(r=>!frozenIds.has(r.reviewId)).sort((a,b)=>rank.get(a.reviewPriorityGroup)-rank.get(b.reviewPriorityGroup)||Number(a.reviewId)-Number(b.reviewId));
 const lastFrozen=Math.max(0,...[...frozen.keys()].map(id=>Number(id.slice(6))));batches=[];let cursor=0,n=1;
 while(cursor<pending.length||n<=lastFrozen){
  const id='batch-'+String(n++).padStart(3,'0'),isFrozen=frozen.has(id);
  const reviewIds=isFrozen?frozen.get(id):pending.slice(cursor,cursor+5).map(r=>r.reviewId);if(!isFrozen)cursor+=reviewIds.length;
  if(!reviewIds.length)continue;
  const priorities=[...new Set(reviewIds.map(id=>byId.get(id).reviewPriorityGroup))];
  const label=priorities.length===1?{plains_without_grapple:'平原 · 无钩索',other_without_grapple:'其他 · 无钩索',grapple:'钩索内容'}[priorities[0]]:'混合 · 按优先级';
  batches.push({id,reviewIds,priorityLabel:isFrozen?(priorities.length===1?label+' · 批次保留':'已收意见 · 批次保留'):label,orderingFrozen:isFrozen});
 }
 const assigned=batches.flatMap(b=>b.reviewIds);if(assigned.length!==rows.length||new Set(assigned).size!==rows.length)throw Error('review ordering lost or duplicated a Module');
 ordering={id:policy.id,preserveModuleReviewIds:true,frozenBatchIds:[...frozen.keys()],priority:policy.priority,description:'未审阅内容：平原无钩索 → 其他无钩索 → 钩索；已审批次与Module编号保留。'};
}else{
 const groups=new Map();for(const row of rows){const n=Math.floor((Number(row.reviewId)-1)/5)+1;const id='batch-'+String(n).padStart(3,'0');if(!groups.has(id))groups.set(id,[]);groups.get(id).push(row.reviewId);}
 batches=[...groups].map(([id,reviewIds])=>({id,reviewIds}));
}
write(path.join(out,'queue.json'),JSON.stringify({schema:'pcg/manual-module-review-queue/v1',catalogSha256:sha(fs.readFileSync(path.join(root,'modules/catalog.json'))),batchSize:5,total:rows.length,ordering,batches,rows},null,2)+'\n');
console.log(JSON.stringify({modules:rows.length,batches:batches.length,sourceDocumentsMutated:false,physicsRun:false,renderer:'existing renderContractSvg(review:true)',output:'generation/manual-review/queue.json'}));
