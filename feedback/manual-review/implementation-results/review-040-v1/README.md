# 审批刷新 040：新增 5 项通过，4 项控制未达标

已合入 main `9a232db349f014d960fb3a97f09eb36726269062`，冻结本轮新增 9 项已审批设计。**166、167、202、204、206 完成正式验证，累计 67 / 72 项在各自声明范围内技术通过。** 本轮正式 Godot 验证 1,082 次，9 个可玩候选包的 29 条回放原生加载通过；未合格项目只交付成功路线样品。镜像、封口组合、完整 Map、人工试玩及生产准入仍为 UNKNOWN。

| Module | 当前结果 | 实机代表片 |
| --- | --- | --- |
| [166](166.json) | PASS，低口到高口及独立返程，123 次正式调用 | [上行](videos/166-entry-to-exit-v3/original-game-recoil_shaft.mp4) |
| [167](167.json) | PASS，四口 12 个方向，678 次正式调用 | [左下到右上](videos/167-entry_left-to-exit_upper_right-v4/original-game-route_junction.mp4) |
| [202](202.json) | PASS，实际取 10 金币、开门通行及独立返程，127 次 | [去程](videos/202-entry-to-exit-v3/brake-gate-catch.mp4) / [返程](videos/202-exit-to-entry-v3/brake-gate-catch.mp4) |
| [204](204.json) | PASS，低顶下观察真实齿轮相位，88 次 | [通行](videos/204-entry-to-exit-v3/saw-pursuit.mp4) |
| [206](206.json) | PASS，真实领取 14 金币后释放底板，再完整身体穿过 AIR 出口，66 次 | [奖励与底口](videos/206-entry-to-exit-v3/trapdoor-commit.mp4) |
| [115](115.json) | UNQUALIFIED；返程 screen 为 clean 1 / mild 6 / moderate 6，去程未达标；原生包仅含返程 | [34.6 秒完整返程](videos/115-exit-to-entry-v3/original-game-moving_transfer.mp4) |
| [220](220.json) | UNQUALIFIED；5/6 无扰动方向成功，C→A 未通过 | [B→A 成功样品](videos/220-B-to-A-v3/windgap-junction.mp4) |
| [223](223.json) | UNQUALIFIED；12/12 clean 成功，C→D moderate 4/6 低于 5/6；完整原生包 C→A 掉血，失败保留；另供 A→C 单路线可玩包 | [C→D 无扰动见证](videos/223-C-to-D-v3/gate-brake-return.mp4) |
| [225](225.json) | UNQUALIFIED；4/6 无扰动方向成功，B→A/C 未通过 | [A→C 成功样品](videos/225-A-to-C-v3/one-shot-two-routes.mp4) |
| [196](196.json) | 继承 DESIGN_CONFLICT；底边 AIR INOUT 与现行 Foundation 冲突；本轮未跑该版本物理 | [原冲突记录](../review-031-v1/196-design-conflict.json) |

实际视频文件名和 SHA 以各项 JSON 的 `videos` 为准。10 段录像均为 **review-only**：原严格比较器保留全部 workshop 快照差异，202 去程、167、206 还存在 support_id 差异，没有把它们改成严格通过。原生位置、输入、资源和全部差异仍可复核；不能用影片替代正式证据。1 倍速度、无剪辑，含 1 秒全画面尾停。AI 实际查看了 [10 张解码抽帧](verification/video-contact-sheet.jpg)，未声称看完每一帧，见 [观感记录](verification/video-observation.json)。两个显示服务启动失败的目录、日志及首次 167 Route 选择错误也保留。

## 未完成原因和下一步

- **115 是控制问题，尚未证明设计有缺陷。** 随机 ferry 相位可使原生承载怪停在台左唇，先登船再开枪会碰怪；最后的岸上开枪策略又在尚未返回 x240 时发出第二枪，把玩家反冲出左边界。下一轮应以实际位置、支撑和反冲结束状态作为再次射击的前置条件，先清左唇怪再登船。原生承载使用实际 ferry 位移和 `move_and_collide`，未直接改怪物 transform。
- **220 的 C→A 消耗了唯一枪次。** 先地面反冲再尝试空中射击，后一次请求被原能力拒绝。下一步可从 (500,562) 复用已成功的 B→A 攀升，并观察空中怪向右的真实窗口；这是待测方案，不能算通过。
- **223 仍有 C 入口战斗和落脚时序问题。** 最后一版改善了顶台落脚，C→D 仍有受伤及 apex 超时。原生完整回放 C→A 在 317 帧时为 HP4，不能用 Harness clean 成功掩盖；原完整失败包留在 `playable/`，交付入口为独立 `playable-representative-v1/`，只验证 A→C。
- **225 还没有稳定的真实空中命中退款。** B 到内部台高差 320px，普通跳加一次反冲约 304px，单次反冲不足；最后的短诱导跳在 0.6 秒预警完成前落地，敌人停止攻击，因此等待俯冲高度超时。下一轮可测试保持敌人激活的完整诱导跳，再用真实空中命中续枪。不擅自降低平台、搬怪或加弹。
- **196 需要设计决策。** 保持底 AIR 可改为仅出并删去从底口进入的目标；若保留上攀目标，需要重新审批实际支撑/端口方案或先修订 Foundation。未自行修改。

四项控制未合格项目均达到 [预登记预算](authorization/request.json) 的初版加 6 次修订上限。依 [Module 工厂 skill](../../../../.agents/skills/pcg-module-factory/SKILL.md)“不能事后提预算、换 seed 或放宽门槛救过”，本轮不增加版本或运行留出。有限搜索失败不证明 Module 无解；逐项失败、下一步假设和完整成功/失败路线均在各项 JSON 中。

## 实现、测量修正和来源

静态岩台、危险、轨迹、矩形、端口位置与权限语义保持审批设计。32×32 敌人图示按原 EnemyDefinition 的 28×32 碰撞体解码：空中怪保留中心、地面怪保留脚底中心；没有改变原生敌人尺寸。206 的图稿 `OUT` 规范化为实际格式 `OUTPUT`。223 的新审批稿已不包含旧 Macro 的门和组件出口，按同一 Module 的真实 Cells 编译，原来源 Macro 原样保留。这些格式适配不构成新模板或改图。

206 新增真实奖励提交后释放支撑的消费者，只有原 `SimpleRoomReward` 接受交易并置为 claimed 才关闭底板碰撞，未写玩家坐标、生命、能量或枪次。原生包和视频增加只读 OPEN 表现，显示真实碰撞释放状态。

166 原总报告因越出矩形的替代反例误作内部通路而失败；206 原总报告因 AIR 终态观测器错误覆盖本地 ROCK 入口稳定计数而失败。两者均保留原报告、原输入及留出，只读重分析真实 raw。206 六个本地入口试验重新计算连续站稳帧，完整身体、孔径、方向、健康和无重置门槛继续保持；重分析新增物理调用和独立留出均为 0。[观测器实际数据及拒绝变体测试](verification/boundary-observer-tests.json)、[反例归因测试](verification/counter-scope-tests.json)、[完整证据复核](verification/deep-proofs.json)。

本轮明确废弃 **75 项已删除**，活动库 **165→90**，累计删除 **135 项**。删除了指向已废弃主项 112 的悬空 alias，历史重复原件和实测保留；见 [删除回执](deletions.json) 与 [alias 回执](retired-aliases.json)。169、41、42 尚未审批，未实施。157 顶部加一格和 171/174/175 的既有澄清版本继续保留。

## 可玩入口与复核

每项 JSON 的 `nativePlayable.path` 指向对应样品，使用完整仓库原项目资源及官方 Godot 4.7.2。默认手动输入：A/D 移动、空格跳跃、鼠标射击；加 `--replay --case 0` 可复播绑定路线。223 请使用单路线代表包，115 包只包含返程。示例：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/review-040-final-v1/game-route-junction/playable/demo.tscn" -- --replay --case 0
python3 -m pcg.tools.restore_archive approved-review040-implementation-v1 --verify-parts-only
python3 -m pcg.tools.restore_archive approved-review040-implementation-v1 --extract
python3 -m pcg.manual_review.audit_review040_observers_v1
python3 -m pcg.manual_review.audit_review040_v1
```

归档覆盖 65 个运行目录、54,652 个逻辑文件、1,744 个去重条目，4 分片共 36,998,029 字节；整体 SHA256 `8ba242ff8d6cf9aeb835608161fd3665f2e3aeb79d124bfcc35bdc7f11d69b52`。已校验各分片、整体 ZIP 与每个条目。原游戏保护清单 870 文件逐一核 SHA，无修改；设计网页未修改。[总状态](index.json)、[几何/原生审计](verification/geometry-and-native-audit.json)、[来源审计](verification/source-audit.json)。公开下载另追加 commit 固定 URL 与 SHA 回执。
