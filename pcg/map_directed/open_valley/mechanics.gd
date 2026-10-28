extends "../direct_join/challenge_extra.gd"
## Original ShotLatch opens its real gate and releases an original carrier.
## Only Cell signal composition; no actor coordinates/resources are assigned.
var release_events: Array = []
func setup(data: Dictionary, world: Node2D, actor: PlayerController, dynamic_context) -> void:
	super.setup(data,world,actor,dynamic_context)
	for spec: Dictionary in data.get("latches", []):
		if not spec.has("starts_ferry"): continue
		var found: ModuleMovingPlatform
		for ferry: ModuleMovingPlatform in context.module.moving_platforms:
			if str(ferry.definition.platform_id) == str(spec.starts_ferry): found = ferry; break
		if found == null: error = "missing_linked_original_carrier"; return
		var bell: ShotLatch
		for child: Node in world.get_children():
			if child is ShotLatch and child.link_id == str(spec.id): bell = child; break
		if bell == null: error = "missing_linked_original_bell"; return
		found.bind_bell_control()
		bell.opened.connect(_release.bind(found,str(spec.id)))
func _release(ferry: ModuleMovingPlatform, bell_id: String) -> void:
	if not ferry.motion_running:
		ferry.set_motion_running(true)
		release_events.append({"frame":context.frame,"bell_id":bell_id,"ferry_id":str(ferry.definition.platform_id),"motion_clock":ferry.motion_clock})
func report() -> Dictionary:
	var value := super.report()
	value.carrier_release_events = release_events.duplicate(true)
	return value
