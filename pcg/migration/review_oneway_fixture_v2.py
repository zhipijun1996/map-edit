"""Exact approved 62: initialize above its one-way top, never inside it."""
DESIGN_VERSION='sha256:25414bcdc74513d7243c4a7d2639fa1a7778562107dfa21451d8a5579fce532e'
def repair(case,port,offset):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='62'or s.get('designVersion')!=DESIGN_VERSION:return
 if port.get('id')!='entry'or port.get('surface')!='ONE_WAY_PLATFORM'or port.get('normal')!=[-1,0]or offset!=2:return
 # Same existing 174 rule: three distinct valid starts -2,0,-4 px. The +2
 # embedding is not a supported initial state on a native one-way collider.
 case['spawn'][1]=port['stagingPosition'][1]-4
