extends "foundry_feedback_runner_v5.gd"
# Observer only: native TraversalAbility reports actual hook collision points.
var source_hook_contacts: Array=[]
func make_fixture(case: Dictionary) -> void:
	source_hook_contacts=[]
	await super.make_fixture(case)
	controller.traversal.hook_contact.connect(func(position: Vector2):
		var nearest:="";var distance:=INF
		for spec: Dictionary in case.get("hooks",[]):
			var d:=position.distance_to(Vector2(spec.x,spec.y))
			if d<distance:distance=d;nearest=str(spec.source_id)
		source_hook_contacts.append({"frame":context.frame,"source_id":nearest if distance<=20. else "UNKNOWN","position":[position.x,position.y],"distance":distance}))
func run_case(case: Dictionary) -> Dictionary:
	var result: Dictionary=await super.run_case(case)
	result.original_hook_contacts=source_hook_contacts.duplicate(true)
	return result
