# Batch30 增量预算审计 v3

**固定截止 2026-10-27T08:58:26.992715+00:00：Harness 输入尝试 16,671，原生录制命令 58；保守合计 16,729，距 24,000 上限剩 7,271。** 不是后续运行的实时余额，不增加任何预算。

相对 v2 已核的 1,605 份输入／15,642 案例与 49 条录制，本轮新增 121 份输入／1029 案例及 9 条录制。v1 尾段 44 已在 v2 计入，本次未重复收费。

| 新增 run | 输入份数 | 尝试案例 | 有帧 | 零帧 | 缺结果 |
| --- | ---: | ---: | ---: | ---: | ---: |
| batch30-blockn13-cheap-v2 | 1 | 4 | 4 | 0 | 0 |
| batch30-blockn13-clean-v2 | 1 | 4 | 4 | 0 | 0 |
| batch30-blockn13-core-v2 | 1 | 3 | 3 | 0 | 0 |
| batch30-blockn13-counters-v2 | 2 | 20 | 20 | 0 | 0 |
| batch30-blockn13-noise-v2 | 1 | 12 | 12 | 0 | 0 |
| batch30-blockn13-repair-clean-v1 | 1 | 2 | 2 | 0 | 0 |
| batch30-blockn13-repair-counters-v1 | 1 | 8 | 8 | 0 | 0 |
| batch30-blockn13-repair-noise-v1 | 1 | 12 | 12 | 0 | 0 |
| batch30-blockn13-repair-return-v1 | 1 | 7 | 7 | 0 | 0 |
| batch30-blockn13-return-v2 | 1 | 5 | 5 | 0 | 0 |
| batch30-blockn18-core-v1 | 1 | 8 | 8 | 0 | 0 |
| batch30-blockn18-core-v2 | 1 | 8 | 8 | 0 | 0 |
| batch30-blockn18-position-controls-v1 | 1 | 4 | 4 | 0 | 0 |
| batch30-blockn19-api-clean-v1 | 1 | 2 | 2 | 0 | 0 |
| batch30-blockn19-core-v1b | 1 | 8 | 7 | 1 | 0 |
| batch30-blockn19-core-v2 | 1 | 8 | 8 | 0 | 0 |
| batch30-blockn19-counters-v1 | 2 | 24 | 24 | 0 | 0 |
| batch30-blockn19-noise-v1 | 2 | 24 | 24 | 0 | 0 |
| batch30-blockn19-recovery-v1 | 1 | 12 | 12 | 0 | 0 |
| workshop-batch30-blockn12-counters-v1 | 2 | 14 | 14 | 0 | 0 |
| workshop-batch30-blockn12-full-v1 | 4 | 38 | 38 | 0 | 0 |
| workshop-batch30-blockn12-full-v2 | 7 | 70 | 70 | 0 | 0 |
| workshop-batch30-blockn12-full-v3 | 19 | 170 | 170 | 0 | 0 |
| workshop-batch30-blockn12-noise-v1 | 1 | 12 | 12 | 0 | 0 |
| workshop-batch30-blockn12-second-core-v1 | 1 | 4 | 4 | 0 | 0 |
| workshop-batch30-blockn14-core-v1 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn14-core-v2 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn14-counters-v1 | 2 | 14 | 14 | 0 | 0 |
| workshop-batch30-blockn14-full-v1 | 18 | 154 | 154 | 0 | 0 |
| workshop-batch30-blockn14-noise-v1 | 2 | 24 | 24 | 0 | 0 |
| workshop-batch30-blockn16-core-v1 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn16-core-v2 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn16-counters-v1 | 1 | 7 | 7 | 0 | 0 |
| workshop-batch30-blockn16-full-v1 | 10 | 77 | 77 | 0 | 0 |
| workshop-batch30-blockn16-noise-v1 | 2 | 24 | 24 | 0 | 0 |
| workshop-batch30-blockn16-return-v1 | 1 | 1 | 1 | 0 | 0 |
| workshop-batch30-blockn17-core-v1 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn17-core-v2 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn17-critical-v1 | 1 | 7 | 7 | 0 | 0 |
| workshop-batch30-blockn17-fourport-core-v2 | 1 | 8 | 8 | 0 | 0 |
| workshop-batch30-blockn17-more-v1 | 1 | 6 | 6 | 0 | 0 |
| workshop-batch30-blockn17-noise-v1 | 1 | 12 | 12 | 0 | 0 |
| workshop-batch30-blockn19-full-v1 | 19 | 164 | 164 | 0 | 0 |

新增结果有帧 1028，零帧 1，缺结果 0；缺执行元数据 0，输出数量不符 0、结果ID不符 0、同路径SHA冲突0。新增原生录制有 trace 9 条，共 2264 帧。失败、零帧、重跑和表现重录命令均计成本；有帧不等于技术通过或独立校准。

原 14 份归档复用 v1/v2 完整核验，仅复核 manifest 身份；本次新核 5 份封装的分片／整ZIP SHA及逻辑索引。相同原路径+SHA只计一次；归档文件数量、去重复对象数和包装版本均不是实验次数。所有 1,605 份基线原输入逐路径比较当前可见SHA，变更会拒绝结算。

活动 probe 原上限仍各80：
- B31-N17：截止内原输入 49，本案余 31。
- B31-N18：截止内原输入 20，本案余 60。

若仅用完上述既有两案的剩余 probe，形式上余额 7,180；未预扣未来 full／留出／录像，也不是扩预算授权。

活动输入结果尚未完成的尝试在 JSON missing_result_inputs 单列并足额收费，本截止缺 0 案例；之后的新结果不追补为本截止通过。未持久化或被覆盖调用、其他 worktree 仍 UNKNOWN。

本审计0 Godot调用、不改原件／源／库／预算。原输入、结果、执行、原生命令、每批帧数、归档与截止来源的SHA见 [JSON原账](budget-audit-v3.json)。
