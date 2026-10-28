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
const rows=catalog.modules.map(entry=>{
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
// Frozen batch membership remains stable when new entries are appended or old entries disappear.
const groups=new Map();for(const row of rows){const n=Math.floor((Number(row.reviewId)-1)/5)+1;const id='batch-'+String(n).padStart(3,'0');if(!groups.has(id))groups.set(id,[]);groups.get(id).push(row.reviewId);}
const batches=[...groups].map(([id,reviewIds])=>({id,reviewIds}));
write(path.join(out,'queue.json'),JSON.stringify({schema:'pcg/manual-module-review-queue/v1',catalogSha256:sha(fs.readFileSync(path.join(root,'modules/catalog.json'))),batchSize:5,total:rows.length,batches,rows},null,2)+'\n');
console.log(JSON.stringify({modules:rows.length,batches:batches.length,sourceDocumentsMutated:false,physicsRun:false,renderer:'existing renderContractSvg(review:true)',output:'generation/manual-review/queue.json'}));
