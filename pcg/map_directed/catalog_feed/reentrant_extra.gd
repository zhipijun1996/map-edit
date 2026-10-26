extends "extra.gd"
func report()->Dictionary:
	var v:Dictionary=super.report();var count:=0
	for event:Dictionary in v.workshop.events:
		if event.type=="chest_claim"and event.accepted:count+=1
	v.reward_claims=count
	v.ok=v.ok and count<=int(data.get("reward_claim_limit",2))and v.workshop.coins<=float(data.get("maximum_coins",48))
	v.scope="Real whole-world rewards; main route must claim zero, excursions must earn named chests"
	return v
