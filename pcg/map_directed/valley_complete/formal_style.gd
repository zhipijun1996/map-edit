extends RefCounted
## Same entry points/default avatar as DemoApp._sync_region_presentation.
## Hidden CourierVisual still owns the authoritative muzzle. No Motor writes.
static func actors(world: Node2D, player: PlayerController, module: PlatformingModule) -> Dictionary:
	world.set_meta("underworld_formal_style",true)
	world.set_meta("pixel_formal_style",true)
	var motor:=player.motor
	# The research runner removed this original presentation node. The formal
	# motion/weapon installer legitimately expects it; restore the original
	# component rather than dropping its accepted-event integration.
	if motor.get_node_or_null("PlayerFeedback")==null:
		var feedback:=PlayerFeedback.new();feedback.name="PlayerFeedback"
		motor.add_child(feedback)
	var body:=PlayerPresentationRuntime.current_body(motor)
	if body==null:
		body=PlayerPresentationRuntime.make_body(motor,player,"PixelPlainsActor","courier")
		motor.add_child(body)
	for key: String in ["CourierVisual","PlayerFeedback"]:
		var legacy:=motor.get_node_or_null(NodePath(key)) as CanvasItem
		if legacy!=null:legacy.hide()
	var adapter:=motor.get_node_or_null("PlayerVisualAdapter")
	if adapter!=null:adapter.process_mode=Node.PROCESS_MODE_DISABLED
	# The main installer attaches the current weapon/motion presentation only
	# when the original sound service exists; don't silently skip that branch.
	if world.get_tree().get_first_node_in_group(&"game_audio")==null:
		var audio:=PlayerWeaponFeelAudioV2.new()
		world.add_child(audio)
	PlayerPresentationRuntime.attach(motor)
	UnderworldActors.install(world)
	module.pixel_mechanism_art=true
	var carriers: Array=[]
	for ferry: ModuleMovingPlatform in module.moving_platforms:
		ferry.set_painted_enabled(true)
		carriers.append({"id":str(ferry.definition.platform_id),"pixel_art_enabled":ferry.pixel_art_enabled,
			"actual_painter":"UnderworldCarrierPaint" if ferry.painted_art is ModuleMovingPlatform.UnderworldCarrierPaint else "missing_or_legacy",
			"formal_material":is_instance_valid(ferry.painted_art)and ferry.painted_art is ModuleMovingPlatform.UnderworldCarrierPaint,
			"texture":str(UnderworldTerrain.mechanism_specification().carrier.texture)})
	var result:={"avatar":"courier","body_class":"PlayerMotionCandidateVisual"if body is PlayerMotionCandidateVisual else str(body.get_class()),
		"body_script":body.get_script().resource_path,"body_matches_main_default":body is PlayerMotionCandidateVisual,
		"legacy_body_hidden":not (motor.get_node("CourierVisual") as CanvasItem).visible,"carriers":carriers,
		"weapon_feel_installed":motor.get_node_or_null("WeaponFeel") is PlayerWeaponFeelV2,
		"motion_feel_installed":motor.get_node_or_null("MotionFeel") is PlayerMotionFeel,
		"ok":body is PlayerMotionCandidateVisual and motor.get_node_or_null("WeaponFeel") is PlayerWeaponFeelV2 and motor.get_node_or_null("MotionFeel") is PlayerMotionFeel and carriers.all(func(row:Dictionary)->bool:return row.formal_material and row.pixel_art_enabled)}
	world.set_meta("formal_style_receipt",result)
	return result
