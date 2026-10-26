"""Demand-driven reverse policies on original rock supports, no new geometry."""
import copy,json,re
from pathlib import Path
from ..block_grid.build import traces
from ..catalog_feed.adapt import target
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.factory.core.quality import digest

def propose(m,result):
    if len(m['ports'])!=2 or len(m['port_transitions'])!=1:raise ValueError('requires_authored_multiport_return')
    if m['case'].get('moving_platforms')or m['case'].get('saws')or m['case'].get('enemies'):raise ValueError('dynamic_return_requires_a_separate_policy')
    c=m['case'];pair=next(iter(m['port_transitions']));a,b=pair.split('>')
    if any('return_access'not in l for l in c.get('latches',[])):raise ValueError('return_bell_access_missing')
    sequence=[]
    for f in result['frames']:
        match=re.fullmatch('Platform([0-9]+)',str(f.get('support_id','')))
        if not f['grounded']or not match:continue
        index=int(match[1])
        if not sequence or sequence[-1]!=index:sequence.append(index)
    if len(sequence)<2:raise ValueError('source_landing_sequence_missing')
    # Require a simple observed route; a different return must not invent an
    # unobserved helper bank or jump across an unknown part of the Module.
    if len(sequence)!=len(set(sequence)):raise ValueError('source_path_revisits_support_needs_authored_return')
    program=[]
    for src,dst in zip(reversed(sequence),list(reversed(sequence))[1:]):
        s,t=c['platforms'][src],c['platforms'][dst];direction=1 if t[0]+t[2]/2>s[0]+s[2]/2 else-1
        launch=[s[0]+s[2]-36 if direction>0 else s[0]+36,s[1]-18];landing=[t[0]+min(80,t[2]/2)if direction>0 else t[0]+t[2]-min(80,t[2]/2),t[1]-18]
        rise=launch[1]-landing[1]
        if abs(landing[0]-launch[0])>460 or rise>160:raise ValueError('return_jump_outside_bounded_policy_domain')
        program.append(dict(kind='walk',target=target(c,launch,'return-launch'),budget_ticks=360))
        shot=dict(direction=[-direction*.6,.8]if rise>=64 else[-direction*.9886859966642595,.15])
        for latch in c.get('latches',[]):
            gx=latch['gate'][0]
            if min(launch[0],landing[0])<gx<max(launch[0],landing[0]):shot=dict(aim_cell=dict(kind='bell',id=latch['id'],receiver='access'))
        plan=[cmd('axis',value=direction),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,**shot),settle(landing[0],6)]
        program.append(dict(kind='module',target=target(c,landing,'reverse-landing'),control_plan=plan,budget_ticks=1200))
    program.append(dict(kind='walk',target=copy.deepcopy(m['ports'][a]['dock']),budget_ticks=360))
    out=copy.deepcopy(m);out['variant_id']+='/return-proposal';out['port_transitions'][b+'>'+a]=program
    out['transition_options'][b+'>'+a]=[dict(program=program,case_id='NEW-demanded-return',features=['reverse_challenge'])]
    out['transition_sources'][b+'>'+a]=dict(status='NEW_UNVERIFIED',source_version=m['source_version'],observed_supports=sequence,geometry_added=0)
    out['adaptation']['return_proposal']=dict(supports=sequence,geometry_added=0,source_physics_inherited=False)
    out['content_version']='sha256:'+digest(dict(case=out['case'],ports=out['ports'],transitions=out['port_transitions']));return out
