// Validate shipped contract documents, diagrams and fail-closed assembly status.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {validateDocument} from '../model.js';
import {validateGenerationContract,contentVersion,assemblyInterface} from '../module-contract.js';
import {renderContractSvg} from '../module-contract-render.js';
const root='generation/contracts';let documents=0;
if(fs.existsSync(root))for(const folder of fs.readdirSync(root)){
 const dir=path.join(root,folder);if(!fs.statSync(dir).isDirectory())continue;
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'))),sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 const files=fs.readdirSync(dir).filter(f=>f.endsWith('.mapnote.json')),docs=files.map(f=>JSON.parse(fs.readFileSync(path.join(dir,f)))),resolve=(id,version)=>docs.find(d=>d.id===id&&d.generationContract.contentVersion===version);
 if(manifest.modules.length!==docs.length)throw Error('Manifest/document count mismatch');
 for(const doc of docs){const index=manifest.modules.find(m=>m.id===doc.id);if(!index||index.contentVersion!==doc.generationContract.contentVersion||sha(path.join(dir,index.file))!==index.contentSha256||sha(path.join(dir,index.diagram))!==index.diagramSha256)throw Error('Manifest version or bytes changed');validateDocument(doc);const v=validateGenerationContract(doc,{resolve});if(!v.versionMatches)throw Error('Stale document '+doc.id);const svg=fs.readFileSync(path.join(dir,doc.generationContract.visualization.path),'utf8');if(svg!==renderContractSvg(doc))throw Error('SVG not regenerated from exact document '+doc.id);for(const route of doc.generationContract.routes){const decision=assemblyInterface(doc,{routeId:route.id,resolve});if(decision.eligible)throw Error('Candidate unexpectedly eligible without entry state/trusted evidence');}documents++;}
 if(!docs.length)throw Error('Empty contract delivery');
}
console.log(JSON.stringify({contract_documents:documents,scope:'Existing document schema + bound SVG + explicit directed graph. Embedded evidence alone never admits a map interface.'}));
