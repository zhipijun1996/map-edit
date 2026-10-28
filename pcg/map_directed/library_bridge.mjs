/* Canonical Module documents stay authoritative; this is a demand query only. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateGenerationContract,assemblyInterface} from '../../module-contract.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(process.argv[2]==='--validate'){
 const doc=JSON.parse(fs.readFileSync(process.argv[3]));
 console.log(JSON.stringify(validateGenerationContract(doc)));process.exit(0);
}
const spec=JSON.parse(fs.readFileSync(0,'utf8')),rows=[];
for(const group of ['plains-v1','plains-round2','plains-three-port-v1']){
 const dir=path.join(root,'generation/contracts',group);
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json')));
 for(const item of manifest.modules){
  if(item.kind!=='module')continue;
  const file=path.join(dir,item.file),doc=JSON.parse(fs.readFileSync(file));
  const validation=validateGenerationContract(doc),c=doc.generationContract,reasons=[];
  if(!validation.versionMatches)reasons.push('stale_content_version');
  if(c.ports.length!==spec.ports.count)reasons.push('port_count');
  const parameters=c.generation.parameters;
  if(parameters.family!==spec.required_family)reasons.push('challenge_family');
  if(spec.rise!=null&&c.ports.length===2){const [a,b]=c.ports;if(Math.abs(a.position[1]-b.position[1]-spec.rise)>1e-5)reasons.push('required_vertical_rise');}
  const evidence=c.validations.filter(v=>v.kind==='physics'&&v.result==='pass');
  if(!evidence.length)reasons.push('no_scoped_physics_witness');
  const interfaces=c.routes.map(r=>assemblyInterface(doc,{routeId:r.id}));
  rows.push({id:doc.id,contentVersion:c.contentVersion,file:path.relative(root,file),title:doc.title,
   sourceCase:c.generation.source,scopedPhysicsWitnesses:evidence.length,match:!reasons.length,reasons,
   productionInterfaceEligible:interfaces.some(x=>x.eligible),interfaceRejections:interfaces,
   disposition:reasons.length?'rejected':'experimental_instance_validation_required'});
 }
}
console.log(JSON.stringify({specId:spec.id,rows,matches:rows.filter(x=>x.match),
 scope:'Existing verified route witnesses only; UNKNOWN general assembly contracts remain blocked.'}));
