"""Real WebGL/keyboard consumer smoke, separately scoped from native tours."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright


def check(url,out,local_play=None,dependencies=None,expected_nodes=7,expected_platforms=96,expected_gates=0,expected_entry='west'):
    out=Path(out)
    if out.exists():raise ValueError('immutable_browser_result_exists')
    out.mkdir(parents=True);events=[]
    with sync_playwright()as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=[
            '--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1280,'height':720},accept_downloads=True)
        page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)))
        page.on('pageerror',lambda e:events.append(dict(type='pageerror',text=str(e))))
        if local_play:
            from pcg.prototype.packaging_v3.overlay_pack import BASE_URL,ENGINE_PREFIX
            prefix=url.rsplit('/',1)[0]+'/'
            def local(route):
                path=Path(local_play)/route.request.url.split('/')[-1].split('?')[0]
                route.fulfill(path=path,headers={'Access-Control-Allow-Origin':'*'})
            page.route(prefix+'**',local)
            for remote,path,mime in [
                ('https://zhipijun1996.github.io'+BASE_URL,Path(dependencies)/'base.pck','application/octet-stream'),
                ('https://zhipijun1996.github.io'+ENGINE_PREFIX+'.js',Path(dependencies)/'index.js','application/javascript'),
                ('https://zhipijun1996.github.io'+ENGINE_PREFIX+'.wasm',Path(dependencies)/'index.wasm','application/wasm')]:
                page.route(remote,lambda route,request,path=path,mime=mime:route.fulfill(path=path,content_type=mime,headers={'Access-Control-Allow-Origin':'*'}))
        try:
            page.goto(url,wait_until='domcontentloaded')
            page.wait_for_function('window.__r2ManualState?.manual_input_armed===true',timeout=120000)
            before=page.evaluate('window.__r2ManualState')
            assert before['nodes']==expected_nodes and before['state_gates']==expected_gates and before['platforms']==expected_platforms,before
            assert before['visited_nodes']==[expected_entry],before
            page.screenshot(path=str(out/'ready.png'))
            page.locator('canvas').focus()
            page.keyboard.down('d')
            # Loading/compiling the public WebGL resources can delay frame
            # delivery. Observe actual movement while held, not an 80ms pulse.
            page.wait_for_function('start=>window.__r2ManualState.position[0]>start+5',arg=before['position'][0],timeout=10000)
            page.keyboard.down('Space');page.wait_for_timeout(80)
            page.keyboard.up('Space');page.keyboard.up('d')
            moved=page.evaluate('window.__r2ManualState')
            assert moved['position'][0]>before['position'][0]+5,(before,moved)
            page.mouse.move(100,650);page.mouse.down();page.wait_for_timeout(40);page.mouse.up()
            page.wait_for_timeout(100)
            page.keyboard.press('r');page.wait_for_function('window.__r2ManualState?.frame<15',timeout=10000)
            page.wait_for_function('window.__r2ManualState?.manual_input_armed===true',timeout=10000)
            reset=page.evaluate('window.__r2ManualState')
            assert abs(reset['position'][0]-before['position'][0])<1,reset
            page.keyboard.press('m');page.wait_for_timeout(100)
            page.screenshot(path=str(out/'whole-map-browser.png'))
            errors=[e for e in events if e['type']in ['error','pageerror']or 'SCRIPT ERROR'in e['text']]
            assert not errors,errors
            result=dict(status='passed',url=url,browser=browser.version,local_transport=bool(local_play),
                original_keyboard_input=dict(before=before,moved=moved,reset=reset),
                scope='Real manual WebGL scene, movement/jump/shoot/retry/map-view smoke; native tours validated separately',
                human_playtests=0,human_fun='unverified')
            (out/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        except Exception as e:
            (out/'failure.json').write_text(json.dumps({'error':str(e)},ensure_ascii=False,indent=2));raise
        finally:
            (out/'console.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n');browser.close()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out',type=Path)
    p.add_argument('--local-play',type=Path);p.add_argument('--dependencies',type=Path)
    a=p.parse_args();check(a.url,a.out,a.local_play,a.dependencies)
