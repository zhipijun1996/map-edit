extends "../valley_complete/rock_mechanics.gd"
## Earned return flags come from actual original chest service receipts.
func capture(frame: int, value: Dictionary) -> void:
	super.capture(frame,value)
	for node: Dictionary in optional:
		if services[str(node.id)].claimed:
			for flag: Variant in node.get("opens",[]):opened_flags[str(flag)]=true
