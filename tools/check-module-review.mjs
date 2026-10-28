// Consumer visualization checks; no normalization or physics certification.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {physicalPortGroups,portCounts,foundationReview,renderFoundationReview,renderPortReview} from '../module-review-overlay.js';
import {renderContractSvg} from '../module-contract-render.js';
const catalog=JSON.parse(fs.readFileSync('modules/catalog.json'));
let logical=0,physical=0,aliasModules=0;
for(const entry of catalog.modules){
 const doc=JSON.parse(fs.readFileSync(entry.file)),before=JSON.stringify(doc),c=doc.generationContract;
 const view=foundationReview(doc),counts=portCounts(c.ports),groups=physicalPortGroups(c.ports);
 assert(view);assert.equal(view.blockSize,128);assert.deepEqual(view.bounds,c.space.bounds);
 assert.equal(counts.logical,c.ports.length);assert.equal(counts.physical,groups.length);
 const svg=renderFoundationReview(doc,{unitsPerPixel:3});
 assert(svg.includes('data-block-grid="128"'));assert(svg.includes('data-module-footprint="true"'));
 assert.equal((svg.match(/data-physical-port=/g)??[]).length,groups.length);
 assert.deepEqual(groups.flatMap(g=>g.ids).sort(),c.ports.map(p=>p.id).sort());
 for(const group of groups){
  const [x,y]=group.position,b=view.bounds,face=group.face;
  assert(Math.abs((face==='LEFT'?x-b.x:face==='RIGHT'?x-b.x-b.w:face==='TOP'?y-b.y:y-b.y-b.h))<1e-5);
  const tangent=face==='LEFT'||face==='RIGHT'?y-b.y:x-b.x;
  assert(Math.abs(tangent/128-.5-Math.round(tangent/128-.5))<1e-5);
 }
 assert(!renderFoundationReview(doc,{grid:false}).includes('data-block-grid="128"'));
 assert(!renderFoundationReview(doc,{ports:false}).includes('data-physical-port='));
 assert(renderPortReview(doc,{unitsPerPixel:3}).includes('scale(3)'));
 assert.equal(JSON.stringify(doc),before,'Review must not rewrite documents, Port IDs or routes');
 assert.equal(fs.readFileSync(entry.thumbnail,'utf8'),renderContractSvg(doc),'Default persistent SVG output stays byte-identical');
 const review=renderContractSvg(doc,{review:true});assert.equal((review.match(/data-physical-port=/g)??[]).length,groups.length);
 logical+=counts.logical;physical+=counts.physical;aliasModules+=Number(counts.logical!==counts.physical);
}
const aliases=[{id:'entry',position:[128,64],face:'RIGHT',normal:[1,0],surface:'ROCK',permission:'INPUT'},
 {id:'exit',position:[128,64],face:'RIGHT',normal:[1,0],surface:'ROCK',permission:'OUTPUT'}];
assert.equal(physicalPortGroups(aliases).length,1,'Coincident logical names represent one geometric glyph');
assert.equal(physicalPortGroups([...aliases,{...aliases[0],id:'opposite',face:'LEFT',normal:[-1,0]}]).length,2,'Different faces cannot be merged');
assert.equal(physicalPortGroups([...aliases,{...aliases[0],id:'near',position:[128,65]}]).length,2,'Nearby Ports are not normalized by presentation');
const app=fs.readFileSync('app.js','utf8');
for(const legacy of ['RepositoryLibraryClient','librarySourceTabs','show-game-library','show-repository-library','checkLibraryUpdate','sync-library.yml'])assert(!app.includes(legacy),'No legacy library UI or refresh entry: '+legacy);
console.log(JSON.stringify({passed:true,currentModules:catalog.modules.length,logicalPorts:logical,physicalPorts:physical,modulesWithAliases:aliasModules,physics:false,sourceDocumentsMutated:false}));
