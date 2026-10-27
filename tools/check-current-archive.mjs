// Checks real persisted current content. No fixtures and no physics inference.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {validateGenerationContract} from '../module-contract.js';
import {renderContractSvg} from '../module-contract-render.js';
import {cornerRelocationRows} from '../corner-port-view.js';
const catalog=JSON.parse(fs.readFileSync('modules/catalog.json'));
assert.equal(catalog.schema,'map-notes/module-archive/v1');
const names=new Set();let routes=0,cornerOptions=0;
for(const entry of catalog.modules){
 assert(!names.has(entry.id));names.add(entry.id);
 const bytes=fs.readFileSync(entry.file),doc=JSON.parse(bytes),c=doc.generationContract;
 assert.equal(createHash('sha256').update(bytes).digest('hex'),entry.contentSha256);
 assert.equal(c.version,2);assert.equal(c.contentVersion,entry.contentVersion);
 assert.equal(doc.id,entry.moduleId);assert.equal(c.generation.migration.moduleId,entry.id);
 assert.equal(c.ports.length,entry.portCount);assert(validateGenerationContract(doc).versionMatches);
 assert.deepEqual(entry.sceneOriginOffsetPixels,[-c.space.bounds.x||0,-c.space.bounds.y||0]);
 assert.equal(fs.readFileSync(entry.thumbnail,'utf8'),renderContractSvg(doc));
 for(const option of cornerRelocationRows(doc)){
  cornerOptions++;
  assert.equal(option.allowed===true,!!option.profileId,'Only a certified whole configuration may appear available');
  assert(['LEFT','RIGHT','TOP','BOTTOM'].includes(option.targetFace));
 }
 for(const ref of entry.cornerConfigurationReceipts??[]){
  const receiptBytes=fs.readFileSync(ref.path),receipt=JSON.parse(receiptBytes);
  assert.equal(createHash('sha256').update(receiptBytes).digest('hex'),ref.sha256);
  assert.equal(receipt.baseContentVersion,c.contentVersion);assert.equal(receipt.baseDocumentSha256,entry.contentSha256);
  assert.equal(receipt.moduleId,entry.id);assert.equal(receipt.allowed,true);assert.equal(receipt.technicalStatus,'verified');
  const configurationBytes=fs.readFileSync(receipt.configuration.path),configuration=JSON.parse(configurationBytes);
  assert.equal(createHash('sha256').update(configurationBytes).digest('hex'),receipt.configuration.sha256);
  assert.equal(configuration.generationContract.contentVersion,receipt.configuration.contentVersion);
  assert(validateGenerationContract(configuration).versionMatches);
  for(const relocation of receipt.relocations){
   const p=configuration.generationContract.ports.find(p=>p.id===relocation.portId);
   assert.equal(p.face,relocation.targetFace);assert.deepEqual(p.position,relocation.targetPosition);
  }
 }
 routes+=c.routes.length;
}
console.log(JSON.stringify({currentTemplates:names.size,declaredRoutes:routes,cornerOptions,passed:true,physics:false,scope:'real current JSON, versions, hashes, bounds origin, SVG and corner-option display; no new certification'}));
