// UI/source association only. These checks do not certify any physics.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedCornerBatch,moduleCornerProgress,loadCornerPreview,stageLabel} from '../corner-batch-review.js';
import {mirrorReviewPorts,renderMirrorReview} from '../module-mirror-review.js';
const catalog=JSON.parse(fs.readFileSync('modules/catalog.json'));
let ports=0;
for(const entry of catalog.modules){
 const doc=JSON.parse(fs.readFileSync(entry.file)),before=JSON.stringify(doc),b=doc.generationContract.space.bounds,mirrored=mirrorReviewPorts(doc);
 assert.equal(mirrored.length,doc.generationContract.ports.length);
 for(const [i,p]of mirrored.entries()){
  const source=doc.generationContract.ports[i];assert.equal(p.id,source.id);assert.equal(p.permission,source.permission);assert.equal(p.surface,source.surface);
  assert.equal(p.position[0]+source.position[0],2*b.x+b.w);assert.equal(p.position[1],source.position[1]);
  assert.equal(p.normal[0],-source.normal[0]||0);assert.equal(p.normal[1],source.normal[1]);
  assert.equal(p.face,{LEFT:'RIGHT',RIGHT:'LEFT',TOP:'TOP',BOTTOM:'BOTTOM'}[source.face]);ports++;
 }
 const view=renderMirrorReview(doc);assert(view.includes('data-mirror-preview="geometry-only"'));assert(view.includes('未认证'));assert(!view.includes('草稿标记偏离合同位置'),'Mirrored review markers must follow mirrored Port positions');
 assert.equal(JSON.stringify(doc),before,'Mirror review must not alter a current Module, route identity or evidence');
}
const entry=catalog.modules[0],key='test-display-only',row={key,moduleId:entry.id,portId:'A',corner:'TOP_LEFT',targetFace:'TOP',baseContentVersion:entry.contentVersion,baseDocumentSha256:entry.contentSha256,status:'preflight_passed'};
const snapshot={schema:'map-notes/corner-batch-status/v1',rows:[row],modules:[],counts:{verified:999},currentOptions:999};
const valid=checkedCornerBatch(snapshot,catalog);
assert.equal(valid.currentOptions,1);assert.equal(valid.counts.preflight_passed,1);assert.equal(valid.counts.verified,undefined,'Untrusted aggregate counts cannot invent certifications');
assert.equal(moduleCornerProgress(valid,entry).certified,entry.cornerConfigurationReceipts.length);
assert(stageLabel(row.status).includes('预检通过'));assert(!stageLabel(row.status).includes('已认证'));
const stale=checkedCornerBatch({...snapshot,rows:[{...row,baseContentVersion:'sha256:'+'0'.repeat(64)}]},catalog);assert.equal(stale.rows.length,0);assert.equal(stale.currentOptions,0);
assert.throws(()=>checkedCornerBatch({...snapshot,rows:[{...row,preview:{path:'generation/module-review/../current.json',sha256:'0'.repeat(64),certified:false}}]},catalog));
assert.throws(()=>checkedCornerBatch({...snapshot,rows:[{...row,preview:{path:'generation/module-review/corner-batches/test/test.mapnote.json',sha256:'0'.repeat(64),certified:true}}]},catalog));
const bytes=fs.readFileSync(entry.file),preview={...row,preview:{path:'generation/module-review/corner-batches/test/test.mapnote.json',sha256:createHash('sha256').update(bytes).digest('hex'),contentVersion:entry.contentVersion,certified:false}};
await loadCornerPreview(preview,entry,'https://example.test/',async()=>new Response(bytes));
await assert.rejects(()=>loadCornerPreview(preview,entry,'https://example.test/',async()=>new Response('{}')),/SHA/);
await assert.rejects(()=>loadCornerPreview({...preview,baseDocumentSha256:'0'.repeat(64)},entry,'https://example.test/',async()=>new Response(bytes)),/此版本/);
console.log(JSON.stringify({passed:true,currentTemplates:catalog.modules.length,mirroredPortViews:ports,previewPhysicsCertification:false,scope:'Read-only geometry, source-version association, stale/hash rejection and separate progress labels.'}));
