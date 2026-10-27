extends ShotLatch
## Eligibility/session/epoch/real projectile delivery/commit are original.
## Only presentation state is new: westbound is lit; both remain shootable.
func _commit_open(request: Dictionary) -> void:
	var old_count:=open_count
	super._commit_open(request)
	if open_count>old_count:
		is_open=motion_target.signed_direction<0
		prompt_text="WEST / REVERSE AGAIN" if is_open else "EAST / REVERSE AGAIN"
		queue_redraw()
