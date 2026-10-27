// Batched invocation of the existing authoritative validator, not a new schema.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {validateGenerationContract} from '../../module-contract.js';
let raw='';for await(const chunk of process.stdin)raw+=chunk;
const files=JSON.parse(raw),rows=[];
for(const file of files){
 try{
  const bytes=fs.readFileSync(file),doc=JSON.parse(bytes),folder=path.dirname(file),components=new Map();
  for(const part of doc.generationContract?.composition?.components??[]){
   const child=path.resolve(folder,'components',part.id,'module.mapnote.json');
   if(!child.startsWith(folder+path.sep))throw Error('Component path outside prepared package');
   if(fs.existsSync(child))components.set(part.moduleId,JSON.parse(fs.readFileSync(child)));
  }
  const checked=validateGenerationContract(doc,components.size?{resolve:(id,version)=>{const child=components.get(id);return child?.generationContract.contentVersion===version?child:null;}}:{});
  rows.push({path:file,documentSha256:crypto.createHash('sha256').update(bytes).digest('hex'),valid:checked.versionMatches===true,result:checked});
 }catch(error){rows.push({path:file,valid:false,error:String(error)});}
}
process.stdout.write(JSON.stringify(rows));
