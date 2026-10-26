extends "../map_directed/shape_search/visual.gd"
## Execute the same frozen Router policy as headless, rather than round-tripping
## proportional double axis values through Godot's JSON float formatting.
## The existing recorder still compares every physical/input/event field exactly.
func prepare_dynamic_frame()->void:
	replay_mode=false
	super.prepare_dynamic_frame()
