"""Fresh-process exact retrieval only; no generator or Godot call."""
import argparse,json,copy
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();manifest=REPO/'generation/workshop/plains50-new-relations/manifest.json';m=json.loads(manifest.read_text());rows=[]
 for item in m['items']:
  s=item['specification'];hits=WorkshopLibrary(ROOT/'map_directed/library').find_single_exact(s);versions=[x['record']['contentVersion']for x in hits];assert item['contentVersion']in versions
  bad=copy.deepcopy(s);bad['space']['max_width']=1;assert not WorkshopLibrary(ROOT/'map_directed/library').find_single_exact(bad)
  rows.append(dict(id=item['id'],specification_id=s['id'],expected_version=item['contentVersion'],matched_versions=versions,wrong_space_rejected=True,generator_called=False,physics_cases=0))
 out=Path(a.out);assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(schema='pcg/fresh-process-reuse/v1',manifest_sha256=file_sha(manifest),matches=len(rows),rows=rows,generator_calls=0,physics_cases=0,production_admitted=False),ensure_ascii=False,indent=2)+'\n');print(out)
