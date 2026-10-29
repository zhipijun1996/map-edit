"""Three real receiver shots; verify same native complementary group and its invariant."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label,OUT
from .finalize_revision058_v1 import folder_for
from .prepare_review045_v1 import at,axis

def main():
 row=next(r for r in rows()if label(r)=='s11');f=folder_for(row);eng,cs,authors=physics._engine(f,'approved-r058-s11-three-access-v1',physics.FULL_PROTOCOL);fixtures=[]
 for name,xy in [('common',[300,302]),('right',[584,78]),('bottom',[448,462])]:
  c=copy.deepcopy(next(c for c in cs if c['route_spec']['from_port']==('R'if name=='right'else'B'if name=='bottom'else'L')));c['id']='r058-s11-access-'+name;c['spawn']=c['entry_port']=xy;c['goal']=[xy[0]-4,xy[1]-4,8,8];shoot=cmd('shoot',direction=[0,-1])
  if name=='common':shoot['aim_cell']=dict(kind='bell',id='common-bell')
  c['control_plan']=[axis(0),shoot,cmd('wait',60)]+at(*xy);c['max_frames']=600;fixtures.append(c)
 checks=[]
 for c,raw,e in eng.run(fixtures,'actual-three-receiver-shots'):
  snap=raw.get('workshop',{}).get('paired_gates',[]);print(c['id'],snap,flush=True);checks.append(dict(id=c['id'],snapshot=snap,evidence=e,originalPlayerHp=raw.get('hp'),actualShots=raw.get('shots')))
 core.write(eng.out/'access-checks.json',dict(rows=checks,originalEvidence=True,newPhysicsAttempts=3,newHoldout=False))
if __name__=='__main__':main()
