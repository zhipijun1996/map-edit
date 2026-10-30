"""Three same-world reward-return observations, never a fresh reverse reset."""
import copy
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
row=core.read(core.REPO/'feedback/manual-review/implementation-handoff-v1.json')['rows'][1]
folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'physics-input-cases.json')['cases'];probes=[]
for phase in [0.,.3,.6]:
 c=copy.deepcopy(cs[0]);c['id']+='-same-world-'+str(phase);c['control_plan']+=copy.deepcopy(cs[1]['control_plan']);c['max_frames']=4800
 c['goal']=cs[1]['goal'][:];c['route_spec'].update(id='continuous-reward-loop',to_port='A',require_bell=True)
 c['fixture_kind']='same-world-A-B-A';c['actual_end_port']='A';c['exportable_standard_route']=False
 c['definition_exit_is_only_a_harness_marker']='B; actual interior return goal is A. This is not a boundary-to-boundary self-loop certificate.'
 for e in c['enemies']:e['initial_idle_cooldown']=phase
 probes.append(c)
eng,_,authors=physics._engine(folder,'approved-b001-02-same-world-return-v1',physics.FULL_PROTOCOL)
core.write(eng.out/'protocol.json',dict(maximumAttempts=3,phases=[0.,.3,.6],freshIndependentHoldout=False,selection='All three predeclared phases, no program selection',source=physics.artifact(__file__)))
rows=[]
for c,r,e in eng.run([physics.fresh(c,'return') for c in probes],'same-world-return'):
 check=checked_purpose(authors[0],c,r);rows.append(dict(id=c['id'],check=check,evidence=e,hp=r['hp'],returns=r['returns'],coins=r['workshop']['coins']));print(c['id'],check['ok'],check['reasons'],flush=True)
core.write(eng.out/'return-check.json',dict(rows=rows,passed=all(v['check']['ok']for v in rows),scope='3 finite same-world interior A-reward-B-A observations; no arbitrary recovery/Port self-loop claim'))
