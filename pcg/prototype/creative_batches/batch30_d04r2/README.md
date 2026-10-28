# D04 repaired reward gap: exact east160 candidate

`api_v1.py` freezes one rule (`rules_v1.py`) over two interface demands. This is the same D04 parking decision, not a second gameplay family. Initial world, player, original projectile/ShotLatch/carrier, and quality/noise are unchanged. C's actual bank, external port, chest and control goals move160 units east. A shot during the outgoing jump leaves the carrier in the middle for the short direct return, or farther east as an actual launch support for C. Return fixtures preserve the same world and chest transaction; their A-return goal never becomes a fake second A port.

Old D04 records remain immutable and design-held: an actual middle-park alternative reached the old C chest119 frames earlier without ever supporting on the carrier. The repair changes geometry rather than insisting on authored button order or the final desired park. Old evidence/costs are not erased.

The first112/120 preregistered probes are complete, with rules version2 and8 probes unused:

- Initial i0: both forward routes and both continuous returns demonstrate their purposes,4/4. Reward route actually uses the parked carrier; same-world reward loop returns to A with12 coins.
- Second-interface clean plus original small perturbations:48/52. All four failures are the same i0 moderate-trial2 outgoing/catch timing perturbation across programs; no gate has been lowered. i1 samples all pass. Full regular calibration and independent held are still required.
- Original active middle-park falsifiers in the new exact world:0/32 same-task reward successes across both interfaces. Some safe no-reward recovery programs return to A, which is recorded separately from obtaining C.
- Additional i0 floor-bank-climb policies and later B falling shots:0/24 actual C-reward successes. Search domains are in `counter_rules_v1.py`; this is finite counterexample search, not proof no other route exists.

`probe-receipt-v1.json` binds commands, source snapshots and raw batches. Old rule probes248 and old full cases1126 remain in the lineage. New cycle full budget1600, calibration261030001 and held261030002 are registered by rootprotocol-v7. No new full case or admission was performed by this probe task. Human fun, playtest and production approval remain UNKNOWN.

Reproduce initial/small-noise/strong-counter probes in fresh directories:

```sh
python3 -m pcg.prototype.creative_batches.batch30_d04r2.probe_v1 --name fresh-d04r2-east160
python3 -m pcg.prototype.creative_batches.batch30_d04r2.probe_v2 --name fresh-d04r2-noise
python3 -m pcg.prototype.creative_batches.batch30_d04r2.probe_v3 --name fresh-d04r2-counter
```

`api_v1.layouts(recipe,interface)` supplies standard forward Modules, `fixtures(interface)` supplies validation-only same-world returns, and `adaptive_counters(interface)` supplies complete-task falsifiers. `alternatives` includes27/52 exact-case policies: the reward-route extra alternatives intentionally leave the middle park and compare actual C attainment. Their own actual world requirement is retained so the producer cannot silently reject them merely for differing from the nominal east park. Missing real carrier use is checked only after the external reward/safety/capability goal is actually achieved. Different shots or timing alone are accepted alternatives.
