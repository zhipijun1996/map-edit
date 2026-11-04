// Generated view of modules/catalog.json + per-ID records. Never scans historical rounds.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const catalog=read('modules/catalog.json'),url=p=>'../../'+p.replace(/^\.\//,'');
const modules=catalog.modules.map(entry=>{
 const doc=read(entry.file),c=doc.generationContract,r=read(entry.record),stage=entry.deliveryStatus==='ready'?'ARCHIVED':entry.technicalStatus==='passed_scoped'?'IMPLEMENTED_CANDIDATE':'NEEDS_REPAIR';
 return {id:entry.id,reviewId:entry.reviewId,title:entry.title,summary:doc.summary??doc.title,category:entry.category,stage,diagram:url(entry.thumbnail),foundation:entry.foundation,ports:c.ports,routes:c.routes,relations:c.relations,capabilityRequirements:entry.capabilityRequirements,mapReady:false,designVersion:r.review.designVersion,designFileSha256:r.source.sha256,designUrl:url(entry.record),reviewUrl:url(entry.record),archiveUrl:url(entry.file),deliveryStatus:entry.deliveryStatus,contentVersion:entry.contentVersion,record:url(entry.record),gaps:r.gaps,implementation:null,humanPlaytest:'UNKNOWN'};
});
const ideas=catalog.designs.map(entry=>{
 const d=read(entry.file);return {id:entry.id,title:entry.title,sourceType:'ai_idea',verbatim:d.summary,stage:'DESIGN_REVIEW',humanApproval:entry.review.decision,interpretation:d.creativeInterpretation??null,gaps:d.gaps??[],design:{version:entry.contentVersion,file:url(entry.file),sha256:entry.contentSha256,diagram:url(entry.thumbnail)}};
});
const counts={ARCHIVED:0,IMPLEMENTED_CANDIDATE:0,READY_FOR_IMPLEMENTATION:0,NEEDS_REPAIR:0,NEEDS_ALIGNMENT:0};for(const m of modules)counts[m.stage]++;
const value={schema:'pcg/module-workshop-view/v1',sources:{catalog:'../../modules/catalog.json',updateRef:'main',uniqueRecords:true},counts,libraryCounts:catalog.counts,modules,ideas};
fs.writeFileSync(path.join(root,'generation/module-workshop/data.json'),JSON.stringify(value,null,2)+'\n');
console.log(JSON.stringify({source:'modules/catalog.json',...catalog.counts}));
