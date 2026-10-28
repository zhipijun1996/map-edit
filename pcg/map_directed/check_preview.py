"""Actual Chromium Godot consumer: manual input and three completed map routes."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def check(url,out):
    out=Path(out)
    if out.exists():raise ValueError('keep_previous_browser_evidence')
    out.mkdir(parents=True);events=[];routes=[]
    with sync_playwright()as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,
            args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1280,'height':720})
        page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)))
        page.on('pageerror',lambda e:events.append(dict(type='pageerror',text=str(e))))
        try:
            page.goto(url,wait_until='domcontentloaded')
            page.wait_for_function('window.__pcgLabStateV3?.case_count===3 && window.__pcgLabStateV3?.map',timeout=90000)
            before=page.evaluate('window.__pcgLabStateV3')
            page.mouse.click(180,600);page.keyboard.down('d');page.wait_for_timeout(350);page.keyboard.up('d')
            moved=page.evaluate('window.__pcgLabStateV3')
            assert moved['position'][0]>before['position'][0]+10,'manual movement did not reach real Motor'
            page.keyboard.press('r')
            page.wait_for_timeout(300)
            for index in range(3):
                if index:
                    page.goto(url+('?case='if'?'not in url else'&case=')+str(index),wait_until='domcontentloaded')
                    page.wait_for_function(f'window.__pcgLabStateV3?.selected==={index} && window.__pcgLabStateV3?.map',timeout=90000)
                page.mouse.click(960,55)
                page.wait_for_function('window.__pcgLabStateV3?.mode==="replay"',timeout=10000)
                page.wait_for_function('window.__pcgLabStateV3?.finished===true',timeout=60000)
                state=page.evaluate('window.__pcgLabStateV3')
                assert state['safe']and state['hp']==5 and state['stable_frames']>=6,state
                assert state['map']['ok'],state['map']
                assert state['map']['wallet_balance']==(0 if index==0 else 12)
                assert not state['map']['missing_seams']and not state['map']['missing_bells']
                routes.append(state);page.screenshot(path=str(out/f'route-{index+1}.png'))
                print('browser route passed',index,state['frame'],flush=True)
            errors=[x for x in events if x['type']in ['error','pageerror']or'SCRIPT ERROR'in x['text']]
            assert not errors,errors
            result=dict(status='passed',url=url,browser=browser.version,
                manual_input=dict(before=before['position'],after=moved['position']),routes=routes,
                human_playtests=0,scope='actual software-WebGL Godot; three scripted replays and manual key input, no human fun/device approval')
            (out/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        except Exception as e:
            (out/'failure.json').write_text(json.dumps({'error':str(e),'routes':routes},ensure_ascii=False,indent=2));raise
        finally:
            (out/'console.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n');browser.close()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');a=p.parse_args();check(a.url,a.out)
