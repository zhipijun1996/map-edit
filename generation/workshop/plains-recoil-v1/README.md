# 当前反冲平原内容库

用户已对上一批20项给出整体正向视频意见。当前平原能力限定移动、普通单跳、射击反冲。

- 统一库44版本，平原视图32候选版本；数量包含接口适配和Macro，不等于玩法家族。
- 上批20种中11种能力兼容，9种高级能力留作后续区域。
- 原六个核心反冲关系的12个Module、1个Map适配、2个Macro现已归拢原库。
- 11个兼容项里包含躲锯、射击改世界和操作顺序等辅助职责，不都算反冲教学。

[完整库状态和方法](../../../docs/l4-mapgen/plains-recoil-method-v1.md) · [候选索引](catalog.json) · [真实用户反馈](../../../pcg/feedback/workshop/creative20-positive-video-v1.json) · [固定创作流程](../../../.agents/skills/pcg-creative-producer/references/plains-recoil-workflow.md)

本轮先检验两个已有配方响应四种新空间：[10秒四段原生录像](adaptation-four.mp4)。4/4通过原regular；跨进程4/4复用。新增家族0，方法稳定性仍需后续跨空间与反馈修订验收。

[能力越界拒绝回执](unsupported-ability-response.json) · [冷批结果](workshop-plains-method-adapt-v1.json) · [新进程复用](workshop-plains-method-warm-v1.json) · [标准需求入口](workshop-plains-request-entry-v1.json)

恢复后从仓库根执行：

```sh
python3 pcg/tools/restore_archive.py content-workshop-creative20-v1 --extract --prefix results/
python3 pcg/tools/restore_archive.py content-workshop-plains-method-v1 --extract
python3 -m pcg.prototype.creative_batches.plains_workshop.catalog_v1
python3 -m pcg.prototype.creative_batches.plains_workshop.produce_v1 --examples > demands.json
python3 -m pcg.prototype.creative_batches.plains_workshop.produce_v1 --name fresh-plains-demand --specifications demands.json
```

现阶段配方优先级：安全教学 → 控制练习 → 世界组合 → 可选奖励 → 同世界回程与恢复。新摆放和整图仍由B验证，UNKNOWN不因入选视图而获得拼装资格。
