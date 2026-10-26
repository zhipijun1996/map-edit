# 平原：先批量生产候选，再集中去重和人工审核

入口是已有 [pcg-creative-producer skill](../../.agents/skills/pcg-creative-producer/SKILL.md)，执行 [批次协议](../../.agents/skills/pcg-creative-producer/references/batch-production-v1.md)，从 [campaign-v2](../../pcg/creative-production/plains-campaign-v2.json) 续作。当前Codex会话及用户授权的子代理实际负责创意和实现；程序继续负责有界生成和真实Godot验证。单独运行旧production_loop不会自动发明新玩法，关闭会话后也不会继续在线生产。

```text
用户原话 / Map需求 / 失败与旧库
              ↓
模型每轮5张因果设计卡 → 明显重复预筛 → 缺Cell/规则工单
              ↓                             ↓
        隔离实现可执行配方 ←────── 有界实现/修订
              ↓
原程序搜索 → 原Godot反例/校准/留出 → 技术候选入原库
              ↓                           ↓
   原库跨进程检索与B局部联调        失败回流下一轮提案
              ↓
达到批量或预算结算 → 独立AI分组、选代表 → 人工集中看短视频
              ↓
   代表保留 / 有用适配保留 / 重复折叠 / 待查修订 → 下一批
```

默认每累计20个**新增技术候选版本**集中去重一次；20是审核节奏，不是20个不同玩法的保证。新颖性按玩家判断、人物与世界的因果、资源/状态、恢复及方向差异评估，不按尺寸、标题或Seed计数。原库复用不算新增；不同接口适配保留但不增加玩法家族数。数量不到而预算耗尽也结算，报告实际差距。

每个提案最多两轮源码修订、每接口最多四个控制候选、最多400次真实物理案例；完整原regular门槛和独立留出不能因预算不足省略。最多同时实现两个提案，每批最多补一种Cell。这些是本批预先选定的成本边界，不是已经证明最优的默认参数。失败结果必须持久化并改变后续选择。

创意阶段只挡住明显重复和已知失效条件；详细AI去重放在候选积累后，比较实际内容而不只比较文案。AI去重索引附着原CandidateLibrary：`representative`进入主视频队列，`useful_adapter`保留接口复用，`redundant_variant`折叠，`needs_review`显式待查。所有原件和证据保留。AI相似性不是技术撤回，也不是人类趣味/生产批准。

人工不需逐项批准提案，最后集中看每组代表的短视频，可在聊天直接反馈。设计认可、视频观感、实际试玩和生产认可分别记录。未获生产认可的技术候选仍可以实现、入库和交B局部集成；未知方向与整图结论继续UNKNOWN。

本次用户逐字反馈保存在 [人工来源](../../pcg/feedback/workshop/idea-sources/human-plains-batch-production/v1.json)，其解释和版本关联保存在 [设计反馈](../../pcg/feedback/workshop/plains-five-design-feedback-v1.json)。PR-D01冗余，从新创意队列剔除，但原基础反冲Module不受影响；D02至D05只有设计正向意见。D02开始首轮真实实现，D03/D04待生成规则，D05仍需真实可射击移动支撑Cell，不能用普通平台替代。

已有32个平原优选版本作为首轮AI批次，见 [AI去重和审阅包](../../pcg/creative-production/curation/plains-batch-001-ai-review-v1.md)。这不是32个新家族，也不是本次新生成32个。新内容实验与续作起点另写cycle回执；稳定性要继续用冻结规则对独立新空间的满足率、成本、返工和反馈回归衡量，不能由库规模推断。

后续直接说：`使用 pcg-creative-producer，按 plains-campaign-v2 继续下一批。` 模型会先恢复反馈与回执，再继续创意、实现、验证和批次审核。

## 本轮实际结果与复现

首次AI批次覆盖32个平原版本：18个审阅组/主代表、6个有用适配、8个冗余变体。原库44个版本均保留；分组不等于新增家族。根复核验证138个来源文件绑定与18段不重复代表视频；G07/G12为严格比较失败的review-only片，G06现有索引只有高路，不能把同一片的两个副本当高/低两路。见 [完整性复核](../../generation/workshop/plains-batch-001/verification.json)。本次模型没有新增观看视频或宣称人类观感。

D02实现首试执行4个原生物理探针（3个到达）和13个廉价策略反例。三条岸上提前停台→跳台策略均无伤领奖并稳定到达，运动承载帧数为0，推翻了“持续下降时调整站位”的目的。另一个后侧上台策略有149帧运动承载，下降231.25单位，属于应接受的替代操作。当前停止该版：17例真实物理、完整校准/留出未执行、新入库0。下一修订要消除提前停台的静态跳板绕法，不能只强迫玩家反向走。

恢复这些新原件（不启动物理）：

```sh
python3 pcg/tools/restore_archive.py content-workshop-plains-batch-v1 --extract
```

归档含1551个文件、原始输入/压缩输出、批次命令/日志、冻结源码及源绑定；ZIP SHA为`3ba1048d9e69362c44899d39b0f5bbe48240dc1870dd8f756bd8ed1f5c14d881`。旧代表视频/案例仍用原`content-workshop-creative20-v1`与`content-workshop-plains-method-v1`归档恢复，详见各原报告。

在已备好原Godot运行环境、尚无这两个输出目录的干净worktree中，从仓库根重新执行本轮17个物理案例：

```sh
python3 -m pcg.prototype.creative_batches.descending_carrier.probe_v1
python3 -m pcg.prototype.creative_batches.descending_carrier.counters_v1
```

它们拒绝覆盖已有实验目录；恢复原件用于检查历史，重跑使用新worktree。这两条是本轮原型/反例入口，不是已通过完整门槛的可拼装Module。原编辑器检查与factory规则测试本轮通过；这些软件检查不替代物理门槛。
