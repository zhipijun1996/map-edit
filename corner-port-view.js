// Read-only presentation of offline corner-Port options. Never changes geometry.
import {validateGenerationContract} from './module-contract.js';

export const CORNER_NAMES={TOP_LEFT:'左上',TOP_RIGHT:'右上',BOTTOM_LEFT:'左下',BOTTOM_RIGHT:'右下'};
export const FACE_NAMES={LEFT:'左',RIGHT:'右',TOP:'上',BOTTOM:'下'};

export function cornerRelocationRows(doc,assessment=null,verifiedConfigurations=[]){
  const c=doc.generationContract;if(c?.version!==2)return [];
  let current=false;try{current=validateGenerationContract(doc).versionMatches;}catch{}
  const bound=assessment?.contentVersion===c.contentVersion&&assessment?.moduleDocumentId===doc.id;
  return c.ports.flatMap(port=>{
    const external=bound?assessment.ports?.find(p=>p.portId===port.id)?.cornerRelocations:null;
    const options=port.cornerRelocations??external??{};
    return Object.entries(CORNER_NAMES).flatMap(([corner,cornerName])=>{
      const option=options[corner];if(!option?.applicable)return [];
      // An assessment is a discovery receipt, never a physics certificate.
      const profile=c.portConfigurations?.find(p=>p.id===option.profileId);
      const receipt=verifiedConfigurations.find(r=>r.baseContentVersion===c.contentVersion&&r.allowed===true&&r.technicalStatus==='verified'&&r.relocations?.some(x=>x.portId===port.id&&x.corner===corner&&x.targetFace===option.targetFace&&JSON.stringify(x.targetPosition)===JSON.stringify(option.targetPosition)));
      const certified=current&&(!!port.cornerRelocations&&option.allowed===true&&profile?.status==='verified'||!!receipt);
      const allowed=certified?true:option.allowed===false?false:'UNKNOWN';
      return [{portId:port.id,corner,cornerName,sourceFace:port.face,targetFace:option.targetFace,
        targetPosition:option.targetPosition,proposedSurface:option.proposedSurface,allowed,
        statusLabel:allowed===true?'已认证可换边':allowed===false?'不可用':'未验证',
        profileId:certified?(receipt?.configurationId??option.profileId):null,reason:option.reason??'',current,
        assessmentOnly:!port.cornerRelocations}];
    });
  });
}
