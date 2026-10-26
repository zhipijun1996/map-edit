# D04 continuous validation and actual design refutation

Original D04 source/contracts unchanged. `run_v1` was interrupted after the parent requested physical-program dedup; 288 submitted cases are conservatively counted, all completed outputs retained (including orphan last output). `run_v2` adds412 actual cases, total700; it reuses old i0 results and executes i1 four distinct middle controls plus one reward control. `equivalent-programmes.json` binds identical reward programs by original candidate hash plus Cell/reward hashes; aliases are not new physics executions.

`pcg/results/workshop-batch30-d04-full-fixtures-v2/summary.json` is the actual receipt. i0 reward-return calibration clean12/mild12/moderate7 failed regular. i1 middle/reward continuous routes selected from calibration and frozen before independent held261028011; held rates12/12/11 and12/12/10 pass original regular. Fixtures add zero Modules and make no generic return assertion.

However, actual adaptive falsifiers invalidate the proposed parking tradeoff: from middle-parked world, B-fall-x780-dy.5 plus floor recovery completes A→B→C chest→A in6shots/4jumps/626frames (i0),643frames(i1). Nominal reward parking takes7shots/6jumps/701,711frames; even the legitimate return-shot omission alternative6shots/6jumps/707frames is dominated. More decisively, middle obtains C first at241/249frames using3shots/1jump and **zero carrier support** before C, while reward parking reaches C at360/368frames using3shots/2jumps with31 carrier support frames. See `claim-cost-analysis-v1.json`. Final desired park is explicitly ignored in this task comparator. Technical route success cannot establish an interesting choice.

Tail-only repair protocol/rules/program were preregistered but **not run (0 cases)** after this counterexample. The old i0 tail overshoot exists (three moderate failures fire last vertical shot nearx353 rather than stagingx300); fixing it alone cannot repair a dominated reward branch. Root holds original two admitted records from the30 target and authorizes a new isolated `batch30_d04r2/` geometry cycle in rootprotocol-v6/v7. All prior originals/failures stay immutable.

Reproduce old cycle (fresh run directories):

```sh
python3 -m pcg.prototype.creative_batches.batch30_d04_validation.run_v1 --name fresh-d04-fixtures-v1
# v2 is a provenance-bound continuation of the recorded namedv1 run, not a clean standalone retry.
python3 -m pcg.prototype.creative_batches.batch30_d04_validation.run_v2 --name fresh-d04-fixtures-v2
```

No human fun/physical playtest/production approval is implied. Actual clips not yet recorded by this task.
