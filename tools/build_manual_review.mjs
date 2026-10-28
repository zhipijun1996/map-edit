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
let next=Math.max(0,...[...old.values()].map(r=>Number(r.reviewId)))+1;
let rows=catalog.modules.map(entry=>{
 const raw=fs.readFileSync(path.join(root,entry.file));const sourceSha256=sha(raw);
 if(sourceSha256!==entry.contentSha256)throw Error('stale catalog: '+entry.id);
 const doc=JSON.parse(raw),c=doc.generationContract;
 const hint=hints.get(entry.id),unchangedHint=hint?.sourceSha256===sourceSha256;
 const reviewId=old.get(entry.id)?.reviewId??String(next++).padStart(2,'0');
 const diagram=unchangedHint?'batch-001/'+hint.diagram:'diagrams/'+entry.id+'--'+sourceSha256.slice(0,16)+'.svg';
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
  const doc=JSON.parse(raw);const diagram='diagrams/'+row.moduleId+'--'+hash.slice(0,16)+'.svg';
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
   previousDiagram:row.diagram,previousVersion:row.contentVersion,summary:revision.summary,reviewRevision:revision.revision,
   receivedFeedback:revision.verbatim,decisionOnPreviousVersion:revision.decisionOnSource,technicalStatus:'revision_draft',
   physicsSummary:revision.physicsSummary,formalLibraryChanged:false};
 });
}
// Frozen batch membership remains stable when new entries are appended or old entries disappear.
const groups=new Map();for(const row of rows){const n=Math.floor((Number(row.reviewId)-1)/5)+1;const id='batch-'+String(n).padStart(3,'0');if(!groups.has(id))groups.set(id,[]);groups.get(id).push(row.reviewId);}
const batches=[...groups].map(([id,reviewIds])=>({id,reviewIds}));
write(path.join(out,'queue.json'),JSON.stringify({schema:'pcg/manual-module-review-queue/v1',catalogSha256:sha(fs.readFileSync(path.join(root,'modules/catalog.json'))),batchSize:5,total:rows.length,batches,rows},null,2)+'\n');
console.log(JSON.stringify({modules:rows.length,batches:batches.length,sourceDocumentsMutated:false,physicsRun:false,renderer:'existing renderContractSvg(review:true)',output:'generation/manual-review/queue.json'}));
