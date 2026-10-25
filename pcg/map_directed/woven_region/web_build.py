"""Thin extension of the existing source-matched formal-art Web packer."""
import argparse,json
from pathlib import Path
from ..valley_complete.web_build import build as valley_build
from ..director import REPO
from ..run import write


def build(cases,out,dependencies,game_tools):
    out=Path(out).resolve();draft=out.parent/(out.name+'-formal')
    valley_build(cases,draft,dependencies,game_tools)
    staging=out.parent/(draft.name+'-base-resources')
    def stage(name,data):
        p=staging/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
    for name in ['manual.gd','manual.tscn','mechanics.gd']:
        stage('woven_region/'+name,Path(__file__).with_name(name).read_text())
    case=json.loads((staging/'r2/cases.json').read_text())['cases'][0]
    case.update(title='风铃平原 · 岩谷织路 · 19地点多路线',extra_script='res://woven_region/mechanics.gd',automatic_shop_input=False)
    data=json.dumps({'cases':[case]},ensure_ascii=False)
    stage('r2/cases.json',data);stage('modules_v3.json',data)
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    result=pack(Path(dependencies)/'base.pck',out,main_scene='res://woven_region/manual.tscn',
        base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    page=out/'index.html';page.write_text(page.read_text().replace('PCG overlay packaging proof','风铃平原 · 岩谷织路 · 完整隔离地图').replace('Packaging proof only · frozen base + independent overlay','A/D 移动 · Space 单跳 · 鼠标松开反冲 · S 下穿 · E 购买 · M 整图 · R 重试'))
    write(out/'overlay-manifest.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();build(a.cases,a.out,a.dependencies,a.game_tools)
