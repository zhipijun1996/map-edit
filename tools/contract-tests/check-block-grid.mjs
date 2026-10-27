import assert from 'node:assert/strict';
import {validateBlockGrid} from '../../module-block-grid.js';
const doc=()=>({objects:[{id:'rock',type:'terrain',x:0,y:96,w:128,h:32}],generationContract:{ports:[{id:'east',position:[128,64],normal:[1,0],grid:{cell:[0,0],edge:'E',profile:'ground64/v1'}}],space:{blockGrid:{schema:'map-notes/block-grid/v1',size:128,origin:[0,0],cells:[[0,0]],port_bindings:[{port_id:'east',cell:[0,0],edge:'E',profile:'ground64/v1'}]},actionClearance:{regions:[]},dynamicEnvelopes:[]}}});
validateBlockGrid(doc());
let x=doc();x.generationContract.ports[0].position[1]=65;assert.throws(()=>validateBlockGrid(x),/boundary center/);
x=doc();x.generationContract.space.blockGrid.cells.push([1,0]);assert.throws(()=>validateBlockGrid(x),/actual shape boundary/);
x=doc();x.generationContract.space.blockGrid.cells.push([0,2]);assert.throws(()=>validateBlockGrid(x),/disconnected/);
x=doc();x.generationContract.space.actionClearance.regions.push({x:100,y:30,w:60,h:36});assert.throws(()=>validateBlockGrid(x),/unreserved/);
x=doc();x.generationContract.space.blockGrid.cells.push([0,0]);assert.throws(()=>validateBlockGrid(x),/duplicate/);
x=doc();x.generationContract.space.blockGrid.size=127;assert.throws(()=>validateBlockGrid(x),/Block size/);
console.log(JSON.stringify({block_contract_checks:7,passed:true,physics:false}));

