"""Capability contracts and a resource-aware action grammar.
Abstract legality is a proposal filter; real Godot execution remains authoritative.
No geometry template or preset capability profile is selected here.
"""
from __future__ import annotations
from dataclasses import dataclass,replace,asdict
from pathlib import Path
import itertools,json,random,hashlib

ROOT=Path(__file__).resolve().parents[2]
REGISTRY_PATH=Path(__file__).with_name('capabilities.json')

class ContractError(ValueError):pass

class Registry:
    def __init__(self,path=REGISTRY_PATH):
        self.path=Path(path);self.data=json.loads(self.path.read_text());self.items=self.data['capabilities']
    def resolve(self,capabilities):
        if not isinstance(capabilities,list) or any(not isinstance(x,str) for x in capabilities):raise ContractError('capabilities must be explicit string IDs')
        if len(capabilities)!=len(set(capabilities)):raise ContractError('duplicate capabilities')
        caps=frozenset(capabilities)
        unknown=caps-self.items.keys()
        if unknown:raise ContractError('unregistered_capability:'+','.join(sorted(unknown)))
        for name in caps:
            entry=self.items[name]
            missing=set(entry.get('requires',[]))-caps
            if missing:raise ContractError(f'{name}: missing '+','.join(sorted(missing)))
            conflict=set(entry.get('incompatible',[]))&caps
            if conflict:raise ContractError(f'{name}: incompatible '+','.join(sorted(conflict)))
            if not entry.get('runtime_binding'):raise ContractError(f'{name}: unbound provider')
        return caps
    def snapshot(self,capabilities):
        caps=self.resolve(list(capabilities))
        return dict(schema='pcg/capability-snapshot/v2',ids=sorted(caps),registry_version=self.data['version'],registry_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),physics_source=self.data['physics_source'])
    def combinations(self,base=('move','jump'),optional=('shot_recoil','double_jump','grapple','wall_climb')):
        for mask in range(1<<len(optional)):
            yield self.resolve(list(base)+[x for i,x in enumerate(optional) if mask&(1<<i)])

@dataclass(frozen=True)
class State:
    mode:str='ground'
    jumps:int=1
    rounds:int=1
    hooks:int=1
    anchors:int=3
    walls:int=1
    used:frozenset=frozenset()

@dataclass(frozen=True)
class Rule:
    id:str
    capabilities:tuple[str,...]
    modes:tuple[str,...]
    resource:str|None=None
    def available(self,caps,state):
        return set(self.capabilities)<=caps and state.mode in self.modes and (self.resource is None or getattr(state,self.resource)>0)

RULES=(
 Rule('ground_jump',('jump',),('ground',),'jumps'),
 Rule('air_jump',('jump','double_jump'),('air',),'jumps'),
 Rule('recoil',('shot_recoil',),('ground','air','hang','wall'),'rounds'),
 Rule('hook_hang',('grapple',),('ground','air','hang'),'anchors'),
 Rule('hook_bounce',('grapple',),('ground','air','hang'),'anchors'),
 Rule('anchor_jump',('jump','grapple'),('hang',)),
 Rule('wall_contact',('wall_climb','move'),('ground','air'),'walls'),
 Rule('wall_jump',('wall_climb',),('wall',),'walls'),
)
RULE_BY_ID={r.id:r for r in RULES}

class Grammar:
    def __init__(self,caps,registry=None):
        self.registry=registry or Registry();self.caps=self.registry.resolve(list(caps))
    def initial(self):return State(jumps=2 if 'double_jump'in self.caps else (1 if 'jump'in self.caps else 0),rounds=int('shot_recoil'in self.caps),hooks=int('grapple'in self.caps))
    def step(self,state,op):
        if op not in RULE_BY_ID:raise ContractError('unregistered_action:'+op)
        rule=RULE_BY_ID[op]
        if not rule.available(self.caps,state):raise ContractError('unmet_action_precondition:'+op)
        used=state.used|set(rule.capabilities)
        if op in ('ground_jump','air_jump'):return replace(state,mode='air',jumps=state.jumps-1,used=frozenset(used))
        if op=='recoil':return replace(state,mode='air',rounds=state.rounds-1,jumps=int('double_jump' in self.caps) if state.mode=='ground' else state.jumps,used=frozenset(used))
        if op.startswith('hook_'):
            # Actual contact restores one extra jump and H. It does NOT grant a round.
            return replace(state,mode='hang' if op=='hook_hang' else 'air',anchors=state.anchors-1,hooks=1,jumps=1 if 'double_jump'in self.caps else state.jumps,used=frozenset(used))
        if op=='anchor_jump':return replace(state,mode='air',jumps=int('double_jump'in self.caps),used=frozenset(used))
        if op=='wall_contact':return replace(state,mode='wall',used=state.used)
        if op=='wall_jump':return replace(state,mode='air',walls=state.walls-1,jumps=int('double_jump'in self.caps),hooks=int('grapple'in self.caps),used=frozenset(used))
        raise ContractError(op)
    def validate_word(self,word):
        state=self.initial();trace=[]
        for op in word:
            before=state;state=self.step(state,op)
            trace.append(dict(action=op,before=asdict(before),after=asdict(state)))
        return state,trace
    def derive(self,seed,limit=48,max_depth=7,require_all=True):
        rng=random.Random(seed);front=[((),self.initial())];candidates=[]
        targets=self.caps-{'move','jump'}
        for depth in range(max_depth):
            nxt=[]
            for word,s in front:
                options=[r for r in RULES if r.available(self.caps,s)];rng.shuffle(options)
                for rule in options:
                    # Resource budgets ensure finite expansion. Avoid repeated contact observations.
                    if word and word[-1]=='wall_contact' and rule.id=='wall_contact':continue
                    w=word+(rule.id,);ns=self.step(s,rule.id)
                    if ns.mode=='air' and ('ground_jump'in w or len(w)>1) and (not require_all or targets<=ns.used):candidates.append(w)
                    nxt.append((w,ns))
            rng.shuffle(nxt);front=nxt[:384]
        # Favor different accepted-event words and a short explanation per challenge.
        candidates=sorted(set(candidates));rng.shuffle(candidates);candidates.sort(key=lambda w:len(w)+rng.random()*2)
        selected=[]
        for w in candidates:
            if w not in selected:selected.append(w)
            if len(selected)>=limit:break
        return selected


def generate_registry():
    data={'schema':'pcg/capability-registry/v2','version':2,'physics_source':'12f6cb006d7119598e3235f4ca4f7323e4c9d092','extension_contract':'New abilities require an implemented runtime binding, action preconditions/effects, affordance synthesis and physical positive/negative tests. An ID alone does not implement a mechanic.','capabilities':{
      'move':{'runtime_binding':'router_axis','actions':['axis'],'requires':[]},
      'jump':{'runtime_binding':'jump_ability.enabled','actions':['ground_jump','anchor_jump'],'requires':[]},
      'shot_recoil':{'runtime_binding':'shoot_ability.enabled+recoil_ability.enabled','actions':['recoil'],'requires':[],'consumes':['air_round'],'restores_from':['grounded','committed_airborne_hit']},
      'double_jump':{'runtime_binding':'traversal.grant(double_jump)','actions':['air_jump'],'requires':['jump'],'restores_from':['grounded','hook_contact','wall_jump','committed_airborne_enemy_hit']},
      'grapple':{'runtime_binding':'traversal.grant(grapple)','actions':['hook_hang','hook_bounce','anchor_jump'],'requires':[],'affordances':['real_grapple_anchor'],'does_not_restore':['air_round']},
      'wall_climb':{'runtime_binding':'traversal.grant(wall_climb)','actions':['wall_contact','wall_jump'],'requires':['move'],'affordances':['wall_climbable_collision'],'does_not_require':['jump_ability.enabled'],'does_not_restore':['air_round']}}}
    REGISTRY_PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':generate_registry()
