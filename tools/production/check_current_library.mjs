import assert from 'node:assert/strict';
import fs from 'node:fs';
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
