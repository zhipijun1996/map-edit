import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {RepositoryLibraryClient,validateRepositoryCatalog} from '../repository-library-client.js';
import {validateDocument,makeRevision,changeRequest} from '../model.js';
import {validateGenerationContract} from '../module-contract.js';
import {renderContractSvg} from '../module-contract-render.js';
const catalog=validateRepositoryCatalog(JSON.parse(fs.readFileSync('library/workshop/catalog.json')));
const digest=b=>createHash('sha256').update(b).digest('hex'),clone=x=>structuredClone(x);
for(const entry of catalog.modules){
 const bytes=fs.readFileSync(entry.file);assert.equal(digest(bytes),entry.contentSha256);
 const doc=validateDocument(JSON.parse(bytes));assert.equal(doc.id,entry.moduleId);assert.equal(doc.generationContract.contentVersion,entry.contentVersion);assert(validateGenerationContract(doc).versionMatches);
 assert.equal(fs.readFileSync(entry.thumbnail,'utf8'),renderContractSvg(doc));
 const copy=makeRevision(doc,'new_variant');assert.notEqual(copy.id,doc.id);assert.equal(changeRequest(copy).target,null);assert.equal(changeRequest(copy).derivedFrom.repository,'zhipijun1996/map-edit');assert.deepEqual(copy.objects,doc.objects);
}
assert(catalog.modules.length>0);const bad=clone(catalog);bad.modules[0].file='https://example.com/untrusted.json';assert.throws(()=>validateRepositoryCatalog(bad));
const old=clone(catalog);old.modules.pop();const tip='f'.repeat(40);let corrupt=false,withdraw=false,limited=false,downloads=0;
const curated={rows:catalog.modules.map(m=>({contentVersion:m.contentVersion,selected_for_plains_candidates:m.scope==='plains',selection_reason:m.scope==='advanced'?'reserved_for_later_abilities':m.scope==='held'?'pacing_held':'unclassified',content_role:m.contentRole}))};
const tree={truncated:false,tree:[...catalog.modules.map(m=>({path:m.recordPath,type:'blob'})),{path:'pcg/feedback/content-withdrawals/test-notice.json',type:'blob'}]};
const json=x=>new Response(JSON.stringify(x));
async function fetcher(url){
 if(url.includes('/commits/'))return limited?new Response('',{status:403}):json({sha:tip});
 if(url.includes('/git/trees/'))return json(tree);
 if(url.endsWith('/test-notice.json'))return json({schema:'pcg/content-technical-withdrawal/v1',contentVersions:withdraw?[catalog.modules[0].contentVersion]:[]});
 if(url.endsWith('/plains-recoil-v1/catalog.json'))return json(curated);
 if(url.includes('raw.githubusercontent.com')){
  const path=url.split('/'+tip+'/')[1],entry=catalog.modules.find(m=>m.recordPath===path||m.sourcePath===path);
  assert(entry,'only pinned repository source paths are fetched');
  if(path===entry.recordPath)return json({id:entry.moduleId,contentVersion:entry.contentVersion,document_sha256:entry.contentSha256});
  downloads++;return new Response(corrupt?Buffer.from('{}'):fs.readFileSync(entry.file));
 }
 const p=new URL(url).pathname.slice(1);if(p==='library/workshop/catalog.json')return json(old);
 return new Response(fs.readFileSync(p));
}
const client=new RepositoryLibraryClient('https://local.example/index.html',fetcher);await client.load();
const before=client.catalog;const result=await client.checkUpdate();assert.equal(result.added,1);assert.equal(result.total,catalog.modules.length);assert(client.baseURL.includes(tip));assert.equal(client.catalog.modules.filter(m=>m.scope==='plains').length,catalog.modules.filter(m=>m.scope==='plains').length);
const first=client.catalog.modules[0],opened=await client.module(first);opened.objects.length=0;assert((await client.module(first)).objects.length>0,'editing a clone never changes cached source');
downloads=0;await client.checkUpdate();assert.equal(downloads,0,'unchanged verified module bytes are reused');
withdraw=true;const removal=await client.checkUpdate();assert.equal(removal.removed,1);assert.equal(removal.total,catalog.modules.length-1);withdraw=false;
const failure=new RepositoryLibraryClient('https://local.example/index.html',fetcher);failure.catalog=before;const originalBase=failure.baseURL;corrupt=true;await assert.rejects(()=>failure.checkUpdate(),/校验失败/);assert.equal(failure.catalog,before);assert.equal(failure.baseURL,originalBase);assert.equal(failure.documents.size,0);corrupt=false;limited=true;await assert.rejects(()=>failure.checkUpdate(),/限额/);assert.equal(failure.catalog,before);
console.log(JSON.stringify({repository_modules:catalog.modules.length,checks:'static document/SVG hashes, discovery beyond bundled index, immutable editing, atomic failure preservation, withdrawal, pinned reads and capability scopes',passed:true}));
