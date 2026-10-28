"""Reuse the woven/formal packer, adding the real main hazard art closure."""
import argparse,json,re
from pathlib import Path
from ..woven_region.web_build import build as woven_build
from ..director import REPO
from ..run import write

def build(cases,out,dependencies,game_tools):
    out=Path(out).resolve();draft=out.parent/(out.name+'-woven')
    woven_build(cases,draft,dependencies,game_tools)
    staging=out.parent/(draft.name+'-formal-base-resources');project=REPO/'pcg/prototype/godot'
    def stage(name,data):
        p=staging/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes)else data.encode())
    for name in ['manual.gd','manual.tscn']:stage('content_routes/'+name,Path(__file__).with_name(name).read_text())
    for record in json.loads((REPO/'pcg/research/content-routes-hazard-art.json').read_text())['files']:
        name=record['path'];stage(name,(project/name).read_bytes())
        if name.endswith('.import'):
            for rel in set(re.findall(r'res://(\.godot/imported/[^"\s]+)',(project/name).read_text())):stage(rel,(project/rel).read_bytes())
    case=json.loads((staging/'r2/cases.json').read_text())['cases'][0];case['title']='风铃平原 · 风隙回响 · 内容驱动完整地图'
    data=json.dumps({'cases':[case]},ensure_ascii=False);stage('r2/cases.json',data);stage('modules_v3.json',data)
    from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
    result=pack(Path(dependencies)/'base.pck',out,main_scene='res://content_routes/manual.tscn',base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
    write(out/'overlay-manifest.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();build(a.cases,a.out,a.dependencies,a.game_tools)
