"""Extend the prior verified lean overlay; keep all inherited resource bytes."""
import argparse,hashlib,json,re,sys,tempfile
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.tools.restore_archive import open_parts

def build(cases,out,game_tools):
 out=Path(out).resolve()
 if out.exists():raise ValueError('immutable_web_output_exists')
 out.mkdir(parents=True);sys.path.insert(0,str(Path(game_tools).resolve()))
 from check_web_bundle import Pack
 from pcg.prototype.packaging_v3.overlay_pack import write_pack,html,BASE_URL,ENGINE_PREFIX
 parent='results/shape-search-web-transport-v2/overlay.3b09aef68f37.pck'
 with open_parts('shape-search-results-v1')as z:
  index=json.loads(z.read('PCG-ARCHIVE-INDEX.json'));info=index[parent];data=z.read(info.get('archive_entry',parent))
  assert len(data)==info['bytes']and hashlib.sha256(data).hexdigest()==info['sha256']
 with tempfile.NamedTemporaryFile(suffix='.pck',dir=out)as tmp:
  tmp.write(data);tmp.flush();pack=Pack(Path(tmp.name));files={k:pack.read(k)for k in pack.entries}
 imported={};seen=set()
 def stage(p):
  p=p.resolve()
  if p in seen:return
  seen.add(p);rel=p.relative_to(REPO/'pcg').as_posix();text=p.read_text()
  text=text.replace('../r2_full/godot/','../../r2/godot/').replace('../r2_full/state_extra.gd','../../r2/state_extra.gd')
  files[rel]=text.encode();imported[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
  for target in re.findall(r'preload\("([^"\n]+)"\)',p.read_text()):
   if target.startswith('res://'):continue
   dep=(p.parent/target).resolve()
   if dep.is_file():stage(dep)
 for name in ['manual.gd','manual.tscn','extra.gd','manual_extra.gd']:
  stage(REPO/'pcg/map_directed/catalog_feed'/name)
 # New thorn Modules exercise a current-main art family absent from the old
 # eight-template lean pack. Keep original import metadata and compiled art.
 project=REPO/'pcg/prototype/godot'
 for name in ['hazard_fine_tileset.tres','hazard_surface_fine.png.import']:
  rel='assets/underworld_plains/hazards/'+name;p=project/rel;files[rel]=p.read_bytes();imported[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
  if name.endswith('.import'):
   for ref in set(re.findall(r'res://(\.godot/imported/[^"\s]+)',p.read_text())):
    files[ref]=(project/ref).read_bytes();imported[ref]=hashlib.sha256(files[ref]).hexdigest()
 payload=json.loads(Path(cases).read_text());case=payload['cases'][0]
 case['extra_script']='res://map_directed/catalog_feed/manual_extra.gd';case['automatic_shop_input']=False
 files['r2/cases.json']=json.dumps({'cases':[case]},ensure_ascii=False).encode();files['modules_v3.json']=files['r2/cases.json']
 files['project.godot']=files['project.godot'].decode().replace('res://shape_search/manual.tscn','res://map_directed/catalog_feed/manual.tscn').encode()
 p=out/'overlay.pck';m=write_pack(p,files);name='overlay.'+m['sha256'][:12]+'.pck';p.rename(out/name);m['pack']=name
 verify=Pack(out/name)
 for k,b in files.items():assert verify.read(k)==b
 old=REPO/'pcg/results/shape-search-web-transport-v2/overlay-manifest.json'
 if old.exists():base=json.loads(old.read_text())['base']
 else:
  with open_parts('shape-search-results-v1')as z:
   k='results/shape-search-web-transport-v2/overlay-manifest.json';i=json.loads(z.read('PCG-ARCHIVE-INDEX.json'))[k];base=json.loads(z.read(i.get('archive_entry',k)))['base']
 result=dict(overlay=m,base=base,parent=dict(archive='shape-search-results-v1',path=parent,sha256=info['sha256']),source_files=imported,cases_source=str(Path(cases).resolve().relative_to(REPO)),cases_sha256=hashlib.sha256(Path(cases).read_bytes()).hexdigest(),byte_verified=True,manual=True,production_admitted=False)
 write(out/'overlay-manifest.json',result);(out/'index.html').write_text(html(name,m['bytes'],'https://zhipijun1996.github.io'+BASE_URL,base['bytes'],'https://zhipijun1996.github.io'+ENGINE_PREFIX));return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();print(json.dumps(build(a.cases,a.out,a.game_tools)['overlay']))
