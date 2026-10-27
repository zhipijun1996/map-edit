"""Explicit current-adapter refusal; no replacement geometry or new physics."""
import argparse,hashlib,json,math
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04r2 import api_v1 as source
from pcg.map_directed.block_grid.contracts import anchor,raster
HERE=Path(__file__).parent;REPO=HERE.parents[3]

def binding(p):return dict(path=str(p.relative_to(REPO)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def response():
 manifest=REPO/'generation/workshop/plains30-v1/manifest-progress-8-v2.json'
 delivery=json.loads(manifest.read_text());held=json.loads((REPO/'pcg/creative-production/batch30/design-holds-v1.json').read_text())
 actual=[m for m in delivery['modules']if m['family']=='park-for-return-repaired']
 assert len(actual)==2 and not set(m['contentVersion']for m in actual)&set(held['contentVersions'])
 interfaces=[]
 for i in [0,1]:
  cs=source.layouts(source.RECIPES[0],i);c=cs[0];b=next(p for p in c['ports']if p['id']=='B');face=math.ceil((b['position'][0]+24)/128)*128
  # The natural common y-phase fits A/B within-22 and C within+22. It
  # demonstrates an actual occupancy collision, not impossibility of all
  # redesigned geometries or all future controllers.
  cell=[int(face/128)-1,2];point=anchor(cell,'E');external=[cell[0]+1,cell[1]];pillar=c['platforms'][2];translated=[pillar[0],pillar[1]-64,*pillar[2:]]
  interfaces.append(dict(interface=i,source_case_ids=[v['id']for v in cs],ports=c['ports'],registered_forward_pairs=[['A','B'],['A','C']],local_route_ids=[v['route_spec']['id']for v in cs],same_world_returns=[v['route_spec']for v in source.fixtures(i)],natural_grid_proposal=dict(translation=[0,-64],A_B_top_delta=-22,C_top_delta=22,B_anchor=point,B_staging=[face-24,334],B_grid_cell=cell,forbidden_outward_cell=external,pillar_actual_rect=translated,pillar_occupies_forbidden_cell=tuple(external)in raster(translated)),control_conflict='A->C departs internal B rightlip; original middle return departs leftlip. Moving a face marker onto either used lip needs new internal direction/control and full-body ownership evidence, not inherited source success.'))
 return dict(schema='pcg/blockD04-constraint-gap/v1',status='needs_design',request_origin='TaskA latestMap-contract adaptation audit; no actualBgraph request claimed',upstream_Map='a685faebdb7596b0808538ab9ef299d6455d2320',source_family=source.RECIPES[0],source_api=binding(Path(source.__file__)),source_manifest=binding(manifest),source_versions=[m['contentVersion']for m in actual],design_held_older_versions_explicitly_excluded=held['contentVersions'],interfaces=interfaces,conflicts=[dict(field='ports.B.grid',reason='natural E midpoint outwardcell contains real fullheight spine; cannot reserve it and call face exterior'),dict(field='space.actionClearance',reason='B is reused as an internal shore, and C continuation/middle return leave opposite lips; no currently verified strategy remains wholly inside an ownership mask with either used side excluded'),dict(field='return_conditions',reason='source same-world A-return programmes have not been adapted; keeping terrain alone cannot transfer evidence')],searched=dict(interfaces=[0,1],family='repaired_D04r2_only',natural_y_phase=-64,port_profiles=['ground64/v1'],scope='Source geometry, actual direction policies and natural shore adaptation; NOT exhaustive search of all new geometries or controllers'),negotiable=['new independently situated B outlet without deleting required recovery','new internal underpass or departure controls that stay out of exterior portcells','explicit direction/profile redesign with fresh regular and independentheld','B accepts current local-only version without claimingBlock compatibility'],may_delete_required_routes=False,may_add_Map_terrain=False,may_reset_resources=False,new_physics_cases=0,new_candidates=0,reverse='UNKNOWN',boundary_crossing='UNKNOWN',human_fun='UNKNOWN',production_admitted=False)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise ValueError('immutable response exists')
 a.out.parent.mkdir(parents=True,exist_ok=True);v=response();a.out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(status=v['status'],new_physics_cases=0,new_candidates=0,conflicts=v['conflicts']),ensure_ascii=False))

if __name__=='__main__':main()
