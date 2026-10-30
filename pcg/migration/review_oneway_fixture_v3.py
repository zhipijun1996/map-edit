"""Exact approved50 C uses the existing174/62 valid one-way initialization rule."""
DESIGN_VERSION='sha256:2f7eb2ae38bd1fc16766f98039a7fc5e5bb7f5a0a189dc520cb566d514633f44'
def repair(case,port,offset):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='50'or s.get('designVersion')!=DESIGN_VERSION:return
 if port.get('id')!='C'or port.get('surface')!='ONE_WAY_PLATFORM'or port.get('normal')!=[1,0]or offset!=2:return
 # Three distinct valid starts -2,0,-4, rather than +2 below a one-way top.
 case['spawn'][1]=port['stagingPosition'][1]-4
