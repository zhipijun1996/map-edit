"""Render actual Map Notes R2 spatial SVGs and check the dataset switch.

Start the repository HTTP server first. Optional Playwright + Chromium required.
Route overlays are measured initial approaches, not prescribed mission chains.
"""
import argparse
import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/region-network-v2'


def main(url):
    runs = json.loads((OUT / 'runs.json').read_text())['runs']
    cards = {'plains': [], 'forest': []}
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1080})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(url + '/experiments/l4-mapgen/viewer.html?dataset=region-network-v2')
        page.wait_for_function("document.querySelector('#status').textContent.includes('40')")
        assert page.locator('article.algorithm').count() == 1
        for region in cards:
            for seed in ['0', '2']:
                page.locator('#region').select_option(region)
                page.locator('#seed').select_option(seed)
                page.locator('#view').select_option('spatial')
                assert page.locator('[data-stage]:visible').count() == 1
                run = next(r for r in runs if r['region'] == region and r['seed'] == seed)
                svg = page.locator('[data-stage="spatial"] svg')
                # Use the actual spatial viewer and corridor geometry. Color
                # two measured routes; do not invent or straighten connections.
                markup = svg.evaluate('''(svg, run) => {
                    const clone=svg.cloneNode(true), g=run.exploration_graph;
                    const paths=run.regional_diagnostics.first_visit_routes_to_forecourt;
                    const pair=(a,b)=>[a,b].sort().join('|');
                    const routes=paths.map(p=>new Set(p.nodes.slice(1).map((n,i)=>pair(p.nodes[i],n))));
                    const edges=new Map(g.edges.map(e=>[e.id,e]));
                    const groups=[...clone.querySelectorAll('g.edge')];
                    run.layout.corridors.forEach((c,i)=>{
                        const e=edges.get(c.edges[0]); if(!e)return;
                        const k=pair(e.from,e.to), a=routes[0].has(k), b=routes[1].has(k);
                        if(a||b){const line=groups[i].querySelector('polyline');
                            line.setAttribute('stroke',a&&b?'#82598b':a?'#16857d':'#3879ca');
                            line.setAttribute('stroke-width','3');}
                    });
                    // Short room IDs remain readable; full landmark names are
                    // printed next to the map in the generated gallery.
                    const labels=new Map(g.nodes.map(n=>[n.id,n]));
                    [...clone.querySelectorAll('g.room')].forEach((room,i)=>{
                        const id=run.layout.rooms[i].node_id??run.layout.rooms[i].node, n=labels.get(id);
                        const text=room.querySelector('text');
                        if(text){text.textContent=n.role==='start'?'入口':n.role==='boss'?'Boss':n.role==='prep'?'前庭':id;
                            text.setAttribute('font-size','8');}
                    });
                    // The full inspectable data stays in runs.json / the live
                    // viewer; static figures only need short object tooltips.
                    clone.querySelectorAll('g[role="button"]>title').forEach(t=>{
                        t.textContent=t.parentElement.getAttribute('aria-label');
                    });
                    return new XMLSerializer().serializeToString(clone);
                }''', run)
                (OUT / f'{region}-{seed}-spatial.svg').write_text(markup)
                names = {n['id']: n['label'] for n in run['exploration_graph']['nodes']}
                landmarks = ' · '.join(f'{n} {names[n]}' for n in run['exploration_graph']['landmarks'])
                paths = run['regional_diagnostics']['first_visit_routes_to_forecourt']
                title = ('风铃平原' if region == 'plains' else '荆棘森林') + f' · Seed {seed}'
                cards[region].append(f'<article><h2>{title}</h2>{markup}<p>{html.escape(landmarks)}</p>'
                    f'<p>入口 → 前庭：最短路线 {len(paths[0]["nodes"])-1} 段；另一条路线 {len(paths[1]["nodes"])-1} 段。'
                    f'共 {len(run["exploration_graph"]["nodes"])} 个空间代理。</p></article>')
        assert not errors, errors
        styles = '''body{margin:0;padding:30px;background:#f4f3ed;color:#303a35;font-family:"Noto Sans CJK SC",sans-serif}
            h1{font-size:24px;margin:0 0 12px}header p{font-size:15px;line-height:1.8;margin:6px 0}
            main{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}
            article{background:#fafaf6;border:1px solid #d9dfd0;border-radius:12px;padding:18px;min-width:0}
            h2{font-size:19px;margin:0 0 8px}article>svg{display:block;width:100%;height:600px;background:#f2f3eb}
            article p{font-size:12px;line-height:1.8;margin:10px 0 0}svg text{font-family:inherit}
            strong{color:#976043}small{font-size:13px}'''
        for region, contents in cards.items():
            title = '区域网 R2：多路线结构修订'
            gallery = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>' + title + '</title><style>' + styles
                + '</style><header><h1>' + title + '</h1><p><strong>抽象空间布局，未实例化真实游戏模块；物理可玩与探索趣味尚未验证。</strong></p>'
                + '<p><span style="color:#16857d">绿色：测得的最短路线</span> · <span style="color:#3879ca">蓝色：另一条初访路线</span>'
                + ' · <span style="color:#82598b">紫色：共享段</span> · 金色：奖励路线 · 红色：能力 / 状态锁</p>'
                + '<small>路线在网络生成后测量，没有预铺横向通关链。两条示例路线均通往前庭；最后的 Boss 门允许形成瓶颈。无真实玩法截图。</small>'
                + '</header><main>' + ''.join(contents) + '</main></html>')
            (OUT / f'{region}-gallery.html').write_text(gallery)
            page.goto(url + f'/experiments/l4-mapgen/results/region-network-v2/{region}-gallery.html')
            page.evaluate('document.fonts.ready')
            page.screenshot(path=str(OUT / f'{region}-comparison.png'), full_page=True)
        page.goto(url + '/experiments/l4-mapgen/viewer.html?dataset=v1')
        page.wait_for_function("document.querySelector('#status').textContent.includes('240')")
        assert page.locator('article.algorithm').count() == 4
        (OUT / 'browser-receipt.json').write_text(json.dumps({'browser': browser.version,
            'status': 'passed', 'checks': ['R2 40 records', 'one R2 card', 'four region/seed spatial exports',
            'spatial view filter', 'v1 switch retains 240 records / four cards'], 'page_errors': errors,
            'scope': 'real local Chromium / saved spatial geometry, no game physics'}, indent=2))
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    main(parser.parse_args().url.rstrip('/'))
