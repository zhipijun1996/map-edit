import fs from 'node:fs';
import {validateGenerationContract} from '../../module-contract.js';
if(process.argv[2]!=='--validate'||process.argv.length!==4)throw Error('Usage: validate_document.mjs --validate document');
console.log(JSON.stringify(validateGenerationContract(JSON.parse(fs.readFileSync(process.argv[3])))));
