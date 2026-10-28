import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {CurrentModuleLibraryClient,CURRENT_MODULES_REF,validateCurrentModuleCatalog,gitBlobSha} from '../current-module-library-client.js';
import {foundationFixture} from './contract-tests/check-foundation.mjs';
import {contentVersion} from '../module-contract.js';
import {cornerRelocationRows} from '../corner-port-view.js';

// Structural network test doubles only. These do not certify or publish any Module.
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const blobHash=bytes=>createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
const tip='a'.repeat(40),root='https://local.example/',pinned=`https://raw.githubusercontent.com/zhipijun1996/map-edit/${tip}/`;
function fixture(id,title){
  const doc=foundationFixture();doc.id=id;doc.title=title;const c=doc.generationContract;
  c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;
  const bytes=Buffer.from(JSON.stringify(doc));
  const entry={id,moduleId:id,title,contentVersion:c.contentVersion,file:`./modules/${id}/module.mapnote.json`,thumbnail:`./modules/${id}/thumbnail.svg`,contentSha256:hash(bytes),portCount:c.ports.length,category:'测试结构样本',capabilityRequirements:doc.capabilityRequirements,difficulty:doc.difficulty,humanReview:'UNKNOWN',technicalStatus:'passed_scoped',mapReady:false};
  return {doc,bytes,entry};
}
const one=fixture('structural-one','TEST ONLY ONE'),two=fixture('structural-two','TEST ONLY TWO');
const directory=entries=>({schema:'map-notes/module-archive/v1',foundationVersion:'1.0',modules:entries});
let next=directory([one.entry,two.entry]),local=directory([one.entry]),corruptDoc=false,corruptCatalog=false,missing=false,limited=false,downloads=0,commits=0;
const requests=[];
async function fetcher(url){
  requests.push(url);
  if(url===root+'modules/catalog.json')return missing?new Response('',{status:404}):Response.json(local);
  if(url.includes('/commits/')){commits++;assert(url.endsWith(encodeURIComponent(CURRENT_MODULES_REF)));return limited?new Response('',{status:429}):Response.json({sha:tip});}
  const catalogBytes=Buffer.from(JSON.stringify(next));
  if(url.includes('/contents/modules/catalog.json?ref=')){assert(url.endsWith(tip));return Response.json({type:'file',path:'modules/catalog.json',sha:corruptCatalog?'0'.repeat(40):blobHash(catalogBytes)});}
  if(url===pinned+'modules/catalog.json')return new Response(catalogBytes);
  const f=[one,two].find(x=>url===pinned+x.entry.file.slice(2)||url===root+x.entry.file.slice(2));
  assert(f,'Only catalog-listed files at the selected commit may be fetched: '+url);downloads++;return new Response(corruptDoc?Buffer.from('{}'):f.bytes);
}
assert.equal(await gitBlobSha(Buffer.from('test')),blobHash(Buffer.from('test')));
assert.equal(validateCurrentModuleCatalog(local),local);
for(const mutate of [x=>x.schema='map-notes/repository-module-library/v1',x=>x.foundationVersion='legacy',x=>x.modules.push({...x.modules[0]}),x=>x.modules[0].file='./pcg/map_directed/library/candidates/fake/module.mapnote.json',x=>x.modules[0].thumbnail='https://example.com/foreign.svg',x=>x.modules[0].portCount=0,x=>x.modules[0].id=undefined]){
  const bad=structuredClone(local);mutate(bad);assert.throws(()=>validateCurrentModuleCatalog(bad));
}
const unavailable=new CurrentModuleLibraryClient(root,fetcher);missing=true;await assert.rejects(()=>unavailable.load(),e=>e.code==='CURRENT_CATALOG_MISSING');assert.equal(unavailable.catalog,null);missing=false;
const client=new CurrentModuleLibraryClient(root,fetcher);await client.load();const before=client.catalog;
const updates=await Promise.all([client.checkUpdate(),client.checkUpdate()]);assert.equal(commits,1,'Concurrent clicks share one update');assert.deepEqual(updates[0],updates[1]);assert.equal(updates[0].added,1);assert.equal(client.snapshotCommit,tip);assert.equal(client.baseURL,pinned);assert.equal(client.catalog.modules.length,2);
assert(!requests.some(x=>x.includes('/git/trees/')||x.includes('/library/candidates/')),'Current library never discovers formal modules from historical candidate trees');
const copy=await client.module(one.entry);copy.objects.length=0;assert((await client.module(one.entry)).objects.length>0,'The editor receives a copy, never the cached source');
downloads=0;await client.checkUpdate();assert.equal(downloads,0,'Unchanged already verified document bytes can be reused');
next=directory([one.entry]);const removed=await client.checkUpdate();assert.equal(removed.removed,1);assert.equal(client.catalog.modules.length,1,'The directory determines membership, not historical records');
const failure=new CurrentModuleLibraryClient(root,fetcher);failure.catalog=before;const originalBase=failure.baseURL;
next=directory([one.entry,two.entry]);corruptDoc=true;await assert.rejects(()=>failure.checkUpdate(),/SHA256/);assert.equal(failure.catalog,before);assert.equal(failure.baseURL,originalBase);assert.equal(failure.documents.size,0);corruptDoc=false;
corruptCatalog=true;await assert.rejects(()=>failure.checkUpdate(),/Git SHA/);assert.equal(failure.catalog,before);corruptCatalog=false;
limited=true;await assert.rejects(()=>failure.checkUpdate(),/限额/);assert.equal(failure.catalog,before);limited=false;
const forged=structuredClone(one);forged.doc.generationContract.version=1;forged.bytes=Buffer.from(JSON.stringify(forged.doc));forged.entry.contentSha256=hash(forged.bytes);
const legacy=new CurrentModuleLibraryClient(root,async url=>url.endsWith('/modules/catalog.json')?Response.json(directory([forged.entry])):new Response(forged.bytes));
await legacy.load();await assert.rejects(()=>legacy.module(forged.entry),/新地基目录/,'A legacy document cannot be promoted merely by appearing in a current catalog');
next=directory([]);const empty=await client.checkUpdate();assert.equal(empty.total,0,'An explicitly published empty directory is valid');assert.equal(client.catalog.modules.length,0);
const assessment={schema:'pcg/corner-port-assessment/v1',scope:'current',moduleDocumentId:one.doc.id,documentSha256:one.entry.contentSha256,contentVersion:one.entry.contentVersion,
  ports:[{portId:one.doc.generationContract.ports[0].id,cornerRelocations:{TOP_LEFT:{applicable:true,allowed:'UNKNOWN',targetFace:'TOP',targetPosition:[-64,128],proposedSurface:'ONE_WAY_PLATFORM',reason:'TEST ONLY; physics not run',profileId:null}}}]};
let external={schema:'pcg/corner-port-inventory/v1',rows:[assessment]};
const assessed=new CurrentModuleLibraryClient(root,async()=>Response.json(external));
const checkedAssessment=await assessed.cornerAssessment(one.entry);
assert(checkedAssessment,'A source-version and byte-bound assessment is available for display');
assert.equal(cornerRelocationRows(one.doc,checkedAssessment)[0].allowed,'UNKNOWN');
checkedAssessment.ports[0].cornerRelocations.TOP_LEFT.allowed=true;
assert.equal(cornerRelocationRows(one.doc,checkedAssessment)[0].allowed,'UNKNOWN','External assessment cannot grant physical permission');
assert.equal((await assessed.cornerAssessment(one.entry)).ports[0].cornerRelocations.TOP_LEFT.allowed,'UNKNOWN','Assessment display receives a copy');
external.rows[0].documentSha256='0'.repeat(64);assessed.cornerInventory=null;
assert.equal(await assessed.cornerAssessment(one.entry),null,'Assessment bytes must bind the exact current document');
const wrongVersion=structuredClone(assessment);wrongVersion.contentVersion='sha256:'+'0'.repeat(64);
assert.equal(cornerRelocationRows(one.doc,wrongVersion).length,0,'Stale assessments do not appear on another version');
const unavailableAssessment=new CurrentModuleLibraryClient(root,async()=>new Response('',{status:404}));
assert.equal(await unavailableAssessment.cornerAssessment(one.entry),null,'An optional assessment cannot block Module loading');
// Explicit structural network doubles only: these do not represent certification.
const targetDoc=structuredClone(one.doc);targetDoc.generationContract.generation.parameters.clientTestConfiguration='TEST ONLY';
targetDoc.generationContract.contentVersion=contentVersion(targetDoc);
targetDoc.generationContract.visualization.contentVersion=targetDoc.generationContract.contentVersion;
if(targetDoc.generationContract.staticChecks)targetDoc.generationContract.staticChecks.contentVersion=targetDoc.generationContract.contentVersion;
const targetBytes=Buffer.from(JSON.stringify(targetDoc)),configPrefix=`modules/${one.entry.id}/port-configurations/test-only/`;
const manifest={schema:'pcg/godot-module-package/v1',stable_id:one.entry.id,source:{module_sha256:hash(targetBytes)}};
const manifestBytes=Buffer.from(JSON.stringify(manifest));
const receipt={schema:'pcg/corner-port-configuration/v1',moduleId:one.entry.id,configurationId:'test-only',baseContentVersion:one.entry.contentVersion,baseDocumentSha256:one.entry.contentSha256,allowed:true,technicalStatus:'verified',
  relocations:[{portId:one.doc.generationContract.ports[0].id,corner:'TOP_LEFT',targetFace:'TOP',targetPosition:[-64,128],surface:'ONE_WAY_PLATFORM'}],
  configuration:{path:configPrefix+'module.mapnote.json',sha256:hash(targetBytes),contentVersion:targetDoc.generationContract.contentVersion},
  package:{path:configPrefix+'godot-package.json',sha256:hash(manifestBytes)},physicsReport:{path:'TEST-ONLY-NOT-ACTUAL-PHYSICS',sha256:'1'.repeat(64)}};
let receiptBytes=Buffer.from(JSON.stringify(receipt)),badTarget=false;
const configEntry={...one.entry,cornerConfigurationReceipts:[{path:configPrefix+'receipt.json',sha256:hash(receiptBytes)}]};
const configClient=new CurrentModuleLibraryClient(root,async url=>{
  if(url.endsWith('/receipt.json'))return new Response(receiptBytes);
  if(url.endsWith('/godot-package.json'))return new Response(manifestBytes);
  if(url.endsWith('/module.mapnote.json'))return new Response(badTarget?'{}':targetBytes);
  throw Error('Unexpected configuration request '+url);
});
const configurations=await configClient.cornerConfigurations(configEntry);assert.equal(configurations.length,1);
assert.equal((await configClient.cornerModule(configEntry,configurations[0])).generationContract.contentVersion,targetDoc.generationContract.contentVersion);
badTarget=true;await assert.rejects(()=>configClient.cornerModule(configEntry,configurations[0]),/SHA256/);
const wrongBase={...configEntry,contentVersion:'sha256:'+'0'.repeat(64)};
assert.deepEqual(await configClient.cornerConfigurations(wrongBase),[],'A certified configuration cannot transfer to another base version');
assert.throws(()=>configClient.configurationPath(configPrefix+'../foreign.json',configEntry),/路径/);
// v2 open-side receipt doubles retain artifact/identity checks; no closure requirement.
badTarget=false;
const adaptation={schema:'pcg/corner-interface-adaptation/v2',retiredSidePolicy:'preserve_geometry_no_extra_closure',baseDocumentSha256:one.entry.contentSha256,targetDocumentSha256:hash(targetBytes)};
let adaptationBytes=Buffer.from(JSON.stringify(adaptation));
const openReceipt={...receipt,schema:'pcg/corner-port-configuration/v2',retiredSidePolicy:'preserve_geometry_no_extra_closure',adaptation:{path:configPrefix+'corner-adaptation.json',sha256:hash(adaptationBytes)}};
let openBytes=Buffer.from(JSON.stringify(openReceipt));
const openEntry={...configEntry,cornerConfigurationReceipts:[{path:configPrefix+'receipt.json',sha256:hash(openBytes)}]};
const openClient=new CurrentModuleLibraryClient(root,async url=>{
  if(url.endsWith('/receipt.json'))return new Response(openBytes);
  if(url.endsWith('/corner-adaptation.json'))return new Response(adaptationBytes);
  if(url.endsWith('/godot-package.json'))return new Response(manifestBytes);
  if(url.endsWith('/module.mapnote.json'))return new Response(targetBytes);
  throw Error('Unexpected open configuration request '+url);
});
const openConfigurations=await openClient.cornerConfigurations(openEntry);assert.equal(openConfigurations.length,1);
assert.equal((await openClient.cornerModule(openEntry,openConfigurations[0])).generationContract.contentVersion,targetDoc.generationContract.contentVersion);
const malformed={...openReceipt,retiredSidePolicy:'closed'};openBytes=Buffer.from(JSON.stringify(malformed));
assert.deepEqual(await openClient.cornerConfigurations({...openEntry,cornerConfigurationReceipts:[{path:configPrefix+'receipt.json',sha256:hash(openBytes)}]}),[],'v2 never accepts a different retired-side policy');
const relabelled={...openReceipt,retiredOpeningReport:{testOnly:true}};openBytes=Buffer.from(JSON.stringify(relabelled));
assert.deepEqual(await openClient.cornerConfigurations({...openEntry,cornerConfigurationReceipts:[{path:configPrefix+'receipt.json',sha256:hash(openBytes)}]}),[],'v1 closure evidence cannot be relabelled as v2');
adaptationBytes=Buffer.from('{}');await assert.rejects(()=>openClient.cornerModule(openEntry,openReceipt),/SHA256/,'Open-side policy still needs exact adaptation artifact bytes');
const categoryClient=new CurrentModuleLibraryClient(root,fetcher);
assert.equal(categoryClient.displayCategory(one.entry),one.entry.category,'An unloaded document keeps its explicit catalog category');
categoryClient.documents.set(one.entry.contentVersion,{doc:{source:{kind:'forest'}}});
assert.equal(categoryClient.displayCategory(one.entry),'森林','Only the actual loaded source metadata can correct forest display');
categoryClient.documents.set(one.entry.contentVersion,{doc:{source:{kind:'generated'},capabilityRequirements:{allOf:['grapple']}}});
assert.equal(categoryClient.displayCategory(one.entry),one.entry.category,'Ability tags never infer a region');
console.log(JSON.stringify({passed:true,scope:'Structural client tests only; no Module certification',checks:'v2 documents, SHA256 bytes and pinned catalog Git SHA, catalog authority, no candidate scan, immutable editing, atomic update/rollback, missing catalog, rate limit, legacy rejection and concurrent clicks'}));
