"""Existing verified overlay packer, full-R2 manual consumer and source bytes."""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
from ..director import REPO
from ..run import write


def build(cases_file,out,dependencies,game_tools, direct_join=False):
    sys.path.insert(0,str(game_tools))
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    out=Path(out);staging=out.parent/(out.name+'-resources')
    if staging.exists():raise ValueError('immutable_preview_staging_exists')
    staging.mkdir(parents=True)
    project=REPO/'pcg/prototype/godot'
    runtime=['main_plains.gd','plains_cells.gd','plains_lifecycle.gd','dynamic_context.gd','capability_adapter.gd','lab_draw_v3.gd']
    replacements={f'res://{name}':f'res://r2/runtime/{name}'for name in runtime}
    def stage(relative,data):
        path=staging/relative;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data if isinstance(data,bytes)else data.encode())
    def rewritten(text):
        for a,b in replacements.items():text=text.replace(a,b)
        return text
    for name in runtime:stage('r2/runtime/'+name,rewritten((project/name).read_text()))
    root=Path(__file__).parent
    included=['state_extra.gd','bell_extra.gd','gate_world.gd',
        'godot/r2_manual_scene.gd','godot/r2_manual_scene.tscn','godot/r2_camera.gd','godot/r2_annotations.gd']
    for name in included:
        text=rewritten((root/name).read_text())
        if name.endswith('r2_manual_scene.gd'):text=text.replace('res://r2_cases.json','res://r2/cases.json')
        stage('r2/'+name,text)
    original=json.loads(Path(cases_file).read_text());case=copy.deepcopy(original['cases'][0])
    case['title']='R2 风铃平原 Seed 0 · 完整多环路地图'
    case['extra_script']='res://r2/bell_extra.gd'
    if direct_join:
        direct=root.parent/'direct_join'
        for name in ['manual.gd','manual.tscn','module_bounds.gd','challenge_extra.gd']:
            stage('direct_join/'+name,(direct/name).read_text().replace('../r2_full/godot/','../r2/godot/').replace('../r2_full/','../r2/'))
        case['title']='风铃平原 · 27个Module直接拼接 · 多路线与回环'
        case['extra_script']='res://direct_join/challenge_extra.gd'
        case.pop('required_optional_challenges',None)
    data=json.dumps({'cases':[case]},ensure_ascii=False,separators=(',',':'))
    stage('r2/cases.json',data);stage('modules_v3.json',data)
    for asset in ['assets/plains_v3/hero/weapon.png','assets/plains_v3/hero/idle_run.png',
                  'assets/plains_v3/hero/actions.png','assets/actor_actions/courier_actions.png']:
        for relative in [asset,asset+'.import']:stage(relative,(project/relative).read_bytes())
        for imported in set(re.findall(r'res://([^"\s]+\.ctex)',(project/(asset+'.import')).read_text())):
            stage(imported,(project/imported).read_bytes())
    result=pack(Path(dependencies)/'base.pck',out,main_scene='res://direct_join/manual.tscn'if direct_join else'res://r2/godot/r2_manual_scene.tscn',
        base_url='https://zhipijun1996.github.io'+BASE_URL,
        engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    html=out/'index.html';page=html.read_text()
    page=page.replace('PCG overlay packaging proof','完整 R2 风铃平原 · 多环路手动探索')
    page=page.replace('Packaging proof only · frozen base + independent overlay','A/D 移动 · Space 单跳 · 鼠标松开射击 · S 下穿 · M 整图 · R 重试')
    if direct_join:page=page.replace('完整 R2 风铃平原 · 多环路手动探索','风铃平原 · Module直接拼接 · 多路线地图')
    html.write_text(page)
    result.update(cases_source=str(Path(cases_file).relative_to(REPO)),
        cases_source_sha256=hashlib.sha256(Path(cases_file).read_bytes()).hexdigest(),
        web_case_adaptation=['single full-world manual case','explicit resource path rewrite','title only'],
        scope='Real Godot manual full-map consumer; no abstract-graph playability claim',
        native_source={str((root/name).relative_to(REPO)):hashlib.sha256((root/name).read_bytes()).hexdigest()for name in included})
    write(out/'overlay-manifest.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--dependencies',type=Path,required=True);p.add_argument('--game-tools',type=Path,required=True)
    a=p.parse_args();print(json.dumps({k:v for k,v in build(a.cases.resolve(),a.out.resolve(),a.dependencies.resolve(),a.game_tools.resolve()).items()if k!='files'},ensure_ascii=False,indent=2))
