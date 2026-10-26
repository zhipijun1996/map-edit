"""Remove rebuildable source images/audio only when their imports are retained.

The rendered resources and scripts remain byte-identical. Real WebGL consumer
validation is still mandatory; this is a transport optimization, not physics.
"""
import argparse,json,sys
from pathlib import Path
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

def build(play,out,game_tools):
    sys.path.insert(0,str(game_tools))
    from check_web_bundle import Pack
    from pcg.prototype.packaging_v3.overlay_pack import write_pack,html,BASE_URL,ENGINE_PREFIX
    play=Path(play);out=Path(out)
    if out.exists():raise ValueError('immutable_trim_output_exists')
    out.mkdir(parents=True);original=json.loads((play/'overlay-manifest.json').read_text());p=play/original['overlay']['pack'];pack=Pack(p)
    files={k:pack.read(k)for k in pack.entries};removed=[]
    for k in list(files):
        if k.endswith(('.png','.mp3','.ogg'))and k+'.import'in files:
            removed.append(dict(path=k,bytes=len(files[k]),sha256=__import__('hashlib').sha256(files[k]).hexdigest(),reason='source bytes only; original .import and engine imported resource retained'));del files[k]
    temp=out/'overlay.pck';m=write_pack(temp,files);name='overlay.'+m['sha256'][:12]+'.pck';temp.rename(out/name);m['pack']=name
    verify=Pack(out/name)
    for k,b in files.items():assert verify.read(k)==pack.read(k)
    result=dict(original,overlay=m,transport_trim=dict(original_pack_sha256=file_sha(p),removed=removed,remaining_entry_bytes_unchanged=True))
    write(out/'overlay-manifest.json',result);page=html(name,m['bytes'],'https://zhipijun1996.github.io'+BASE_URL,original['base']['bytes'],'https://zhipijun1996.github.io'+ENGINE_PREFIX);(out/'index.html').write_text(page)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--out',required=True);p.add_argument('--game-tools',required=True);a=p.parse_args();r=build(a.play,a.out,a.game_tools);print(json.dumps(r['overlay']))
