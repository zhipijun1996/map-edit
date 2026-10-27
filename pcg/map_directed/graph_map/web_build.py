"""Portable manual consumer of this exact whole Map, using existing packer."""
import argparse,json,re,sys
from pathlib import Path
from ..director import REPO
from ..run import write
from ..shape_search.web_build import build as formal_build


def build(cases,out,dependencies,game_tools):
    out=Path(out).resolve();draft=out.parent/(out.name+'-formal')
    formal_build(cases,draft,dependencies,game_tools)
    staging=out.parent/(draft.name+'-formal-base-resources');project=REPO/'pcg/prototype/godot'
    if not staging.exists():raise ValueError('formal_staging_missing/'+str(staging))
    def rewrite(text):return text.replace('../r2_full/','../r2/').replace('../../prototype/','res://prototype/').replace('res://main_plains.gd','res://r2/runtime/main_plains.gd').replace('res://r2_cases.json','res://r2/cases.json')
    def stage(name,data):
        p=staging/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes)else data.encode())
    # Preserve relative paths of the actual custom Cell and economy adapters.
    # Their recursive dependencies are source files, never a substitute runtime.
    pending=[p for folder in ['graph_map','catalog_feed']for p in (Path(__file__).parent.parent/folder).glob('*')if p.suffix in ['.gd','.tscn']]
    pending += [REPO/'pcg/prototype/workshop/mechanics.gd']
    seen=set()
    while pending:
        p=pending.pop().resolve()
        if p in seen:continue
        seen.add(p);text=p.read_text();name=p.relative_to(REPO/'pcg').as_posix()
        # Map-directed siblings retain their exact directory relationships.
        name=name.removeprefix('map_directed/')
        for ref in re.findall(r'(?:preload|extends|load)\s*\(?\s*["\']([^"\']+)["\']',text):
            if not ref.startswith('res://'):
                dep=(p.parent/ref).resolve()
                if dep.exists()and dep.suffix in ['.gd','.tscn','.tres']:pending.append(dep)
        if '/r2_full/'in str(p):name='r2/'+p.relative_to(REPO/'pcg/map_directed/r2_full').as_posix()
        stage(name,rewrite(text))
    # Base pack is an old immutable asset carrier. Overlay every current formal
    # text resource, so cached class names cannot silently load old game logic.
    provenance=json.loads((project/'source_provenance.json').read_text())
    for name in provenance['files']:
        if Path(name).suffix in ['.gd','.tscn','.tres']:stage(name,(project/name).read_bytes())
    stage('.godot/global_script_class_cache.cfg',(project/'.godot/global_script_class_cache.cfg').read_bytes())
    original=json.loads(Path(cases).read_text())['cases'][0]
    case=dict(original,extra_script='res://graph_map/extra.gd',automatic_shop_input=False,preview_title='风铃平原 · 同图驱动22 Macro隔离原型')
    # Verification-only goals do not constrain a human's exploration order.
    for key in ['require_purchase','require_parking','required_optional_challenges','required_reward_ids','recorded_frames']:case.pop(key,None)
    data=json.dumps({'cases':[case]},ensure_ascii=False);stage('r2/cases.json',data);stage('modules_v3.json',data)
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    result=pack(Path(dependencies)/'base.pck',out,main_scene='res://graph_map/manual.tscn',base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    result.update(cases_source=str(Path(cases)),human_fun='UNREVIEWED',production_admitted=False,scope='Same full world, original manual Router; real browser validation is separate')
    page=out/'index.html';page.write_text(page.read_text().replace('PCG overlay packaging proof','风铃平原 · 多路线Map原型').replace('Packaging proof only · frozen base + independent overlay','A/D 移动 · 空格跳跃 · 鼠标松开射击 · E 购买 · M 地图 · R 重试'))
    write(out/'overlay-manifest.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();build(a.cases,a.out,a.dependencies,a.game_tools)
