extends SceneTree
## TEST ONLY: use the package's existing loader and the locked native player.
const REGISTRY=preload("res://module_pack/integration/module_registry.gd")
const PLAYER=preload("res://scenes/player/player.tscn")
const CAPS=preload("res://module_pack/integration/player_capabilities.gd")
var output:=""
var rows: Array=[]
var errors: Array=[]
var serial:=0

func _initialize() -> void:
    for arg: String in OS.get_cmdline_user_args():
        if arg.begins_with("--report="):output=arg.trim_prefix("--report=")
    run.call_deferred()

func verify(ok: bool, label: String) -> void:
    if not ok:errors.append(label);push_error(label)

func make_fixture(baseline: String, mid: String, at: Vector2, seal_rect: Array=[]) -> Dictionary:
    serial+=1
    var world:=Node2D.new();root.add_child(world)
    var motor: PlayerMotor=PLAYER.instantiate();motor.get_node("PlayerFeedback").free();motor.position=at;world.add_child(motor)
    var player: PlayerController=motor.get_node("Controller");player.enable_shot_energy()
    CAPS.apply(player,["move","jump","shot_recoil"]);player.set_physics_process(false)
    motor.get_node("KeyboardMouseAdapter").set_process_unhandled_input(false)
    var lifetime:=DemoLifetime.new();var wallet:=RunWallet.new();var policy:=FrameDamagePolicy.new();policy.lifetime=lifetime;world.add_child(policy);policy.register_player_controller(player);policy.register_target(&"player",player.actor_resources.health,true)
    var registry=REGISTRY.new();registry.open("res://module_pack")
    var instance: Node2D
    var bound: Dictionary
    if baseline=="main":
        instance=load("res://main_sample/module.tscn").instantiate();instance.position=Vector2(128,-76);world.add_child(instance)
        bound=instance.bind_player(player,policy,lifetime,wallet,null,"audit/main/"+str(serial))
    else:
        bound=registry.instantiate_module(mid,"audit/pkg/"+str(serial),Vector2i.ZERO,world,player,{"policy":policy,"lifetime":lifetime,"wallet":wallet})
        if bound.get("ok",false):instance=bound.instance
    verify(bound.get("ok",false),"fixture_bind:"+mid+":"+baseline)
    var seal: StaticBody2D
    if not seal_rect.is_empty():
        seal=StaticBody2D.new();seal.name="AuditedSeal";seal.position=Vector2(seal_rect[0]+seal_rect[2]/2.0,seal_rect[1]+seal_rect[3]/2.0);seal.collision_layer=1
        var shape:=CollisionShape2D.new();shape.shape=RectangleShape2D.new();shape.shape.size=Vector2(seal_rect[2],seal_rect[3]);seal.add_child(shape);world.add_child(seal)
    await physics_frame;await process_frame
    var shape: CollisionShape2D=motor.get_node("CollisionShape2D")
    verify(shape.shape.size==Vector2(24,36),"native_body_size")
    return {"world":world,"motor":motor,"player":player,"wallet":wallet,"policy":policy,"lifetime":lifetime,"instance":instance,"registry":registry,"seal":seal,"shape":shape.shape}

func overlap_seal(f: Dictionary, at: Vector2) -> bool:
    if not is_instance_valid(f.seal):return false
    var q:=PhysicsShapeQueryParameters2D.new();q.shape=f.shape;q.transform=Transform2D(0,at);q.collision_mask=1;q.exclude=[f.motor.get_rid()];q.margin=0
    var hits: Array=f.world.get_world_2d().direct_space_state.intersect_shape(q)
    return hits.any(func(hit: Dictionary) -> bool:return hit.collider==f.seal)

func dispose(f: Dictionary) -> void:
    f.player.shoot_ability.clear_projectiles();f.world.queue_free();await process_frame;await process_frame

func wind(baseline: String, start: Vector2, shoot: bool=true) -> void:
    var f: Dictionary=await make_fixture(baseline,"game-plains-windchime-lesson",start,[0,128,32,128])
    var overlaps:=overlap_seal(f,start)
    var initial_valid: bool=not overlaps and start.x>=12 and start.y>=18
    var row:={"baseline":baseline,"module":"game-plains-windchime-lesson","spawnOwnedPixels":[start.x,start.y],"sealOwnedPixels":[0,128,32,128],"nativeSealOverlap":overlaps,"initialPlacementValid":initial_valid,"shootStrategy":shoot}
    if not initial_valid:
        row.status="REJECT_INITIAL_OVERLAP_OR_OUTSIDE";rows.append(row);await dispose(f);return
    f.player.set_physics_process(true)
    for i: int in 30:await physics_frame
    row.initialGrounded=f.motor.is_on_floor();row.standingOwnedPixels=[f.motor.global_position.x,f.motor.global_position.y]
    var latch: ShotLatch=f.instance.cells.latches[0]
    var count:={"shots":0};f.player.shoot_ability.shot_fired.connect(func(_d: Vector2,_id: int):count.shots+=1)
    var fired:=false
    var target_x:=744.0 if baseline=="main" else 496.0
    var fire_x:=268.0 if baseline=="main" else 140.0
    for tick: int in 300:
        var dx: float=target_x-f.motor.global_position.x
        f.player.router.set_move_axis(clampf(dx*5.5/f.motor.tuning.ground_speed,-1,1))
        if shoot and not fired and f.motor.global_position.x>=fire_x-3 and f.motor.is_on_floor():
            var target: Vector2=latch.bell_body.global_position
            var aim: Vector2=(target-f.motor.global_position).normalized()
            var visual: CourierVisual=f.motor.get_node("CourierVisual")
            for j: int in 4:aim=(target-visual.muzzle_position(aim)).normalized()
            f.player.router.request_action(&"shoot_release",aim);fired=true
        await physics_frame
    f.player.router.set_move_axis(0)
    var arrived: bool=f.motor.is_on_floor()and absf(f.motor.global_position.x-target_x)<3
    row.merge({"bellOpenCount":latch.open_count,"actualShots":count.shots,"arrivedAtExitDock":arrived,"finalOwnedPixels":[f.motor.global_position.x,f.motor.global_position.y],"hp":f.player.actor_resources.health.current,"wallet":f.wallet.balance,"status":"OBSERVED_CANDIDATE" if arrived else "BLOCKED"})
    verify(row.initialGrounded,"wind_initial_grounding")
    if shoot:verify(arrived and latch.open_count>0 and count.shots>0 and f.player.actor_resources.health.current==5,"wind_shoot_to_exit:"+baseline+":"+str(start.x))
    else:verify(not arrived and latch.open_count==0,"wind_no_shot_control")
    rows.append(row);await dispose(f)

func orbit() -> void:
    var f: Dictionary=await make_fixture("package","idea-orbit-choice-001",Vector2(24,334),[256,0,128,32])
    var probes: Array=[]
    for at: Vector2 in [Vector2(320,14),Vector2(340,18),Vector2(312,0),Vector2(368,40)]:
        var hit:=overlap_seal(f,at);verify(hit,"orbit_closed_claim_body_overlap");probes.append({"centerOwnedPixels":[at.x,at.y],"nativeSealOverlap":hit})
    rows.append({"baseline":"package","module":"idea-orbit-choice-001","configuration":"C_closed_exact_user_geometry","sealOwnedPixels":[256,0,128,32],"probes":probes,"status":"CLAIM_REGION_PHYSICALLY_BLOCKED","closedConfigurationCertified":false})
    await dispose(f)
    # Independent original-content control. The audited closed fixture is never opened or repaired.
    f=await make_fixture("package","idea-orbit-choice-001",Vector2(320,14))
    f.player.set_physics_process(true)
    for i: int in 45:await physics_frame
    var claimed: bool=f.instance.rewards.services["reward"].claimed
    verify(claimed and f.wallet.balance==4 and f.motor.is_on_floor(),"orbit_original_claim_semantics")
    rows.append({"baseline":"package","module":"idea-orbit-choice-001","configuration":"original_open_content_control_only","sourceStandingPixels":[320,14],"grounded":f.motor.is_on_floor(),"actualRewardClaimed":claimed,"wallet":f.wallet.balance,"events":f.instance.rewards.events,"scope":"Native standing/claim semantics only; not a full Route or closed-C witness."})
    await dispose(f)

func run() -> void:
    for baseline: String in ["package","main"]:
        await wind(baseline,Vector2(0,192))
        await wind(baseline,Vector2(24,206))
        await wind(baseline,Vector2(0,0))
        await wind(baseline,Vector2(48,206))
        await wind(baseline,Vector2(64,206))
        await wind(baseline,Vector2(140,206))
        await wind(baseline,Vector2(64,206),false)
    await orbit()
    var report:={"schema":"map-edit/runtime-readiness-probes/v1","passed":errors.is_empty(),"engine":Engine.get_version_info().string,"actorBodyPixels":[24,36],"mainSourceCommit":"9b712fe814ef228b368c0eb9adf660e39de29e37","historicalPackageVersion":"1.1.0","windSealAssumption":"Unmirrored map-gen stable-v2 default 32px left seal; actual map/next-neighbor seam not supplied.","rows":rows,"errors":errors,"scope":"Targeted fixed-condition audit observations. No module edits, new spawn declaration, closed/mirrored certification, or whole-map proof."}
    var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"  ")+"\n");file.close();print("RUNTIME_READINESS_AUDIT ",JSON.stringify({"passed":errors.is_empty(),"rows":rows.size(),"errors":errors}));quit(0 if errors.is_empty()else 4)
