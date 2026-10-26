"""Publish this experiment through the existing immutable preview host."""
import argparse,json,shutil
from pathlib import Path
from pcg.tools.publish_woven_preview import publish,HOST
from pcg.map_directed.thin_preview import build as thin_build
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

TASK='MAPGEN-REAL-SHAPE-01'
def run(play,media,out):
    play=Path(play).resolve();media=Path(media).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    if(out/'publication.json').exists():raise ValueError('immutable_publication_exists')
    result=json.loads((media/'results.json').read_text());source=result['source_commit'];m=json.loads((play/'overlay-manifest.json').read_text());build=m['overlay']['sha256'][:12]
    stage=out/'assets';stage.mkdir(exist_ok=True)
    for p in media.iterdir():
        if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:shutil.copy2(p,stage/p.name)
    pack='index.'+build+'.pck';shutil.copy2(play/m['overlay']['pack'],stage/pack);shutil.copy2(play/'overlay-manifest.json',stage/'overlay-manifest.json')
    report=media/('report-reviewed.html'if(media/'report-reviewed.html').exists()else'report.html')
    write(stage/'build-info.json',dict(task=TASK,algorithm_source_commit=source,build_id=build,report_sha256=file_sha(report),
        scope='Five fixed-topology eight-Macro maps; real shape/action CSP; 30 nominal + 30 perturbed routes and 60 paired old-layout routes; full failures retained; no stable superiority claim',
        production_admitted=False,human_fun='unreviewed'))
    if(out/'assets-publication.json').exists():assets=json.loads((out/'assets-publication.json').read_text())
    else:assets=publish(stage,'artifacts/'+TASK+'/'+source+'/'+build,'Archive real-shape spatial search maps, paired failures and native movies [skip ci]',out/'assets-publication.json')
    base='https://raw.githubusercontent.com/'+HOST+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+source+'/'+build
    thin=out/'thin';thin_build(play,base,thin);page=report.read_text()
    for p in stage.iterdir():page=page.replace('"'+p.name+'"','"'+base+'/'+p.name+'"')
    (thin/'report.html').write_text(page);url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+source+'/'+build+'/'
    write(thin/'remote-preview.json',dict(task=TASK,url=url,source_commit=source,asset_commit=assets['host_commit'],asset_base=base,files=assets['files'],production_admitted=False))
    launcher=publish(thin,'site/launchers/'+TASK+'/'+source+'/'+build,'Publish real Macro shape/action search playable and complete negative-result comparison',out/'thin-publication.json')
    final=dict(**launcher,url=url,source_commit=source,asset_commit=assets['host_commit'],asset_base=base,build_id=build);write(out/'publication.json',final);print(json.dumps(final),flush=True);return final

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--media',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.play,a.media,a.out)
