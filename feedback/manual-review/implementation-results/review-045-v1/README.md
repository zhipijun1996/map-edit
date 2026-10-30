# 最后一批旧编号审批实现：76 / 82 项技术通过

已同步 main `b18edf952d894fc92d99ac559f45f126938d6788`。本轮冻结开始时的原编号 **82 项获批设计、143 项废弃、0 项待审**；新增/修复 **41、55、57、61、62、115、169、223、225** 共 9 项完成各自声明方向的正式认证，累计 **76 / 82**。main 随后新增批准的 `idea-orbit-choice-001` 不在本轮冻结范围，单独待实现；最新交接总数为 83。见[同步回执](verification/latest-main.json)。

本轮正式 Godot 调用 **2,415 次**，包含 62 的两次精确边界夹具修复；原校准、留出与失败保留。14 个可玩候选均已编译，12 个包的 43 条原生回放通过；51、52 的 4 条原生回放受伤并被拒绝，其包仅供人工操作排查。候选没有直接升入正式库；镜像、封口组合、完整 Map、真人试玩与生产认可仍为 UNKNOWN。

| Module | 结果与范围 |
| --- | --- |
| [41](41.json)、[61](61.json) | 各自主路 PASS，各 69 次；几何相同由人工明确保留，分别实际验证，不另算玩法家族或继承证据 |
| [55](55.json) | PASS，原反冲接近、短距真实钩索；68 次 |
| [57](57.json) | PASS，原主路和两钩实际接触；79 次，不冒称全部四口互通 |
| [62](62.json) | PASS，原三钩主路；原 69 次加 2 次边界夹具修复，名义程序及留出字节不变 |
| [115](115.json) | PASS，双向真实 ferry 承载；169 次，先从岸上清理真实左唇怪再登船 |
| [169](169.json) | PASS，双向跨坑/荆棘，实际早射击制动上升；126 次 |
| [223](223.json) | PASS，四口全部 12 个方向；972 次，原生 12 条回放均无伤 |
| [225](225.json) | PASS，三口全部 6 个方向；487 次，真实空中命中退款后第二反冲 |
| [42](42.json) | UNQUALIFIED，4/6 正式方向 PASS，entry→exit 与 C→exit 的 moderate 校准为 6/12、5/12；这两向留出 NOT_RUN。6 条 clean/原生样品均成功，实际原区域 OR 箱选择 4 金币 |
| [50](50.json) | UNQUALIFIED，6/6 clean 与原生通过；C→entry/exit moderate screen 为 4/6、3/6，低于预登记 5/6 |
| [51](51.json)、[52](52.json) | UNQUALIFIED，连续钩索/中央返程起跳发生真实尖刺接触与 HP4，零无伤方向；附失败影片和原生拒绝回执 |
| [220](220.json) | UNQUALIFIED，4/6 clean/原生方向成功；B/C→A 最后上岸仍失败，真实空中命中与退款已发生 |
| [196](196.json) | DESIGN_CONFLICT，底边 AIR INOUT 与现行 Foundation 冲突；保留原设计，未擅改或重跑 |

各项 JSON 中的 `nativePlayable.path` 指向可玩目录，`videos` 提供影片/manifest/SHA。以 55 为例，在仓库完整原游戏工程内运行：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --path pcg/prototype/godot \
  pcg/manual_review/implementation/review-045-final-v1/game-forest-hollow-upper-candidate-build/playable/demo.tscn
```

使用该包原生场景提供的键盘、跳跃、射击和钩索操作；包本身不是独立发行的完整游戏。51/52 不标为已验证可通关。

## 未完成原因及可改方向

- **42：上层落点、钩索和取箱衔接不稳。** 扰动中一次钩后回落错失上层，后续取箱动作等待超时；C→exit 的跳跃会错过支撑。下一轮可依据真实钩索结束、落地和交互状态调度，不能继续调整本轮已见正式条件。
- **50：第二钩漏接。** C 上行已真实接触下钩，但有噪声时上钩光线/时机失败，随后跌出矩形。应在新的有界轮次观察实际安全施放位置与第一次钩索结束；若要远离柱壁移动上钩或恢复中间落台，属于另需批准的设计修订，本轮没有应用。
- **51/52：控制调度与净空尚未解决。** 起跳后钩索会取消原跳跃请求，不能假定同帧松跳已生效；原钩接触不补枪次。最后方案虽然钩弹碰到第一环，身体仍撞屋顶 danger_0；返程抵达中央地面后左跳触刺。可在新轮次按实际运动分开松跳/施钩，并从中央安全区更内侧起跳。增加落台、移钩、扩大净空或免费补弹均未实施。
- **220：上岸空间与时序，而非退款缺失。** C→A 已完成 3 次真实空中命中，B→A 还利用陆怪再获一次退款；最后反冲仍从 A 岩台下方撞底或到岸过晚。下一轮应先在岩台外上升到顶面上方，再横移落岸；这是待测控制假设，不是设计不可能的证明。
- **196：规范冲突。** 需要另行确定合法接口或修订 Foundation，不能由实现会话自行把底部 AIR 双向口改成别的方案。

50、51、52、220 达到预登记的 7 个控制版本上限；42 已消耗本轮唯一选定正式版本。[工厂 skill](../../../../.agents/skills/pcg-module-factory/SKILL.md) 要求“不能事后提预算、换 seed 或放宽门槛救过”。控制未达标不推断玩家无解，旧轮失败和停止记录均保留。

## 证据与复现

15 段原生录像均为 **review-only**，1 倍、无剪辑、1 秒全世界尾停。51/52 两段明确展示失败，预期退出码 4；未改严格比较器。全部影片保留 workshop 差异，55/57 有 support_id 差异，62 还有少量位置/速度差异，完整逐帧差异随片提供，不计作严格一致。42 的原区域服务实际金币选择另有[消费审计](verification/native-region42.json)。

本会话实际查看了 45 张解码抽帧组成的三张联系表，非全片逐帧观看，见[AI 观感记录](verification/video-observation.json)。[总状态](index.json)、[几何/原生审计](verification/geometry-and-native-audit.json)、[完整正式证明复核](verification/deep-proofs.json)、[版本预算](verification/revision-budget.json)、[原源保护](verification/source-audit.json)、[精确夹具正反测试](verification/oneway62-lineage-tests.json)。870 个原游戏保护文件 SHA 全部不变，设计网页无实现侧编辑。保留 157 上增 1 Block 和 171/174/175 的既有澄清。

显式删除本次新废弃 44、49、53、54、56、58、59、60，累计删除 143，当前正式活动目录 82。所有删除有[事务回执](deletions.json)；未因技术失败删除获批模板。

原始证据归档覆盖 **95 个运行目录、79,002 个逻辑文件、2,259 个去重条目**，8 分片 **83,580,811 字节**，整体 SHA256 `f5db714a4836bbd2a201f0ada6bb7e452e5abbd2e20f46a053b1a449b406ddaa`。已验证分片、整体 ZIP 及每个解压条目。归档不覆盖旧轮原件。

```bash
python3 -m pcg.tools.restore_archive approved-review045-implementation-v1 --verify-parts-only
python3 -m pcg.tools.restore_archive approved-review045-implementation-v1 --extract
python3 -m pcg.manual_review.test_review045_fixtures_v1
python3 -m pcg.manual_review.audit_review045_v1
```

公开链接仅在匿名下载核对 SHA 后追加发布回执。复核命令只读已有正式证据，不重新抽留出；不要重新运行冻结/正式 qualifier 来覆盖原目录。
