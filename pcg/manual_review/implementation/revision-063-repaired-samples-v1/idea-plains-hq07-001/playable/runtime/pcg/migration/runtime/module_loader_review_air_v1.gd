extends "module_loader_v3.gd"
const REVIEW_AIR=preload("../../manual_review/runtime/air_enemy_binding_v1.gd")
func bind_player(player: PlayerController, policy: FrameDamagePolicy, lifetime: DemoLifetime, wallet: RunWallet, existing_scope=null, instance_id: String="") -> Dictionary:
	var original_enemies: Array=content.enemies
	content.enemies=REVIEW_AIR.ordinary(content).enemies
	var result:=super.bind_player(player,policy,lifetime,wallet,existing_scope,instance_id)
	content.enemies=original_enemies
	if result.ok:REVIEW_AIR.install(content,self,player,scope,cells)
	return result
