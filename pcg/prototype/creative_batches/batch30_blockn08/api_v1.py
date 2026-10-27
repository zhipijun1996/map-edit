"""Standard two directions plus already-qualified, separately bound loop sidecar."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules,module_counters_v1 as counters,counter_policy_v1 as policy
from .full_loop_v1 import world_binding
from . import purpose_v1 as observed_purpose
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;REPO=HERE.parents[3]
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
EXPORT_SCRIPT=HERE/'export_v1.mjs';COUNTER_CLASSIFIER=policy.classify
ATTACHMENT=HERE/'loop-attachment-v1.json';BINDING=json.loads(ATTACHMENT.read_text());LOOP=REPO/BINDING['loop_evidence']['path']
SOURCE_DEPENDENCIES=[*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),Path(policy.__file__),HERE/'comparisons_v1.py',HERE/'full_loop_v1.py',HERE/'purpose_v1.py',HERE/'control-selection-v1.json',ATTACHMENT,EXPORT_SCRIPT,LOOP,REPO/BINDING['frozen_loop_source_case']['path'],REPO/BINDING['same_reward_comparison']['path']]


def metadata(c):
 if c['fixture_kind']=='same-world-A-B-A':raise ValueError('Neverexportloopselfroute')
 sidecar=json.loads(LOOP.read_text())
 if sidecar['status']!='scoped_regular_pass'or sidecar['layout_uid']!=c['layout_uid']or sidecar['world_binding_sha256']!=world_binding(c):raise ValueError('needs_verification: exact continuousloop missing/stale')
 if not c.get('counterexample_kind') and sidecar['program_sha256']['back'if c['route_spec']['from_port']=='B'else'out']!=digest(c['control_plan']):raise ValueError('needs_verification: directionalprogram differs from earnedreturnfixture')
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(REPO));c['continuous_loop_attachment']=dict(artifact=BINDING['loop_evidence'],status=sidecar['status'],layout_uid=c['layout_uid'],not_standard_route=True)
 c['scope_limits']=dict(return_scope='FreshB->A andexactcontinuousA->B->A bothseparatelytested; noarbitrarypairstateorboundaryreturn',reward='Actual16cointransactionoutbound; freshBstarts0coins/unclaimedbox, neverfakeearnedstate',choice='Lowerbridgealternative, notshortcut; oldupperreturnlegal/faster19framesameactions',map='PairedCellBinstallation, seam andwholeMapUNKNOWN')
 return c


def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: onecompactN08spaceonly; noheld-guidedsecondspace')
 return[metadata(rules.candidate(0,route))for route in ['out','back']]


def purpose(c,r):return observed_purpose.purpose(c,r)
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]


def candidate_for_request(spec,interface=0):
 wanted=rules.candidate(0,'out')['map_specification']
 if interface!=0 or not isinstance(spec,dict)or digest(spec)!=digest(wanted):
  return dict(status='needs_design',conflicts=[dict(field='exact_reward_return_demand',reason='Onlyexacttwoports/sharedinitialpairedstate/16coinrewardworld supported. Rewardfreetraversal,othergeometry/state/space orforcedfast-returnbenefit notsilentlysubstituted.')],searched=dict(interfaces=[0],physical_rule_revisions=2,maximum_probes=80,ordered_pairs=[['A','B'],['B','A']],continuous_loop_separate=True),negotiable=['Exactrewardreturnrequirement','Freshregisteredsize/port/resource/stateversion','Acceptalternate-returnnotshortcut'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),continuous_fixture=BINDING['loop_evidence'],new_modules_from_fixture=0,assembly='UNKNOWN',human_fun='UNKNOWN',production_admitted=False)
