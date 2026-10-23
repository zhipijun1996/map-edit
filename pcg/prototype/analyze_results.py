#!/usr/bin/env python3
from pathlib import Path
import json,collections,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
ROOT=Path(__file__).resolve().parents[1]

def main():
 s=json.loads((ROOT/'results/holdout-v2/summary.json').read_text())
 noise=json.loads((ROOT/'results/deliverables-v2/robustness-table.json').read_text())
 pooled=[]
 for k in ('recoil','grapple'):
  for level in ('mild','moderate'):
   rows=[r for r in noise if r['kind']==k and r['level']==level]
   pooled.append(dict(kind=k,level=level,success=sum(r['ok'] for r in rows),n=len(rows),unique_physical_modules=4,perturbations_per_module=30))
 (ROOT/'results/deliverables-v2/pooled-robustness.json').write_text(json.dumps(pooled,indent=2))
 fig,axs=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
 for i,k in enumerate(('recoil','grapple')):
  rows=[r for r in s['rows'] if r['kind']==k];xx=[j+(i-.5)*.28 for j in range(3)]
  axs[0].bar(xx,[r['feasible']/r['proposal_budget']*100 for r in rows],width=.27,label=k)
 axs[0].set_xticks(range(3),['A: action','B: dual archive','C: + landing CP'])
 axs[0].set_ylabel('Valid outputs / proposal budget (%)');axs[0].set_ylim(0,100);axs[0].legend();axs[0].set_title('One pilot run; 96 requests per group')
 for i,k in enumerate(('recoil','grapple')):
  rows=[r for r in pooled if r['kind']==k];xx=[j+(i-.5)*.28 for j in range(2)]
  axs[1].bar(xx,[r['success']/r['n']*100 for r in rows],width=.27,label=k)
 axs[1].set_xticks(range(2),['timing +/-1f, aim +/-2 deg','timing +/-3f, aim +/-6 deg'])
 axs[1].set_ylabel('Perturbed witness success (%)');axs[1].set_ylim(0,100);axs[1].set_title('4 physical modules per kind; 30 trials each')
 fig.savefig(ROOT/'delivery/figures/pilot.png',dpi=180);plt.close(fig)
 cases=json.loads((ROOT/'results/deliverables-v2/modules.json').read_text())['cases'];rr=json.loads((ROOT/'results/deliverables-v2/delivery-replay.output.json').read_text())['results'];byid={r['id']:r for r in rr}
 for c in cases:
  fig,ax=plt.subplots(figsize=(12,4),layout='constrained')
  for x,y,w,h in c['platforms']:ax.add_patch(Rectangle((x,y),w,h,color='#495d6b'))
  for x,y,w,h in c['hazards']:ax.add_patch(Rectangle((x,y),w,h,color='#dc5a69'))
  for h in c['hooks']:ax.add_patch(Circle((h['x'],h['y']),12,fill=False,edgecolor='#d59813',linewidth=2))
  for key,color in [('goal','#44bf88'),('reward_region','#f5c542')]:
   if key in c:
    x,y,w,h=c[key];ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor=color,linewidth=2))
  fs=byid[c['id']]['frames'];ax.plot([f['x'] for f in fs],[f['y'] for f in fs],color='#1799d0',lw=1.5,label='real Motor trajectory (body center)')
  for f in fs:
   if any(e['type'] in ('shot','hook_contact') for e in f['accepted']):ax.scatter(f['x'],f['y'],c='#a22abb',s=28)
  ax.set_xlim(-100,max(p[0]+p[2] for p in c['platforms'])+50);ax.set_ylim(680,min(0,min(p[1] for p in c['platforms'])-60));ax.set_aspect('equal');ax.set_title(c['id']+' | static overlay, not a recording');ax.legend(fontsize=7)
  ax.set_xlabel('World units');fig.savefig(ROOT/'delivery/figures'/(c['id']+'.png'),dpi=160);plt.close(fig)
 print('Wrote pooled statistics and seven static figures')
if __name__=='__main__':main()
