"""Two necessary landform junctions; real rock steps, no auxiliary thin platforms."""
from pcg.prototype.plains.graph_landforms import make,walk,jump
from pcg.prototype.workshop.rules import cmd

def shelf_rise(c,point,label,direction):
    leg=jump(c,point,label,direction)
    leg["control_plan"][0]["value"]=0
    leg["control_plan"].insert(4,cmd("axis",4,value=direction))
    return leg

def fork():
    p=[[0,352,384,96],[0,448,128,128],[256,224,128,64],[64,96,128,64],[256,-32,128,64],[512,-160,128,64],[384,480,256,128]]
    center=[128,334]
    def routes(c,k,inside):
        if k=='upper':
            if inside:return [walk(c,[536,-178],'top-return-launch'),jump(c,[320,-50],'top-rock',-1,.15),walk(c,[128,78],'second-rock'),walk(c,[320,206],'first-rock'),walk(c,[128,334],'base-return')]
            return [jump(c,[320,206],'first-rock',1),jump(c,[128,78],'second-rock',-1),jump(c,[320,-50],'third-rock',1),jump(c,[576,-178],'upper-choice',1),walk(c,[616,-178],'upper-port')]
        if k=='lower':return [walk(c,[408,462],'under-rim-launch'),jump(c,[320,334],'base-return',-1),walk(c,center,'choice')]if inside else[walk(c,[320,334],'lower-rim'),walk(c,[448,462],'lower-choice'),walk(c,[616,462],'lower-port')]
        return [walk(c,center,'choice')]if inside else[walk(c,[24,334],'reward-mouth')]
    m=make('content-rock-fork',p,[],center,[('upper',[4,-2],'E',[616,-178]),('lower',[4,3],'E',[616,462]),('reward',[0,2],'W',[24,334])],routes);m['functional_roles']=['junction','fork'];return m

def merge(lower_offset=256):
    low_width=320 if lower_offset==0 else 192
    p=[[0,-160,192,64],[0,-96,96,96],[448,224,192,96],[544,320,96,128],[320,352,128,32],[lower_offset,480,low_width,128]]
    center=[512,206]
    def routes(c,k,inside):
        if k=='upper':return [walk(c,[128,-178],'upper-lookout'),jump(c,center,'merge-upper',1,.15)]if inside else[]
        if inside:
            launch=[128,462]if lower_offset==0 else[lower_offset+24,462]
            return [walk(c,launch,'lower-approach'),shelf_rise(c,[384,334],'rock-lip',1),walk(c,[400,334],'last-rise-launch'),shelf_rise(c,[480,206],'merge-lower',1),walk(c,center,'landmark')]
        return [walk(c,[488,206],'return-launch'),jump(c,[384,334],'lower-rock-return',-1,.15),walk(c,[lower_offset+24,462],'lower-return')]
    m=make('content-landmark-'+str(lower_offset),p,[],center,[('upper',[0,-2],'W',[24,-178]),('lower',[lower_offset//128,3],'W',[lower_offset+24,462])],routes);m['functional_roles']=['merge','open_space'];return m
