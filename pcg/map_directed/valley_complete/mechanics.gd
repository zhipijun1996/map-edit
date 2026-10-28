extends "../open_valley/mechanics.gd"
## Economy belongs to the original reward and ShopService APIs. No injected
## coins/items; a chest requires its actual opened bell and supported location.
var shop := ShopService.new()
var build := BuildState.new()
var shop_spec: Dictionary = {}
var shop_events: Array = []
var chest_sprites: Dictionary = {}
var merchant: Sprite2D
var host_world: Node2D
var initial_data: Dictionary
var purchase_pending := false
var purchase_required := false
var auto_purchase := false
var parking_events: Array = []

func setup(data: Dictionary, world: Node2D, controller: PlayerController, dynamic_context) -> void:
	super.setup(data,world,controller,dynamic_context)
	host_world=world;initial_data=data
	shop_spec=data.get("valley_shop",{})
	purchase_required=bool(data.get("require_purchase",false))
	auto_purchase=bool(data.get("automatic_shop_input",false))
	build.configure(controller);shop.configure(context.lifetime,build,wallet)
	if not shop.add_offer(&"light-barrel",load("res://resources/items/damage_blue.tres"),8,1): error="invalid_original_shop_offer"
	for item: Node in world.get_children():
		if item is ShotLatch and item.motion_mode: item.opened.connect(_park_event.bind(item))
	for spec: Dictionary in data.get("latches",[]):
		if not spec.has("return_access"):continue
		for item: Node in world.get_children():
			if item is ShotLatch and item.link_id==str(spec.id):item.add_access_bell(Vector2(spec.return_access[0],spec.return_access[1]),false,true)
	# These actors are presentation-only and share the real services' state.
	for node: Dictionary in optional:
		var sprite:=Sprite2D.new();world.add_child(sprite);chest_sprites[str(node.id)]=sprite
		UnderworldObjects.place_chest(sprite,Vector2(node.target.position[0],node.target.position[1]+18),false)
	merchant=Sprite2D.new();merchant.texture=UnderworldActors.icon_texture(&"merchant")
	world.add_child(merchant);UnderworldActors.place_humanoid(merchant,Vector2(shop_spec.position[0],shop_spec.position[1]+18))

func _park_event(bell: ShotLatch) -> void:
	parking_events.append({"frame":context.frame,"bell_id":bell.link_id,"running":bell.motion_target.motion_running,
		"airborne":not actor.motor.is_on_floor(),"position":[bell.motion_target.position.x,bell.motion_target.position.y],
		"motion_clock":bell.motion_target.motion_clock})

func request_purchase() -> void:
	purchase_pending=true

func capture(frame: int, value: Dictionary) -> void:
	super.capture(frame,value)
	for node: Dictionary in optional:
		UnderworldObjects.place_chest(chest_sprites[str(node.id)],Vector2(node.target.position[0],node.target.position[1]+18),services[str(node.id)].claimed)
	var at_shop:=actor.motor.is_on_floor() and actor.motor.position.distance_to(Vector2(shop_spec.position[0],shop_spec.position[1]))<54
	if auto_purchase and at_shop and wallet.balance>=8 and build.count_item(&"damage_blue")==0: request_purchase()
	if not purchase_pending:return
	purchase_pending=false
	if not at_shop:return
	var request:=ShopPurchaseRequest.new();request.token=context.lifetime.token();request.offer_id=&"light-barrel";request.transaction_id=&"valley-shop/barrel"
	var receipt:=shop.purchase(request)
	shop_events.append({"frame":frame,"status":receipt.status,"accepted":receipt.accepted(),"balance":wallet.balance,
		"owned":build.count_item(&"damage_blue"),"position":[actor.motor.position.x,actor.motor.position.y]})

func report() -> Dictionary:
	var value:=super.report()
	value.shop_events=shop_events.duplicate(true);value.owned_items=build.item_ids();value.parking_events=parking_events.duplicate(true)
	value.ok=value.ok and (not purchase_required or build.count_item(&"damage_blue")>0)
	if initial_data.get("require_parking",false):value.ok=value.ok and parking_events.any(func(event: Dictionary)->bool:return event.airborne and not event.running)
	return value
