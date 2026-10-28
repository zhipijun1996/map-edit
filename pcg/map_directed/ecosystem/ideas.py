"""Mechanism-relation hypotheses, not a claim of automatic human creativity.

Rules describe decisions, causal relationships and falsifiers. Parameter and
reward-role variants share a relationship ID and never inflate novelty counts.
Only explicitly implemented producers may be sent to the physics pipeline.
"""
from copy import deepcopy
from pcg.prototype.factory.core.quality import digest

# Executable adapters cover the existing small region. Open proposals are kept
# visible instead of silently substituting a nearby implemented room family.
RULES = [
 dict(id='recoil-height', cells=['rock','recoil'], decision='Choose a takeoff and shot direction to clear a real cliff',
      coupling=['shot -> actor height','rock -> landing constraint'], falsifiers=['ordinary jump reaches the same receiver'], implemented=True),
 dict(id='recoil-diagonal', cells=['rock','recoil'], decision='Trade vertical lift for horizontal reach toward a visible receiver',
      coupling=['shot angle -> height and distance'], falsifiers=['floor walking reaches the receiver'], implemented=True),
 dict(id='timed-cache', cells=['rock','recoil','bell','timed_gate','chest'], decision='Shoot in flight, enter the timed chamber and leave before closure',
      coupling=['same shot -> recoil and temporary gate opening'], falsifiers=['closed gate can be bypassed','reward earned without supported chamber contact','timer strands a player inside'], implemented=True),
 dict(id='recoil-canyon', cells=['rock','recoil'], decision='Use a short jump and lateral recoil below a low rock arch',
      coupling=['recoil -> horizontal reach','rock ceiling -> height constraint'], falsifiers=['no-shot long jump crosses safely'], implemented=True),
 dict(id='zigzag-return', cells=['rock','recoil'], decision='Climb alternating rock banks; choose a separate rapid descent on return',
      coupling=['landing -> real action recovery','port direction -> different movement cost'], falsifiers=['continuous floor bypasses ascent','descent cannot return to the network'], implemented=True),
 dict(id='air-refund', cells=['enemy','recoil','chest'], decision='Use an airborne enemy hit to earn another shot before landing',
      coupling=['airborne hit -> real resource refund -> second recoil'], falsifiers=['the apparent refund is actually a landing reset'], implemented=True),
 dict(id='gear-window', cells=['rock','gear'], decision='Read a gear window, move through shelter and jump from a safe departure',
      coupling=['hazard phase -> departure timing','rock overhang -> movement choice'], falsifiers=['safe observation position lies in hazard sweep'], implemented=True),
 dict(id='merchant-hub', cells=['merchant','chest'], decision='Return with earned chest coins and decide whether to spend',
      coupling=['optional exploration -> purchasing power'], falsifiers=['free starting coins replace earned reward'], implemented=True),
 dict(id='reunion', cells=['rock'], decision='Recognize a landmark from a second approach and select the next route',
      coupling=['multiple ports -> spatial recognition'], falsifiers=['all ports lead through the same forced corridor'], implemented=True),
 dict(id='thorn-slot', cells=['rock','recoil','thorns','chest'], decision='Enter a readable thorn-lined slot and use horizontal recoil through it',
      coupling=['shot direction -> speed','upper/lower thorns -> flight-height band'], falsifiers=['fly over the entire slot','body clearance requires frame-perfect input'], implemented=False),
 dict(id='chase-landing', cells=['bell','controlled_platform','recoil'], decision='Shoot to release a platform and intercept its future position',
      coupling=['same shot -> actor acceleration and moving landing'], falsifiers=['passive waiting is the dominant strategy'], implemented=False),
 dict(id='brake-under-ledge', cells=['rock','recoil','chest'], decision='Fall past a rock lip and brake into a recessed reward pocket',
      coupling=['recoil -> braking','overhang -> approach direction'], falsifiers=['the chest is reachable by walking from above'], implemented=False),
 dict(id='one-shot-two-routes', cells=['rock','recoil','chest'], decision='Spend one airborne shot on either a high reward route or a fast low route',
      coupling=['one resource -> mutually different destinations'], falsifiers=['both rewards are collected without a second decision'], implemented=False),
 dict(id='escape-rising-platform', cells=['controlled_platform','rock','recoil'], decision='Leave an ascending carrier before the low ceiling and recoil into a side cave',
      coupling=['platform progress -> shrinking headroom','shot -> lateral escape'], falsifiers=['waiting safely completes the challenge'], implemented=False),
 dict(id='visible-detour', cells=['rock','chest'], decision='See a nearby reward first, discover its entrance later from another route',
      coupling=['visibility before access -> exploration goal'], falsifiers=['reward is hidden from every earlier approach'], implemented=False),
 dict(id='reward-return-reveal', cells=['rock','chest','bell'], decision='Earn a reward then open a short return to a familiar landmark',
      coupling=['reward exploration -> new network connection'], falsifiers=['shortcut saves no meaningful return cost'], implemented=False),
]

NODE_RULES = {'west':['recoil-height'],'ridge':['recoil-diagonal'],
 'lookout':['merchant-hub'],'arch':['timed-cache'],'east':['reunion'],
 'hollow':['gear-window'],'bell':['zigzag-return','recoil-canyon'],'relay':['air-refund']}

def brief(spec, gate_seconds=1.2):
    rules = [deepcopy(next(r for r in RULES if r['id']==key)) for key in NODE_RULES[spec['node_id']]]
    value = dict(schema='pcg/challenge-design-hypothesis/v1',relationships=rules,
        role=spec['node']['role'],risk_reward=deepcopy(spec['risk_reward']),
        failure_policy='Recover through authored terrain; no resets or resource writes',
        resource_policy='Only original move/jump/recoil; airborne extra shots require actual enemy-hit refund',
        originality='rule-derived proposal, no trained/online model call; parameter variants are not new ideas',
        human_fun='unreviewed')
    if spec['node_id']=='arch':value['gate_window_seconds']=gate_seconds
    value['hypothesis_sha256']=digest(value)
    return value

def proposals(request):
    """Generate role-specific ideas from causal rules, including honest gaps."""
    required=set(request.get('cells',[]));roles=request.get('roles',['main','reward','return'])
    out=[]
    for rule in RULES:
        if required and not required<=set(rule['cells']):continue
        for role in roles:
            proposal=dict(schema='pcg/content-idea/v1',relationship=deepcopy(rule),map_role=role,
                implementation='existing measured adapter' if rule['implemented'] else 'producer implementation required',
                status='hypothesis_only',novelty_family=rule['id'],human_fun='unreviewed')
            proposal['id']=digest(proposal);out.append(proposal)
    return out

def demand_key(spec):
    # IDs, prose labels and seed metadata are not gameplay constraints. The
    # present adapter deliberately retains local port IDs and geometry: it must
    # not pretend to support arbitrary relabeling, mirroring or resizing.
    value=deepcopy(spec)
    for key in ['id','map_seed','objective','revision','mechanic_requirements','budget']:value.pop(key,None)
    if 'node'in value:value['node'].pop('label',None)
    if 'design_contract'in value:
        value['design_contract'].pop('hypothesis_sha256',None)
    return digest(value)
