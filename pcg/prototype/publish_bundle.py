"""Stage a standalone research preview using the existing immutable host byte contract.
No production game changes, no old site deletions, no guard changes.
"""
from pathlib import Path
import hashlib,json,shutil,re,subprocess,html,gzip
ROOT=Path(__file__).resolve().parents[1]
HOST=Path('/workspace/pcg-preview-host')
TASK='PCG-RESEARCH-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def stage():
    web=ROOT/'delivery/web-lean'
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    packhash=sha(web/'index.pck');build=packhash[:12]
    base=Path('previews')/TASK/source/build
    dest=HOST/'site'/base
    if dest.exists():raise RuntimeError('Immutable destination already exists')
    dest.mkdir(parents=True)
    for p in web.iterdir():
        if p.is_file():shutil.copy2(p,dest/p.name)
    name=f'index.{build}.pck';(dest/'index.pck').rename(dest/name)
    page=(dest/'index.html').read_text()
    page=page.replace('"index.pck":',json.dumps(name)+':')
    page=page.replace('"executable":"index",','"executable":"index","mainPack":'+json.dumps(name)+',')
    page=page.replace('</body>','<a href="REPORT.html" style="position:fixed;bottom:4px;left:4px;z-index:50;background:#162332;color:white;padding:5px;font:12px sans-serif">PCG研究报告 · 非正式内容</a></body>')
    (dest/'index.html').write_text(page)
    info=dict(schema='disordered-clock/research-export/v1',source_commit=source,game_source_commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',build_id=build,pack=name,pack_bytes=(dest/name).stat().st_size,scope='standalone research adapter, original production physics; not a production game build',physics_hz=60)
    (dest/'build-info.json').write_text(json.dumps(info,indent=2))
    record={name:dict(sha256=packhash,bytes=info['pack_bytes'],chunks=[])}
    (dest/'index.cache-sw.js').write_text('// Transport integrity metadata for existing host verifier. This is not registered as a service worker.\nconst RESOURCE_MAP = '+json.dumps(record)+';\n')
    # Carry technical sources and readable reports, not heavyweight dependency originals.
    import markdown
    paths=[ROOT/'REPORT.md',ROOT/'README.md',*sorted((ROOT/'research').rglob('*'))]
    paths += [ROOT/'prototype/godot'/n for n in ('ADAPTATION.md','source_provenance.json','asset_licenses_provenance.json')]
    paths += [ROOT/'results/environment.json']
    paths += list((ROOT/'results/holdout-v2').glob('summary.json'))+list((ROOT/'results/deliverables-v2').glob('summary.json'))
    paths += [ROOT/'results/deliverables-v2'/n for n in ('delivery-replay.output.json','modules.json','pooled-robustness.json')]
    paths += [p for p in (ROOT/'delivery').rglob('*') if p.is_file() and p.suffix in ('.md','.json','.png','.mp4') and not any(x in p.parts for x in ('web','web-lean'))]
    paths += [ROOT/'delivery/pcg-research-source-and-data.zip']
    for p in paths:
        if not p.is_file():continue
        rel=p.relative_to(ROOT);q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        if p.suffix=='.md':
            text=p.read_text();text=re.sub(r'\]\(([^\s():]+)\.md\)',r'](\1.html)',text)
            body=markdown.markdown(text,extensions=['tables','fenced_code'])
            q.with_suffix('.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>失序之钟PCG研究</title><style>body{max-width:1080px;margin:30px auto;padding:0 20px;font:16px/1.8 system-ui,sans-serif;color:#172b3a}a{color:#1263a0}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #becbd3;padding:7px}pre{background:#edf2f5;padding:15px;overflow:auto}img{max-width:100%}</style>'+body+'</html>')
    # Explicit standalone-source and license ledger accompanies exported bytes.
    licenses=json.loads((ROOT/'prototype/godot/asset_licenses_provenance.json').read_text())['files']
    for rel,expected in licenses.items():
        p=ROOT/'prototype/godot'/rel
        if sha(p)!=expected:raise RuntimeError('License source drift: '+rel)
        q=dest/'licenses'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    verification=dict(scope='exact exported research PCK; original core code and adapter provenance separately recorded',source_commit=source,build_id=build,pack=name,pack_bytes=info['pack_bytes'],pack_sha256=packhash,reconstructed=False,failed=0)
    files={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
    url='https://zhipijun1996.github.io/gunman-rush-previews/'+base.as_posix()+'/'
    meta=dict(schema_version=1,task=TASK,pr=None,source_commit=source,game_source_commit=info['game_source_commit'],build_id=build,seed='724030–724061; generated validated candidates',entry='standalone-research-scene',scene='res://main.tscn',url=url,pack_verification=verification,validation='Real Godot static swept-body witness + actual browser controls; not production reward/damage, human fun or devices approval.',files=files)
    (dest/'preview.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    (ROOT/'delivery/staged-preview.json').write_text(json.dumps(dict(path=str(dest),url=url,source_commit=source,build_id=build,pack_sha256=packhash),indent=2))
    # Add one link without regenerating or removing old index entries.
    index=HOST/'site/index.html';old=index.read_text();link='<p><a href="'+base.as_posix()+'/">PCG-RESEARCH-01 · 动作生成研究试玩</a> · <a href="'+base.as_posix()+'/REPORT.html">研究报告与实验数据</a></p>'
    index.write_text(old.replace('</body>',link+'</body>') if '</body>' in old else old+link)
    print(json.dumps(dict(path=str(dest),url=url,build=build),ensure_ascii=False))
if __name__=='__main__':stage()
