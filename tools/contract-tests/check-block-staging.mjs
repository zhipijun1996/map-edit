// Pure contract regressions. No synthetic physical pass or assembly approval.
import assert from 'node:assert/strict';
import {moduleDocument} from '../export-module-contracts.mjs';
import {UNKNOWN,canonical,sha256,contentVersion,validateGenerationContract as validate} from '../../module-contract.js';
import {renderContractSvg} from '../../module-contract-render.js';
const copy=structuredClone;
function fixture(){
 const d=moduleDocument({case:{id:'block-staging-test',factory_id:'block-staging-test',capabilities:['move','jump'],platforms:[[0,96,256,32]],spawn:[24,78],entry_port:[24,78],exit_port:[232,78],goal:[212,74,40,8],control_plan:[],thorns:[],latches:[],saws:[],moving_platforms:[],enemies:[],hooks:[]},result:UNKNOWN,geometryDefinitions:{player:{size:[24,36],source:{path:'TEST ONLY',sha256:'test-only'}},bell:{size:[28,34]}},sourceCases:{path:'TEST ONLY',sha256:'test-only'},sourceRun:UNKNOWN,protocol:UNKNOWN,binding:UNKNOWN},'0'.repeat(40));
 const c=d.generationContract;c.space.bounds={x:0,y:0,w:256,h:128};
 c.space.blockGrid={schema:'map-notes/block-grid/v1',size:128,origin:[0,0],cells:[[0,0],[1,0]],port_bindings:[]};
 for(const [i,p]of c.ports.entries()){
  const cell=[i,0],edge=i?'E':'W',stage=[...p.position];
  p.position=[i?256:0,64];p.grid={cell,edge,profile:'ground64/v1',stagingPosition:stage};
  c.space.blockGrid.port_bindings.push({port_id:p.id,cell,edge,profile:'ground64/v1'});
  const marker=d.objects.find(o=>o.id===p.objectId);marker.x=p.position[0]-marker.w/2;marker.y=p.position[1]-marker.h/2;
 }
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>d.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(d);c.visualization.contentVersion=c.contentVersion;c.staticChecks.contentVersion=c.contentVersion;
 return d;
}
const d=fixture();assert(validate(d).versionMatches);assert.notDeepEqual(d.generationContract.ports[0].position,d.generationContract.ports[0].grid.stagingPosition);
let x=copy(d);delete x.generationContract.ports[0].grid.stagingPosition;assert.throws(()=>validate(x),/standing player geometry/);
x=copy(d);x.generationContract.ports[0].grid.stagingPosition[1]-=14;assert.throws(()=>validate(x),/standing player geometry/);
x=copy(d);delete x.generationContract.space.blockGrid;assert.throws(()=>validate(x),/grid staging/);
x=copy(d);x.generationContract.space.blockGrid.cells.pop();assert.throws(()=>validate(x),/owned|boundary|unreserved/);
const svg=renderContractSvg(d);assert(svg.includes('data-block-cell="0,0"'));assert(svg.includes('data-staging-port="entry"'));
assert.equal(d.generationContract.validations.length,0);
console.log(JSON.stringify({block_staging_checks:7,passed:true,physics:false}));
