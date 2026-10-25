"""Reuse the existing verified overlay builder and original manual consumer."""
import argparse,json,re
from pathlib import Path
from ..r2_full.web_build import build as original_build
from ..director import REPO
from ..run import write

def build(cases,out,dependencies,game_tools):
 out=Path(out).resolve();draft=out.parent/(out.name+'-base')
 original_build(Path(cases).resolve(),draft,Path(dependencies).resolve(),Path(game_tools).resolve(),open_valley=True)
 staging=draft.parent/(draft.name+'-resources');project=REPO/'pcg/prototype/godot'
 def stage(name,data):
  p=staging/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes)else data.encode())
 for p in Path(__file__).parent.glob('*'):
  if p.suffix in ['.gd','.tscn']:stage('valley_complete/'+p.name,p.read_text().replace('../r2_full/godot/','../r2/godot/'))
 case=json.loads((staging/'r2/cases.json').read_text())['cases'][0]
 case['extra_script']='res://valley_complete/mechanics.gd';case['automatic_shop_input']=False
 for key in ['require_parking','require_purchase','required_optional_challenges']:case.pop(key,None)
 data=json.dumps({'cases':[case]},ensure_ascii=False)
 stage('r2/cases.json',data);stage('modules_v3.json',data)
 # These source-matched dynamic JSON texture references were absent from the
 # old lean base closure. Stage source/import/actual compressed texture bytes.
 extra_names=[r['path']for r in json.loads((REPO/'pcg/research/valley-current-art.json').read_text())['files']]
 terrain=json.loads((project/'assets/underworld_plains/terrain/fine_32/terrain_build.json').read_text())
 for key in ['source_texture','atlas']:
  path=terrain[key].removeprefix('res://');extra_names += [path,path+'.import']
 mechanisms=json.loads((project/'assets/underworld_plains/mechanisms/mechanisms_fine_build.json').read_text())
 for value in mechanisms.values():
  if isinstance(value,dict)and value.get('texture'):
   path=value['texture'].removeprefix('res://');extra_names += [path,path+'.import']
 for name in extra_names:
  stage(name,(project/name).read_bytes())
  if name.endswith('.import'):
   for rel in set(re.findall(r'res://([^"\s]+\.ctex)',(project/name).read_text())):stage(rel,(project/rel).read_bytes())
 stage('resources/items/damage_blue.tres',(project/'resources/items/damage_blue.tres').read_bytes())
 from pcg.prototype.packaging_v3.overlay_pack import build as pack,BASE_URL,ENGINE_PREFIX
 result=pack(Path(dependencies)/'base.pck',out,main_scene='res://valley_complete/manual.tscn',base_url='https://zhipijun1996.github.io'+BASE_URL,engine_prefix='https://zhipijun1996.github.io'+ENGINE_PREFIX,extra_dir=staging)
 page=out/'index.html';page.write_text(page.read_text().replace('PCG overlay packaging proof','风铃平原 · 宝箱与停靠风铃').replace('Packaging proof only · frozen base + independent overlay','A/D 移动 · Space 跳跃 · 鼠标松开反冲 · E 购买 · M 整图 · R 重试'))
 write(out/'overlay-manifest.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--dependencies',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();print(build(a.cases,a.out,a.dependencies,a.game_tools)['overlay'])
