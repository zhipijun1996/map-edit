extends RefCounted
## Read only: original actors, rays and original projectile disappearance.
var host
var seen: Dictionary={}
var pending_hits: Dictionary={}
var exits: Array=[]

func setup(runner) -> void:
	host=runner;seen={};pending_hits={};exits=[]

func body_label(body: Object) -> String:
	if body==host.motor:return "player"
	for latch in host.cells.latches:
		if body==latch.gate_body:return "pair/"+str(latch.link_id)+"/A"
		if latch.has_method("snapshot_pair") and body==latch.paired_gate_body:return "pair/"+str(latch.link_id)+"/B"
	if body is EnemyMotor:return "enemy_body"
	return "other_static_body"

func projectile_left(shot: EnemyAttackProjectile) -> void:
	var live: bool=is_instance_valid(shot.behavior) and shot.behavior._active()
	exits.append({"frame":host.context.frame,"event_id":str(shot.event_id),"position":[shot.global_position.x,shot.global_position.y],"spent":shot.spent,"remaining":shot.remaining,"source_active_at_exit":live,"last_actual_world_sweep_hits":pending_hits.get(str(shot.event_id),[]).duplicate()})

func snapshot() -> Dictionary:
	var rays: Array=[]
	var shots: Array=[]
	var space=host.motor.get_world_2d().direct_space_state
	for actor: EnemyActor in host.cells.enemies:
		var origin: Vector2=actor.motor.global_position
		var ray:=PhysicsRayQueryParameters2D.create(origin,host.motor.global_position,1,[actor.motor.get_rid()])
		var hit: Dictionary=space.intersect_ray(ray)
		rays.append({"enemy":str(actor.definition.stable_id),"enemy_position":[origin.x,origin.y],"player_position":[host.motor.global_position.x,host.motor.global_position.y],"distance":origin.distance_to(host.motor.global_position),"activation_range":actor.definition.activation_range,"enemy_alive":not actor.health.terminal,"actual_original_can_engage":actor.attack_behavior._can_engage() if actor.attack_behavior!=null else false,"ray_hit":"clear" if hit.is_empty() else body_label(hit.collider),"ray_hit_position":[] if hit.is_empty() else [hit.position.x,hit.position.y]})
	for child: Node in host.world.get_children():
		if not child is EnemyAttackProjectile:continue
		var shot:=child as EnemyAttackProjectile
		var key:=str(shot.event_id)
		if not seen.has(key):
			seen[key]=true
			shot.tree_exiting.connect(projectile_left.bind(shot))
		var query:=PhysicsShapeQueryParameters2D.new()
		query.shape=shot._shape;query.transform=Transform2D(0,shot.global_position);query.motion=shot.direction*shot.speed/60.0;query.collision_mask=1
		query.exclude=[shot.behavior.actor.motor.get_rid()]
		var overlaps: Array=space.intersect_shape(query,8)
		var fraction: float=0.0 if not overlaps.is_empty() else 1.0
		if overlaps.is_empty():
			var cast: PackedFloat32Array=space.cast_motion(query)
			fraction=cast[1] if cast.size()==2 else 1.0
		var labels: Array=[]
		if fraction<1.0 or not overlaps.is_empty():
			query.transform.origin+=query.motion*minf(1.0,fraction+0.001);query.motion=Vector2.ZERO
			var hits: Array=overlaps if not overlaps.is_empty() else space.intersect_shape(query,8)
			for item: Dictionary in hits:labels.append(body_label(item.collider))
		labels.sort();pending_hits[key]=labels
		shots.append({"event_id":key,"position":[shot.global_position.x,shot.global_position.y],"direction":[shot.direction.x,shot.direction.y],"remaining":shot.remaining,"spent":shot.spent,"actual_world_sweep_hits":labels})
	return {"rays":rays,"projectiles":shots,"projectile_exits":exits.duplicate(true)}
