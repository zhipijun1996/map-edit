"""Native latest-library junction/treasure compositions, no legacy eight roles."""
import copy,json,gzip
from .adapt import exterior,target,leg,samples
from ..shape_search.catalog import reflect
from ..director import REPO
from pcg.prototype.factory.core.quality import digest,module_hash

def gate_join(item,node):
    """Use the library's real return Macro instead of inventing a reverse fork."""
    from pcg.prototype.workshop.macro import climb_plan
    c=copy.deepcopy(item['cases'][0]);c.setdefault('shop_sites',[])
    for l in c['latches']:l.setdefault('prompt','')
    for s in c['reward_sites']:s['target']=target(c,s['position'],node+'/'+s['id'])
    high=next(v for v in c['ports']if v['id']=='C')['position'];pocket=next(v for v in c['ports']if v['id']=='B')['position'];lower_y=max(r[1]for r in c['platforms'])-18
    frames=[f for source in item['cases']for f in samples()[(item['record']['contentVersion'],source['id'])]]
    bottom=[f['x']+12 for f in frames if f['grounded']and abs(f['y']-lower_y)<2]
    lower_edge=__import__('math').ceil((max(bottom)+24)/8)*8
    for r in c['platforms']:
        if abs(r[1]-(lower_y+18))<1:r[2]=min(r[0]+r[2],lower_edge)-r[0]
    upper_edge=__import__('math').floor(max(c['platforms'][i][0]+c['platforms'][i][2]for i in [1,6])/8)*8
    c['platforms'][6][2]=upper_edge-c['platforms'][6][0]
    for r in c['platforms']:
        if r[1]<438 and r[0]<upper_edge<r[0]+r[2]:r[2]=upper_edge-r[0]
    # Deliberately declared one-way entry: descend with the original drop action.
    c['one_way_platform_indices']=sorted(set(c.get('one_way_platform_indices',[]))|{1,6})
    center=target(c,[80,420],node+'/center');hi=target(c,[upper_edge-24,420],node+'/hi');lo=target(c,[lower_edge-24,lower_y],node+'/lo');out=target(c,[c['platforms'][0][0]+24,420],node+'/out')
    def port(key,x,y,normal,dock):return dict(id=key,position=[x,y],normal=normal,kind='side',aperture=[x-48,y-64,96,128],dock=dock,connection_mode='continuous_terrain')
    ports={'hi':port('hi',upper_edge,420,[1,0],hi),'lo':port('lo',lower_edge,lower_y,[1,0],lo),'out':port('out',c['platforms'][0][0],420,[-1,0],out)}
    back=next(v for v in item['cases']if v['route_spec']['id']=='return')
    lower_dock=600+40*c['rule_parameters']['variant']-140
    inbound={'hi':[dict(kind='drop',target=target(c,pocket,node+'/drop-in')),leg(c,[80,420],back['control_plan'],node+'/native-return')],
             'lo':[dict(kind='walk',target=target(c,[lower_dock,lower_y],node+'/return-start')),leg(c,[80,420],climb_plan(),node+'/native-climb')]}
    m=dict(id=node,case=c,ports=ports,center=center,core=None,center_to_port={'out':[dict(kind='walk',target=out)]},port_to_center=inbound,core_visit_program=[],boundary_gates=[],
        spec=dict(id='catalog-feed/'+node,node_id=node,node=dict(id=node,role='junction',label='原生回程 Macro 汇合'),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[0,0,1100,1100]),ports=list(ports.values())),
        source_version=item['record']['contentVersion'],source_title=item['title'],variant_id=node+'/'+item['record']['contentVersion'][7:15],source_shape_sha256=digest(c['platforms']),action_clearance=[],
        motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),adaptation=dict(new_one_way_entry=True,unused_bottom_tail_cut=lower_edge,added_geometry=0,source_return_recipe_reused=True,proof='Fresh local/whole-map verification required'))
    W=m['spec']['space']['core_bounds'][2];m=reflect(m)
    for s in m['case']['reward_sites']:s['position'][0]=W-s['position'][0];r=s['region'];s['region']=[W-r[0]-r[2],r[1],r[2],r[3]]
    micro=REPO/'pcg/results/catalog-feed-native-macro-probe-v2'
    if(micro/'summary.json').exists():
        cases={v['id']:v for v in json.loads((micro/'cases.json').read_text())['cases']}
        for b in json.loads((micro/'physics/batches.json').read_text()):
            for r in json.loads(gzip.decompress((micro/'physics'/b['gzip_path']).read_bytes()))['results']:
                if r['ok']and cases[r['id']]['rule_parameters']['variant']==c['rule_parameters']['variant']:m['action_clearance'] += [[f['x']-12,f['y']-18,24,36]for f in r['frames'][::2]]
    m['source_shape_sha256']=digest(m['case']['platforms']);m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports']));return m

def deep_fork(item,drop):
    result=copy.deepcopy(item)
    for c in result['cases']:
        c['id']+='-drop-'+str(drop);c['world_bounds'][3]+=drop
        for i in [2,3]:c['platforms'][i][1]+=drop
        for p in c['ports']:
            if p['id']=='B':p['position'][1]+=drop
        for s in c['reward_sites']:
            if s['position'][1]>400:s['position'][1]+=drop;s['region'][1]+=drop
        if c['route_spec']['to_port']=='B':c['exit_port'][1]+=drop;c['goal'][1]+=drop
        for k in ['factory_evidence','recorded_frames','validation_summary']:c.pop(k,None)
        c['module_sha256']=module_hash(c)
    return result
