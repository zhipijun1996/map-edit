extends "module_loader_review_refresh_v1.gd"
const BOOTSTRAP=preload("../../manual_review/runtime/refresh_carrier_bootstrap_v1.gd")
func bind_player(player: PlayerController, policy: FrameDamagePolicy, lifetime: DemoLifetime, wallet: RunWallet, existing_scope=null, instance_id: String="") -> Dictionary:
	var result:=super.bind_player(player,policy,lifetime,wallet,existing_scope,instance_id)
	if result.ok and not refresh_consumers.is_empty():
		var bootstrap=BOOTSTRAP.new();bootstrap.observed=refresh_consumers;add_child(bootstrap)
	return result
