"""Immutable Block pilot delivery using the established preview host/transport."""
import argparse,json,shutil,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.thin_preview import build as thin_build
from pcg.tools.publish_woven_preview import publish,HOST
from pcg.prototype.factory.core.engine import file_sha

TASK='MAPGEN-BLOCK-GRID-01'
def run(play,media,out,task=TASK,scope=None):
    play=Path(play).resolve();media=Path(media).resolve();out=Path(out).resolve()
    out.mkdir(exist_ok=False);stage=out/'assets';stage.mkdir()
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    m=json.loads((play/'overlay-manifest.json').read_text());build=m['overlay']['sha256'][:12]
    for p in media.iterdir():
        if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:shutil.copy2(p,stage/p.name)
    shutil.copy2(play/m['overlay']['pack'],stage/('index.'+build+'.pck'))
    shutil.copy2(play/'overlay-manifest.json',stage/'overlay-manifest.json')
    write(stage/'build-info.json',dict(task=task,implementation_commit=source,build_id=build,source_cases_sha256=m['cases_sha256'],
        scope=scope or '3 bounded Block128 maps, 33 whole-map checks plus 5 exact-demand warm reruns; 44-node regional design remains logical only',human_playtests=0,production_admitted=False))
    prefix=task+'/'+source+'/'+build
    assets=publish(stage,'artifacts/'+prefix,'Archive Block128 maps and exact real-physics videos [skip ci]',out/'assets-publication.json')
    base='https://raw.githubusercontent.com/'+HOST+'/'+assets['host_commit']+'/artifacts/'+prefix
    thin=out/'thin';thin_build(play,base,thin);report=(media/'report.html').read_text()
    for p in stage.iterdir():report=report.replace('"'+p.name+'"','"'+base+'/'+p.name+'"')
    (thin/'report.html').write_text(report)
    url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+prefix+'/'
    write(thin/'remote-preview.json',dict(task=task,implementation_commit=source,url=url,asset_base=base,asset_commit=assets['host_commit'],files=assets['files'],human_playtests=0,production_admitted=False))
    site=publish(thin,'site/launchers/'+prefix,'Publish Graph Block Module technical pilot and manual play',out/'thin-publication.json')
    result=dict(url=url,asset_base=base,source_commit=source,asset_commit=assets['host_commit'],launcher_commit=site['host_commit'],build_id=build)
    write(out/'publication.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--media',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.play,a.media,a.out)
