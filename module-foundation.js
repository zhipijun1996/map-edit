// Foundation v1.0 semantics for generationContract.version=2.
// Helpers are injected by module-contract.js; no circular import or second geometry.
export function validateFoundation(doc,{need,finite,vec,rect,ids,UNKNOWN}){
 const c=doc.generationContract,f=c.foundation,s=c.space,b=s.bounds;
 need(f&&f.version==='1.0','foundation version');
 need(f.blockSize===128,'foundation Block size must be 128');
 need(Number.isSafeInteger(f.widthBlocks)&&f.widthBlocks>0&&Number.isSafeInteger(f.heightBlocks)&&f.heightBlocks>0,'foundation positive integer rectangle dimensions');
 need(rect(b)&&b.w===f.widthBlocks*f.blockSize&&b.h===f.heightBlocks*f.blockSize,'foundation bounds must equal the full Block rectangle');
 const near=(a,z)=>Math.abs(a-z)<1e-5;
 const centers=(value,origin,count)=>{const n=Math.round((value-origin)/f.blockSize-.5);return near(value,origin+(n+.5)*f.blockSize)&&n>=0&&n<count;};
 const normals={LEFT:[-1,0],RIGHT:[1,0],TOP:[0,-1],BOTTOM:[0,1]};
 const ports=new Map(c.ports.map(p=>[p.id,p])),routes=new Map(c.routes.map(r=>[r.id,r])),objects=new Map(doc.objects.map(o=>[o.id,o]));
 const stringList=(xs,label,allowed)=>{need(Array.isArray(xs)&&xs.every(x=>typeof x==='string'&&x.length>0&&x.trim()===x)&&new Set(xs).size===xs.length,label+' must be unique strings');if(allowed)need(xs.every(x=>allowed.has(x)),label+' unknown reference');};
 for(const p of c.ports){
  need(Object.hasOwn(normals,p.face),'foundation Port face');
  need(['AIR','ROCK','ONE_WAY_PLATFORM'].includes(p.surface),'foundation Port surface');
  need(['INPUT','OUTPUT','INOUT'].includes(p.permission),'foundation initial Port permission');
  need(vec(p.normal)&&p.normal.every((v,i)=>near(v,normals[p.face][i])),'foundation Port normal must match face');
  const [x,y]=p.position;
  const onFace=p.face==='LEFT'?near(x,b.x)&&centers(y,b.y,f.heightBlocks):p.face==='RIGHT'?near(x,b.x+b.w)&&centers(y,b.y,f.heightBlocks):p.face==='TOP'?near(y,b.y)&&centers(x,b.x,f.widthBlocks):near(y,b.y+b.h)&&centers(x,b.x,f.widthBlocks);
  need(onFace,'foundation Port must be an outer boundary Block face center');
  need(!(p.surface==='AIR'&&p.face==='BOTTOM'&&p.permission!=='OUTPUT'),'foundation bottom AIR cannot have INPUT permission');
  need(p.surface!=='ROCK'||['LEFT','RIGHT'].includes(p.face),'foundation ROCK Port only LEFT/RIGHT');
  if(p.permission!=='INOUT')need(p.initialPermissionConditions!==undefined,'foundation one-way Port requires initialPermissionConditions');
  if(p.initialPermissionConditions!==undefined){
   const conditions=p.initialPermissionConditions;
   need(conditions&&typeof conditions==='object'&&!Array.isArray(conditions),'foundation initialPermissionConditions must be an object');
   stringList(conditions.availableAbilitiesExact,'foundation initialPermissionConditions.availableAbilitiesExact');
   need(conditions.availableAbilitiesExact.length>0&&!conditions.availableAbilitiesExact.includes(UNKNOWN),'foundation initialPermissionConditions.availableAbilitiesExact must be nonempty known abilities');
   if(Object.hasOwn(conditions,'requiresRevalidationWithAdditionalUpwardAbilities'))need(conditions.requiresRevalidationWithAdditionalUpwardAbilities===true,'foundation initialPermissionConditions requiresRevalidationWithAdditionalUpwardAbilities must be true');
  }
  if(p.stagingPosition!==undefined)need(vec(p.stagingPosition),'foundation stagingPosition');
  // Support geometry is still the existing referenced object, never a second copy.
  if(p.support!==UNKNOWN&&p.surface!=='AIR')need(objects.get(p.support.objectId)?.type===(p.surface==='ROCK'?'terrain':'platform'),'foundation Port support surface mismatch');
 }
 for(const r of c.routes){
  stringList(r.requiredAbilities,'foundation route requiredAbilities');
  stringList(r.actionTags,'foundation route actionTags');
  need(r.durationSeconds===UNKNOWN||finite(r.durationSeconds)&&r.durationSeconds>=0,'foundation route durationSeconds');
  for(const key of ['resourceProfile','initialConditions'])need(r[key]===UNKNOWN||r[key]!==null&&typeof r[key]==='object'&&!Array.isArray(r[key]),'foundation route '+key);
  const from=ports.get(r.from),to=ports.get(r.to);
  need(vec(r.localDisplacementBlocks)&&r.localDisplacementBlocks.every((v,i)=>near(v,(to.position[i]-from.position[i])/f.blockSize)),'foundation route localDisplacementBlocks must match Port displacement');
  const rel=c.relations.find(x=>x.from===r.from&&x.to===r.to);
  need(rel?.routeIds.includes(r.id),'foundation route missing from actual directed relation');
  if(rel.status==='path')need(from.permission!=='OUTPUT'&&to.permission!=='INPUT','foundation path violates initial Port permissions');
 }
 const validationMap=new Map(c.validations.map(v=>[v.id,v]));
 const statusValues=['declared','verified','failed',UNKNOWN];
 function evidence(profile,label){
  stringList(profile.validationIds,label+' validationIds',new Set(validationMap.keys()));
  if(profile.status==='verified')need(profile.validationIds.length>0&&profile.validationIds.every(id=>{const v=validationMap.get(id);return v.contentVersion===c.contentVersion&&v.result==='pass'&&v.artifacts.length>0;}),label+' verified requires current passing artifact references');
 }
 ids(c.closures,'foundation closures');
 for(const closure of c.closures){
  need(statusValues.includes(closure.status),'foundation closure status');
  stringList(closure.closedPorts,'foundation closure closedPorts',new Set(ports.keys()));
  stringList(closure.objectIds,'foundation closure objectIds',new Set(objects.keys()));
  stringList(closure.routeIds,'foundation closure routeIds',new Set(routes.keys()));
  for(const id of closure.objectIds)need(!['entry','exit','anchor','note','route','trackLine','trackArc'].includes(objects.get(id).type),'foundation closure must reference actual Cell geometry');
  for(const id of closure.routeIds){const r=routes.get(id);need(!closure.closedPorts.includes(r.from)&&!closure.closedPorts.includes(r.to),'foundation closure cannot retain a Route through a closed Port');}
  evidence(closure,'foundation closure');
  if(closure.status==='verified'&&closure.closedPorts.length)need(closure.objectIds.length>0,'foundation verified closure needs actual Cell references');
 }
 need(c.mirror&&[...statusValues,'unsupported'].includes(c.mirror.status),'foundation mirror status');
 evidence(c.mirror,'foundation mirror');
 // Optional extension: existing frozen v2 documents without this field remain
 // UNKNOWN. A corner alternative is a whole offline-certified configuration,
 // never another simultaneously open Port or an online geometry instruction.
 const corners=['TOP_LEFT','TOP_RIGHT','BOTTOM_LEFT','BOTTOM_RIGHT'];
 const configurations=c.portConfigurations??[];
 ids(configurations,'foundation port configurations');
 const configurationMap=new Map(configurations.map(p=>[p.id,p]));
 for(const p of c.ports){
  if(p.cornerRelocations===undefined)continue;
  const options=p.cornerRelocations;
  need(options&&typeof options==='object'&&!Array.isArray(options)&&Object.keys(options).length===4&&corners.every(k=>Object.hasOwn(options,k)),'foundation cornerRelocations requires all four corners');
  for(const corner of corners){
   const o=options[corner],left=corner.endsWith('LEFT'),top=corner.startsWith('TOP');
   const faces=[left?'LEFT':'RIGHT',top?'TOP':'BOTTOM'];
   const bx=left?0:f.widthBlocks-1,by=top?0:f.heightBlocks-1;
   const positions={LEFT:[b.x,b.y+(by+.5)*f.blockSize],RIGHT:[b.x+b.w,b.y+(by+.5)*f.blockSize],TOP:[b.x+(bx+.5)*f.blockSize,b.y],BOTTOM:[b.x+(bx+.5)*f.blockSize,b.y+b.h]};
   const applicable=faces.includes(p.face)&&p.position.every((v,i)=>near(v,positions[p.face][i]));
   need(o&&o.applicable===applicable,'foundation corner relocation applicability');
   need([true,false,UNKNOWN].includes(o.allowed),'foundation corner relocation allowed must be true false UNKNOWN');
   need(typeof o.reason==='string'&&o.reason.length>0,'foundation corner relocation needs reason');
   if(!applicable){need(o.allowed===false&&o.profileId===null,'foundation non-corner relocation cannot be allowed');continue;}
   const target=faces.find(face=>face!==p.face);
   need(o.targetFace===target&&vec(o.targetPosition)&&o.targetPosition.every((v,i)=>near(v,positions[target][i])),'foundation corner relocation must target adjacent face of the same corner Block');
   need(['AIR','ROCK','ONE_WAY_PLATFORM',UNKNOWN].includes(o.proposedSurface),'foundation corner relocation proposedSurface');
   need(o.permission===p.permission,'foundation corner relocation preserves initial permissions');
   if(o.allowed===true){
    need(!(o.proposedSurface==='ROCK'&&['TOP','BOTTOM'].includes(target)),'foundation relocated ROCK only LEFT/RIGHT');
    need(!(o.proposedSurface==='AIR'&&target==='BOTTOM'&&o.permission!=='OUTPUT'),'foundation relocated bottom AIR cannot have INPUT');
    need(o.proposedSurface!==UNKNOWN,'foundation allowed corner relocation requires actual surface');
    const profile=configurationMap.get(o.profileId);
    need(profile?.status==='verified'&&Array.isArray(profile.relocations)&&profile.relocations.some(r=>r.portId===p.id&&r.corner===corner),'foundation allowed corner relocation needs verified whole configuration');
   }else need(o.profileId===null||configurationMap.has(o.profileId),'foundation corner relocation unknown configuration');
  }
 }
 for(const profile of configurations){
  need(statusValues.includes(profile.status),'foundation port configuration status');
  evidence(profile,'foundation port configuration');
  stringList(profile.routeIds,'foundation port configuration routeIds',new Set(routes.keys()));
  need(Array.isArray(profile.relocations)&&profile.relocations.length>0,'foundation port configuration relocations');
  const selected=new Set();
  for(const r of profile.relocations){
   need(ports.has(r.portId)&&corners.includes(r.corner)&&!selected.has(r.portId),'foundation port configuration unique logical Ports');selected.add(r.portId);
   const option=ports.get(r.portId).cornerRelocations?.[r.corner];
   need(option?.applicable,'foundation port configuration references applicable corner');
  }
  if(profile.status==='verified'){
   need(profile.routeIds.length===routes.size,'foundation port configuration must preserve all declared routes');
   need(profile.configuration&&typeof profile.configuration.path==='string'&&profile.configuration.path.length>0&&/^[a-f0-9]{64}$/.test(profile.configuration.sha256),'foundation verified port configuration needs actual configuration artifact');
   need(profile.validationIds.every(id=>{const v=validationMap.get(id);return v.coverage?.portConfigurationId===profile.id&&v.coverage?.configurationSha256===profile.configuration.sha256&&v.artifacts.some(a=>a.path===profile.configuration.path&&a.sha256===profile.configuration.sha256);}),'foundation port configuration evidence must bind exact selected configuration');
  }
 }
 return {foundationVersion:f.version,rectangle:{...b},routeMatrixSize:c.ports.length*c.ports.length};
}
