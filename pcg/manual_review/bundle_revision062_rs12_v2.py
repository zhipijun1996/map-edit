"""Append a new ZIP for read-only-qualified S12; preserve its earlier failed ZIP."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import zipfile,shutil
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT

def main():
 f=core.REPO/'pcg/manual_review/implementation/revision-062-final-v1/idea-spec02-s12-001';root=OUT/'downloads';old=root/'rs12-native.zip';new=root/'rs12-native-reobserved-v2.zip';assert not new.exists();assert core.read(f/'qualification.json')['passed']
 with zipfile.ZipFile(old)as source,zipfile.ZipFile(new,'x',zipfile.ZIP_DEFLATED,compresslevel=7)as out:
  for item in source.infolist():
   data=source.read(item.filename)
   if item.filename==core.relative(f/'qualification.json'):data=(f/'qualification.json').read_bytes()
   out.writestr(item,data)
  for p in [OUT/'fixtures/rs12-native-neighbor-observation-v1/analysis.json',OUT/'fixtures/original-motor-margin-v1/report.json',OUT/'verification/rs12-same-reserved-execution-alias.json']:out.write(p,core.relative(p))
 with zipfile.ZipFile(new)as z:assert z.testzip()is None
 before=root/'index-initial-v1.json';assert not before.exists();shutil.copyfile(root/'index.json',before);index=core.read(root/'index.json');row=next(r for r in index['rows']if r['name']=='rs12');row.update(file=physics.artifact(new),bytes=new.stat().st_size,qualified=True,originalUnqualifiedZip=physics.artifact(old));index.update(originalIndex=physics.artifact(before),source=physics.artifact(__file__));core.write(root/'index.json',index);print('RS12_NEW_NATIVE_ZIP_V2',new.stat().st_size,flush=True)
if __name__=='__main__':main()
