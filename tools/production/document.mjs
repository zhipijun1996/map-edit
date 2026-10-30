import fs from 'node:fs';
import {contentVersion,validateGenerationContract,canonical,sha256} from '../../module-contract.js';
import {renderContractSvg} from '../../module-contract-render.js';
const [action,file,target]=process.argv.slice(2),doc=JSON.parse(fs.readFileSync(file));
if(action==='refresh'){
 const c=doc.generationContract,objects=new Map(doc.objects.map(o=>[o.id,o]));
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>objects.get(id));if(os.some(o=>!o))throw Error('missing Cell');cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(doc);if(c.staticChecks)c.staticChecks.contentVersion=c.contentVersion;
 c.visualization={contentVersion:c.contentVersion,path:'thumbnail.svg'};validateGenerationContract(doc);
 fs.writeFileSync(file,JSON.stringify(doc,null,2)+'\n');
}else if(action==='check'){
 if(!validateGenerationContract(doc).versionMatches)throw Error('stale module content version');
}else if(action==='thumbnail')fs.writeFileSync(target,renderContractSvg(doc));
else throw Error('unknown document operation');
