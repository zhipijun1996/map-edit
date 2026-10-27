"""Publish this immutable Map review through the existing binary/Pages host."""
import argparse,json,os,shutil
from pathlib import Path
from pcg.tools.publish_woven_preview import publish,HOST
from pcg.map_directed.thin_preview import build as thin_build
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
TASK='MAPGEN-GRAPH-MAP-01'

def run(play,media,out):
    play,media,out=map(lambda p:Path(p).resolve(),[play,media,out]);out.mkdir(parents=True,exist_ok=False)
    source=json.loads((media/'results.json').read_text())['source_commit'];m=json.loads((play/'overlay-manifest.json').read_text());build=m['overlay']['sha256'][:12];stage=out/'assets';stage.mkdir()
    for p in media.iterdir():
        if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:os.link(p,stage/p.name)
    name='index.'+build+'.pck';os.link(play/m['overlay']['pack'],stage/name);os.link(play/'overlay-manifest.json',stage/'overlay-manifest.json')
    write(stage/'build-info.json',dict(task=TASK,source_commit=source,build_id=build,scope='22 Macro / 24 actual Module components; real whole Map, not full regional or stable multi-Seed acceptance',physics='10/10 plus9 finite reverse probes',independent_seed_audit='0/3 spatial feasible within budget',human_fun='UNREVIEWED',production_admitted=False))
    assets=publish(stage,'artifacts/'+TASK+'/'+source+'/'+build,'Archive graph-driven Map and exact native route movies [skip ci]',out/'assets-publication.json')
    base='https://raw.githubusercontent.com/'+HOST+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+source+'/'+build
    thin=out/'thin';thin_build(play,base,thin);page=(media/'report.html').read_text()
    for p in stage.iterdir():page=page.replace('"'+p.name+'"','"'+base+'/'+p.name+'"')
    (thin/'report.html').write_text(page);url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+source+'/'+build+'/'
    write(thin/'remote-preview.json',dict(task=TASK,url=url,source_commit=source,asset_commit=assets['host_commit'],asset_base=base,files=assets['files'],production_admitted=False))
    launcher=publish(thin,'site/launchers/'+TASK+'/'+source+'/'+build,'Publish same-graph Map prototype, videos and explicit design failures',out/'thin-publication.json')
    result=dict(**launcher,url=url,source_commit=source,asset_commit=assets['host_commit'],asset_base=base,build_id=build);write(out/'publication.json',result);print(json.dumps(result),flush=True);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--media',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.play,a.media,a.out)
