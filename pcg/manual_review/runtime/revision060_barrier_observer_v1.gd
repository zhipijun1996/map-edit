extends Node
## Passive original PlayerProjectile signals, no collision or state writes.
var world
var scope
var watched: Dictionary={}
var latest: Dictionary={}
var events: Array=[]
func setup(root: Node,context) -> void:world=root;scope=context;process_physics_priority=-1
func _physics_process(_delta: float) -> void:_scan(world)
func _scan(node: Node) -> void:
 for child: Node in node.get_children():
  if child is PlayerProjectile and not child.spent:
   var id:=child.get_instance_id()
   if not watched.has(id):
    watched[id]=true;child.terrain_impacted.connect(_terrain.bind(child,id));child.tree_exiting.connect(_disposed.bind(child,id))
  _scan(child)
func _terrain(point: Vector2,_direction: Vector2,p: PlayerProjectile,id: int) -> void:
 for deck: ModuleMovingPlatform in scope.module.moving_platforms:
  if str(deck.definition.platform_id)!='P'or deck.collision_layer!=8:continue
  var rect:=Rect2(deck.position-deck.definition.size*.5,deck.definition.size).grow(p.radius+.1)
  if rect.has_point(point):latest[id]={'type':'original_projectile_hit_barrier','frame':scope.frame,'shot_id':p.shot_id,'faction':str(p.faction),'position':[point.x,point.y],'native_terrain_impacted_signal':true,'barrier_layer':deck.collision_layer,'remaining_before_dispose':p.lifetime-p._age}
func _disposed(p: PlayerProjectile,id: int) -> void:
 if latest.has(id)and p.spent and p.lifetime-p._age>0:
  var event: Dictionary=latest[id].duplicate();event.original_spent=true;event.remaining_after_dispose=p.lifetime-p._age;events.append(event)
