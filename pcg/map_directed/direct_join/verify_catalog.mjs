import fs from 'node:fs';
import path from 'node:path';
import {validateDocument} from '../../../model.js';
import {validateGenerationContract,contentVersion} from '../../../module-contract.js';
const manifest=process.argv[2],root=path.dirname(manifest);
for(const entry of JSON.parse(fs.readFileSync(manifest)).modules){
 const document=JSON.parse(fs.readFileSync(path.join(root,entry.file)));
 validateDocument(document);validateGenerationContract(document);
 if(contentVersion(document)!==entry.contentVersion)throw Error('Persisted Module content version mismatch');
}
