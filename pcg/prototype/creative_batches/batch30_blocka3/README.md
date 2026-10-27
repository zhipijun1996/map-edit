# A3 短时风铃门 · Block128 双向适配

冻结入口 `api_v1.py`，由原 `batch30_runtime.produce_v3` 执行 root index 13，两接口都要求 A→B 与 B→A，不允许单向代替。当前仅小样通过，原 regular 校准/独立留出及候选入库由根任务执行，人工趣味、试玩、生产批准均 UNKNOWN。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_IMMUTABLE_NAME \
  --rules pcg.prototype.creative_batches.batch30_blocka3.api_v1 \
  --index 13 --interfaces 0 1
```

原始用户 A3、两份 timed-cache 候选及真实 `rules.timed`、`gate_window`、`transitions`、`ShotLatch` 绑定见 `source-baseline-v1.json`。这次保留内部通道与完整恢复底岸；原右端墙挡住真正东边界，因此生成规则明确将上墙内移，并开出 64px 地面口。双口锚点 [0,320] W / [768,320] E，身体检查点 [24,334] / [744,334]，51 个不规则 Block，外接尺寸为 128 倍数。没有新增物理、Map 铺路、传送或资源恢复。

去程观察短门与对岸，跳后向左下铃射击，同一枪使人右上反冲、真实弹丸开门、全身体穿门到东岸。回程使用原 `return_access`：地面重开门、左行落恢复岸、真实回枪后跳射回西岸。首两种空中直接返回只到恢复底岸，不能回入口，其 4 次失败完整保留；没有用对称假设继承回程。合法多枪预开/重试按实际因果与成本评估，不要求复现名义序列。

本次明确提供**无奖励 Map traversal 变体**：实际 `6c864ae` 的 exp0_0 请求 rewards=[]，原图 `required_pairs` 精确要求 e23↔e24，暂映射 A↔B，见 `map-input-v1.json` / `required-pairs-v1.json`。用户 A3 原文不要求宝箱；旧 12 币候选保持不变。本次不声称保留旧取箱动机，也不自动承诺相邻图布局/状态或整图可行。

`protocol-v1.json` 在执行前登记 2 规则 / 80 probe。实际用 1 规则、80 次：clean 6/10（按 first-valid 冻结四路线），独立于选择的 mild/moderate 每路线各 6 次，48/48；每方向 5 个精确廉价反例，共 20 次无反驳；两次同世界 A→B，停至实际闭门，再重开返回 A，2/2（481/482 帧、3 枪 2 跳，未重建世界）。API 每条精确方向提供 20 个完整几何绑定反例，包括省枪、普通长跳、越顶、地面预开门、付费二枪、恢复底路。尚未测试的 full 反例可能推翻设计。

原 0.55s / 0.65s 窗口未改。实测去程弹丸飞行 3–5 ticks，开门到全身体清门最多 21 / 27 ticks；回程飞行 8–10 ticks、全身体清门 11 ticks。当前观察窗口余量至少 12 ticks，不能把原防夹延迟算余量。原 `gate_rect.grow(24)` 防夹与实际碰撞行为完全保留，身体检查为每帧 24×36 AABB。门测量使用原实际射击/开门/门状态，不用中心点代替身体。

小样复现入口（每次必须新 run 名，禁止覆盖原件）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_blocka3.probe_v1 --name NEW_CLEAN --stage clean
python3 -m pcg.prototype.creative_batches.batch30_blocka3.probe_v1 --name NEW_SCREEN --stage screen
python3 -m pcg.prototype.creative_batches.batch30_blocka3.probe_v1 --name NEW_COUNTERS --stage counters
python3 -m pcg.prototype.creative_batches.batch30_blocka3.roundtrip_v1 --name NEW_RETURN
```

冻结选择已存在，`clean` 为保护原件会在结果写完后拒绝覆盖选择文件；需要完整新生产周期时，应另开版本目录而不是覆盖。现存所有原输入、压缩 raw、源码快照和证据在 `pcg/results/batch30-blocka3-{clean,screen,counters,roundtrip}-v1`。`probe-receipt-v1.json` 汇总实际计数、失败与源码 SHA。通用接缝、任意入口资源/动态相位与完整 Map 仍 UNKNOWN。

## 原完整校准/留出结果

root index13 full-v1实际308案例，两空间四方向全部原regular通过；所有cal/held clean1/1、mild12/12、moderate12/12。两版入库5afb538d…/f7a091b3…。正向两native各157帧严格比较通过。一次反向native仅frame60 normal_velocity/support_id不同，原strict失败、无公开MP4；完整trace/原日志保留。

强反例另有合法地面预开+空中反冲：去程多一枪（2枪）141帧，较名义1枪157帧更快；回程同2枪159/160帧也比底岸名义220帧快。它们是真实可用替代，不因不复现指定序列而拒绝。名义展示同枪开门/反冲，但不宣称它对所有解必要；底岸是经过验证的恢复策略，也不宣称唯一返程。
