extends "module_loader_ideas_v2.gd"
const APPROVED_HQ=preload('../../manual_review/runtime/revision059_hq_binding_v1.gd')
var approved_hq
func bind_player(player: PlayerController, policy: FrameDamagePolicy, lifetime: DemoLifetime, wallet: RunWallet, existing_scope=null, instance_id: String='') -> Dictionary:
 var original:=content;content=APPROVED_HQ.ordinary(original)
 var result: Dictionary=super.bind_player(player,policy,lifetime,wallet,existing_scope,instance_id);content=original
 if not result.ok:return result
 approved_hq=APPROVED_HQ.new();add_child(approved_hq);approved_hq.setup(original,self,player,scope,cells,rewards);return result
func snapshot() -> Dictionary:
 var result:=super.snapshot()
 if is_instance_valid(approved_hq):result.approved_hq=approved_hq.snapshot()
 return result
