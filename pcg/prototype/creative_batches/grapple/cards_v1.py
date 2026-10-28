import json
from pathlib import Path
p=Path('pcg/creative-production/grapple')
ideas=[
('anchor-gap','挂点停稳后选择跃出','先看到深沟与挂环，再选择何时从稳定悬挂跃向高岸。','挂接清除先前速度，anchor_jump提供第二次起点；只挂不跃无法上岸。','低入口—沟上固定挂环—较高远岸','move jump grapple','对岸可见箱','不用挂点；挂着等；直接掉落','空间重置起点，主动跃出；区别自动弹射和射击回充。'),
('hang-phase','空中避让后择时出发','悬挂时观察往复齿轮让开的间隙，再跃向其后岸。','挂点提供可无限停稳的观察位，离挂时机决定是否与动态危险相交。','沟上避让位与横穿出发通道的原往复齿轮','move jump grapple','齿轮后岸箱','不等立即跃；入口等待后直跳；绕过齿轮','主动停稳与动态相位绑定，而非仅把anchor-gap延长等待。'),
('jump-refill','耗尽二跳后触环复跳','先用二跳够到挂环，接触后把恢复的二跳留给离环后的高台。','真实接触恢复额外air_jump；离挂anchor_jump后仍要再次air_jump，但弹药不补充。','挂环高于首跳够取范围，高台高于离环单跳','move jump grapple double_jump','最高台箱','省略接触前二跳；省略恢复后二跳；直接双跳','恢复可重用跳跃资源而非恢复枪弹，必须观测接触前后实际remaining_jumps。'),
('bounce-brake','弹出后转向刹入偏置岸','接受弹点自动向来路反弹，随后决定用唯一一枪修正落点。','bounce不能悬停；原反冲改变自动弹射后的运动，偏置岸不在自然轨迹。','弹点外侧空腔与偏置接收岸','move jump grapple shot_recoil','偏置岸箱','不用弹钩直接射；只弹不射；改成原地跳','强制自动离开与后续取舍；区别hang的主动起跳。'),
('hang-recast','挂停观察后转投第二挂点','第一环停稳后选中另一方向的环，主动重抛绕过岩角。','真实hang恢复grapple且再次cast离挂；第二环改变去向，不靠枪弹补给。','岩角遮住直达路径，两个分离挂环提供转角','move jump grapple','岩角后高岸箱','跳过第一环直接第二环；一环直跳；只等不重抛','重新瞄准目标与折线路径，不以多挂环数量充作新玩法。')]
for id,title,obs,cause,geo,caps,reward,counter,diff in ideas:
 d=dict(schema='pcg/creative-design-card/v1',id='grapple/'+id,title=title,source_type='llm_subagent_proposal',source_task='/root/grapple_creator',status='proposal',observation_decision=obs,causal_hypothesis=cause,terrain=geo,capabilities=caps.split(),resources='原Traversal.restore_air_actions仅恢复二跳与grapple；不恢复airShots。实际Godot资源字段验证。',reward=reward,failure_return='下落代价与无伤出口分别检验；反向与连续回程UNKNOWN，不宣称通用重试。',cheap_counterexamples=counter.split('；'),difference_from_existing=diff,parent_family='original grapple hang/bounce',implementation=dict(path='pcg/prototype/creative_batches/grapple/recipes_v1.py',engine='existing WorkshopEngine and Godot 4.7.2',interfaces=1,controls_max=4,checker='actual events/states/resources and safe rewarded stable exit; same-core alternatives allowed',counterexamples_min=18),human_fun='unreviewed',manual_play='unreviewed',production_approval=False)
 (p/(id+'-v1.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
