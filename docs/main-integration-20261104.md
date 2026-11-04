# main 整合记录（2026-11-04）

本次按“全部合并 main”整合 PR77、PR21、PR1，保留已合入 main 的 PR78。原始 head、实际测试提交、输出哈希和结果见 [机器记录](../evidence/main-integration-20261104.json)。

| 来源 | 处理 |
|---|---|
| PR77 `c2e23fec` | 统一源库、生产工具、现有 1.1.1 交付物进入 main；不重新发布 |
| PR78 / main `da1d6120` | 原审计、冻结 930001 和 actual-profile producer 原样保留 |
| PR21 `8d40619c` | 授权预检、失败归因已包含于现行生产 skill；保留现行流程及该 PR 合并祖先 |
| PR1 `9838516e` | 早期隔离意图由统一库取代；保留完整 Git 合并祖先与两份标明历史范围的隔离说明，不恢复 94-candidate 生产副本或旧 Map 入口 |

唯一源库仍是 `modules/<稳定ID>/` 与工具生成的 `modules/catalog.json`：115 个已实现可交付模块、3 个开发设计、148 条退役记录。后续新增、修订、审批、认证、废弃和打包只使用 [现行生产流程](module-production.md)。数量和版本以 catalog/record 为准，不另设人工维护清单。

PR1 两份归档说明中的历史命令只适用于原 head，原始全部文件可从该 commit 恢复。PR21 原候选迁移入口不覆盖现在的原子更新工具。两者的提交 ancestry 均进入本次合并，避免再次把旧目录作为未集成内容恢复。

## 本次验证

- `npm run check`：当前目录、内容/证据哈希、编辑器/工坊、正式更新来源和 38 项 foundation 检查通过。
- `npm run test:production`：14 项通过，包含重复 ID、缺文件、错版本、未声明依赖、事务回滚、退役及交付包可重复构建。
- `python3 tools/build_editor_site.py --out <临时目录>`：115 个当前模块、3 个开发设计；543 个资源闭包完整，无历史网页资源或旧 catalog。
- `python3 tools/runtime_audit/verify_actual_profile.py --inputs <实际输入目录> --zip110 <历史1.1.0.zip> --legacy-inputs <冻结930001输入> --zip111 <已有1.1.1.zip> --work <新临时目录>`：旧 43 输入/10 输出逐字一致；default 13 组/109 对象，gears 14 组/110 对象；38 个上游及 48 个新增拒绝反例、2 个输出覆盖保护通过，原输入未改变。精确输入获取与绑定仍以 [actual-profile 交接](runtime-integration-audit/actual-profile-04.md) 为准。
- `git diff --exit-code c2e23fec -- modules runtime integration module_pipeline`：零差异；本次没有改模块、运行时或宿主依赖，未重复运行全部原生 Godot 资格验证。

CI 同时执行现有 7 项审计单元检查；actual-profile 的完整外部输入复验不以单元检查替代。此次 producer 输出所有新行仍为未验证；“数据提取成功”不升级为“宿主适配成功”。钟门下一轮仍需精确新宿主 commit 及真实执行证据。

## 版本边界

PR78 初次审计中的“main”是冻结 `9b712fe8` 的 82 项库，并非本次 main；原文历史对比与原 Godot 证据不回写。对应机制文档的旧 main 样本链接已固定到该 commit。

下游继续锁定历史 1.1.0：SHA-256 `5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723`。现有 1.1.1 与五项奖励关联变化保留在 PR77 原证据和 PR78 迁移条件中；合并源库不修改历史 ZIP，不自动升级 map-gen 或主游戏，不授予新的镜像/封口/奖励认证。此次没有发布新包。
