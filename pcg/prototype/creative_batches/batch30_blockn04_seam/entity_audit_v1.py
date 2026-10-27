"""Independent exact array comparison; no simulation or generated connector."""
import copy,json
from pathlib import Path
from . import fixtures_v2 as fixtures
from . import audit_v1 as audit
from pcg.prototype.factory.core.engine import file_sha
def main():
 c=fixtures.fixture();left,right,placement=audit.audit();checks=[]
 for field in ['platforms','moving_platforms','hazards','enemies','saws','hooks','thorns']:
  expected=left.get(field,[])+right.get(field,[]);actual=c.get(field,[]);checks.append(dict(field=field,equal=actual==expected,expected_count=len(expected),actual_count=len(actual)))
 for field in ['latches','reward_sites']:
  actual=copy.deepcopy(c[field])
  for item in actual:item['id']=item['id'].split('/',1)[1]
  expected=left[field]+right[field];checks.append(dict(field=field,equal=actual==expected,expected_count=len(expected),actual_count=len(actual),permitted_difference='Only deterministic unique left/right ID prefix'))
 expected=set(map(tuple,left['block_grid']['cells']))|{(x+10,y-3)for x,y in left['block_grid']['cells']}
 checks.append(dict(field='owned_cells_exact_disjoint_union',equal=set(map(tuple,c['block_grid']['cells']))==expected,expected_count=160,actual_count=len(c['block_grid']['cells'])))
 reservations=left['block_reservations']+[[x+1280,y-384,w,h]for x,y,w,h in left['block_reservations']]
 checks.append(dict(field='reserved_action_space_exact_union',equal=c['block_reservations']==reservations))
 assert all(r['equal']for r in checks),checks
 out=Path(__file__).with_name('entity-union-audit-v1.json')
 if out.exists():raise ValueError('immutable entity audit exists')
 out.write_text(json.dumps(dict(schema='pcg/N04-exact-entity-union-audit/v1',actual_physics_cases=0,source_version='sha256:'+audit.VERSION,source_binding=placement['source_left'],fixture_version=c['seam_specimen']['fixture_version'],transform=[1280,-384],checks=checks,new_entity_count=0,deleted_entity_count=0,scoped_ids_only=True,audit_source_sha256=file_sha(Path(__file__))),ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(exact_union=True,new_entities=0,deleted_entities=0,checks=len(checks))))
if __name__=='__main__':main()
