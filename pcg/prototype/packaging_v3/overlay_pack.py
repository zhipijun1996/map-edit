"""Build an independently identified Godot 4 format-4 overlay over a frozen base.

This writes the documented unencrypted pack directory layout and verifies every
entry with the game's existing Pack reader. It never edits the base PCK.
Runtime load_resource_pack and browser execution remain required checks.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys
from pathlib import Path

TOOLS = Path('/workspace/gunman-rush-latest/tools')
sys.path.insert(0, str(TOOLS))
from check_web_bundle import Pack, resource_path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PREFIX = '/gunman-rush-previews/previews/PCG-RESEARCH-01/7c7b42e46e33c895d51741c1ca5d26a516568a27/8f8ded8ce59a/index'
BASE_URL = '/gunman-rush-previews/previews/PCG-RESEARCH-02/c8b7a735ce3befc8ada013a21a6e69577443f4dc/f7ae17e42bf4/index.f7ae17e42bf4.pck'

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write_pack(path: Path, files: dict[str, bytes]) -> dict:
    """Equivalent unencrypted format-4 container, no executable/compiler patching."""
    for name in files: resource_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries=[]
    with path.open('wb') as f:
        f.write(bytes(112))
        for name,data in sorted(files.items()):
            f.write(bytes((-f.tell()) % 16))
            offset=f.tell()-112
            f.write(data)
            entries.append((name,offset,len(data),hashlib.md5(data).digest()))
        f.write(bytes((-f.tell()) % 16))
        directory=f.tell();f.write(struct.pack('<I',len(entries)))
        for name,offset,size,md5 in entries:
            encoded=name.encode()+b'\0';encoded+=bytes((-len(encoded))%4)
            f.write(struct.pack('<I',len(encoded)));f.write(encoded)
            f.write(struct.pack('<QQ',offset,size));f.write(md5);f.write(struct.pack('<I',0))
        f.seek(0)
        f.write(struct.pack('<4sIIIIIQQ',b'GDPC',4,4,7,2,2,112,directory))
    check=Pack(path)
    for name,data in files.items():
        if check.read(name)!=data:raise RuntimeError('PCK byte mismatch: '+name)
    return dict(bytes=path.stat().st_size,sha256=sha(path.read_bytes()),entries=len(files))

def boot_files(main_scene: str, base_sha256: str, base_bytes: int) -> dict[str, bytes]:
    if not main_scene.startswith('res://') or not main_scene.endswith('.tscn'):
        raise ValueError('Expected a resource scene')
    script='''extends Node
## Mount a byte-verified frozen base before parsing any game-specific classes.
func _ready() -> void:
    _mount_and_start.call_deferred()

func _mount_and_start() -> void:
    var file := FileAccess.open("/base.pck", FileAccess.READ)
    if file == null:
        push_error("OVERLAY_BASE_FILE_MISSING");return
    var bytes := file.get_buffer(file.get_length())
    var hashing := HashingContext.new()
    hashing.start(HashingContext.HASH_SHA256);hashing.update(bytes)
    var actual := hashing.finish().hex_encode()
    if bytes.size() != BASE_BYTES or actual != BASE_SHA:
        push_error("OVERLAY_BASE_IDENTITY_MISMATCH");return
    file.close();bytes.clear()
    if not ProjectSettings.load_resource_pack("/base.pck", false):
        push_error("OVERLAY_BASE_MOUNT_FAILED");return
    print("OVERLAY_BASE_MOUNTED ",actual)
    # The base font becomes available only after mounting. No game-specific
    # custom theme/font is referenced before the mount.
    var font := load("res://assets/ui/demo_ui_01/r2/fonts/fusion-pixel-12px-proportional-zh_hans.otf") as Font
    if font != null:
        ThemeDB.get_default_theme().default_font = font
        ThemeDB.fallback_font = font
    var scene := load(MAIN_SCENE) as PackedScene
    if scene == null:
        push_error("OVERLAY_GAME_SCENE_FAILED");return
    var result := get_tree().change_scene_to_packed(scene)
    print("OVERLAY_SCENE_REQUESTED ",MAIN_SCENE," ",result)
'''
    script=script.replace('BASE_BYTES',str(base_bytes)).replace('BASE_SHA',json.dumps(base_sha256)).replace('MAIN_SCENE',json.dumps(main_scene))
    settings='''config_version=5
[application]
config/name="PCG immutable overlay research"
run/main_scene="res://pcg_overlay_boot.tscn"
config/features=PackedStringArray("4.7", "GL Compatibility")
[display]
window/size/viewport_width=1280
window/size/viewport_height=720
[physics]
common/physics_ticks_per_second=60
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
environment/defaults/default_clear_color=Color(0.055,0.075,0.105,1)
'''
    scene='''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://pcg_overlay_boot.gd" id="1"]
[node name="ImmutableOverlayBoot" type="Node"]
script = ExtResource("1")
'''
    return {'project.godot':settings.encode(),'pcg_overlay_boot.gd':script.encode(),'pcg_overlay_boot.tscn':scene.encode()}

def html(pack: str, pack_bytes: int, base_url: str, base_bytes: int, engine_prefix: str) -> str:
    cfg=dict(executable=engine_prefix,mainPack=pack,canvasResizePolicy=2,focusCanvas=True,
        fileSizes={pack:pack_bytes,base_url:base_bytes,engine_prefix+'.wasm':39514754},
        args=[],gdextensionLibs=[],ensureCrossOriginIsolationHeaders=False)
    return '''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>PCG overlay packaging proof</title>
<style>html,body{margin:0;background:#0e141c;color:#d7e5ef;width:100%;height:100%;overflow:hidden}canvas{width:100%;height:100%;display:block}#loading{position:fixed;bottom:4px;left:8px;font:12px monospace;background:#122432;padding:4px}</style>
<canvas id="canvas" width="1280" height="720" tabindex="0"></canvas><div id="loading">Loading byte-verified immutable base and independent overlay...</div>
<script src="ENGINE_JS"></script><script>
const config=CONFIG;
const engine=new Engine(config);
window.__overlayTransport={base:BASE_URL,pack:PACK,stage:'loading'};
Promise.all([engine.init(config.executable),engine.preloadFile(BASE_URL,'/base.pck')]).then(()=>engine.startGame()).then(()=>{window.__overlayTransport.stage='engine_started';document.getElementById('loading').textContent='Packaging proof only · frozen base + independent overlay';}).catch(error=>{window.__overlayTransport.error=String(error);document.getElementById('loading').textContent=String(error);console.error(error);});
</script></html>'''.replace('ENGINE_JS',engine_prefix+'.js').replace('CONFIG',json.dumps(cfg)).replace('BASE_URL',json.dumps(base_url)).replace('PACK',json.dumps(pack))

def build(base_path: Path, out: Path, full_path: Path|None=None, main_scene='res://main_v2.tscn',base_url=BASE_URL,engine_prefix=ENGINE_PREFIX,extra_dir: Path|None=None):
    if out.exists() and any(out.iterdir()):raise RuntimeError('Refuse to overwrite nonempty overlay proof')
    out.mkdir(parents=True,exist_ok=True)
    base=Pack(base_path);base_data=base_path.read_bytes();base_hash=sha(base_data)
    files={}
    changed=[]
    if full_path:
        full=Pack(full_path)
        for name in full.entries:
            if name=='project.binary':continue
            data=full.read(name)
            if name not in base.entries or base.read(name)!=data:
                files[name]=data;changed.append(name)
    if extra_dir:
        for path in sorted(extra_dir.rglob('*')):
            if path.is_file():
                name=path.relative_to(extra_dir).as_posix();resource_path(name)
                if name in ('project.binary','project.godot','pcg_overlay_boot.gd','pcg_overlay_boot.tscn'):raise ValueError('Reserved bootstrap resource: '+name)
                files[name]=path.read_bytes();changed.append(name)
    # Global classes/UIDs are registered at engine startup, before base mounting.
    # Full-export cache wins when provided; otherwise the exact base cache is used.
    for name in ('.godot/global_script_class_cache.cfg','.godot/uid_cache.bin'):
        if name not in files and name in base.entries:files[name]=base.read(name)
    files.update(boot_files(main_scene,base_hash,len(base_data)))
    draft=out/'overlay.pck';receipt=write_pack(draft,files);name='overlay.'+receipt['sha256'][:12]+'.pck';draft.rename(out/name)
    (out/'index.html').write_text(html(name,receipt['bytes'],base_url,len(base_data),engine_prefix))
    manifest=dict(schema='pcg/immutable-overlay/v1',base=dict(path=str(base_path),url=base_url,bytes=len(base_data),sha256=base_hash),overlay=receipt|dict(pack=name),main_scene=main_scene,engine=dict(prefix=engine_prefix,version='4.7.2.stable.official.ed1daf0bf'),files={name:dict(bytes=len(data),sha256=sha(data)) for name,data in sorted(files.items())},new_or_changed_from_full=changed,runtime_verified=False,limits=['Transport/pack directory verification only until real browser execution passes.','A base pack mount reuses assets/code; it is not an assertion of V3 gameplay quality.'])
    (out/'overlay-manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=ROOT/'delivery/composable-v2/web/index.pck');p.add_argument('--full',type=Path);p.add_argument('--extra-dir',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--scene',default='res://main_v2.tscn');p.add_argument('--base-url',default=BASE_URL);p.add_argument('--engine-prefix',default=ENGINE_PREFIX)
    a=p.parse_args();r=build(a.base,a.out,a.full,a.scene,a.base_url,a.engine_prefix,a.extra_dir);print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2))
