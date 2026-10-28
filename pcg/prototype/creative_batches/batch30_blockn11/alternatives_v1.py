import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground
def alternatives(c):
 out=[];sign=c['rule_parameters']['outward_sign'];lip=c['rule_parameters']['upper_lip'];target=c['exit_port'][0];p=c['control_plan']
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 q=copy.deepcopy(p);q[2]=dict(op='wait',trigger=q[2]['trigger']);add('omit-recoil',q)
 for offset in [16,40,64,90]:add('drop-air-turn-no-gun-'+str(offset),[cmd('axis',value=sign),wait_x(lip+sign*offset,sign),settle(target,0)])
 for offset in [-2,8]:
  for hold in [0,8,20,32]:add(f'ordinary-jump-o{offset}-h{hold}',[cmd('axis',value=sign),wait_x(lip+sign*offset,sign),cmd('jump'),cmd('jump_release',hold),settle(target,0)])
 for offset in [-24,-8]:
  add('early-ledge-recoil-'+str(offset),[cmd('axis',value=sign),wait_x(lip+sign*offset,sign),cmd('shoot',direction=[sign,0]),cmd('axis',value=sign,after=9),wait_x(lip+sign*16,sign),settle(target,0)])
 add('ground-preparation-extra-shot',[cmd('shoot',direction=[sign,0]),cmd('wait',15)]+copy.deepcopy(p))
 for offset in [140,175]:
  add('late-fall-recoil-'+str(offset),[cmd('axis',value=sign),wait_x(lip+sign*offset,sign),cmd('shoot',direction=[sign,0]),settle(target,6)])
 # The original bottom bank is retained. A paid one-jump upshot can be a valid alternative.
 add('bottom-paid-jump-shot',[cmd('axis',value=sign),wait_x(lip+sign*180,sign),cmd('axis',value=0),ground(),cmd('axis',value=-sign),wait_x(sign*160,-sign),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[sign*.4,math.sqrt(.84)]),settle(target,0)])
 add('bottom-no-gun-jump',[cmd('axis',value=sign),wait_x(lip+sign*180,sign),cmd('axis',value=0),ground(),cmd('axis',value=-sign),wait_x(sign*160,-sign),cmd('axis',value=0),cmd('jump'),cmd('jump_release',32),settle(target,0)])
 assert len(out)==20,len(out)
 return out
def critical(c):
 names=['drop-air-turn-no-gun-16','drop-air-turn-no-gun-40','ordinary-jump-o8-h32','bottom-no-gun-jump']
 return[v for v in alternatives(c)if v['counterexample_kind']in names]
