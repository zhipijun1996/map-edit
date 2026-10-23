"""Freeze playable input witnesses, honest review labels, figures and editor drafts."""
import json,copy,hashlib
from pathlib import Path
from simulator import ROOT,Simulator
from synthesis import replay_case,actual_word

def run():
    source=ROOT/'results/composable-evaluation-final';dest=ROOT/'delivery/composable-v2';dest.mkdir(parents=True,exist_ok=True)
    entries=json.loads((source/'selected.json').read_text());summary=json.loads((source/'summary.json').read_text());cases=[]
    names={'ground_jump':'起跳','air_jump':'空跳','recoil':'反冲','hook_hang':'挂点','hook_bounce':'弹点','anchor_jump':'离钩跳','wall_jump':'蹬墙'}
    for i,(e,score) in enumerate(zip(entries,summary['modules'])):
        c=replay_case(e['case'],e['result']);c['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested']) for f in e['result']['frames']]
        c['title']=f'{i+1:02d} '+ ' → '.join(names[x] for x in e['actual_word'])
        warnings=[]
        if score['remaining_shortcuts']:warnings.append('已发现较少动作/能力的替代解')
        if score['scores']['feedback/mild']['success']<18:warnings.append('容错待优化')
        c['review_warnings']=warnings
        if warnings:c['title']+='【'+ '；'.join(warnings)+'】'
        c['review_status']='awaiting_human_playtest';c['quality_evidence']=score
        cases.append(c)
    sim=Simulator(ROOT/'results/composable-delivery-v2');rs=sim.run(cases,'recorded-input-replay')
    if any(not r['ok'] or actual_word(r)!=tuple(e['actual_word']) for r,e in zip(rs,entries)):raise RuntimeError('Recorded input replay differs from clean witness')
    data=dict(schema='pcg/playable-candidates/v2',generation='offline; browser only manual play or real-input replay',physics_source='12f6cb006d7119598e3235f4ca4f7323e4c9d092',cases=cases)
    (ROOT/'prototype/godot/modules_v2.json').write_text(json.dumps(data,ensure_ascii=False));(dest/'modules_v2.json').write_text(json.dumps(data,ensure_ascii=False))
    (dest/'replay-summary.json').write_text(json.dumps(dict(cases=len(cases),success=sum(r['ok'] for r in rs),settled_grounded=all(r['frames'][-1]['grounded'] and abs(r['frames'][-1]['vx'])<=1 and abs(r['frames'][-1]['vy'])<=1 for r in rs)),indent=2))
    # Map Notes drawings remain review-only. Preserve exact witness caps without
    # declaring them proven minimum requirements or equating difficulty with AI scores.
    notes=dest/'mapnotes';notes.mkdir(exist_ok=True)
    for c,r in zip(cases,rs):
        dx=100-min(p[0] for p in c['platforms']);dy=140-min(p[1] for p in c['platforms']);objects=[]
        def obj(typ,x,y,w,h,**kw):objects.append(dict(id=f'{c["id"]}-{len(objects)}',type=typ,x=x+dx,y=y+dy,w=w,h=h,rotation=0,label='',note='')|kw)
        for j,(x,y,w,h) in enumerate(c['platforms']):obj('terrain',x,y,w,h,note='可攀墙' if j in c.get('wall_platform_indices',[]) else ('单向落台' if j in c.get('one_way_platform_indices',[]) else ''))
        for rect in c['hazards']:obj('hazard',*rect,note='研究危险包络；未连接正式荆棘伤害消费者')
        for h in c['hooks']:obj('hookHang' if h['kind']=='hang' else 'hookBounce',h['x']-19,h['y']-19,38,38)
        obj('entry',c['spawn'][0]-12,c['spawn'][1]-18,24,36);obj('exit',*c['goal'])
        points=[dict(x=f['x']+dx,y=f['y']+dy,action=', '.join(e['type'] for e in f['accepted']) or ('落地' if f['grounded'] else '空中')) for i,f in enumerate(r['frames']) if i%3==0 or f['accepted'] or i==len(r['frames'])-1]
        obj('route',0,0,0,0,points=points,duration=len(r['frames'])/60,mode='once')
        doc=dict(schema='gunman-rush-level-sketch/v1',id=c['id'],title=c['title'],description='能力组合生成研究候选；需真人试玩；修改几何或能力后验证收据失效。',constraints='保留完整身体净空及真实资源恢复；能力必要性尚无完备证明。',objects=objects,canvas=dict(width=max(1600,max(p[0]+p[2] for p in c['platforms'])+dx+100),height=max(900,max(p[1]+p[3] for p in c['platforms'])+dy+100),units='world',positionPrecision='exact'),capabilityRequirements=dict(version=1,status='unspecified',allOf=[],anyOfGroups=[],note='能力快照不是最低能力条件，见researchEvidence'),difficulty=dict(version=1,scale='gunman-rush/module-difficulty/v1',score=None,note='待真人校准'),intent=dict(operation='new_module'),updatedAt='2026-10-23T00:00:00Z',source=dict(repository='https://github.com/zhipijun1996/gunman-rush',commit=data['physics_source'],path='pcg-research/composable',moduleId=c['id'],editorTranslation=dict(x=dx,y=dy),researchOnly=True),researchEvidence=dict(witnessCapabilities=c['capabilities'],actionWord=c['word'],quality=c['quality_evidence'],inputProgram=c,validationScope='real Motor + static whole-body sweeps; no human or production-consumer approval'))
        (notes/(c['id']+'.mapnote.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2))
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axes=plt.subplots(4,5,figsize=(19,12))
    for i,(ax,c,r) in enumerate(zip(axes.flat,cases,rs)):
        for key,color in [('platforms','#657b87'),('hazards','#d45064')]:
            for x,y,w,h in c[key]:ax.add_patch(Rectangle((x,y),w,h,color=color,alpha=.75))
        for h in c['hooks']:ax.scatter(h['x'],h['y'],c='#d6a829',marker='o' if h['kind']=='hang' else '^',s=35)
        ax.plot([f['x'] for f in r['frames']],[f['y'] for f in r['frames']],color='#168b9a',lw=1.8)
        gx,gy,gw,gh=c['goal'];ax.add_patch(Rectangle((gx,gy),gw,gh,fill=False,color='#30a46c',lw=2))
        xs=[c['spawn'][0],gx,*[f['x'] for f in r['frames']]];ys=[c['spawn'][1],gy,*[f['y'] for f in r['frames']]]
        ax.set_xlim(min(xs)-80,max(xs)+100);ax.set_ylim(max(ys)+80,min(ys)-80);ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_title(f'{i+1:02d} C{c["combo_index"]}: '+ '/'.join(c['word']),fontsize=7,wrap=True)
    fig.suptitle('20 generated candidates / real Godot input replays / human fun unverified');fig.tight_layout();fig.savefig(dest/'modules.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));labels=['Clean','Mild (1f,2deg)','Moderate (3f,6deg)']
    for offset,policy,color in [(-.18,'fixed','#718096'),(.18,'feedback','#168b9a')]:
        vals=[summary['pooled'][policy+'/'+x]['success']/summary['pooled'][policy+'/'+x]['trials'] for x in ('clean','mild','moderate')]
        bars=ax.bar([i+offset for i in range(3)],vals,.36,label=policy,color=color)
        ax.bar_label(bars,labels=[f'{v:.1%}' for v in vals])
    ax.set_xticks(range(3),labels);ax.set_ylim(0,1.16);ax.legend();ax.set_ylabel('Automated stable-exit success');ax.set_title('Paired inputs: same geometry, same shared-command noise seeds');fig.tight_layout();fig.savefig(dest/'robustness.png',dpi=150);plt.close(fig)
    print('Frozen and physically replayed',len(cases),'candidates')
if __name__=='__main__':run()
