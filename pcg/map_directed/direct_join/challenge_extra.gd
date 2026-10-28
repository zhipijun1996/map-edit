extends "../r2_full/bell_extra.gd"
## A visit alone cannot satisfy the optional real shot-latch challenge.
var required_challenges: Array = []
func setup(data: Dictionary, world: Node2D, controller: PlayerController, dynamic_context) -> void:
	required_challenges = data.get("required_optional_challenges", []).duplicate()
	super.setup(data, world, controller, dynamic_context)
func report() -> Dictionary:
	var value := super.report()
	var missing: Array = []
	for key: Variant in required_challenges:
		if not services.has(str(key)) or not services[str(key)].claimed: missing.append(key)
	value.missing_optional_challenges = missing
	value.ok = value.ok and missing.is_empty()
	return value
