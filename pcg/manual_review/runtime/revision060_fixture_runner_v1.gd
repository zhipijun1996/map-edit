extends "revision060_runner_v2.gd"
const BARRIER_PROOF=preload('revision060_barrier_observer_v1.gd')
var barrier_proof
func make_fixture(data: Dictionary) -> void:
 await super.make_fixture(data);barrier_proof=BARRIER_PROOF.new();world.add_child(barrier_proof);barrier_proof.setup(world,context)
func run_case(data: Dictionary) -> Dictionary:
 var r: Dictionary=await super.run_case(data)
 if not r.get('rejected',false):r.barrier_evidence=barrier_proof.events.duplicate(true)
 return r
