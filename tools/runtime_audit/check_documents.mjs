import fs from 'node:fs';
import {validateGenerationContract} from '../../module-contract.js';
const paths=JSON.parse(fs.readFileSync(process.argv[2]));
const results=paths.map(job=>{const p=job.file;try{const result=validateGenerationContract(JSON.parse(fs.readFileSync(p)));return {baseline:job.baseline,file:p.split('/modules/')[1],passed:result.versionMatches};}catch(e){return {baseline:job.baseline,file:p.split('/modules/')[1],passed:false,error:String(e)};}});
console.log(JSON.stringify({checked:results.length,passed:results.filter(r=>r.passed).length,results}));
if(results.some(r=>!r.passed))process.exitCode=2;
