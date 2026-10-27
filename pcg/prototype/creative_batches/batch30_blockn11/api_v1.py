"""Frozen same-face dock adaptation; two independent directional worlds."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'control-selection-v1.json',HERE/'source-baseline-v1.json']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or str(interface)not in CONTROL:raise ValueError('needs_design:onlyregisteredW-WandfreshE-Edemands')
 choice=CONTROL[str(interface)];c=rules.candidate(interface,choice['width'],choice['control'])
 c['play_hint']='走出岩唇，身体低于檐底后向外射击，反冲折回袋内取箱。落底后可付费跳射恢复。'
 c['source_map_request']=copy.deepcopy(c['map_specification'])
 c['map_shape_demand']=copy.deepcopy(json.loads((HERE/'idea-source-v1.json').read_text())['card_original']['two_space_demands'][interface])
 c['map_request_response']=dict(status='requires_physics',request_origin='B_CSPsameface_shape_requirement_plus_explicitA4currencyadaptation',registered_normals=[p['normal']for p in c['ports']],ordered_pairs=[['A','B']],unknown_ordered_pairs=[['B','A']],currency_allocation=dict(amount=10,status='preservedparentproposal_requiresactualMapbudgetbinding'),map_added_terrain=0,production_admitted=False,unresolved=['ActualMapedgeassignment/allrequiredpairs','Rewardbudgetbinding','Arbitraryingress/resources','Boundarycrossing','Genericrecovery/seam/fullMap'])
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return[c]
def candidate_for_request(spec,interface=0):
 if interface not in [0,1]:return dict(status='needs_design',conflicts=[dict(field='interface',reason='OnlyW-W/E-Esamefaceoffset')],new_physics_cases=0)
 cs=layouts(RECIPES[0],interface)
 if not isinstance(spec,dict)or digest(spec)!=digest(cs[0]['map_specification']):return dict(status='needs_design',conflicts=[dict(field='request',reason='Outsideexactregistered10coin/samefaceoffset/A->Brequest; actualMapreverse/allpairs/rewardsnotquietlysubstituted')],searched=dict(interfaces=[0,1],source_widths=[75,96],selected_width=96,ordered_pairs=[['A','B']],currency=10),negotiable=['Exactderivedsamefaceadaptor','FreshrewardbindingwithMap','Independentreverse/entry/stateproof'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=cs,production_admitted=False,assembly='UNKNOWN')
purpose=rules.purpose
