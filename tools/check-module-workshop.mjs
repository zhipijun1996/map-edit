import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {filterModules,matchingRoutes,validateDraft,designFeedback} from '../generation/module-workshop/model.js';
const req=(allOf,status='defined',anyOfGroups=[])=>({version:1,status,allOf,anyOfGroups,note:''});
const m={id:'test',title:'test',summary:'',category:'平原',stage:'IMPLEMENTED_CANDIDATE',foundation:{widthBlocks:4,heightBlocks:3},ports:[{id:'a',face:'LEFT',permission:'INOUT'},{id:'b',face:'RIGHT',permission:'INOUT'},{id:'c',face:'TOP',permission:'INOUT'}],routes:[{id:'ab',from:'a',to:'b',capabilityRequirements:req(['shot_recoil'])},{id:'ba',from:'b',to:'a',capabilityRequirements:req(['shot_recoil'])},{id:'ac',from:'a',to:'c',capabilityRequirements:req(['grapple'])}]};
assert.equal(filterModules([m],{width:4,height:3,from:'LEFT',to:'RIGHT',ability:'shot_recoil'}).length,1);
assert.equal(filterModules([m],{width:3}).length,0);
assert.equal(filterModules([m],{from:'LEFT',to:'RIGHT',ability:'grapple'}).length,0,'Ability on another Route cannot satisfy the selected direction');
assert.equal(matchingRoutes(m,{from:'LEFT',to:'RIGHT',bidirectional:true}).length,1);
assert.equal(matchingRoutes(m,{from:'LEFT',to:'TOP',bidirectional:true}).length,0,'Do not invent the reverse direction');
assert.equal(matchingRoutes(m,{from:'LEFT',to:'RIGHT',available:['jump'],includeUnknown:true}).length,0);
const or=structuredClone(m);or.routes[0].capabilityRequirements=req(['jump'],'defined',[['shot_recoil','grapple']]);
assert.equal(matchingRoutes(or,{from:'LEFT',to:'RIGHT',available:['jump','grapple']}).length,1);
assert.equal(matchingRoutes(or,{from:'LEFT',to:'RIGHT',available:['grapple']}).length,0,'All AND terms still apply');
const partial=structuredClone(m);partial.routes[0].capabilityRequirements=req(['shot_recoil'],'partial');
assert.equal(matchingRoutes(partial,{from:'LEFT',to:'RIGHT',available:['shot_recoil'],includeUnknown:false}).length,0);
assert.equal(matchingRoutes(partial,{from:'LEFT',to:'RIGHT',available:['shot_recoil'],includeUnknown:true}).length,1);
const forbidden=structuredClone(m);forbidden.ports[0].permission='OUTPUT';assert.equal(matchingRoutes(forbidden,{from:'LEFT'}).length,0);
assert.equal(filterModules([{...m,stage:'READY_FOR_IMPLEMENTATION'}],{stage:'complete'}).length,0);
assert.equal(filterModules([{...m,stage:'NEEDS_ALIGNMENT'}],{stage:'complete'}).length,0);
const conditional=structuredClone(m);conditional.ports[0].initialPermissionConditions={availableAbilitiesExact:['shot_recoil']};assert.equal(matchingRoutes(conditional,{from:'LEFT',to:'RIGHT',available:['shot_recoil']}).length,1);assert.equal(matchingRoutes(conditional,{from:'LEFT',to:'RIGHT',available:['shot_recoil','grapple']}).length,0,'Do not inherit initial one-way permissions with extra abilities');
const raw='  原话\n保持原样 <script>  ';
const draft=validateDraft({id:'idea-abcdef',sourceType:'human_idea',title:'test',verbatim:raw,stage:'IDEA',implemented:true});assert.equal(draft.verbatim,raw);assert(!('implemented'in draft));
assert.throws(()=>validateDraft({...draft,stage:'ARCHIVED'}));
assert.throws(()=>designFeedback({id:'idea-abcdef'},'KEEP',''));
assert.match(designFeedback({id:'idea-abcdef',design:{version:'sha256:exact',sha256:'bytes'}},'KEEP','保留'),/sha256:exact/);
const read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const data=read('generation/module-workshop/data.json'),h=read('feedback/manual-review/implementation-handoff-v1.json'),q=read('generation/manual-review/queue.json'),catalog=read('modules/catalog.json');
assert.equal(data.sources.catalogSha256,hash('modules/catalog.json'));assert.equal(data.sources.handoffRevision,h.revision);assert.equal(data.modules.length,h.rows.length);assert.equal(new Set(data.modules.map(m=>m.id)).size,data.modules.length);
for(const m of data.modules){
 const approved=h.rows.find(h=>h.moduleId===m.id);assert.equal(m.designVersion,approved.designVersion);assert.equal(hash(m.designFile),m.designFileSha256);
 assert(m.ports.every(p=>['LEFT','RIGHT','TOP','BOTTOM'].includes(p.face)));
 if(['IMPLEMENTED_CANDIDATE','ARCHIVED'].includes(m.stage)){assert.equal(m.foundationCheck,'PASS');assert.equal(m.mapReady,false);}
 if(m.stage==='IMPLEMENTED_CANDIDATE'){assert.equal(m.implementation.designVersion,m.designVersion);assert.equal(m.implementation.declaredStatus,'PASS');assert(m.implementation.nativePlayable);}
 if(m.stage==='ARCHIVED'){const source=catalog.modules.find(c=>c.id===m.id);assert(source);assert.equal(hash(source.file),source.contentSha256);}
 const reviewed=q.rows.find(q=>q.moduleId===m.id);if(reviewed)assert.equal(reviewed.receivedDecision,'KEEP');
 assert.equal(m.productionApproval,false);
}
for(const[s,n]of Object.entries(data.counts))assert.equal(data.modules.filter(m=>m.stage===s).length,n);
const snapshot=read('generation/module-workshop/implementation-snapshot.json');assert.equal(data.sources.reportedTechnicalPass,snapshot.rows.filter(r=>r.declaredStatus==='PASS').length);for(const m of data.modules.filter(m=>m.stage==='NEEDS_ALIGNMENT'))assert.notEqual(m.implementation.designVersion,m.designVersion);for(const m of data.modules.filter(m=>m.stage==='NEEDS_REPAIR'))assert(m.implementation.declaredStatus!=='PASS'||!m.implementation.interface||!m.implementation.nativePlayable);
assert(!data.modules.some(m=>q.rows.find(q=>q.moduleId===m.id)?.receivedDecision==='DISCARD'));
for(const i of data.ideas.filter(i=>i.design)){assert.equal(hash(i.design.file),i.design.sha256);assert(fs.existsSync('generation/module-workshop/'+i.design.diagram));}
console.log('Module workshop: directed AND/OR filtering, permissions, exact approvals, candidate/archival gates and source bindings pass. No physics run.');
