#!/usr/bin/env python3
"""One-way review export to existing Map Notes v1; never claims game round-trip."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]

def export():
    cases=json.loads((ROOT/'results/deliverables/modules.json').read_text())['cases']
    results=json.loads((ROOT/'results/deliverables/delivery-replay.output.json').read_text())['results']
    byid={r['id']:r for r in results}
    dest=ROOT/'delivery/mapnotes';dest.mkdir(parents=True,exist_ok=True)
    for c in cases:
        result=byid[c['id']]
        xs=[p[0] for p in c['platforms']];ys=[p[1] for p in c['platforms']]
        dx=100-min(xs);dy=140-min(ys)
        objects=[]
        def obj(typ,x,y,w,h,**kw):
            objects.append(dict(id=f"{c['id']}-{len(objects)}",type=typ,x=x+dx,y=y+dy,w=w,h=h,rotation=0,label='',note='') | kw)
        for x,y,w,h in c['platforms']:obj('terrain',x,y,w,h)
        for x,y,w,h in c['hazards']:obj('hazard',x,y,w,h,note='精确静态危险包络；原型以全身扫掠验证，不等于正式伤害消费者')
        for h in c['hooks']:obj('hookHang' if h['kind']=='hang' else 'hookBounce',h['x']-19,h['y']-19,38,38)
        obj('entry',c['spawn'][0]-12,c['spawn'][1]-18,24,36)
        obj('exit',*c['goal'])
        if 'reward_region' in c:obj('reward',*c['reward_region'],note='到达区域；未实现正式奖励交易')
        ps=[]
        for i,f in enumerate(result['frames']):
            if i%3==0 or f['accepted'] or i==len(result['frames'])-1:
                ps.append(dict(x=f['x']+dx,y=f['y']+dy,action='; '.join(e['type']+(':'+e['state'] if 'state'in e else '') for e in f['accepted']) or ('落地' if f['grounded'] else '空中输入')))
        obj('route',0,0,0,0,points=ps,duration=len(result['frames'])/60,mode='once',note='来自真实输入见证轨迹；编辑后原验证即失效')
        doc=dict(schema='gunman-rush-level-sketch/v1',id=c['id'],title=c['id'],description='动作驱动程序生成研究候选；无完整预制Module。真人趣味/设备/正式伤害未验。',constraints='请保留完整身体净空、入口资源、物理版本和动作恢复关系。修改后须重新真实验证。',
            capabilityRequirements=dict(version=1,status='unspecified',allOf=[],anyOfGroups=[],note='最低能力条件未求解，不能把见证使用能力直接声明为必需能力。'),
            difficulty=dict(version=1,scale='gunman-rush/module-difficulty/v1',score=None,note='待真人校准，未把自动成功率换算为1–10分'),intent=dict(operation='new_module'),
            canvas=dict(width=max(1600,max(p[0]+p[2] for p in c['platforms'])+dx+100),height=max(900,max(p[1]+p[3] for p in c['platforms'])+dy+100),units='world',positionPrecision='exact'),
            objects=objects,updatedAt='2026-10-23T00:00:00Z',source=dict(repository='https://github.com/zhipijun1996/gunman-rush',commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',path='pcg-research/generated-candidate',moduleId=c['id'],method='real_motor_trace_synthesis',editorTranslation=dict(x=dx,y=dy),researchOnly=True),
            researchEvidence=dict(witnessCapabilities=(['shot_recoil'] if result['shots'] else [])+(['grapple'] if result['grapples'] else []),inputProgram=c,validation=result|{'frames':[]},trace_file='results/deliverables/delivery-replay.output.json',validation_scope='Static swept-body and real Motor witness only; edits invalidate receipt'))
        (dest/(c['id']+'.mapnote.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2))
    print(f'Exported {len(cases)} Map Notes review drafts to {dest}')
if __name__=='__main__':export()
