import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {moduleDocument} from '../export-module-contracts.mjs';
import {UNKNOWN as U,unknownState,contentVersion,canonical,sha256,validateGenerationContract as validate,assemblyInterface} from '../../module-contract.js';
const tests=[];
const test=(name,fn)=>{fn();tests.push(name);};
const copy=v=>structuredClone(v);
function seal(d){const c=d.generationContract;c.contentVersion=contentVersion(d);c.visualization.contentVersion=c.contentVersion;if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;for(const v of c.validations)v.contentVersion=c.contentVersion;return d;}
function legacy(){return moduleDocument({case:{id:'foundation-test-only',factory_id:'foundation-test-only',capabilities:['move','jump'],platforms:[[-128,210,256,174]],spawn:[-104,192],entry_port:[-104,192],exit_port:[104,192],goal:[92,174,24,36],control_plan:[],thorns:[],latches:[],saws:[],moving_platforms:[],enemies:[],hooks:[]},result:U,geometryDefinitions:{player:{size:[24,36],source:{path:'TEST FIXTURE',sha256:'test-only'}},bell:{size:[28,34]}},sourceCases:{path:'TEST FIXTURE',sha256:'test-only'},sourceRun:U,protocol:U,binding:U},'0'.repeat(40));}
function position(d,p,at,face){p.position=at;p.face=face;p.normal={LEFT:[-1,0],RIGHT:[1,0],TOP:[0,-1],BOTTOM:[0,1]}[face];const o=d.objects.find(o=>o.id===p.objectId);o.x=at[0]-o.w/2;o.y=at[1]-o.h/2;}
function displacement(d){const c=d.generationContract;for(const r of c.routes){const a=c.ports.find(p=>p.id===r.from),b=c.ports.find(p=>p.id===r.to);r.localDisplacementBlocks=b.position.map((v,i)=>(v-a.position[i])/128);}}
function fixture(){
 const d=legacy(),c=d.generationContract;c.version=2;c.foundation={version:'1.0',blockSize:128,widthBlocks:2,heightBlocks:2};c.space.bounds={x:-128,y:128,w:256,h:256};
 for(const [i,p]of c.ports.entries()){p.stagingPosition=[...p.position];position(d,p,[i?128:-128,192],i?'RIGHT':'LEFT');p.surface='ROCK';p.permission=i?'OUTPUT':'INPUT';p.initialPermissionConditions={availableAbilitiesExact:['move','jump'],requiresRevalidationWithAdditionalUpwardAbilities:true};}
 for(const p of c.ports)c.relations.push({from:p.id,to:p.id,status:U,routeIds:[],conditions:U});
 for(const r of c.routes)Object.assign(r,{requiredAbilities:['jump'],actionTags:['jump'],durationSeconds:U,resourceProfile:U,initialConditions:U});
 c.closures=[];c.mirror={status:U,validationIds:[]};displacement(d);return seal(d);
}
const rejects=(d,re)=>assert.throws(()=>validate(d),re);
function mockEvidence(d){const c=d.generationContract;c.validations=[{id:'TEST-ONLY-NOT-PHYSICS-PROOF',contentVersion:c.contentVersion,kind:'physics',result:'pass',routeId:c.routes[0].id,from:c.routes[0].from,to:c.routes[0].to,capabilityConfiguration:{available:['jump'],equipment:U},entryState:unknownState(),method:'TEST DOUBLE; not an actual experiment',coverage:{testOnly:true},failures:[],unverified:['test fixture only'],artifacts:[{path:'TEST-ONLY-NOT-A-REAL-ARTIFACT',sha256:'0'.repeat(64)}]}];return seal(d);}
function closure(d){const c=d.generationContract;return c.closures[0]={id:'close-exit',closedPorts:['exit'],objectIds:[d.objects[0].id],routeIds:[],status:'declared',validationIds:[]};}
function selfRoute(d){const c=d.generationContract,r=copy(c.routes[0]);r.id='same-port-reward';r.from=r.to='entry';r.role='reward';r.localDisplacementBlocks=[0,0];c.routes.push(r);c.ports[0].permission='INOUT';const rel=c.relations.find(x=>x.from==='entry'&&x.to==='entry');rel.routeIds=[r.id];return r;}
function addEnemy(d,track=false){const c=d.generationContract,o={id:'test-enemy',type:'enemy',x:0,y:160,w:24,h:36,rotation:0};if(track){d.objects.push({id:'test-enemy-path',type:'trackLine',x:0,y:160,w:400,h:0,rotation:0,points:[{x:12,y:178},{x:400,y:178}],duration:3,mode:'loop'});o.trackId='test-enemy-path';c.space.occupancy.objectIds.push('test-enemy-path');}d.objects.push(o);c.space.occupancy.objectIds.push(o.id);c.space.dynamicEnvelopes.push({objectId:o.id,status:'observed_only',region:{x:-32,y:128,w:460,h:128}});}

// Shared structural fixture: UNKNOWN evidence, never a certified Module.
export const foundationFixture=fixture;
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
test('v1 remains accepted without Foundation fields and excludes diagonal matrix cells',()=>{const d=legacy();assert(validate(d).versionMatches);assert.equal(d.generationContract.relations.length,2);d.generationContract.relations.push({from:'entry',to:'entry',status:U,routeIds:[],conditions:U});rejects(d,/bad\/duplicate directed pair/);});
test('v2 full rectangle may have a nonzero negative origin; conversion is not certification',()=>{const d=fixture();assert(validate(d).versionMatches);assert.equal(d.generationContract.relations.length,4);assert.equal(assemblyInterface(d,{routeId:'main'}).eligible,false);assert(assemblyInterface(d).reasons.includes('foundation_v2_requires_static_route_consumer'));});
test('unsupported contract and Foundation versions fail',()=>{let d=fixture();d.generationContract.version=3;rejects(d,/unsupported/);d=fixture();d.generationContract.foundation.version='0.9';rejects(d,/foundation version/);});
test('rectangle dimensions and blockSize must match actual full bounds',()=>{for(const mutate of [f=>f.widthBlocks=1.5,f=>f.heightBlocks=0,f=>f.blockSize=64]){const d=fixture();mutate(d.generationContract.foundation);rejects(d,/foundation/);}const d=fixture();d.generationContract.space.bounds.w+=1;rejects(d,/full Block rectangle/);});
test('v2 never invokes the historical polyomino contract',()=>{const d=fixture();d.generationContract.space.blockGrid={schema:'legacy-invalid-test-only'};assert(validate(d).wellFormed);});
test('ports must be outer-face Block centers, not internal docks or corners',()=>{for(const at of [[-104,192],[-128,128],[-128,200],[-128,192.0001]]){const d=fixture();position(d,d.generationContract.ports[0],at,'LEFT');rejects(d,/boundary Block face center/);}});
test('normal, face, surface and initial permission are explicit',()=>{for(const [key,value]of [['face','W'],['surface','ground64/v1'],['permission',U],['normal',[1,0]]]){const d=fixture();d.generationContract.ports[0][key]=value;rejects(d,/foundation/);}});
test('TOP INPUT can declare its exact move and wall_climb condition without claiming physics certification',()=>{
 const d=fixture(),c=d.generationContract,p=c.ports[0];position(d,p,[-64,128],'TOP');p.surface='ONE_WAY_PLATFORM';p.support=U;
 p.initialPermissionConditions={availableAbilitiesExact:['move','wall_climb'],requiresRevalidationWithAdditionalUpwardAbilities:true};
 c.routes[0].requiredAbilities=['wall_climb'];displacement(d);assert(validate(seal(d)).wellFormed);
 delete p.initialPermissionConditions.requiresRevalidationWithAdditionalUpwardAbilities;assert(validate(seal(d)).wellFormed);
 assert.equal(assemblyInterface(d,{routeId:'main'}).eligible,false,'A condition declaration never grants actual physics admission');
});
test('v2 INPUT and OUTPUT require an explicit initial ability condition; INOUT remains optional',()=>{
 for(const permission of ['INPUT','OUTPUT']){const d=fixture(),p=d.generationContract.ports[0];p.permission=permission;delete p.initialPermissionConditions;rejects(d,/one-way Port requires initialPermissionConditions/);}
 const d=fixture();for(const p of d.generationContract.ports){p.permission='INOUT';delete p.initialPermissionConditions;}assert(validate(seal(d)).wellFormed);
});
test('initial permission masks reject UNKNOWN empty duplicate and non-string ability names',()=>{
 for(const abilities of [U,[],['move',U],['move','move'],[''],[' move'],[false],null]){
  const d=fixture();d.generationContract.ports[0].initialPermissionConditions.availableAbilitiesExact=abilities;rejects(d,/initialPermissionConditions/);
 }
});
test('initial permission conditions must be an object and optional revalidation flag can only be true',()=>{
 for(const value of [null,[],U,false]){const d=fixture();d.generationContract.ports[0].initialPermissionConditions=value;rejects(d,/initialPermissionConditions/);}
 for(const flag of [false,U,1,null]){const d=fixture();d.generationContract.ports[0].initialPermissionConditions.requiresRevalidationWithAdditionalUpwardAbilities=flag;rejects(d,/requiresRevalidationWithAdditionalUpwardAbilities must be true/);}
 const d=fixture();d.generationContract.ports[0].permission='INOUT';d.generationContract.ports[0].initialPermissionConditions.availableAbilitiesExact=[];rejects(d,/initialPermissionConditions/);
});
test('legacy v1 does not acquire the new optional Foundation permission-mask semantics',()=>{
 const d=legacy();assert(validate(d).wellFormed);d.generationContract.ports[0].initialPermissionConditions=U;assert(validate(d).wellFormed);
});
test('changing an exact initial ability mask changes semantic version and leaves admission unverified',()=>{
 const d=fixture(),before=d.generationContract.contentVersion;d.generationContract.ports[0].initialPermissionConditions.availableAbilitiesExact.push('shot_recoil');
 assert.notEqual(contentVersion(d),before);assert.equal(validate(d).versionMatches,false);assert.equal(assemblyInterface(d).eligible,false);
});
test('bottom AIR INPUT and INOUT fail, OUTPUT remains a typed but unconnected candidate',()=>{for(const permission of ['INPUT','INOUT','OUTPUT']){const d=fixture(),p=d.generationContract.ports[0];position(d,p,[-64,384],'BOTTOM');p.surface='AIR';p.permission=permission;p.support=U;displacement(d);if(permission==='OUTPUT')assert(validate(seal(d)).wellFormed);else rejects(d,/bottom AIR/);}});
test('ROCK rejects vertical faces; ONE_WAY_PLATFORM can use all four sides',()=>{for(const [face,at]of [['LEFT',[-128,192]],['RIGHT',[128,192]],['TOP',[-64,128]],['BOTTOM',[-64,384]]]){const d=fixture(),p=d.generationContract.ports[0];position(d,p,at,face);p.support=U;displacement(d);if(['TOP','BOTTOM'].includes(face))rejects(d,/ROCK Port only/);p.surface='ONE_WAY_PLATFORM';assert(validate(seal(d)).wellFormed);}});
test('typed support still references the one existing geometry object',()=>{const d=fixture();d.generationContract.ports[0].surface='ONE_WAY_PLATFORM';rejects(d,/support surface mismatch/);});
test('new stagingPosition and legacy grid staging stay separate from the boundary Port',()=>{const d=fixture();assert(validate(d).wellFormed);const p=d.generationContract.ports[0];p.grid={stagingPosition:p.stagingPosition};delete p.stagingPosition;assert(validate(seal(d)).wellFormed);});
test('N×N must include every diagonal and route direction must match the matrix',()=>{let d=fixture();d.generationContract.relations.pop();rejects(d,/including self/);d=fixture();d.generationContract.relations[1].routeIds=['main'];rejects(d,/lies about route direction/);});
test('same-Port reward route has zero displacement and requires both permissions when path',()=>{const d=fixture(),r=selfRoute(d),rel=d.generationContract.relations.find(x=>x.from===r.from&&x.to===r.to);rel.status='path';assert(validate(seal(d)).wellFormed);d.generationContract.ports[0].permission='INPUT';rejects(d,/initial Port permissions/);});
test('path status respects initial INPUT/OUTPUT without inferring an opening sequence',()=>{const d=fixture(),c=d.generationContract;c.relations[0].status='path';assert(validate(seal(d)).wellFormed);c.ports[0].permission='OUTPUT';rejects(d,/initial Port permissions/);});
test('UNKNOWN reverse and diagonal are preserved; a route cannot disappear from actual relations',()=>{const d=fixture();assert.equal(d.generationContract.relations[1].status,U);assert.equal(d.generationContract.relations[2].status,U);d.generationContract.relations[0].routeIds=[];rejects(d,/missing from actual directed relation/);});
test('new Route metadata is explicit and displacement comes from boundary Ports',()=>{for(const [key,value]of [['requiredAbilities',['jump','jump']],['actionTags',null],['durationSeconds',-1],['resourceProfile',[]],['initialConditions',null],['localDisplacementBlocks',[1,0]]]){const d=fixture();d.generationContract.routes[0][key]=value;rejects(d,/foundation route/);}});
test('static geometry and reservations remain bounded',()=>{let d=fixture();d.objects[0].x-=1;rejects(d,/bounds exclude actual object/);d=fixture();d.generationContract.space.occupancy.regions.push({x:-140,y:200,w:20,h:20});rejects(d,/occupied region\/bounds/);});
test('body clearance across a real interface is not static rectangle overlap',()=>{const d=fixture();d.generationContract.space.actionClearance.regions.push({x:-152,y:174,w:48,h:36});assert(validate(seal(d)).wellFormed);const old=legacy();old.generationContract.space.actionClearance.regions.push({x:-152,y:174,w:48,h:36});rejects(old,/clearance out of bounds/);});
test('dynamic enemy range and enemy motion annotation may leave the rectangle',()=>{for(const track of [false,true]){const d=fixture();addEnemy(d,track);assert(validate(seal(d)).wellFormed);}});
test('enemy spawn geometry and environment collision envelopes still obey rectangle bounds',()=>{let d=fixture();addEnemy(d);d.objects.find(o=>o.id==='test-enemy').x=120;rejects(d,/bounds exclude actual object/);d=fixture();d.generationContract.space.dynamicEnvelopes.push({objectId:d.objects[0].id,status:'declared',region:{x:-140,y:200,w:280,h:184}});rejects(d,/dynamic envelope\/bounds/);});
test('closure profiles reference real Ports/Cells/routes, not copied geometry or markers',()=>{const d=fixture(),p=closure(d);assert(validate(seal(d)).wellFormed);p.closedPorts=['invented'];rejects(d,/closedPorts unknown reference/);p.closedPorts=['exit'];p.objectIds=[d.generationContract.ports[0].objectId];rejects(d,/actual Cell geometry/);});
test('a closure cannot claim to preserve a route whose external Port it closes',()=>{const d=fixture(),p=closure(d);p.routeIds=['main'];rejects(d,/through a closed Port/);});
test('verified closure or mirror requires current passing artifact references',()=>{for(const kind of ['closure','mirror']){const d=fixture(),p=kind==='closure'?closure(d):d.generationContract.mirror;p.status='verified';rejects(d,/current passing artifact references/);mockEvidence(d);p.validationIds=[d.generationContract.validations[0].id];assert(validate(seal(d)).wellFormed);d.generationContract.validations[0].artifacts=[];rejects(d,/physics pass requires/);}});
test('a failed or stale evidence record cannot be reused as verified closure proof',()=>{const d=fixture(),p=closure(d);mockEvidence(d);p.status='verified';p.validationIds=[d.generationContract.validations[0].id];seal(d);d.generationContract.validations[0].result='failed';d.generationContract.validations[0].failures=['TEST FAILURE'];rejects(d,/current passing artifact references/);d.generationContract.validations[0].contentVersion='sha256:'+'f'.repeat(64);rejects(d,/another content version/);});
test('verified closure cannot have no referenced boundary Cell',()=>{const d=fixture(),p=closure(d);mockEvidence(d);p.status='verified';p.validationIds=[d.generationContract.validations[0].id];p.objectIds=[];rejects(d,/actual Cell references/);});
test('mirrored coordinates preserve Port IDs/permissions and matrix direction',()=>{const d=fixture(),c=d.generationContract,b=c.space.bounds,original=copy(c.relations);for(const o of d.objects){o.x=2*b.x+b.w-o.x-o.w;if(o.points)o.points=o.points.map(p=>({...p,x:2*b.x+b.w-p.x}));if(o.control)o.control.x=2*b.x+b.w-o.control.x;}
 for(const p of c.ports){p.position[0]=2*b.x+b.w-p.position[0];p.stagingPosition[0]=2*b.x+b.w-p.stagingPosition[0];p.normal[0]=-p.normal[0];p.face=p.face==='LEFT'?'RIGHT':'LEFT';}
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>d.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}displacement(d);assert.deepEqual(c.relations,original);assert.equal(c.ports[0].permission,'INPUT');assert.deepEqual(c.routes[0].localDisplacementBlocks,[-2,0]);assert(validate(seal(d)).wellFormed);});
test('changing Foundation semantics changes contentVersion and does not create trusted certification',()=>{const d=fixture(),old=d.generationContract.contentVersion;d.generationContract.ports[0].permission='INOUT';assert.notEqual(contentVersion(d),old);assert.equal(validate(d).versionMatches,false);assert.equal(assemblyInterface(d).eligible,false);});
function cornerOptions(d,p,corner,targetFace,targetPosition){
 p.cornerRelocations=Object.fromEntries(['TOP_LEFT','TOP_RIGHT','BOTTOM_LEFT','BOTTOM_RIGHT'].map(k=>[k,{applicable:k===corner,allowed:k===corner?U:false,reason:k===corner?'actual local adaptation and physics required':'not this corner',profileId:null}]));
 Object.assign(p.cornerRelocations[corner],{targetFace,targetPosition,proposedSurface:'ONE_WAY_PLATFORM',permission:p.permission});
 d.generationContract.portConfigurations=[];return p.cornerRelocations[corner];
}
test('all four corners allow only the same Block adjacent outer face; permission remains UNKNOWN',()=>{
 for(const [corner,at,target,destination]of [['TOP_LEFT',[-128,192],'TOP',[-64,128]],['TOP_RIGHT',[128,192],'TOP',[64,128]],['BOTTOM_LEFT',[-128,320],'BOTTOM',[-64,384]],['BOTTOM_RIGHT',[128,320],'BOTTOM',[64,384]]]){
  const d=fixture(),p=d.generationContract.ports[0];position(d,p,at,corner.endsWith('LEFT')?'LEFT':'RIGHT');displacement(d);const o=cornerOptions(d,p,corner,target,destination);assert(validate(seal(d)).wellFormed);assert.equal(o.allowed,U);o.targetPosition[0]+=128;rejects(d,/same corner Block/);
 }
});
test('missing corner extension is backward compatible; incomplete or falsely applicable attributes fail',()=>{
 const d=fixture(),p=d.generationContract.ports[0];assert(validate(d).wellFormed);cornerOptions(d,p,'TOP_LEFT','TOP',[-64,128]);delete p.cornerRelocations.BOTTOM_RIGHT;rejects(d,/all four corners/);cornerOptions(d,p,'TOP_LEFT','TOP',[-64,128]);p.cornerRelocations.BOTTOM_RIGHT.applicable=true;rejects(d,/applicability/);
});
test('corner flags cannot grant a Port direction or claimed physical success without a full configuration',()=>{
 const d=fixture(),p=d.generationContract.ports[0],o=cornerOptions(d,p,'TOP_LEFT','TOP',[-64,128]);o.permission='INOUT';rejects(d,/preserves initial permissions/);o.permission=p.permission;o.allowed=true;o.profileId='invented';rejects(d,/verified whole configuration/);o.proposedSurface='ROCK';rejects(d,/relocated ROCK/);
});
test('verified configuration binds artifact bytes and explicitly preserves all routes',()=>{
 const d=fixture(),c=d.generationContract,p=c.ports[0],o=cornerOptions(d,p,'TOP_LEFT','TOP',[-64,128]);mockEvidence(d);const v=c.validations[0],config={path:'TEST-ONLY-configuration.json',sha256:'b'.repeat(64)};
 const profile={id:'TEST-ONLY-corner-config',status:'verified',validationIds:[v.id],routeIds:c.routes.map(r=>r.id),relocations:[{portId:p.id,corner:'TOP_LEFT'}],configuration:config};c.portConfigurations=[profile];o.allowed=true;o.profileId=profile.id;
 rejects(d,/bind exact selected configuration/);v.coverage={portConfigurationId:profile.id,configurationSha256:config.sha256};v.artifacts.push(config);assert(validate(seal(d)).wellFormed);profile.routeIds=[];rejects(d,/preserve all declared routes/);
});
test('one logical Port cannot select two corner destinations in one configuration',()=>{
 const d=fixture(),c=d.generationContract,p=c.ports[0];cornerOptions(d,p,'TOP_LEFT','TOP',[-64,128]);c.portConfigurations=[{id:'duplicate-selection',status:U,validationIds:[],routeIds:[],relocations:[{portId:p.id,corner:'TOP_LEFT'},{portId:p.id,corner:'TOP_LEFT'}]}];rejects(d,/unique logical Ports/);
});
console.log(JSON.stringify({foundation_contract_tests:tests.length,passed:tests.length,physics:false,scope:'Pure structural tests and explicit evidence test doubles; no Module certification or migration count increase.'}));
}
