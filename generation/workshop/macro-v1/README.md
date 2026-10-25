# 双宝箱回程 Macro · 第一批

先看 [31 秒合集](videos/overview.mp4)：[M01 取宝并返回](videos/M01.mp4)、[M02 另一尺寸](videos/M02.mp4)、[M03 漏接后恢复重试](videos/M03.mp4)。均为真实 Godot 原生输入回放，1 倍，段内无剪辑。

录像严格比较有 18 帧 `support_id` 顺序差异；其余位置、速度、输入、资源、机关/奖励事件一致。**0 段计为全字段精确录像**；完整差异见 [视频 manifest](videos/manifest.json)。录像用于观感，不代替技术留出。

2 个三端口 Macro 候选、4 份组成 Module 版本依赖；未增加第七动作家族。450 条新留出中 444 条满足目的，各路线组均通过原 regular 门槛；完整去回程 48/50，故意漏接恢复另为 26/26。生产认可、人工试玩、新 Macro 观感及整图验收未完成。

- [完整报告与运行命令](../../../docs/l4-mapgen/content-workshop-macro-v1.md)
- [标准文档与 SVG 清单](modules/manifest.json)
- [需求试件](specifications.json) / [具体接缝](internal-seams.json)
- [审计](audit.json) / [持久化复用](retrieval.json) / [提案与失败反馈](proposal-feedback.json)

`review_cases.json` 可通过原工坊 `main.tscn -- --cases-json ...` 加载，包含完整循环、分段方向和恢复试件。原始源码、失败、输入/输出、录像 trace 与日志恢复归档 `content-workshop-macro-v1`；原六家族交付仍在 `../v2/`。
