"""Reuse the immutable preview host; stage verified media with hard links."""
import argparse,json,os
from pathlib import Path
from pcg.tools.publish_woven_preview import publish,HOST
from pcg.map_directed.thin_preview import build as thin_build
from pcg.map_directed.run import write
TASK='MAPGEN-LIBRARY-FEED-01'
def run(play,media,out):
 play=Path(play).resolve();media=Path(media).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 if(out/'publication.json').exists():raise ValueError('immutable_publication_exists')
 result=json.loads((media/'results.json').read_text());source=result['source_commit'];m=json.loads((play/'overlay-manifest.json').read_text());build=m['overlay']['sha256'][:12]
 stage=out/'assets';stage.mkdir(exist_ok=True)
 def link(a,b):
  if not b.exists():os.link(a,b)
 for p in media.iterdir():
  if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:link(p,stage/p.name)
 link(play/m['overlay']['pack'],stage/('index.'+build+'.pck'));link(play/'overlay-manifest.json',stage/'overlay-manifest.json')
 write(stage/'build-info.json',dict(task=TASK,source_commit=source,library_versions=94,source_routes=121,whole_map_routes=12,passed=result['total_passed'],unique_parent_versions=result['unique_versions_placed'],production_admitted=False,human_fun='unreviewed'))
 assets=json.loads((out/'assets-publication.json').read_text())if(out/'assets-publication.json').exists()else publish(stage,'artifacts/'+TASK+'/'+source+'/'+build,'Archive all three current-library maps, failures and exact native movies [skip ci]',out/'assets-publication.json')
 base='https://raw.githubusercontent.com/'+HOST+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+source+'/'+build
 thin=out/'thin';thin_build(play,base,thin);page=(media/'report.html').read_text()
 for p in stage.iterdir():page=page.replace('"'+p.name+'"','"'+base+'/'+p.name+'"')
 (thin/'report.html').write_text(page);url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+source+'/'+build+'/'
 write(thin/'remote-preview.json',dict(task=TASK,url=url,source_commit=source,asset_base=base,asset_commit=assets['host_commit'],files=assets['files'],production_admitted=False))
 launcher=publish(thin,'site/launchers/'+TASK+'/'+source+'/'+build,'Publish current 94-version Module library whole-map experiment and honest failure comparison',out/'thin-publication.json')
 final=dict(**launcher,url=url,asset_base=base,asset_commit=assets['host_commit'],source_commit=source,build_id=build);write(out/'publication.json',final);print(json.dumps(final));return final
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--media',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.play,a.media,a.out)
