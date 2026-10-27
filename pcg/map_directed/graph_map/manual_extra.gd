extends "extra.gd"
## Present the existing real network/economy ledger to the manual UI.
func report()->Dictionary:
	var result:Dictionary=super.report()
	var state:Dictionary=result.network
	result.visited_nodes=state.get("visited_nodes",[])
	result.opened_flags=state.get("opened_flags",[])
	result.wallet_balance=rewards.wallet.balance
	return result
