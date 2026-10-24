"""Reuse the existing immutable-base overlay packer for a playable Godot map."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
from .director import REPO
from .run import write


def build(run,out,dependency_dir,game_tools):
    sys.path.insert(0,str(game_tools))
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    run=Path(run);out=Path(out);staging=out.parent/(out.name+'-resources')
    if staging.exists():raise ValueError('immutable_preview_staging_exists')
    staging.mkdir(parents=True)
    project=REPO/'pcg/prototype/godot'
    runtime=['main_plains.gd','plains_cells.gd','plains_lifecycle.gd','dynamic_context.gd','capability_adapter.gd','lab_draw_v3.gd']
    replacements={f'res://{n}':f'res://maploop/runtime/{n}'for n in runtime}
    for name in runtime:
        source=(project/name).read_text()
        for a,b in replacements.items():source=source.replace(a,b)
        p=staging/'maploop/runtime'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
    # External native scripts become regular res:// helpers in the Web overlay.
    for name in ['map_scene.gd','map_observer.gd','map_overlay.gd']:
        source=(REPO/'pcg/map_directed/godot'/name).read_text()
        for a,b in replacements.items():source=source.replace(a,b)
        if name=='map_scene.gd':
            source+='''
func publish_state() -> void:
\tsuper.publish_state()
\tif OS.has_feature("web") and map_observer != null:
\t\tJavaScriptBridge.eval("window.__pcgLabStateV3.map="+JSON.stringify(map_observer.report()),true)
'''
        p=staging/'maploop'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
    (staging/'maploop/cases.json').write_bytes((run/'replay_cases.json').read_bytes())
    # The inherited UI initializes from its original fixed resource before the
    # map adapter selects the explicit cases path. Provide the same list there.
    (staging/'modules_v3.json').write_bytes((run/'replay_cases.json').read_bytes())
    # These dynamically loaded formal-player textures are not in the older
    # immutable base's literal-preload closure. Keep their original source and
    # the actual imported texture bytes; do not substitute a different player.
    for asset in ['assets/plains_v3/hero/weapon.png','assets/plains_v3/hero/idle_run.png',
                  'assets/plains_v3/hero/actions.png','assets/actor_actions/courier_actions.png']:
        for relative in [asset,asset+'.import']:
            target=staging/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((project/relative).read_bytes())
        for imported in set(re.findall(r'res://([^"\s]+\.ctex)',(project/(asset+'.import')).read_text())):
            target=staging/imported;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((project/imported).read_bytes())
    (staging/'maploop/main.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://maploop/map_scene.gd" id="1"]
[node name="MapDirectedExperiment" type="Node2D"]
script = ExtResource("1")
''')
    result=pack(Path(dependency_dir)/'base.pck',out,main_scene='res://maploop/main.tscn',
        base_url='https://zhipijun1996.github.io'+BASE_URL,
        engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    html=out/'index.html';text=html.read_text().replace('"args": []','"args": ["--", "--cases-json", "res://maploop/cases.json"]')
    text=text.replace('PCG overlay packaging proof','Map-driven module library · 风铃平原隔离试玩')
    text=text.replace('Packaging proof only · frozen base + independent overlay','隔离实验 · A/D移动，Space跳跃，鼠标松开射击 · 可选Replay · 人工趣味待评')
    text=text.replace('const engine=new Engine(config);','''const requestedCase=Number(new URLSearchParams(location.search).get('case')??0);
if(Number.isInteger(requestedCase)&&requestedCase>=0&&requestedCase<3)config.args.push('--case',String(requestedCase));
const engine=new Engine(config);''')
    html.write_text(text)
    result.update(map_run=str(run.relative_to(REPO)),cases_sha256=hashlib.sha256((run/'replay_cases.json').read_bytes()).hexdigest(),
        scope='Actual Godot Web consumer; resource-path adaptation and read-only map telemetry; browser execution still required',
        native_source={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (REPO/'pcg/map_directed/godot').glob('*.gd')})
    write(out/'overlay-manifest.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--dependencies',type=Path,required=True);p.add_argument('--game-tools',type=Path,required=True)
    a=p.parse_args();build(a.run.resolve(),a.out.resolve(),a.dependencies.resolve(),a.game_tools.resolve())
