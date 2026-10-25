"""Thin regional entry point over the existing complete formal overlay builder."""
import argparse
from pathlib import Path
from ..valley_complete.web_build import build as formal_build
from ..run import write

def build(cases,out,dependencies,game_tools):
 out=Path(out).resolve();draft=out.parent/(out.name+'-formal')
 formal_build(cases,draft,dependencies,game_tools)
 from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
 staging=draft.parent/(draft.name+'-base-resources')
 for name in ['manual.gd','manual.tscn']:
  p=staging/'region_scale'/name;p.parent.mkdir(exist_ok=True)
  p.write_bytes(Path(__file__).with_name(name).read_bytes())
 result=pack(Path(dependencies)/'base.pck',out,main_scene='res://region_scale/manual.tscn',base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
 p=out/'index.html';p.write_text(p.read_text().replace('PCG overlay packaging proof','平原大图接缝实验').replace('Packaging proof only · frozen base + independent overlay','A/D 移动 · Space 跳跃 · 鼠标松开反冲 · S 下穿 · M 整图 · R 重试'))
 write(out/'overlay-manifest.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();print(build(a.cases,a.out,a.dependencies,a.game_tools)['overlay'])
