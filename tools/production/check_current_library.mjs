import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {webcrypto,createHash} from 'node:crypto';
import {CURRENT_MODULES_REF,validateCurrentModuleCatalog,CurrentModuleLibraryClient} from '../../current-module-library-client.js';
import {validateGenerationContract} from '../../module-contract.js';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const catalog=JSON.parse(fs.readFileSync('modules/catalog.json'));assert.equal(CURRENT_MODULES_REF,'main');validateCurrentModuleCatalog(catalog);
const fetcher=async url=>{const p=new URL(url).pathname.slice(1);return fs.existsSync(p)?new Response(fs.readFileSync(p)):new Response('',{status:404});};
const client=new CurrentModuleLibraryClient('https://current-library.local/',fetcher);await client.load();
for(const m of catalog.modules){const doc=await client.module(m);assert.equal(doc.id,m.id);assert(validateGenerationContract(doc).versionMatches);assert.equal(createHash('sha256').update(fs.readFileSync(m.file)).digest('hex'),m.contentSha256);}
const view=JSON.parse(fs.readFileSync('generation/module-workshop/data.json'));assert.deepEqual(new Set(view.modules.map(m=>m.id)),new Set(catalog.modules.map(m=>m.id)));assert.deepEqual(new Set(view.ideas.map(m=>m.id)),new Set(catalog.designs.map(m=>m.id)));assert.equal(view.sources.updateRef,'main');
const active=new Set(catalog.modules.map(m=>m.id));for(const retired of catalog.withdrawn)assert(!active.has(retired.id));
console.log(`Current editor and workshop: ${catalog.modules.length} authoritative Modules, ${catalog.designs.length} pending designs; hashes and versions match.`);

// Explicit HTTP test doubles exercise one pinned main snapshot and rollback.
const tip=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
const bytes=fs.readFileSync('modules/catalog.json');
const gitBlob=createHash('sha1').update(Buffer.from(`blob ${bytes.length}\0`)).update(bytes).digest('hex');
let corrupt=false;const requested=[];
const remote=async url=>{
 requested.push(url);
 if(url===`https://api.github.com/repos/zhipijun1996/map-edit/commits/main`)return Response.json({sha:tip});
 if(url.includes('/contents/modules/catalog.json?ref='))return Response.json({type:'file',path:'modules/catalog.json',sha:gitBlob});
 const prefix=`https://raw.githubusercontent.com/zhipijun1996/map-edit/${tip}/`;
 if(url===prefix+'modules/catalog.json')return new Response(bytes);
 if(url.startsWith(prefix)){
  const name=url.slice(prefix.length);assert(name.startsWith('modules/'));
  return new Response(corrupt&&name.endsWith('/module.mapnote.json')?Buffer.from('{}'):fs.readFileSync(name));
 }
 return fetcher(url);
};
const fresh=new CurrentModuleLibraryClient('https://current-library.local/',remote);await fresh.load();
const refreshed=await fresh.checkUpdate();assert.equal(refreshed.total,catalog.modules.length);assert.equal(fresh.snapshotCommit,tip);
assert(requested.some(url=>url.endsWith('/commits/main')));assert(!requested.some(url=>url.includes('content/task-a-workshop')||url.includes('library/workshop')));
const failed=new CurrentModuleLibraryClient('https://current-library.local/',remote);await failed.load();const previous=failed.catalog;corrupt=true;
await assert.rejects(()=>failed.checkUpdate(),/SHA256/);assert.strictEqual(failed.catalog,previous);assert.equal(failed.snapshotCommit,null);
console.log('main refresh pins every file to one commit; a corrupt source preserves the old snapshot (HTTP test doubles).');
