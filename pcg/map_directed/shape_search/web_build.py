"""Stage this experiment over the existing formal-art/manual overlay packer."""
import argparse,json,re
from pathlib import Path
from ..director import REPO
from ..run import write
from ..valley_complete.web_build import build as formal_build

def build(cases,out,dependencies,game_tools):
    out=Path(out).resolve();draft=out.parent/(out.name+'-formal')
    formal_build(cases,draft,dependencies,game_tools)
    staging=out.parent/(draft.name+'-base-resources');project=REPO/'pcg/prototype/godot'
    def stage(name,data):
        p=staging/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data if isinstance(data,bytes)else data.encode())
    for name in ['manual.gd','manual.tscn','mechanics.gd','presentation.gd']:
        stage('shape_search/'+name,Path(__file__).with_name(name).read_text().replace('../r2_full/godot/','../r2/godot/'))
    for record in json.loads((REPO/'pcg/research/shape-search-art-closure.json').read_text())['files']:
        name=record['path'];stage(name,(project/name).read_bytes())
        if name.endswith('.import'):
            for rel in set(re.findall(r'res://(\.godot/imported/[^"\s]+)',(project/name).read_text())):stage(rel,(project/rel).read_bytes())
    for name in ['underworld_scenery.gd','underworld_local_composition.gd','grounded_contact.gd','underworld_presentation.gd','underworld_foreground.gd','underworld_windmill.gd']:
        rel='scripts/underworld_plains/'+name;stage(rel,(project/rel).read_bytes())
    case=json.loads((staging/'r2/cases.json').read_text())['cases'][0]
    case.update(title='风铃平原 · 实际 Macro 形状搜索',extra_script='res://shape_search/mechanics.gd',automatic_shop_input=False)
    data=json.dumps({'cases':[case]},ensure_ascii=False);stage('r2/cases.json',data);stage('modules_v3.json',data)
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    result=pack(Path(dependencies)/'base.pck',out,main_scene='res://shape_search/manual.tscn',base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    write(out/'overlay-manifest.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();build(a.cases,a.out,a.dependencies,a.game_tools)
