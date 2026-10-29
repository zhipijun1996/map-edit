"""Exact clarified 174: a one-way top cannot catch a body initialized below it."""
# Authorization is an immutable chat-derived target, not an inferred surface swap.
DESIGN_VERSION='sha256:eca607abbd56361397a7624b5bd56db34e7092247496ae38e1026ada76434cf9'
def repair(case,port,offset):
 spec=case.get('approved_implementation',{})
 if spec.get('reviewId')!='174'or port.get('surface')!='ONE_WAY_PLATFORM'or not port['normal'][0]or offset!=2:return
 if spec.get('designVersion')!=DESIGN_VERSION:return
 # Retain three distinct heights: -2,0,-4. +2 embeds feet below the one-way
 # top and is an invalid supported initial state, rather than approach noise.
 case['spawn'][1]=port['stagingPosition'][1]-4
