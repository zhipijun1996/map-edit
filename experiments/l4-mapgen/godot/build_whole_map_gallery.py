#!/usr/bin/env python3
"""Lay out unchanged Godot screenshots and actual prototype SVGs for comparison."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

LAB = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8090/experiments/l4-mapgen')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    report = json.loads((output / 'report.json').read_text())
    assert report.get('all_passed') and len(report['cases']) == 9
    names = {'plains': '风铃平原 · 当前实装', 'forest': '荆棘森林 · 默认 v15', 'forest-v18': '荆棘森林 · v18 开发候选'}
    styles = '''*{box-sizing:border-box}body{margin:0;background:#efeee8;color:#263931;font-family:Arial,"Noto Sans CJK SC",sans-serif}main{width:1680px;margin:auto}.sheet{padding:32px 40px;background:#efeee8}h1{font-size:34px;margin:0 0 10px}p{font-size:18px;line-height:1.6;margin:0 0 24px;color:#56665c}figure{margin:0 0 24px;background:#fff;border:1px solid #c9cebf;border-radius:8px;overflow:hidden}figcaption{padding:16px 22px;font-size:23px;display:flex;justify-content:space-between}figcaption small{font-size:17px;color:#667466}img{display:block;width:1600px;height:900px;object-fit:contain;background:#15272c}.proxy{width:1600px;height:760px;background:#f2f3eb;display:flex;align-items:center;justify-content:center}.proxy svg{width:94%;height:94%}a{color:inherit}nav{padding:30px;font-size:20px}'''
    sections = []
    for label, title in names.items():
        cards = []
        for suffix in ['00', '03', '04']:
            row = next(c for c in report['cases'] if c['id'] == label + '-' + suffix)
            receipt = row['receipt']
            source = f'{label}-{suffix}/whole-map.png'
            cards.append(f'<figure><figcaption><b>Seed l4-baseline-{suffix}</b><small>地图 2 · {html.escape(receipt["family"])} · {receipt["area_count"]} 区域</small></figcaption><a href="{source}"><img src="{source}" loading="eager" alt="{title} Seed {suffix} 整图"></a></figure>')
        sections.append(f'<section class="sheet" id="{label}"><h1>{title}</h1><p>真实 Godot 整图截图 · 每张 4096 × 2304 · 各自适应整图，隐藏 HUD。只改变观察镜头，不代表新 A/B/C 已实装。</p>{"".join(cards)}</section>')
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1800, 'height': 1200}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(args.base_url + '/viewer.html')
        page.wait_for_function("document.querySelector('#status').textContent.includes('240')")
        for region, title in [('plains', '平原'), ('forest', '森林')]:
            page.locator('#region').select_option(region)
            page.locator('#seed').select_option('0')
            cards = []
            for i, name in enumerate(['A', 'B', 'C']):
                svg = page.locator('article.algorithm').nth(i).locator('[data-stage="spatial"] svg').evaluate('(n)=>new XMLSerializer().serializeToString(n)')
                (output / f'prototype-{region}-{name}-0.svg').write_text(svg)
                label = {'A': 'A · 图改写 + 回溯', 'B': 'B · 循环图 + ASP', 'C': 'C · 拓扑 MAP-Elites + 嵌入'}[name]
                cards.append(f'<figure><figcaption><b>{label}</b><small>Seed 0 · 18 节点 · 物理未验证</small></figcaption><div class="proxy">{svg}</div></figure>')
            sections.append(f'<section class="sheet" id="prototype-{region}"><h1>新算法 · {title}整图空间布局</h1><p>这是原型实际输出的占用掩码与连接通道：相同 Seed / 合成内容。没有贴入游戏场景，不是可玩地图截图。</p>{"".join(cards)}</section>')
        document = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>整图生成效果 · Map Notes</title><style>' + styles + '</style><nav>当前实装：<a href="#plains">平原</a> · <a href="#forest">森林 v15</a> · <a href="#forest-v18">森林 v18候选</a>　新算法：<a href="#prototype-plains">平原布局</a> · <a href="#prototype-forest">森林布局</a></nav><main>' + ''.join(sections) + '</main></html>'
        (output / 'gallery.html').write_text(document)
        relative = output.relative_to(LAB).as_posix()
        page.goto(args.base_url + '/' + relative + '/gallery.html')
        page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        for section in ['plains', 'forest', 'forest-v18', 'prototype-plains', 'prototype-forest']:
            page.locator('#' + section).screenshot(path=str(output / (section + '-comparison.png')))
        assert not errors, errors
        screenshots = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*-comparison.png')}
        (output / 'gallery-receipt.json').write_text(json.dumps({'kind': 'actual Chromium contact sheet; source Godot PNG bytes unchanged',
            'browser': browser.version, 'page_errors': errors, 'source_game_commit': report['source_game_commit'], 'screenshots': screenshots}, indent=2))
        browser.close()
    print('GALLERY PASS: nine native images, six actual algorithm SVGs, five comparison sheets.')


if __name__ == '__main__':
    main()
