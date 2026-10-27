extends ModuleMovingPlatformDefinition
## NEW Cell: original first dwell/travel segment, manual signed sampling.
## Original Definition owns travel interpolation; endpoint hold is explicit.
var initial_clock_offset:=0.0
func at_time(clock: float) -> Vector2:
	return super.at_time(clampf(clock+initial_clock_offset,0.0,dwell_duration+travel_duration))
func minimum_clock() -> float:return -initial_clock_offset
func maximum_clock() -> float:return dwell_duration+travel_duration-initial_clock_offset
