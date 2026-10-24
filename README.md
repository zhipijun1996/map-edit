# 失序之钟 · 关卡生成工坊 / Map Notes

本仓库现在以**离线自动生成高质量动作 Module**为主要任务：动作语法、真实Godot验证、质量多样性搜索、失败修复与短视频反馈。原Map Notes草图编辑器继续保留，作为设计与审阅工具。

- [最新三端口Module短视频 T](https://zhipijun1996.github.io/map-edit/generation/videos/plains-three-port-v1/all-samples.mp4)（约16.7秒） · [实验报告](pcg/PLAINS-THREE-PORT-REPORT.md)
- [生成研究与短视频下载](https://zhipijun1996.github.io/map-edit/generation/)
- [最新平原连续挑战 R · MP4](https://zhipijun1996.github.io/map-edit/generation/videos/plains-round2/all-samples.mp4)（约17.3秒，正常速度） · [本轮报告](pcg/PLAINS-REVIEW-ROUND2.md)
- [草图编辑器](https://zhipijun1996.github.io/map-edit/) · [编辑器原说明](docs/map-notes-editor.md)
- [生成工作区与恢复命令](pcg/WORKSPACE.md) · [迁移与本轮实验报告](pcg/MIGRATION-AND-NEXT.md)

L4 与 Module 联动研究：[L4研究报告](docs/l4-mapgen/report.md) · [区域探索修订](docs/l4-mapgen/region-exploration-revision.md) · [工作台](experiments/l4-mapgen/WORKBENCH.md)。PR #1 保留隔离实验，正式流程未改。

当前完整Map实验：[R2多环路真实落地与限制](docs/l4-mapgen/full-r2-playable-v1.md)，27场所/39连接，实际连续巡视覆盖74有向边，另有闭环视频与真实风铃库补缺；仍是内容不足的可玩结构候选。媒体在 `generation/maps/r2-full-v2/`。

历史小motif技术闭环：[v1实现与证据](docs/l4-mapgen/map-driven-library-v1.md)。用户已指出其范围太小、安全连接过长；不作为完整区域的设计验收。

## 开始研究

`pcg/`保留原研究程序的相对布局，可直接运行Python模块；并非只有报告或预制模块压缩包。

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py research-results-v1 --extract --prefix results/factory-production-v1/
# 将官方Godot4.7.2放到pcg/toolchain，具体SHA与导入命令见pcg/WORKSPACE.md
cd pcg
python3 -m prototype.factory.core.producer --name new-run --tier regular
python3 -m prototype.factory.compare_landing_repairs --name guided-new-run
```

当前程序不调用大模型生成每个模块；AI辅助开发与分析，生成、搜索和验证由程序执行。固定角色物理，不把反复墙跳/二段跳恢复循环当道具库存。未实现的新能力/机关不能只添加名称。优先证明Module质量，再扩Macro/Map与Runtime。

## 资料与资产

- `pcg/prototype/`：算法、真实输入worker、自动评价、回放与录像脚本。
- `pcg/research/`及各阶段`*-REPORT.md`：论文、开源代码/许可、架构审计和算法结论。
- `pcg/archives/`：完整旧实验原件、870份固定运行素材/脚本、审阅产物；每片与整体有SHA，不只保存成功。引擎、Godot缓存和可重建AVI不重复提交。
- `pcg/results/`：可直接查看的紧凑结果；大轨迹从归档恢复，旧失败不覆盖。
- `generation/`：发布短视频及观察入口，Pages仅部署这一部分和原编辑器，不上传原始轨迹/源码资产归档。
- `.agents/skills/`：生产实验、物理合同、视频评审三项可复用方法，按实际反例和数据迭代。

## 人工反馈方式

默认看短视频即可，直接说“样例03等待太久”“样例01路线难读”等，不要求亲自试玩或填写网页。观感意见进入设计返工；操作手感/真实玩家成功率保持未知，不把看视频计为手动试玩。当前还没有真实观感评分或批准模块。

Factory05已完成1002次真实物理运行，strict regular有4待评+2返工；这不等于稳定量产好玩成品。本轮继续比较轨迹指导落点修复与盲参数变异，选择使用校准集，新留出不参与搜索。一次相关家族试验不能证明任意能力和区域都适用。

## 开发检查

```sh
npm run check
cd pcg && python3 -m unittest discover -s prototype/factory/tests -v
```

编辑器库绑定游戏74d8a06；当前生成物理绑定12f6cb0。两个版本均原样保留，不混用回执。正式游戏没有因本次迁移被改写，编辑器工程仍不自动回写游戏。

本轮平原生成见[PLAINS-REPORT](pcg/PLAINS-REPORT.md)：仅单跳/反冲，围绕击钟同时抬升、真实命中回充后二次反冲、低顶棚后齿轮时机三种动作关系生成；[下载短视频](https://zhipijun1996.github.io/map-edit/generation/videos/plains-v1/all-samples.mp4)。技术候选尚待人类观感反馈。

后续生成的Module/Macro按[输出契约](pcg/OUTPUT-CONTRACT.md)交付，继续使用Map Notes工程格式。[查看模块图及JSON](https://zhipijun1996.github.io/map-edit/generation/contracts/plains-v1/)；UNKNOWN关系保持不可自动拼装。
