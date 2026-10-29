"""Immutable diagnostic input folders; independent versions cannot mutate running cases."""
import copy
from pcg.migration import core,physics
from .continue_revision060_v1 import OUT,label

def frozen_row(row,version):
 r=copy.deepcopy(row);source=core.REPO/r['outputDirectory'];dest=core.REPO/('pcg/manual_review/implementation/revision-060-executed-'+version)/r['moduleId']
 if not dest.exists():
  for name in ['module.mapnote.json','cases.json','migration.json','parameters.json']:core.write(dest/name,core.read(source/name))
  core.write(dest/'execution-input-freeze.json',dict(version=version,source=core.relative(source),artifacts={n:physics.artifact(dest/n)for n in ['module.mapnote.json','cases.json','migration.json','parameters.json']},stopping='Never overwrite this input directory. Package/evidence files may be appended.'))
 r['outputDirectory']=core.relative(dest);return r
