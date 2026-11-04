if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import subprocess
from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT
from .finalize_revision059_v1 import folder_for

def main():
 r=next(r for r in rows()if label(r)=='hq04');f=folder_for(r);out=core.REPO/'pcg/results/approved-r059-hq04-native-reentry-v1';out.mkdir();receipt=out/'receipt.json';scene=core.REPO/'pcg/manual_review/runtime/revision059_native_reward_reload_v1.tscn';engine=core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64';command=[str(engine),'--headless','--path',str(core.REPO/'pcg/prototype/godot'),'--fixed-fps','60',str(scene),'--','--native-scene',str(f/'playable-final-v2/demo.tscn'),'--verify-package','--receipt',str(receipt)]
 core.write(out/'command.json',dict(command=command,engine=physics.artifact(engine),scene=physics.artifact(scene),script=physics.artifact(scene.with_suffix('.gd'))))
 with(out/'execution.log').open('w')as stream:p=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
 assert p.returncode==0,(out/'execution.log').read_text()[-1500:];result=core.read(str(receipt)+'.persistence.json');assert result['passed'];core.write(OUT/'verification/hq04-native-reentry.json',dict(passed=True,proof=physics.artifact(core.REPO/(str(receipt)+'.persistence.json')),receipt=physics.artifact(receipt)));print('HQ04_NATIVE_REENTRY_PASS')
if __name__=='__main__':main()
