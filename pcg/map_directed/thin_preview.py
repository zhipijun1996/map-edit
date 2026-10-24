"""Official Engine transport with an immutable, byte-verified external PCK.

This keeps historical Pages files and the existing site-size gate unchanged.
It does not change the PCK or relax its physical/content verification.
"""
import argparse
import json
from pathlib import Path


def build(play,asset_base,out):
    play=Path(play);out=Path(out)
    if out.exists():raise ValueError('immutable_thin_launcher_exists')
    out.mkdir(parents=True)
    manifest=json.loads((play/'overlay-manifest.json').read_text())
    old_name=manifest['overlay']['pack'];name='index.'+manifest['overlay']['sha256'][:12]+'.pck'
    page=(play/'index.html').read_text().replace(old_name,name)
    loader='''async function loadExactPack(){
 const response=await fetch(PACK_URL);if(!response.ok)throw Error('Map pack HTTP '+response.status);
 const bytes=await response.arrayBuffer();
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
 if(bytes.byteLength!==PACK_BYTES||digest!==PACK_SHA)throw Error('Map pack identity mismatch');
 window.__overlayTransport.external_pack_verified={url:PACK_URL,bytes:bytes.byteLength,sha256:digest};
 return engine.preloadFile(bytes,config.mainPack);
}
'''.replace('PACK_URL',json.dumps(asset_base+'/'+name)).replace('PACK_BYTES',str(manifest['overlay']['bytes'])).replace('PACK_SHA',json.dumps(manifest['overlay']['sha256']))
    page=page.replace('Promise.all([engine.init',loader+'Promise.all([engine.init')
    old=']).then(()=>engine.startGame())'
    if page.count(old)!=1:raise ValueError('unexpected_official_overlay_startup')
    page=page.replace(old,",loadExactPack()]).then(()=>engine.start({args:['--main-pack',config.mainPack,...config.args]}))")
    (out/'index.html').write_text(page)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',type=Path,required=True);p.add_argument('--asset-base',required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(a.play,a.asset_base,a.out)
