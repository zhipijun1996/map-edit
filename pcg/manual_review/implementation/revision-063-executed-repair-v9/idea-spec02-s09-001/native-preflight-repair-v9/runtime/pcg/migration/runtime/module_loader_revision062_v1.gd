extends "module_loader_revision061_v2.gd"
const MOUNT062=preload('../../manual_review/runtime/revision062_mount_v1.gd')
func bind_player(player: PlayerController,policy: FrameDamagePolicy,lifetime: DemoLifetime,wallet: RunWallet,existing_scope=null,instance_id: String='') -> Dictionary:
 var result: Dictionary=super.bind_player(player,policy,lifetime,wallet,existing_scope,instance_id)
 if result.ok:MOUNT062.install(content,scope,cells)
 return result
