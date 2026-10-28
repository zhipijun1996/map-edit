import fs from 'node:fs';
import {contentVersion,validateGenerationContract,canonical,sha256} from '../../module-contract.js';
import {renderContractSvg} from '../../module-contract-render.js';
const [file,flag]=process.argv.slice(2),doc=JSON.parse(fs.readFileSync(file));
if(flag==='--refresh'){
 const c=doc.generationContract;
 const objects=new Map(doc.objects.map(o=>[o.id,o]));
 for(const cell of c.composition?.cells??[]){const os=cell.objectIds.map(id=>objects.get(id));if(os.some(o=>!o))throw Error('Missing Cell geometry');cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(doc);
 for(const v of c.validations)v.contentVersion=c.contentVersion;
 if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;
 c.visualization={contentVersion:c.contentVersion,path:'thumbnail.svg'};
 fs.writeFileSync(file,JSON.stringify(doc,null,2)+'\n');
 fs.writeFileSync(new URL('./thumbnail.svg','file://'+file),renderContractSvg(doc));
}
const components=new Map();
if(doc.generationContract.kind==='macro'){
 for(const part of doc.generationContract.composition.components){
  const child=new URL('./components/'+part.id+'/module.mapnote.json','file://'+file);
  if(fs.existsSync(child))components.set(part.moduleId,JSON.parse(fs.readFileSync(child)));
 }
}
console.log(JSON.stringify(validateGenerationContract(doc,components.size?{resolve:(id,version)=>{const child=components.get(id);return child?.generationContract.contentVersion===version?child:null;}}:{})));

