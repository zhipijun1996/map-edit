import importlib,zipfile
from pcg.migration import core,physics

def main():
 for v in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+v+'_v1');final=importlib.import_module('pcg.manual_review.finalize_revision'+v+'_v1');out=scope.OUT/'downloads';out.mkdir(exist_ok=True);rows=[]
  for r in scope.rows():
   n=scope.label(r);f=final.folder_for(r);package=f/('playable-presentation-v2'if v=='060'and n=='hq09'else'playable');target=out/(n+'-native.zip');assert package.exists()and not target.exists();readme=f'''{r['moduleId']} / {r['designVersion']}\n\nExtract at repository root on the implementation branch. Restore original project resources using pcg/WORKSPACE.md. Original game assets and official Godot binary are referenced, not duplicated here.\n\nPlayable scene: {core.relative(package/'demo.tscn')}\nRun with the official Godot 4.7.2:\npcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/{core.relative(package/'demo.tscn')}" -- --case 0\nAdd --replay for actual recorded input playback; omit for manual control. --case N selects another included direction.\n\nRead {core.relative(f/'qualification.json')} for exact FULL/partial/failed scope. A fixed playable sample does not certify untested initial states, mirrors, closures or production approval.\n'''
   with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
    z.writestr(r['moduleId']+'-README.txt',readme)
    for p in sorted(package.rglob('*')):
     if p.is_file()and'.godot'not in p.parts:z.write(p,core.relative(p))
    for name in ['module.mapnote.json','physics-input-cases.json','parameters.json','qualification.json','frozen.json']:
     z.write(f/name,core.relative(f/name))
   with zipfile.ZipFile(target)as z:assert z.testzip()is None
   rows.append(dict(name=n,file=physics.artifact(target),bytes=target.stat().st_size,scene=physics.artifact(package/'demo.tscn'),qualified=core.read(f/'qualification.json')['passed']))
  core.write(out/'index.json',dict(schema='pcg/native-playable-downloads/v1',rows=rows,source=physics.artifact(__file__),originalGameAssets='restore per pcg/WORKSPACE.md',officialEngine='4.7.2',productionAdmitted=False));print(v,'NATIVE_ZIP_BUNDLES',len(rows),flush=True)
if __name__=='__main__':main()
