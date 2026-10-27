extends "../catalog_feed/extra.gd"
## Actual game RewardService / BuildState / healing / ShopService / Bellstrider.
var build:=BuildState.new()
var items:=RewardService.new()
var shop:=ShopService.new()
var typed_sites:Array=[]
var item_offers:Dictionary={}
var healing:Dictionary={}
var claimed:Dictionary={}
var typed_events:Array=[]
var typed_sprites:Dictionary={}
var host
var actor:PlayerController
var scope
var bosses:Dictionary={}
var boss_events:Array=[]
var contacts:Dictionary={}
var shop_specs:Array=[]
var merchant_sprites:Array=[]
var purchase_pending:=false
var initial:Dictionary
const STATE=preload("../r2_full/state_extra.gd")
var network
var earned_flag_events:Array=[]

func setup(value:Dictionary,world:Node2D,controller:PlayerController,context)->void:
	initial=value;actor=controller;scope=context;host=context.runner
	var ordinary:Dictionary=value.duplicate(true)
	ordinary.reward_sites=ordinary.get("reward_sites",[]).filter(func(s:Dictionary)->bool:return s.get("reward_kind","currency")=="currency")
	super.setup(ordinary,world,controller,context)
	data=value
	var state_data:Dictionary=value.duplicate(true)
	var deferred:Dictionary=value.get("reward_flag_requirements",{})
	for n:Dictionary in state_data.get("r2_semantics",{}).get("nodes",[]):
		n.opens=n.get("opens",[]).filter(func(flag:Variant)->bool:return not deferred.has(str(flag)))
		n.reward=0
	network=STATE.new();network.setup(state_data,world,controller,context)
	for flag:Variant in value.get("initial_opened_flags",[]):network.opened_flags[str(flag)]=true
	build.configure(controller);items.configure(context.lifetime,build);shop.configure(context.lifetime,build,rewards.wallet)
	for spec:Dictionary in value.get("reward_sites",[]):
		var kind:String=spec.get("reward_kind","currency")
		if kind=="currency":continue
		typed_sites.append(spec)
		if kind in ["major_item","hidden_collectible"]:
			var item:ItemDefinition=load("res://resources/items/"+str(spec.item)+".tres")
			var choices:Array[ItemDefinition]=[item]
			var offer:RewardOffer=items.create_cache_offer(StringName(spec.id),choices,StringName("map-source/"+str(spec.id)))
			if offer==null:host.setup_error="invalid_map_item_offer/"+str(spec.id);return
			item_offers[str(spec.id)]=offer
		elif kind=="recovery":
			var def:=SimpleRewardDefinition.new();def.stable_id=StringName(spec.id);def.kind=SimpleRewardDefinition.Kind.HEAL_CURRENT;def.amount=float(spec.amount)
			var service:=SimpleRoomReward.new()
			if not service.configure(def,scope.lifetime,actor.actor_resources.health,rewards.wallet):host.setup_error="invalid_map_recovery";return
			healing[str(spec.id)]=service
		else:host.setup_error="unsupported_map_reward_kind/"+kind;return
		var sprite:=Sprite2D.new();world.add_child(sprite);typed_sprites[str(spec.id)]=sprite
		UnderworldObjects.place_chest(sprite,Vector2(spec.position[0],spec.position[1]+18),false)
	shop_specs=value.get("shop_sites",[])
	for spec:Dictionary in shop_specs:
		if not shop.add_offer(StringName(spec.id),load("res://resources/items/"+str(spec.item)+".tres"),int(spec.price),1):host.setup_error="invalid_map_shop_offer";return
		var sprite:=Sprite2D.new();sprite.texture=UnderworldActors.icon_texture(&"merchant");world.add_child(sprite);UnderworldActors.place_humanoid(sprite,Vector2(spec.position[0],spec.position[1]+18));merchant_sprites.append(sprite)
	for spec:Dictionary in value.get("boss_encounters",[]):
		var motor:BossMotor=(load(str(spec.scene))as PackedScene).instantiate()as BossMotor
		motor.position=Vector2(spec.position[0],spec.position[1]);world.add_child(motor)
		var encounter:BossEncounter=motor.get_node("Encounter")as BossEncounter
		if not encounter.configure_arena(float(spec.arena[0]),float(spec.arena[1]),actor.motor):host.setup_error="invalid_map_boss_arena";return
		var receiver:Damageable=motor.get_node("Damageable")as Damageable
		scope.policy.bind_damageable(StringName(spec.id),receiver,encounter.health)
		encounter.projectile_created.connect(_projectile)
		var contact:=DemoContactEmitter.new();contact.policy=scope.policy;contact.controller=actor;contact.source_id=StringName(str(spec.id)+"_contact");contact.kind=DamageRequest.Kind.MONSTER;contact.half_size=Vector2(64,55);contact.position=Vector2(0,10);contact.enabled=false;motor.add_child(contact)
		bosses[str(spec.id)]={"motor":motor,"encounter":encounter,"spec":spec};contacts[str(spec.id)]=contact

	currency_presentation()

func request_purchase()->void:purchase_pending=true

func currency_presentation()->void:
	for spec:Dictionary in rewards.specs:
		var id:String=str(spec.id);var sprite:Sprite2D=rewards.sprites[id]
		sprite.texture=UnderworldActors.icon_texture(&"coin");sprite.scale=Vector2.ONE*20./sprite.texture.get_width();sprite.position=Vector2(spec.position[0],spec.position[1]+2);sprite.visible=not(rewards.services[id]as SimpleRoomReward).claimed

func _projectile(projectile:BossProjectile)->void:
	projectile.hit.connect(func(body:Node2D,event_id:StringName,amount:float)->void:
		if body!=actor.motor or not scope.lifetime.active:return
		var request:=DamageRequest.new();request.token=scope.lifetime.token();request.actor_epoch=scope.lifetime.actor_epoch;request.health_epoch=actor.actor_resources.health.epoch;request.target_id=&"player";request.source_id=&"map_boss_projectile";request.event_id=event_id;request.amount=amount;request.kind=DamageRequest.Kind.MONSTER;scope.policy.submit(request))

func before_leg(leg:Dictionary,_state:Dictionary)->Dictionary:
	if leg.has("boss_duel"):
		var id:String=leg.boss_duel
		if not bosses.has(id):return {"ok":false,"reason":"required_real_boss_missing"}
		var encounter:BossEncounter=bosses[id].encounter
		if not encounter.active and not encounter.health.terminal:
			var accepted:=encounter.activate();boss_events.append({"frame":scope.frame,"type":"activate","id":id,"accepted":accepted,"hp":encounter.health.current})
			if not accepted:return {"ok":false,"reason":"boss_activation_rejected"}
	return {"ok":true}

func duel_input(id:String,frame:int,anchor:Array)->Dictionary:
	var encounter:BossEncounter=bosses[id].encounter;var motor:BossMotor=bosses[id].motor
	if encounter.health.terminal:return {"done":true}
	var dx:float=float(anchor[0])-actor.motor.position.x
	actor.router.set_move_axis(clampf(dx/12.,-1.,1.))
	var requests:Array=[]
	if (not encounter is WindkeeperEncounter or (encounter as WindkeeperEncounter).accepts_combat_damage())and actor.shoot_ability.cooldown_remaining<=0 and (actor.motor.is_on_floor()or actor.action_resources.shot_charges>0):
		var aim:Vector2=(motor.global_position-actor.motor.global_position).normalized()
		var visual:CourierVisual=actor.motor.get_node("CourierVisual")
		for _i:int in 4:aim=(motor.global_position-visual.muzzle_position(aim)).normalized()
		actor.router.request_action(&"shoot_release",aim);requests.append({"type":"shoot_release","direction":[aim.x,aim.y],"plan_index":host.plan_index})
	if encounter is BellstriderEncounter and (encounter as BellstriderEncounter).mode==&"ring_warning"and actor.motor.is_on_floor():
		actor.router.request_action(&"jump");requests.append({"type":"jump","direction":[0,0],"plan_index":host.plan_index})
	if not actor.motor.is_on_floor()and frame%12==0:
		actor.router.request_action(&"jump_release");requests.append({"type":"jump_release","direction":[0,0],"plan_index":host.plan_index})
	return {"done":false,"requested":requests}

func capture(frame:int,value:Dictionary)->void:
	super.capture(frame,value)
	currency_presentation()
	network.capture(frame,value)
	for discovery:Dictionary in data.get("knowledge_discoveries",[]):
		if not network.opened_flags.has(str(discovery.flag))and actor.motor.is_on_floor()and discovery.targets.any(func(t:Dictionary)->bool:return Rect2(t.region[0],t.region[1],t.region[2],t.region[3]).has_point(actor.motor.position)):
			network.opened_flags[str(discovery.flag)]=true;earned_flag_events.append({"frame":frame,"flag":discovery.flag,"source":"actual_hidden_entrance_discovered"})
	for id:String in bosses:
		var e:BossEncounter=bosses[id].encounter;contacts[id].enabled=e.body_contact_enabled()
		var activation:Array=bosses[id].spec.activation_region
		if actor.motor.is_on_floor()and Rect2(activation[0],activation[1],activation[2],activation[3]).has_point(actor.motor.position)and not e.active and not e.health.terminal:
			var activated:=e.activate();boss_events.append({"frame":frame,"type":"activate","id":id,"accepted":activated,"hp":e.health.current})
	var p:Vector2=actor.motor.position
	if actor.motor.is_on_floor():
		for spec:Dictionary in typed_sites:
			var id:String=str(spec.id)
			if claimed.has(id)or not Rect2(spec.region[0],spec.region[1],spec.region[2],spec.region[3]).has_point(p):continue
			var accepted:=false;var amount:=0.
			if healing.has(id):
				if actor.actor_resources.health.current>=actor.actor_resources.health.capacity:continue
				var receipt:SimpleRewardResult=healing[id].claim(scope.lifetime.token(),StringName("map-claim/"+id));accepted=receipt.accepted();amount=receipt.amount_applied
			else:
				var request:=RewardClaimRequest.new();request.token=scope.lifetime.token();request.offer_id=StringName(id);request.option_id=item_offers[id].candidates[0].stable_id;request.claim_id=StringName("map-claim/"+id)
				var receipt:=items.claim(request);accepted=receipt.accepted()
			typed_events.append({"frame":frame,"id":id,"kind":spec.reward_kind,"accepted":accepted,"amount":amount,"items":build.item_ids()})
			if accepted:claimed[id]=true;UnderworldObjects.place_chest(typed_sprites[id],Vector2(spec.position[0],spec.position[1]+18),true)
		for spec:Dictionary in shop_specs:
			if (not initial.get("automatic_shop_input",false)and not purchase_pending)or p.distance_to(Vector2(spec.position[0],spec.position[1]))>54 or rewards.wallet.balance<int(spec.price)or claimed.has(str(spec.id)):continue
			var request:=ShopPurchaseRequest.new();request.token=scope.lifetime.token();request.offer_id=StringName(spec.id);request.transaction_id=StringName("map-shop/"+str(spec.id))
			var receipt:=shop.purchase(request);typed_events.append({"frame":frame,"id":spec.id,"kind":"shop","accepted":receipt.accepted(),"coins":rewards.wallet.balance})
			if receipt.accepted():claimed[str(spec.id)]=true
	purchase_pending=false
	var earned:Array=claimed.keys()
	for event:Dictionary in rewards.events:
		if event.get("type")=="chest_claim"and event.get("accepted",false):earned.append(str(event.id))
	for flag:String in data.get("reward_flag_requirements",{}):
		if network.opened_flags.has(flag):continue
		var required:Array=data.reward_flag_requirements[flag]
		if not required.is_empty()and required.all(func(id:Variant)->bool:return str(id)in earned):
			network.opened_flags[flag]=true;earned_flag_events.append({"frame":frame,"flag":flag,"actual_claim_ids":required})
	value.graph_map={"bosses":boss_snapshot(),"items":build.item_ids(),"coins":rewards.wallet.balance,"typed_claims":claimed.keys(),"opened_flags":network.opened_flags.keys()}

func boss_snapshot()->Array:
	var values:Array=[]
	for id:String in bosses:
		var e:BossEncounter=bosses[id].encounter;var m:BossMotor=bosses[id].motor
		values.append({"id":id,"hp":e.health.current,"dead":e.health.terminal,"active":e.active,"position":[m.position.x,m.position.y],"combat":(e as BellstriderEncounter).combat_snapshot()})
	return values

func report()->Dictionary:
	var ordinary:Dictionary=super.report();var currency_claims:Array=[]
	for e:Dictionary in ordinary.workshop.events:
		if e.type=="chest_claim"and e.accepted:currency_claims.append(str(e.id))
	var missing:Array=[]
	for id:String in data.get("required_reward_ids",[])+data.get("required_shop_ids",[]):
		if id not in currency_claims and not claimed.has(id):missing.append(id)
	var required_bosses:Array=data.get("required_bosses",[])
	for id:String in required_bosses:
		if not bosses.has(id)or not(bosses[id].encounter as BossEncounter).health.terminal:missing.append("boss/"+id)
	return {"ok":missing.is_empty()and not scope.fatal and network.report().ok,"missing":missing,"workshop":ordinary.workshop,"scenery":scenery,"typed_events":typed_events.duplicate(true),"items":build.item_ids(),"bosses":boss_snapshot(),"boss_events":boss_events,"network":network.report(),"earned_flags":earned_flag_events,"scope":"Actual original economy and encounters; finite whole-world policy, no human fun approval"}
