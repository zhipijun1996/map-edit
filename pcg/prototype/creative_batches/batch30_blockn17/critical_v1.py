"""Original geometry, cheaper counter policies and an explicit paid detour."""
import copy,math
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground

def variant(c,kind,plan):
 v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;return v
def direct_D(c,kind='direct-D-wall-crest'):
 return variant(c,kind,[cmd('axis',value=-1),wait_x(816,-1),cmd('axis',value=0),ground(),cmd('wait',20),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.35,math.sqrt(1-.35**2)]),settle(1128),ground(),cmd('wait',20)])
def via_B(c,direct=False):
 i=c['interface'];entry=c['route_spec']['from_port'];b=rules.candidate('B',1,i,entry);base=direct_D(b)['control_plan']if direct else b['control_plan'];prefix_size=9 if entry=='D'else 8
 # The nominal B policy is interrupted at its actual first real landing,
 # not run all the way to B's external dock before returning.
 return variant(c,'direct-D-B-then-upper-C'if direct else'paid-B-first-then-upper-C',copy.deepcopy(base[:-1])+[settle(848),wait_x(854,-1),ground(),cmd('wait',8),settle(688),cmd('jump'),cmd('jump_release',20),ground(),cmd('wait',8)]+copy.deepcopy(c['control_plan'][prefix_size+6:]))
def preopen(c):
 n=9 if c['route_spec']['from_port']=='D'else 8;branch=copy.deepcopy(c['control_plan'][n:]);branch[2]=cmd('shoot',direction=[-.5,math.sqrt(.75)])
 return variant(c,'ground-preopen-miss-on-second-shot',copy.deepcopy(c['control_plan'][:n])+[cmd('shoot',aim_cell=dict(kind='bell',id='cross-pair')),ground(),cmd('wait',12)]+branch)
