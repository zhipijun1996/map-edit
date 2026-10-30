import zipfile
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,OUT
from .record_revision063_native_v1 import folder_for
def main():
 out=OUT/'downloads';out.mkdir(exist_ok=True);items=[]
 for row in rows():
  n=label(row);f=folder_for(row);package=f/'playable';target=out/(n+'-native.zip');assert package.exists()and not target.exists()
  readme=f'''{row['moduleId']} / {row['designVersion']}

Extract at the root of the implementation branch. Restore original project
resources with pcg/WORKSPACE.md; official engine and game assets are referenced.

Playable scene: {core.relative(package/'demo.tscn')}
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/{core.relative(package/'demo.tscn')}" -- --case 0

Omit --replay for manual control. Add --replay to replay actual recorded inputs.
--case N selects another included direction. Read qualification.json for the
exact FULL/partial/failed scope. Playable success does not imply qualification.
Human playtest, arbitrary entry states, mirrors and production approval UNKNOWN.
'''
  with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
   z.writestr(row['moduleId']+'-README.txt',readme)
   for p in sorted(package.rglob('*')):
    if p.is_file()and'.godot'not in p.parts:z.write(p,core.relative(p))
   for name in ['module.mapnote.json','physics-input-cases.json','parameters.json','qualification.json','frozen.json','implementation-provenance.json']:
    z.write(f/name,core.relative(f/name))
  with zipfile.ZipFile(target)as z:assert z.testzip()is None
  items.append(dict(name=n,file=physics.artifact(target),bytes=target.stat().st_size,scene=physics.artifact(package/'demo.tscn'),qualified=core.read(f/'qualification.json')['passed']))
 bonus=OUT/'fixtures/lift-optional-chest-v1';assert core.read(bonus/'reward-evidence.json')['passed'];target=out/'lift-optional-chest-native.zip'
 with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
  for p in sorted(bonus.rglob('*')):
   if p.is_file()and'.godot'not in p.parts:z.write(p,core.relative(p))
 with zipfile.ZipFile(target)as z:assert z.testzip()is None
 core.write(out/'index.json',dict(schema='pcg/native-playable-downloads/v1',rows=items,bonus=[dict(name='lift-optional-chest',file=physics.artifact(target),actualCoins=4,formalQualification=False)],source=physics.artifact(__file__),officialEngine='4.7.2',originalAssets='restore per pcg/WORKSPACE.md',productionAdmitted=False));print('R063_NATIVE_BUNDLES',len(items),'+ chest bonus',flush=True)
if __name__=='__main__':main()
