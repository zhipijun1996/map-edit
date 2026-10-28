# 前 40 项人工审核实现与证据

本轮基于 main `8999c3aa`，在独立分支/worktree 实施已批准的精确设计。40 项中保留 21 项、废弃 19 项。设计 JSON、人工意见与设计网页没有修改。**21/21 保留项本地技术通过，67 条名义路线完成可玩包原生加载回放。** 当前逐项状态和可玩入口以 [index.json](index.json) 及编号 JSON 为准；[此前前 30 项结论](../first-30-v2/README.md) 保留原样，不覆盖历史失败。

## 此前没有完全完成的原因

- **01** 已完成。首轮选择了容不下实际调用量的协议；修正预算预检和到岸控制后重新完成实际验证。旧超预算记录不追认为通过。
- **02/03** 此前真实参数和控制已经修正，但原任务登记的两次修订留出池已用完，技术结论停留 UNKNOWN。这是流程预算和先前驱动问题，不能推出 Module 无解。本轮在新增前 40 项任务授权下，先记录每个精确冻结版本仅一次的[后续验证预算](authorization/continuation-verification-budget.json)，再各分配一次独立池；不重抽种子，不更换候选，不更改原门槛。两件全部路线的校准、独立留出、接缝及反例检查通过（172/176 次）。此记录是本任务的前瞻执行决定，不声称用户单独批准了种子或结果；历史协议和失败保留。
- **17** 此前控制在扰动下不稳定：反冲易越过顶部，回程容易错过已赚取的桥，或撞到中央墙底。修正实际高度触发、接桥和窄道控制后，A→C 与同一世界完整 A→C→A 均通过校准及独立留出。桥、金币、弹药都由原机制产生，未重建世界或注入状态。任意“全新 C 初态→A”仍为 UNKNOWN；它与设计中去程赚取桥状态后的返回分开。出口探针曾在落稳前离岸，保留原失败，仅追加一次修正探针及严格谱系复核。
- **35** 原先前 30 项范围外，本轮才获准实施。三个真实 plains_diver 已接原敌人/伤害/子弹机制。第一份正式控制在中扰动仅 7/12：最后小岸的固定松跳时刻太短撞岸、太长越顶。改为按实际高度松跳，预先固定的三个控制小样均 25/25，按先登记的顺序选第一份；不改设计几何。旧校准失败及其 NOT_RUN 留出保留。可玩包原来误选不支持 diver 的第一批加载器；改用已有的原敌人适配器，已通过实际加载回放。
- **36** 原 1 跳/2 空中射击 fixture 在真实引擎初始化一次，按实际高度、射击冷却与弹量控制，未额外补弹。一次正式执行因代理同时修改共享验证源码而中断，记录 25 次校准、0 次留出；同一冻结候选、同一协议条件在源码稳定后完成验证。此项是执行编排错误，不算设计失败，原中断原样保留。
- **32/34/37/39** 新增的实际路线均完成验证。34 的顶部 C/D 仅入含六条目标路线；旧接口探针误继承过长稳定等待，仅追加 12 次修正接口探针。32/34/37/39 的运行时/观测器来源标签曾错误指向旧通用脚本，实际执行脚本没有换：以不改任何输入/raw/路线/协议的严格谱系修正标签，未新增留出。

现有证据没有证明需要改变设计方案的物理冲突。有限策略失败不能证明玩家无法通过；协议、缺绑定、观察错误、控制失误分别记录。

## 交付范围

可玩包的 `demo.tscn` 可手动操作，A/D 移动、空格跳、鼠标射击；对应案例支持 `--replay` 冻结输入回放。例如：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/first-40-final-v2/game-challenge-ferry-ascent/playable/demo.tscn" -- --case 0
```

21 项均为隔离的实现候选，没有自动替换正式保留项或授予生产认可。17 第二条可玩路线展示原世界完整往返；全新 C 初态、未测进入状态、镜像、封口组合、完整 Map、人工视频评价和真实人工试玩仍 UNKNOWN。

19 个废弃项已按人工结论从 `modules/` 目录和 catalog 删除：08、09、11、13、14、15、16、18、19、20、21、22、24、26、29、31、33、38、40。本轮新增删除 31/33/38/40，catalog 210→206；其余 15 个沿用上一轮删除。[删除回执](deletions.json) 可核查。

新增 7 段实机录像在 [videos](videos/)，包含 17 完整往返与新增六个 module。官方 Godot 4.7.2、60 Hz、1 倍播放、无剪切，保留 1 秒明确尾停留。严格逐帧比较失败的影片均为 review-only，并提供全部差异；这些影片用于观感，不替代通过的物理/原生加载证据。已实际查看其中 6 段片的中段与近结尾抽帧，另查看 35 中段抽帧：完整矩形、真实 Port、主要地貌/机制可见，39 双钩可辨；35 全矩形视图下角色偏小。抽帧记录见 verification/visual-review.json，不声称人工试玩或逐帧看完视频。

## 复核与恢复

使用仓库已有 `godot-runtime-v1` 安装原始游戏资源及 Harness；工具链固定官方 Godot 4.7.2。新增原始音乐、背景及原生 profile UI 资源按原游戏 Git blob SHA 精确恢复，清单见 `restored-*.json`，不以占位资源替代。当前 raw、失败、校准筛选、源码快照和新增原始资源归档到 `pcg/archives/approved-first40-implementation-v1`；此前两轮归档继续保留。

```sh
python3 pcg/tools/restore_archive.py approved-first40-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-first40-implementation-v1 --extract
python3 pcg/tools/restore_archive.py approved-first30-implementation-v2 --extract
python3 pcg/tools/restore_archive.py approved-designs-batch001-implementation-v1 --extract
python3 -m pcg.manual_review.audit_first40_evidence_v1
python3 -m pcg.manual_review.index_first40_v1
npm run check
python3 -m unittest pcg.migration.tests.test_godot_package pcg.migration.tests.test_holdout_guard pcg.migration.tests.test_pool_protocols pcg.migration.tests.test_offline_reanalysis pcg.migration.tests.test_review_air_runtime
```

索引重建和证据审计只读复核既有证明，不启动新的校准或留出。历史 Harness 的绝对 extends 需 `/workspace/map-edit-task-a` 指向当前仓库；可玩包不使用控制搜索。原游戏 870 个保护文件 SHA 不变；42 个框架回归通过（1 个跳过）。新增谱系/篡改检查见 [verification/evidence-audit.json](verification/evidence-audit.json)，视频抽帧/ffprobe 和仓库检查日志同目录。公网链接仅在匿名下载并核对 SHA 后写入单独回执。

本轮归档核验通过：56 个运行目录、9 个精确恢复的原始资源、45,162 个逻辑文件；17 分片，172,460,023 字节，整包 SHA `a2cc9c382e9110bf19a8f5192c03b3e59dc9c382be8fe3b4c706eabfa00617dd`。
