"""Install data-only boundary approach controls on the existing Godot Harness.

This wrapper selects a declared full control program for a continuous fixture;
all movement, collision, resources, projectiles and mechanisms remain inherited
from the candidate's actual original runner. Runtime Module geometry is untouched.
"""
from pathlib import Path
import copy
from . import core
from pcg.prototype.factory.core.quality import digest


def bind(document,input_cases):
    from .physics import author_for,runner_for
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases);records=[]
    directory=Path(__file__).parent/'boundary_runners'
    ports={p['id']for p in doc['generationContract']['ports']}
    for case in cases:
        plans=case.get('migration_boundary_plans')
        if not plans:continue
        if not isinstance(plans,dict)or not set(plans)<=ports:raise ValueError('boundary_plan_unknown_port')
        for port_id,entry in plans.items():
            if not isinstance(entry,dict)or not set(entry)<={'ingress','egress','local_ingress','local_egress'}:raise ValueError('invalid_boundary_plan_direction')
            for direction,plan in entry.items():
                if not isinstance(plan,list)or not plan or len(plan)>128 or not all(isinstance(c,dict)and isinstance(c.get('op'),str)for c in plan):
                    raise ValueError('boundary_plan_requires_complete_original_DSL_program')
        author=author_for(case);author_path=core.relative(author.__file__)
        parent_runner=core.relative(runner_for(case,author))
        runner_token=digest(dict(runner=parent_runner,protocol=4))[:16]
        wrapper_token=digest(dict(author=author_path,runner=parent_runner,protocol=4))[:16]
        runner=directory/('runner_'+runner_token+'.gd');wrapper=directory/('binding_'+wrapper_token+'.py')
        gd=('extends '+repr(str(core.REPO/parent_runner)).replace("'",'"')+'\n'
            +'# Only choose a declared complete control program; inherit actual game physics.\n'
            +'func validate_plan(raw: Variant) -> String:\n'
            +'\tvar error:=super.validate_plan(raw)\n'
            +'\tif not error.is_empty():return error\n'
            +'\tfor command: Dictionary in raw:\n'
            +'\t\tvar trigger: Dictionary=command.get("trigger",{})\n'
            +'\t\tif trigger.has("migration_drop_ready") and (not trigger.migration_drop_ready is bool or trigger.get("state","")!="grounded"):return "invalid_migration_drop_guard"\n'
            +'\t\tif not trigger.has("migration_goal"):continue\n'
            +'\t\tvar goal: Variant=trigger.migration_goal\n'
            +'\t\tif not goal is Array or goal.size()!=4:return "invalid_migration_goal_rectangle"\n'
            +'\t\tfor value: Variant in goal:\n'
            +'\t\t\tif not (value is float or value is int) or not is_finite(float(value)):return "invalid_migration_goal_rectangle"\n'
            +'\t\tif float(goal[2])<=0. or float(goal[3])<=0. or trigger.get("state","")!="grounded":return "invalid_migration_goal_guard"\n'
            +'\treturn ""\n'
            +'func condition_met(state: String) -> bool:\n'
            +'\tif not super.condition_met(state):return false\n'
            +'\tvar trigger: Dictionary=plan[plan_index].get("trigger",{})\n'
            +'\tif trigger.get("migration_drop_ready",false) and is_instance_valid(motor.get("_drop_body")):return false\n'
            +'\treturn not trigger.has("migration_goal") or rect(trigger.migration_goal).has_point(motor.position)\n'
            +'func run_case(data: Dictionary) -> Dictionary:\n'
            +'\tvar routed:=data.duplicate(true)\n'
            +'\tvar probe: Dictionary=data.get("migration_probe",{})\n'
            +'\tvar kind: String=probe.get("kind","")\n'
            +'\tvar selected: Dictionary={}\n'
            +'\tif kind in ["continuous_entry","continuous_exit","local_boundary"]:\n'
            +'\t\tvar port_id: String=probe.get("portId","")\n'
            +'\t\tvar direction: String=("local_"+str(probe.get("direction",""))) if kind=="local_boundary" else ("ingress" if kind=="continuous_entry" else "egress")\n'
            +'\t\tvar all_plans: Dictionary=data.get("migration_boundary_plans",{})\n'
            +'\t\tvar port_plans: Dictionary=all_plans.get(port_id,{})\n'
            +'\t\tif port_plans.has(direction):\n'
            +'\t\t\trouted.control_plan=port_plans[direction].duplicate(true)\n'
            +'\t\t\tselected={"portId":port_id,"direction":direction,"completeControlPlan":true}\n'
            +'\tvar result: Dictionary=await super.run_case(routed)\n'
            +'\tif not selected.is_empty():result.migration_boundary_control=selected\n'
            +'\treturn result\n')
        py=('from pathlib import Path\nfrom importlib import import_module\n'
            +'_original=import_module('+repr(author_path.removesuffix('.py').replace('/','.'))+')\n'
            +'purpose=_original.purpose\n'
            +'SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]\n'
            +'RUNNER_SCRIPT=Path(__file__).with_name('+repr('runner_'+runner_token+'.gd')+')\n')
        directory.mkdir(parents=True,exist_ok=True)
        for path,text in ((runner,gd),(wrapper,py)):
            if path.exists()and path.read_text()!=text:raise ValueError('immutable_boundary_runner_changed')
            if not path.exists():path.write_text(text)
        case.setdefault('generation_rule',{})['registration_source']=core.relative(wrapper)
        record=dict(caseId=case['id'],schema='pcg/boundary-controller-binding/v1',originalAuthorSource=author_path,
            originalRunner=parent_runner,runnerSource=core.relative(runner),wrapperSource=core.relative(wrapper),
            fullPlansSha256=digest(plans),scope='Continuous entry/exit controls only; no geometry or physics implementation changes.')
        case['migration_boundary_control_binding']=record;records.append(record)
    if records:doc['generationContract']['generation']['migration']['boundaryControllers']=records
    return doc,cases,records
