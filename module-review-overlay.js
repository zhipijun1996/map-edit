// Consumer-only geometry views. Never edits a Module, Route or permission.
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const NORMALS={LEFT:[-1,0],RIGHT:[1,0],TOP:[0,-1],BOTTOM:[0,1]};
const FACE_NAMES={LEFT:'左',RIGHT:'右',TOP:'上',BOTTOM:'下'};

export function physicalPortGroups(ports=[]){
  const groups=new Map();
  for(const port of ports){
    const face=port.face??Object.keys(NORMALS).find(k=>NORMALS[k].every((v,i)=>v===port.normal?.[i]));
    if(!face||!Array.isArray(port.position)||port.position.length!==2||!port.position.every(Number.isFinite))continue;
    // Exact physical coincidence only; this is not a contract normalization.
    const key=JSON.stringify([port.position,face]);
    if(!groups.has(key))groups.set(key,{key,position:[...port.position],face,normal:[...NORMALS[face]],members:[]});
    groups.get(key).members.push(port);
  }
  return [...groups.values()].map(group=>({...group,ids:group.members.map(p=>p.id),
    surfaces:[...new Set(group.members.map(p=>p.surface??'UNKNOWN'))],
    permissions:[...new Set(group.members.map(p=>p.permission??'UNKNOWN'))]}));
}

export function portCounts(ports=[]){
  return {physical:physicalPortGroups(ports).length,logical:ports.length};
}

export function foundationReview(document){
  const c=document?.generationContract,b=c?.space?.bounds,f=c?.foundation;
  return c?.version===2&&f?.blockSize===128&&b&&[b.x,b.y,b.w,b.h].every(Number.isFinite)
    ?{bounds:b,blockSize:f.blockSize,widthBlocks:f.widthBlocks,heightBlocks:f.heightBlocks,ports:c.ports}:null;
}

export function renderPortReview(document,{unitsPerPixel=1,interactive=false}={}){
  const review=foundationReview(document);if(!review)return '';
  const u=Number.isFinite(unitsPerPixel)&&unitsPerPixel>0?unitsPerPixel:1;
  const objects=new Map(document.objects.map(o=>[o.id,o]));
  return physicalPortGroups(review.ports).map(group=>{
    const [x,y]=group.position,[nx,ny]=group.normal,ids=group.ids.join(' / ');
    const surface=group.surfaces.join(' / '),permission=group.permissions.length===1?group.permissions[0]:group.members.map(p=>`${p.id}:${p.permission}`).join(' / ');
    const mismatch=group.members.some(p=>{const o=objects.get(p.objectId);return o&&(Math.abs(o.x+o.w/2-x)>1e-5||Math.abs(o.y+o.h/2-y)>1e-5);});
    const towardLeft=nx>0||(nx===0&&x>=review.bounds.x+review.bounds.w/2);
    const color=mismatch?'#b94743':'#195f6b',anchor=towardLeft?'end':'start',tx=towardLeft?-14:14;
    const ty=ny>0?-39:ny<0?21:-18;
    const alias=group.ids.length>1?`${group.ids.length} 个逻辑名 · 同一物理口`:'';
    const lines=[ids,`${FACE_NAMES[group.face]} ${group.face} · ${surface} · ${permission}`,...(alias?[alias]:[]),...(mismatch?['草稿标记偏离合同位置，需重新对齐']:[])];
    const width=Math.max(...lines.map(line=>[...line].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?11:6.3),0)))+12;
    const left=anchor==='end'?tx-width+6:tx-6;
    const meta=interactive?`data-id="${esc(group.members[0].objectId)}"`:'';
    return `<g data-physical-port="${esc(group.ids[0])}" data-port-aliases="${esc(JSON.stringify(group.ids))}" data-port-position="${x},${y}" data-port-face="${group.face}" data-logical-port-count="${group.ids.length}" transform="translate(${x} ${y}) scale(${u})" ${meta}><title>${esc(`${ids}：${group.face} · ${surface} · ${permission}${alias?'；'+alias:''}；逻辑路线仍分别保留`)}</title><circle r="6" fill="#fffdf7" stroke="${color}" stroke-width="2"/><line x1="${nx*8}" y1="${ny*8}" x2="${nx*30}" y2="${ny*30}" stroke="${color}" stroke-width="2"/><path d="M${nx*31} ${ny*31}L${nx*23-ny*4} ${ny*23+nx*4}L${nx*23+ny*4} ${ny*23-nx*4}Z" fill="${color}"/><rect x="${left}" y="${ty-12}" width="${width}" height="${lines.length*15+4}" rx="3" fill="#fffdf5" fill-opacity=".94" stroke="${color}" stroke-opacity=".25"/>${lines.map((line,i)=>`<text x="${tx}" y="${ty+i*15}" text-anchor="${anchor}" font-size="${i?10.5:11.5}" font-weight="${i?400:650}" font-family="system-ui,sans-serif" fill="${color}">${esc(line)}</text>`).join('')}</g>`;
  }).join('');
}

export function renderFoundationReview(document,{unitsPerPixel=1,grid=true,ports=true,interactive=false}={}){
  const review=foundationReview(document);if(!review)return '';
  const b=review.bounds,u=unitsPerPixel>0?unitsPerPixel:1;
  const counts=portCounts(review.ports),id='module-review-grid';
  const lattice=grid?`<defs><pattern id="${id}" x="${b.x}" y="${b.y}" width="128" height="128" patternUnits="userSpaceOnUse"><path d="M128 0H0V128" fill="none" stroke="#6c9695" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".65"/></pattern></defs><rect data-block-grid="128" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="url(#${id})" pointer-events="none"/>`:'';
  const caption=`${review.widthBlocks}×${review.heightBlocks} Block · 128 px · ${counts.physical} 物理 Port${counts.logical!==counts.physical?' / '+counts.logical+' 逻辑名':''}`;
  return `<g data-module-review="true">${lattice}<rect data-module-footprint="true" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="none" stroke="#37788c" stroke-width="2" stroke-dasharray="9 5" vector-effect="non-scaling-stroke" pointer-events="none"/><g transform="translate(${b.x} ${b.y-10*u}) scale(${u})" pointer-events="none"><text data-module-review-caption="true" x="0" y="0" font-size="12" font-family="system-ui,sans-serif" fill="#245c6a" paint-order="stroke" stroke="#fffdf5" stroke-width="4" stroke-linejoin="round">${esc(caption)}</text></g>${ports?renderPortReview(document,{unitsPerPixel:u,interactive}):''}</g>`;
}
