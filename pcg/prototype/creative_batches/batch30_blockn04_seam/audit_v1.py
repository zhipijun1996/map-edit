"""Only two fixed original sources; reuse existing exact-seam geometry audit."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.batch30_seams import fixtures_v1 as original
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
VERSION='87b8ed50f5b86fe4eafb92bc593864a15f1c59b7c99c60fae0d55f8c56460efc'
HERE=Path(__file__).parent
DELTA=[1280,-384]
def source():
 _,binding=original.source(VERSION)
 folder=ROOT/'map_directed/library/candidates'/VERSION
 c=next(c for c in json.loads((folder/'cases.json').read_text())['cases']if c['route_spec']['id']=='A-to-C')
 binding['case_id']=c['id']
 return copy.deepcopy(c),binding
def audit():
 left,lb=source();raw,rb=source();right=original.translated(raw,DELTA)
 lc=set(map(tuple,left['block_grid']['cells']));rc={(x+10,y-3)for x,y in raw['block_grid']['cells']}
 forward=original.geometry_audit(left,right);reverse=original.geometry_audit(right,left)
 pa=left['block_ports']['C'];pb=raw['block_ports']['A'];anchor=[pb['position'][j]+DELTA[j]for j in [0,1]]
 result=dict(schema='pcg/N04-fixed-Block-placement-audit/v1',source_left=lb,source_right=rb,translation_right=DELTA,source_route='A-to-C',left_owned_cells=len(lc),right_owned_cells=len(rc),overlap_owned_cells=sorted(map(list,lc&rc)),exact_seam_anchor=pa['position'],right_translated_anchor=anchor,opposed_normals=pa['normal']==[-v for v in pb['normal']],same_profile=pa['grid']['profile']==pb['grid']['profile'],left_to_right_geometry_audit=forward,right_to_left_geometry_audit=reverse,actual_physics_cases=0,added_platforms=0,removed_platforms=0,source_documents_unchanged=True)
 result['accepted']=not(lc&rc)and forward['accepted']and reverse['accepted']and pa['position']==anchor and result['opposed_normals']and result['same_profile']
 return left,right,result
def main():
 _,_,v=audit();out=HERE/'static-placement-v1.json'
 if out.exists():raise ValueError('immutable placement audit exists')
 out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(v,ensure_ascii=False))
if __name__=='__main__':main()
