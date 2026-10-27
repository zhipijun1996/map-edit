"""Source-owned Bellstrider arena using the current first Plains stage Boss."""
import copy
from pcg.prototype.plains.graph_landforms import make,walk,jump
from pcg.map_directed.catalog_feed.adapt import target
from pcg.prototype.factory.core.quality import digest


def bellstrider():
    arena=[0,352,1152,80]
    m=make('bellstrider-court',[arena,[96,256,32,96],[290,222,120,20],[750,162,100,20],[890,222,120,20]],[],[176,334],[('W',[0,2],'W',[24,334])],lambda c,k,inside:[walk(c,[176,334]if inside else[24,334],'court-dock')])
    duel=dict(kind='module',target=target(m['case'],[176,334],'bellstrider-duel'),control_plan=[dict(op='settle',target_x=176,deadband=3,trigger=dict(after=0))],budget_ticks=2400,boss_duel='bellstrider')
    m['case']['boss_encounters']=[dict(id='bellstrider',scene='res://scenes/bosses/bellstrider.tscn',position=[800,287],arena=[128,1120],action_bounds=[128,-64,1024,416],activation_region=[96,250,1056,102],source='plains_region_stage map_index1 original Bellstrider',actual_health=16)]
    m['port_transitions']={'W>W':[jump(m['case'],[176,334],'court-entry',1,.15),duel,jump(m['case'],[24,334],'court-return',-1,.15)]}
    from pcg.map_directed.director import REPO
    m['verification_extra']=str(REPO/'pcg/map_directed/graph_map/extra.gd')
    m['center_port']='W';m['functional_roles']=['boss','open_space'];m['boss_contract']=dict(scene=m['case']['boss_encounters'][0]['scene'],must_defeat=True,physics='PENDING')
    m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],program=m['port_transitions']));m['source_version']=m['content_version'];return m
