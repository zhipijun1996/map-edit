"""Small acceptance Mission/Exploration, no poses or inherited room skeleton."""
from pcg.prototype.factory.core.quality import digest

def create(seed):
    definitions=[('start','junction','split-cliff','同处选择高处窄路或下坠溪谷'),('rise','challenge','rising-shoulder','向高处爬升'),('ridge','challenge','existing-timed-ridge','空中击铃穿越'),('cliff','junction','braking-cliff','下坠制动与深处奖励分叉'),('switchback','challenge','switchback','折返反冲攀升'),('landmark','rest','landmark-bowl','两路真实汇合地标'),('cache','reward','needle-cache-foldback','尖刺窄通路宝箱与逆向返回')]
    g=dict(schema='pcg/exploration-graph/v1',seed=seed,entry='start',goal='landmark',initial_abilities=['move','jump','shot_recoil'],nodes=[],edges=[],branches=[],source='Same graph drives every physical node/edge; no prior layout consumed',region='plains',block_size=128)
    for key,role,family,label in definitions:g['nodes'].append(dict(id=key,role=role,macro_family=family,label=label,grants=[],opens=[],reward=0,risk=3 if role=='reward'else 1,intent=label))
    def edge(a,b,pa,pb,purpose,bidir=False):
        g['edges'].append(dict(id='e'+str(len(g['edges'])),**{'from':a,'to':b},port_roles={a:pa,b:pb},purpose=purpose,bidirectional=bidir,cost=1,requires=[],switch=None))
    edge('start','rise','upper','in','upper_main');edge('rise','ridge','out','in','upper_main');edge('ridge','landmark','out','upper','upper_main')
    edge('start','cliff','lower','in','lower_main',True);edge('cliff','switchback','out','in','lower_main',True);edge('switchback','landmark','out','lower','lower_main',True)
    edge('cliff','cache','reward','in','reward_foldback',True)
    g['principal_routes']=[dict(id='upper',nodes=['start','rise','ridge','landmark'],experience=['climb','timed_air_shot','high_landmark']),dict(id='lower',nodes=['start','cliff','switchback','landmark'],experience=['fall_brake','recoil_switchback','low_landmark'])]
    g['branches']=[dict(id='needle-detour',kind='foldback',entry='cliff',nodes=['cache'],reward='cache',rejoin='cliff')]
    g['mission_policy']=dict(shared_choice='start',merge='landmark',major_items=0,currency_chests=1,currency_total=18,goal_is_boss=False)
    return g
