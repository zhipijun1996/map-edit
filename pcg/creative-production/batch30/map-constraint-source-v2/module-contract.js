// Additive extension of gunman-rush-level-sketch/v1. UNKNOWN never grants access.
import {validateDocument} from './model.js';
import {validateRequirements,evaluateRequirements} from './capabilities.js';
import {validateDifficulty} from './difficulty.js';
import {validateBlockGrid} from './module-block-grid.js';
export const UNKNOWN='UNKNOWN';
export const CONTRACT_VERSION=1;
export const canonical=v=>JSON.stringify(sort(v));
function sort(v){if(Array.isArray(v))return v.map(sort);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sort(v[k])]));return v;}
// Synchronous SHA-256 so the editor and Node use exactly the same version gate.
export function sha256(text){
 const bytes=new TextEncoder().encode(text),n=bytes.length,padded=new Uint8Array((n+9+63>>6)<<6);padded.set(bytes);padded[n]=128;
 const view=new DataView(padded.buffer);view.setUint32(padded.length-8,Math.floor(n/0x20000000));view.setUint32(padded.length-4,n*8>>>0);
 const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
 const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const ro=(x,b)=>x>>>b|x<<32-b,w=new Uint32Array(64);
 for(let offset=0;offset<padded.length;offset+=64){
  for(let i=0;i<16;i++)w[i]=view.getUint32(offset+4*i);
  for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(ro(a,7)^ro(a,18)^a>>>3)+w[i-16]+(ro(b,17)^ro(b,19)^b>>>10)+w[i-7];}
  let [a,b,c,d,e,f,g,q]=h;
  for(let i=0;i<64;i++){const t1=(q+(ro(e,6)^ro(e,11)^ro(e,25))+((e&f)^(~e&g))+k[i]+w[i])|0,t2=((ro(a,2)^ro(a,13)^ro(a,22))+((a&b)^(a&c)^(b&c)))|0;q=g;g=f;f=e;e=d+t1|0;d=c;c=b;b=a;a=t1+t2|0;}
  for(const [i,v]of[a,b,c,d,e,f,g,q].entries())h[i]=h[i]+v|0;
 }
 return h.map(v=>(v>>>0).toString(16).padStart(8,'0')).join('');
}
export function contentVersion(doc){
 const c=structuredClone(doc.generationContract);if(!c)throw Error('Missing generationContract');
 delete c.contentVersion;delete c.validations;delete c.staticChecks;delete c.visualization;
 // Integration review is evidence, not a geometry edit. Keep it separate.
 const source=structuredClone(doc.source??{});delete source.integration;
 return 'sha256:'+sha256(canonical({id:doc.id,canvas:doc.canvas,objects:doc.objects,source,capabilityRequirements:doc.capabilityRequirements,difficulty:doc.difficulty,intent:doc.intent,contract:c}));
}
const need=(ok,msg)=>{if(!ok)throw Error('Module contract: '+msg);};
const finite=n=>typeof n==='number'&&Number.isFinite(n);
const vec=v=>Array.isArray(v)&&v.length===2&&v.every(finite);
const rect=r=>r&&['x','y','w','h'].every(k=>finite(r[k]))&&r.w>0&&r.h>0;
const range=v=>Array.isArray(v)&&v.length===2&&v.every(finite)&&v[0]<=v[1];
const ids=(xs,what)=>{need(Array.isArray(xs),what+' must be an array');const s=new Set();for(const x of xs){need(typeof x.id==='string'&&x.id.length>0&&!s.has(x.id),what+' duplicate/missing ID');s.add(x.id);}return s;};
const contained=(a,b)=>a.x>=b.x-1e-5&&a.y>=b.y-1e-5&&a.x+a.w<=b.x+b.w+1e-5&&a.y+a.h<=b.y+b.h+1e-5;
export const unknownState=()=>({capabilityRequirements:{version:1,status:'unspecified',allOf:[],anyOfGroups:[],note:''},equipment:UNKNOWN,grounded:UNKNOWN,velocity:UNKNOWN,remainingJumps:UNKNOWN,airShots:UNKNOWN,stamina:UNKNOWN,health:UNKNOWN,shotCooldown:UNKNOWN,traversalState:UNKNOWN,mechanisms:UNKNOWN,phase:UNKNOWN,recoveryConditions:UNKNOWN});
export function validateState(s){
 need(s&&typeof s==='object','missing state');validateRequirements(s.capabilityRequirements);
 for(const key of Object.keys(unknownState()))need(Object.hasOwn(s,key),'state missing '+key+'; use UNKNOWN');
 need(s.grounded===UNKNOWN||typeof s.grounded==='boolean','grounded must be boolean/UNKNOWN');
 for(const key of ['remainingJumps','airShots','stamina','health','shotCooldown'])need(s[key]===UNKNOWN||range(s[key]),'invalid state range '+key);
 for(const key of ['remainingJumps','airShots','stamina','health','shotCooldown'])if(s[key]!==UNKNOWN){need(s[key][0]>=0,'negative resource '+key);if(['remainingJumps','airShots'].includes(key))need(s[key].every(Number.isInteger),'non-integer action count');}
 need(s.velocity===UNKNOWN||s.velocity&&range(s.velocity.x)&&range(s.velocity.y),'invalid velocity range');
 for(const key of ['equipment','mechanisms','phase','recoveryConditions'])need(s[key]===UNKNOWN||s[key]!==null&&typeof s[key]==='object','invalid state '+key);
 need(s.traversalState===UNKNOWN||typeof s.traversalState==='string','invalid traversal state');return s;
}
function shapeBounds(o){
 if(o.points){const ps=[...o.points,...(o.control?[o.control]:[])];return {x:Math.min(...ps.map(p=>p.x)),y:Math.min(...ps.map(p=>p.y)),w:Math.max(...ps.map(p=>p.x))-Math.min(...ps.map(p=>p.x)),h:Math.max(...ps.map(p=>p.y))-Math.min(...ps.map(p=>p.y))};}
 const angle=(o.rotation??0)*Math.PI/180,w=Math.abs(o.w*Math.cos(angle))+Math.abs(o.h*Math.sin(angle)),h=Math.abs(o.w*Math.sin(angle))+Math.abs(o.h*Math.cos(angle));return {x:o.x+o.w/2-w/2,y:o.y+o.h/2-h/2,w,h};
}
export function validateGenerationContract(doc,{resolve}={}){
 validateDocument(doc);const c=doc.generationContract;need(c&&c.version===1,'unsupported/missing extension');need(['module','macro'].includes(c.kind),'kind');
 need(typeof doc.id==='string'&&doc.id.length>0,'stable document ID');need(/^sha256:[a-f0-9]{64}$/.test(c.contentVersion),'contentVersion');
 need(c.seed&&['known','not_used',UNKNOWN].includes(c.seed.status)&&Object.hasOwn(c.seed,'value'),'explicit seed status/value');if(c.seed.status==='known')need(typeof c.seed.value==='string'||Number.isSafeInteger(c.seed.value),'safe integer/string seed');
 need(Object.hasOwn(c,'seed')&&c.generation?.parameters&&c.generation?.source,'seed, generation parameters/source required');
 need(['declared',UNKNOWN].includes(c.designStatus),'designStatus');need(doc.source?.integration&&[true,false,null].includes(doc.source.integration.isIntegrated),'existing source.integration required');need(Object.hasOwn(doc,'capabilityRequirements')&&Object.hasOwn(doc,'difficulty'),'explicit existing capability/difficulty fields');validateRequirements(doc.capabilityRequirements);validateDifficulty(doc.difficulty);
 const objects=new Map(doc.objects.map(o=>[o.id,o]));need(objects.size===doc.objects.length,'duplicate geometry IDs');
 const s=c.space;need(s?.units==='godot_world_unit'&&s.axes?.x==='right'&&s.axes?.y==='down'&&vec(s.localOrigin),'world units/axes/origin');need(doc.canvas.units==='godot_world_unit'&&doc.canvas.positionPrecision==='exact','exact canvas units');need(rect(s.bounds),'bounds');need(s.actorBody&&vec(s.actorBody.size)&&s.actorBody.size.every(x=>x>0),'actor body dimensions');
 need(s.occupancy&&Array.isArray(s.occupancy.objectIds)&&Array.isArray(s.occupancy.regions)&&s.occupancy.status,'occupancy');
 for(const id of s.occupancy.objectIds)need(objects.has(id),'unknown occupied object '+id);
 for(const o of objects.values())if(!['entry','exit','note','route','anchor'].includes(o.type)){const b=shapeBounds(o);need(contained(b,s.bounds),'bounds exclude actual object '+o.id);need(s.occupancy.objectIds.includes(o.id),'unreserved actual object '+o.id);}
 for(const region of s.occupancy.regions)need(rect(region)&&contained(region,s.bounds),'occupied region/bounds');
 need(s.actionClearance&&Array.isArray(s.actionClearance.regions)&&typeof s.actionClearance.coverage==='string'&&s.actionClearance.status,'separate actionClearance required');
 for(const region of s.actionClearance.regions)need(rect(region)&&contained(region,s.bounds),'clearance out of bounds');
 need(Array.isArray(s.dynamicEnvelopes)&&Array.isArray(s.seams)&&Array.isArray(s.transforms),'dynamic envelopes, seams, transforms');
 for(const e of s.dynamicEnvelopes){need(objects.has(e.objectId),'dynamic envelope object missing');need(e.region===UNKNOWN||rect(e.region)&&contained(e.region,s.bounds),'dynamic envelope/bounds');need(e.status,'dynamic envelope status');const o=objects.get(e.objectId),track=objects.get(o.trackId);if(e.region!==UNKNOWN&&track)for(const point of [...track.points,...(track.control?[track.control]:[])])need(contained({x:point.x-o.w/2,y:point.y-o.h/2,w:o.w,h:o.h},e.region),'dynamic activity envelope too small');}
 for(const o of objects.values())if(o.trackId||o.type==='enemy')need(s.dynamicEnvelopes.some(e=>e.objectId===o.id),'missing activity envelope '+o.id);
 const transformIds=ids(s.transforms,'transforms');for(const t of s.transforms){need(vec(t.translation)&&vec(t.scale)&&finite(t.rotation)&&typeof t.mirrorX==='boolean','explicit transform');need(t.status&&Array.isArray(t.validationIds),'transform evidence');}
 const portIds=ids(c.ports,'ports'),routeIds=ids(c.routes,'routes');need(c.ports.length>0,'ports required');
 for(const p of c.ports){
  if(p.grid)need(s.blockGrid,'grid staging requires explicit Block contract');
  need(objects.has(p.objectId)&&['entry','exit','anchor'].includes(objects.get(p.objectId).type),'port geometry reference');need(vec(p.position)&&vec(p.normal)&&Math.abs(Math.hypot(...p.normal)-1)<1e-5,'port position/normal');
  const marker=objects.get(p.objectId);need(Math.abs(marker.x+marker.w/2-p.position[0])<1e-5&&Math.abs(marker.y+marker.h/2-p.position[1])<1e-5,'port marker not at actual declared position');
  need(p.connection&&p.connection.status&&(p.connection.region===UNKNOWN||rect(p.connection.region)),'connection range/status required');
  need(p.support===UNKNOWN||objects.has(p.support.objectId)&&p.support.face,'support reference');
  if(p.support!==UNKNOWN&&p.support.face==='top'){const b=shapeBounds(objects.get(p.support.objectId)),at=p.grid?.stagingPosition??p.position;need(vec(at)&&at[0]>=b.x&&at[0]<=b.x+b.w&&Math.abs(at[1]+s.actorBody.size[1]/2-b.y)<1,'port support does not match standing player geometry');}
  for(const key of ['ingress','egress']){const m=p.motion?.[key];need(m&&Object.hasOwn(m,'directions')&&Object.hasOwn(m,'modes'),'separate ingress/egress');need(m.directions===UNKNOWN||Array.isArray(m.directions)&&m.directions.every(vec),'motion directions');need(m.modes===UNKNOWN||Array.isArray(m.modes)&&m.modes.every(x=>typeof x==='string'),'motion modes');}
  validateState(p.preconditions?.ingress);validateState(p.preconditions?.egress);need(Array.isArray(p.seamIds)&&p.seamIds.every(id=>s.seams.some(x=>x.id===id&&x.portId===p.id)),'port seam mapping');
 }
 ids(s.seams,'seams');for(const seam of s.seams)need(portIds.has(seam.portId)&&(seam.region===UNKNOWN||rect(seam.region))&&Array.isArray(seam.allowedOverlap)&&seam.status,'seam');
 const pairKeys=new Set();need(Array.isArray(c.relations),'relations');
 for(const rel of c.relations){const key=rel.from+'\0'+rel.to;need(portIds.has(rel.from)&&portIds.has(rel.to)&&rel.from!==rel.to&&!pairKeys.has(key),'bad/duplicate directed pair');pairKeys.add(key);need(['path','no_path',UNKNOWN].includes(rel.status),'directed pair status');need(Array.isArray(rel.routeIds)&&rel.routeIds.every(id=>routeIds.has(id)),'relation route reference');if(rel.status==='path')need(rel.routeIds.length>0,'path without route');if(rel.status==='no_path')need(rel.routeIds.length===0,'no_path cannot contain routes');need(Object.hasOwn(rel,'conditions'),'relation conditions or UNKNOWN');}
 need(pairKeys.size===c.ports.length*(c.ports.length-1),'every ordered port pair must be explicit');
 const validationIds=ids(c.validations,'validations');
 for(const r of c.routes){need(portIds.has(r.from)&&portIds.has(r.to)&&r.from!==r.to,'route endpoints');need(['main','reward','return','recovery','shortcut'].includes(r.role),'route role');need(objects.has(r.pathObjectId)&&objects.get(r.pathObjectId).type==='route','actual route object');need(Object.hasOwn(r,'capabilityRequirements')&&Object.hasOwn(r,'difficulty'),'explicit per-route capabilities/difficulty');validateRequirements(r.capabilityRequirements);validateDifficulty(r.difficulty);validateState(r.transfer?.requires);validateState(r.transfer?.ensures);need(['declared','observed_only','verified',UNKNOWN].includes(r.transfer.status),'transfer status');need(r.resourcePressure&&r.resourcePressure.status,'route resource pressure');need(r.return&&['yes','no',UNKNOWN].includes(r.return.status)&&Object.hasOwn(r.return,'conditions'),'return and conditions');if(r.return.status==='yes')need(routeIds.has(r.return.routeId)&&c.routes.some(back=>back.id===r.return.routeId&&back.from===r.to&&back.to===r.from),'return must reference reverse route');need(r.onward&&Object.hasOwn(r.onward,'target')&&r.onward.status,'onward/safe recovery declaration');validateState(r.onward.requiredState);if(r.onward.status==='verified')need(r.onward.target!==UNKNOWN&&(objects.has(r.onward.target.supportObjectId)||portIds.has(r.onward.target.portId)||routeIds.has(r.onward.target.routeId)),'fictional onward target');need(Array.isArray(r.validationIds)&&r.validationIds.every(id=>validationIds.has(id)),'route validation refs');need(Object.hasOwn(r,'availability'),'route availability');}
 for(const rel of c.relations)for(const id of rel.routeIds)need(c.routes.some(r=>r.id===id&&r.from===rel.from&&r.to===rel.to),'relation lies about route direction');
 need(Array.isArray(c.unlocks),'unlocks');ids(c.unlocks,'unlocks');for(const u of c.unlocks){need(objects.has(u.trigger.objectId)&&u.trigger.condition&&u.changes,'unlock trigger/change');for(const phase of ['before','after']){const x=u[phase];need(x&&portIds.has(x.from)&&portIds.has(x.to)&&x.conditions&&['path','no_path',UNKNOWN].includes(x.status),'unlock '+phase+' directed endpoints/state');if(x.status==='path')need(routeIds.has(x.routeId),'unlock route reference');}}
 for(const v of c.validations){need(v.contentVersion===c.contentVersion,'evidence bound to another content version');need(['static','physics'].includes(v.kind),'validation kind');need(['pass','failed','partial',UNKNOWN].includes(v.result),'validation result');need(Object.hasOwn(v,'routeId')&&Object.hasOwn(v,'from')&&Object.hasOwn(v,'to'),'scoped validation route/pair');if(v.routeId!==UNKNOWN){need(routeIds.has(v.routeId),'unknown validated route');const r=c.routes.find(r=>r.id===v.routeId);need(v.from===r.from&&v.to===r.to,'validation direction mismatch');}need(v.capabilityConfiguration&&Array.isArray(v.capabilityConfiguration.available),'validated abilities');validateState(v.entryState);need(v.method&&v.coverage&&Array.isArray(v.failures)&&Array.isArray(v.unverified)&&Array.isArray(v.artifacts),'validation method/coverage/failures/unknowns/artifacts');need(Object.hasOwn(v.capabilityConfiguration,'equipment'),'validated equipment or UNKNOWN');need(v.artifacts.every(a=>typeof a.path==='string'&&/^[a-f0-9]{64}$/.test(a.sha256)),'artifact SHA256');if(v.result==='failed')need(v.failures.length>0,'failed verification requires failure reasons');if(v.kind==='physics'&&v.result==='pass')need(v.routeId!==UNKNOWN&&v.artifacts.length>0,'physics pass requires a directed route and artifacts');}
 for(const t of s.transforms)need(t.validationIds.every(id=>validationIds.has(id)),'transform validation reference');
 if(c.staticChecks)need(c.staticChecks.contentVersion===c.contentVersion&&['pass','failed','partial',UNKNOWN].includes(c.staticChecks.result),'static checks version/status');
 need(c.visualization?.contentVersion===c.contentVersion&&typeof c.visualization.path==='string'&&!c.visualization.path.includes('/')&&!c.visualization.path.includes('\\'),'version-bound visualization');
 need(c.composition&&Array.isArray(c.composition.components)&&Array.isArray(c.composition.connections)&&Array.isArray(c.composition.exports)&&Array.isArray(c.composition.cells),'composition');
 ids(c.composition.cells,'standalone cells');for(const cell of c.composition.cells){need(/^sha256:[a-f0-9]{64}$/.test(cell.contentVersion)&&Array.isArray(cell.objectIds)&&cell.objectIds.length>0&&cell.objectIds.every(id=>objects.has(id)),'versioned Cell geometry refs');const os=cell.objectIds.map(id=>objects.get(id));need(cell.contentVersion==='sha256:'+sha256(canonical(os.length===1?os[0]:os)),'stale Cell content version');}
 if(c.kind==='macro')validateComposition(doc,resolve);
 validateBlockGrid(doc);
 return {wellFormed:true,currentVersion:contentVersion(doc),versionMatches:contentVersion(doc)===c.contentVersion};
}
function transformed(p,t){const a=t.rotation*Math.PI/180,x=p[0]*t.scale[0]*(t.mirrorX?-1:1),y=p[1]*t.scale[1];return [x*Math.cos(a)-y*Math.sin(a)+t.translation[0],x*Math.sin(a)+y*Math.cos(a)+t.translation[1]];}
function validateComposition(doc,resolve){
 const c=doc.generationContract,m=c.composition,components=ids(m.components,'component instances'),links=ids(m.connections,'internal links');need(m.components.length>0,'macro components required');
 for(const part of m.components){need(typeof part.moduleId==='string'&&/^sha256:[a-f0-9]{64}$/.test(part.contentVersion)&&part.transform&&vec(part.transform.translation)&&vec(part.transform.scale)&&finite(part.transform.rotation)&&typeof part.transform.mirrorX==='boolean','versioned component placement');if(resolve){const child=resolve(part.moduleId,part.contentVersion);need(part.moduleId!==doc.id,'self-referencing macro');need(child&&child.id===part.moduleId&&child.generationContract.contentVersion===part.contentVersion&&contentVersion(child)===part.contentVersion,'missing/stale component');validateGenerationContract(child);need(part.transform.scale.every(x=>x===1)&&part.transform.rotation===0&&!part.transform.mirrorX,'Macro geometry transformer currently supports explicit translations only');for(const o of child.objects){const actual=doc.objects.find(x=>x.id===part.id+'/'+o.id);need(actual,'missing actual component geometry '+o.id);const expected=structuredClone(o);expected.x+=part.transform.translation[0];expected.y+=part.transform.translation[1];if(expected.points)expected.points=expected.points.map(p=>({...p,x:p.x+part.transform.translation[0],y:p.y+part.transform.translation[1]}));if(expected.control)expected.control={x:expected.control.x+part.transform.translation[0],y:expected.control.y+part.transform.translation[1]};for(const key of ['trackId','targetId','hostId'])if(expected[key])expected[key]=part.id+'/'+expected[key];const keys=['type','x','y','w','h','rotation','points','control','trackId','targetId','hostId'];need(canonical(Object.fromEntries(keys.map(k=>[k,expected[k]??null])))===canonical(Object.fromEntries(keys.map(k=>[k,actual[k]??null]))),'Macro geometry differs from versioned component '+o.id);}}}
 if(resolve){const owned=new Set(m.cells.flatMap(x=>x.objectIds));for(const part of m.components){const child=resolve(part.moduleId,part.contentVersion);for(const o of child.objects)owned.add(part.id+'/'+o.id);}for(const o of doc.objects)if(!['route','entry','exit','anchor','note'].includes(o.type))need(owned.has(o.id),'Macro physical geometry not owned by versioned component/Cell');}
 const endpoint=e=>{need(components.has(e.instanceId)&&typeof e.portId==='string','internal endpoint');if(resolve){const part=m.components.find(p=>p.id===e.instanceId),d=resolve(part.moduleId,part.contentVersion);need(d.generationContract.ports.some(p=>p.id===e.portId),'fictional internal port');}};
 for(const link of m.connections){endpoint(link.from);endpoint(link.to);need(['connected','disconnected',UNKNOWN].includes(link.status)&&Object.hasOwn(link,'transfer')&&Array.isArray(link.validationIds),'explicit link status/state');}
 const exported=new Set(),sourcePorts=new Set();for(const e of m.exports){need(!exported.has(e.portId)&&c.ports.some(p=>p.id===e.portId),'duplicate/fictional macro export');exported.add(e.portId);const key=e.source.instanceId+'\0'+e.source.portId;need(!sourcePorts.has(key),'multiple aliases cannot invent additional physical ports');sourcePorts.add(key);endpoint(e.source);if(resolve){const part=m.components.find(p=>p.id===e.source.instanceId),child=resolve(part.moduleId,part.contentVersion),p=child.generationContract.ports.find(p=>p.id===e.source.portId),actual=transformed(p.position,part.transform),out=c.ports.find(p=>p.id===e.portId);need(actual.every((x,i)=>Math.abs(x-out.position[i])<1e-5),'macro export not at actual internal port');need(out.objectId===part.id+'/'+p.objectId,'macro export geometry not traceable');}}
 need(exported.size===c.ports.length,'every macro port must map to a real component port');
 for(const r of c.routes){need(Array.isArray(r.steps)&&r.steps.length>0,'macro path needs explicit steps');for(const step of r.steps)if(step.kind==='connection')need(links.has(step.id),'macro path missing internal link');else need(step.kind==='component_route'&&components.has(step.instanceId)&&typeof step.routeId==='string','macro path missing component route');if(resolve){const endpoints=r.steps.map(step=>{if(step.kind==='connection'){const link=m.connections.find(x=>x.id===step.id);return [link.from,link.to];}const part=m.components.find(p=>p.id===step.instanceId),child=resolve(part.moduleId,part.contentVersion),route=child.generationContract.routes.find(x=>x.id===step.routeId);need(route,'fictional component route');return [{instanceId:part.id,portId:route.from},{instanceId:part.id,portId:route.to}];});const first=m.exports.find(x=>x.portId===r.from).source,last=m.exports.find(x=>x.portId===r.to).source;need(canonical(first)===canonical(endpoints[0][0])&&canonical(last)===canonical(endpoints.at(-1)[1]),'Macro route endpoints not traced');for(let i=1;i<endpoints.length;i++)need(canonical(endpoints[i-1][1])===canonical(endpoints[i][0]),'implicit/discontinuous Macro connection');}}
}
function hasUnknown(v){return v===UNKNOWN||v===null||v===undefined||typeof v==='object'&&Object.values(v).some(hasUnknown);}
function stateKnown(s){return !!s&&s.capabilityRequirements.status==='defined'&&!hasUnknown(s);}
function conditionsSatisfied(conditions,state){
 if(!Array.isArray(conditions)||!state)return false;return conditions.every(c=>{if(!c||typeof c.field!=='string')return false;let v=state;for(const k of c.field.split('.'))v=v?.[k];if(v===undefined||v===UNKNOWN)return false;if(c.op==='eq')return canonical(v)===canonical(c.value);if(c.op==='gte')return finite(v)&&finite(c.value)&&v>=c.value;if(c.op==='lte')return finite(v)&&finite(c.value)&&v<=c.value;return false;});
}
function motionAllowed(rule,motion){return !!motion&&vec(motion.direction)&&typeof motion.mode==='string'&&Array.isArray(rule.directions)&&Array.isArray(rule.modes)&&rule.modes.includes(motion.mode)&&rule.directions.some(v=>Math.hypot(v[0]-motion.direction[0],v[1]-motion.direction[1])<1e-5);}
function stateSatisfies(actual,required){
 if(!stateKnown(required)||!stateKnown(actual))return false;
 if(evaluateRequirements(required.capabilityRequirements,actual.capabilityRequirements.allOf).satisfied!==true)return false;
 for(const key of ['remainingJumps','airShots','stamina','health','shotCooldown'])if(actual[key][0]<required[key][0]||actual[key][1]>required[key][1])return false;
 if(actual.grounded!==required.grounded||actual.traversalState!==required.traversalState)return false;
 for(const key of ['x','y'])if(actual.velocity[key][0]<required.velocity[key][0]||actual.velocity[key][1]>required.velocity[key][1])return false;
 for(const key of ['equipment','mechanisms','phase','recoveryConditions'])if(canonical(actual[key])!==canonical(required[key]))return false;return true;
}
// A declaration or embedded 'pass' is not evidence. Consumers must verify artifacts
// in their own trusted evidence store, and explicitly accept the tested coverage.
export function assemblyInterface(doc,{routeId,entryState,transformId='identity',capabilityConfiguration,entryMotion,resolve,verifyEvidence,acceptCoverage}={}){
 const reasons=[];let check;try{check=validateGenerationContract(doc,{resolve});}catch(e){return {eligible:false,reasons:[e.message]};}if(!check.versionMatches)reasons.push('stale_content_version');
 const c=doc.generationContract,r=c.routes.find(x=>x.id===routeId);if(!r)return {eligible:false,reasons:[...reasons,'unknown_route']};
 const rel=c.relations.find(x=>x.from===r.from&&x.to===r.to);if(rel.status!=='path'||!rel.routeIds.includes(r.id))reasons.push('directed_relation_not_available');
 if(!conditionsSatisfied(rel.conditions,entryState)||!conditionsSatisfied(r.availability,entryState))reasons.push('unknown_or_unsatisfied_route_conditions');
 for(const p of c.ports.filter(p=>[r.from,r.to].includes(p.id))){if(p.support===UNKNOWN||p.connection.status!=='verified'||p.connection.region===UNKNOWN||p.seamIds.length===0)reasons.push('unverified_port_'+p.id);const activeMotion=p.id===r.from?p.motion.ingress:p.motion.egress,activeState=p.id===r.from?p.preconditions.ingress:p.preconditions.egress;if(activeMotion.directions===UNKNOWN||activeMotion.modes===UNKNOWN||!activeMotion.modes.length||!activeMotion.directions.length)reasons.push('unknown_port_motion_'+p.id);if(!stateKnown(activeState))reasons.push('unknown_port_preconditions_'+p.id);if(p.id===r.from&&(!entryState||!stateSatisfies(entryState,activeState)))reasons.push('entry_port_state_mismatch');if(p.id===r.to&&(!stateKnown(r.transfer.ensures)||!stateSatisfies(r.transfer.ensures,activeState)))reasons.push('exit_port_state_mismatch');for(const id of p.seamIds)if(c.space.seams.find(x=>x.id===id).status!=='verified')reasons.push('unverified_seam_'+id);}
 if(c.space.occupancy.status!=='verified'||c.space.actionClearance.status!=='verified'||c.space.actionClearance.coverage!=='declared_route_state_envelope')reasons.push('unverified_space_or_action_envelope');if(c.space.dynamicEnvelopes.some(x=>x.region===UNKNOWN||x.status!=='verified'))reasons.push('unverified_dynamic_envelope');
 const fromPort=c.ports.find(p=>p.id===r.from),toPort=c.ports.find(p=>p.id===r.to);if(!motionAllowed(fromPort.motion.ingress,entryMotion))reasons.push('unknown_or_disallowed_entry_motion');
 const t=c.space.transforms.find(x=>x.id===transformId);if(!t||t.status!=='verified')reasons.push('unverified_transform');
 if(r.transfer.status!=='verified'||!stateKnown(r.transfer.requires)||!stateKnown(r.transfer.ensures)||!entryState||!stateSatisfies(entryState,r.transfer.requires))reasons.push('unknown_or_incompatible_state_transfer');
 if(r.return.status==='yes'){const back=c.routes.find(x=>x.id===r.return.routeId),backRel=c.relations.find(x=>x.from===r.to&&x.to===r.from);if(!back||backRel?.status!=='path'||back.transfer.status!=='verified'||!stateSatisfies(r.transfer.ensures,back.transfer.requires)||!conditionsSatisfied(r.return.conditions,r.transfer.ensures))reasons.push('return_not_usable_with_earned_exit_state');}
 if(r.return.status!=='yes'&&(r.onward.status!=='verified'||r.onward.target===UNKNOWN||!stateSatisfies(r.transfer.ensures,r.onward.requiredState)))reasons.push('unknown_onward_or_safe_recovery');
 if(!capabilityConfiguration||evaluateRequirements(r.capabilityRequirements,capabilityConfiguration.available??[]).satisfied!==true||!entryState||evaluateRequirements(entryState.capabilityRequirements,capabilityConfiguration.available??[]).satisfied!==true)reasons.push('unknown_or_missing_required_ability_configuration');
 const evidence=c.validations.filter(v=>r.validationIds.includes(v.id)&&v.kind==='physics'&&v.result==='pass'&&v.from===r.from&&v.to===r.to);
 if(!evidence.some(v=>v.unverified.length===0&&capabilityConfiguration&&canonical(v.capabilityConfiguration.available)===canonical(capabilityConfiguration.available)&&canonical(v.capabilityConfiguration.equipment)===canonical(capabilityConfiguration.equipment)&&stateKnown(v.entryState)&&stateSatisfies(entryState??unknownState(),v.entryState)&&motionAllowed(fromPort.motion.ingress,v.coverage.portMotion?.ingress)&&motionAllowed(toPort.motion.egress,v.coverage.portMotion?.egress)&&canonical(entryMotion)===canonical(v.coverage.portMotion?.ingress)&&typeof verifyEvidence==='function'&&verifyEvidence(v,doc)===true&&typeof acceptCoverage==='function'&&acceptCoverage(v.coverage,doc)===true))reasons.push('no_trusted_physics_for_this_entry_and_coverage');
 if(r.return.status==='yes'){const back=c.routes.find(x=>x.id===r.return.routeId);if(!back||!c.validations.some(v=>back.validationIds.includes(v.id)&&v.kind==='physics'&&v.result==='pass'&&v.from===back.from&&v.to===back.to&&v.unverified.length===0&&stateSatisfies(r.transfer.ensures,v.entryState)&&typeof verifyEvidence==='function'&&verifyEvidence(v,doc)===true&&typeof acceptCoverage==='function'&&acceptCoverage(v.coverage,doc)===true))reasons.push('return_missing_its_own_trusted_physics');}
 if(!t||!t.validationIds.some(id=>evidence.some(v=>v.id===id)))reasons.push('transform_not_bound_to_route_evidence');
 if(c.kind==='macro'&&(!resolve||c.composition.connections.some(x=>x.status!=='connected'||x.transfer===UNKNOWN||x.transfer.status!=='verified')))reasons.push('unverified_macro_connections');
 return {eligible:reasons.length===0,reasons:[...new Set(reasons)],contentVersion:c.contentVersion,routeId,from:r.from,to:r.to,scope:'Interface eligibility only; placement overlap, inter-module joins and whole-map validation remain separate.'};
}
