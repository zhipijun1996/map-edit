import copy
from pcg.migration import core,physics
def frozen_row(row,version):
 r=copy.deepcopy(row);source=core.REPO/r['outputDirectory'];dest=core.REPO/('pcg/manual_review/implementation/revision-063-executed-'+version)/r['moduleId']
 if not dest.exists():
  for n in ['module.mapnote.json','cases.json','migration.json','parameters.json']:core.write(dest/n,core.read(source/n))
  core.write(dest/'execution-input-freeze.json',dict(version=version,source=core.relative(source),artifacts={n:physics.artifact(dest/n) for n in ['module.mapnote.json','cases.json','migration.json','parameters.json']},stopping='Never overwrite executed input.'))
 r['outputDirectory']=core.relative(dest);return r
