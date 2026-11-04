---
name: pcg-map-director
description: 保留 MAP_FOUNDATION 对在线 Map 的模型边界，区分 Module 工作与 Map 授权，防止恢复退役入口或把局部认证冒称整图通过。
---

# Current single-source workflow

For current work read [pcg-module-production](../pcg-module-production/SKILL.md) first. Only `modules/<stable-ID>/record.json` and its current source are authoritative. Use `python3 -m module_pipeline`; source/design previews are generated into that ID, and workshop data is derived from `modules/catalog.json` on `main`. Historical round paths, `tools/module_workshop.py`, candidate libraries, migration catalog/promote and batch production commands below are retired examples, not current write targets. Preserve the native physics, causal/holdout and design-quality principles below. A downstream Map consumer reads the explicit versioned package, never old experiments.

# 当前状态：旧生成器退役，新Map不在本轮范围

读根 [MAP_FOUNDATION.md](../../../MAP_FOUNDATION.md)（规范）、[MAP_GENERATION_GUIDE.md](../../../MAP_GENERATION_GUIDE.md)（推荐）和[Module迁移skill](../pcg-module-migration/SKILL.md)。Module 修改、确认设计实现和新生成按[Module 共用工作流程](../pcg-module-factory/references/module-workflow.md)及当前授权分别执行，不能从历史迁移排序或旧任务限制推定权限。本 skill 不自行实现新Map、不恢复旧Map入口/固定骨架/物化链。历史Map代码、旧逻辑图、试件与报告只作参考和证据，不是新系统当前可用入口。

旧 `block_grid.plan`、graph_map、produce等入口不再由本skill推荐执行为新Map流程；本轮不修复旧生成器、不另写替代Map，也不把逻辑图输出称可玩地图。用户以后单独授权新Map工作时，再依据届时可用认证库和真实实现安排；Guide推荐规模不自动触发开工。

# 迁移库须服务的新模型

- 唯一布局网格为Block，默认128像素可配置；Module为完整W×H正整数矩形、实例整数原点、互不重叠。内部地貌像素级、不规则地貌不改变矩形占用，不要求可见边框。
- Port在矩形外边BoundaryBlock外侧边中心；连接点重合、法线相反、surface同类、初始INPUT/OUTPUT/INOUT兼容且接缝认证。ROCK仅左右，ONE_WAY_PLATFORM四面，AIR底边无INPUT/INOUT进入；顶部AIR OUTPUT无合法同类底边INPUT，不作必接向上出口。
- 允许只连接部分Port，不能要求模板总口数恰等于实例连接数；其余使用所属矩形内认证局部封口/天然封闭，实际阻断或可靠终止，视觉荆棘/少量伤害不是封口。封口不得破坏保留Route，受影响组合有认证。
- N×N含自环，每格多Route，正反独立。自环仍需对应初始进出权限；全部实际有效Route进入实际有向图，不能按规划删额外捷径。节点至少区分instance和Port。
- 水平镜像是同base方向变体，完整映射Cell/碰撞/Port/机关/视觉/方向行为，权限语义与Route逻辑起止不交换，矩阵不转置；只用认证方向，不增原创模板计数。
- 未来在线纯程序读取一次静态能力、区域配置和已认证库，以必要能力子集和初始权限过滤/建图；不在线追HP、速度、精力、背包、装备/机关步骤，不在线LLM补Module。动态动作与资源属于离线认证和Godot运行时。

迁移检索采用必要Route/接口/矩形/镜像/可封口性，不用角色标签锁死模板用途。保留全部真实通路与奖励合法去向，未开门的后续连接不能预借给初始图；特殊谜题依赖动态回程需完整结构离线认证。Guide的40–65实例、2–3主路线、5–8奖励支路、库数量和尺寸是建议，非通用硬门槛。

# 本轮输出

只交既有内容的规范差距、最小修改、真实认证、身份/去重/引用和三去向记录。`modules/`与`modules-recycle/`由迁移流程整理，失败与近似待审原处保留；验证/回读之后才归档原件。技术通过、AI设计判断、人工观感、试玩与生产认可独立。

本skill不宣称现有schema、消费者、库编译或验证器已经支持新模型。缺实现具体报告，不用新字段/旧pass重标完成，不自行启动新的Map/Module生产；提交、推送、发布与合并遵循当前任务授权。
