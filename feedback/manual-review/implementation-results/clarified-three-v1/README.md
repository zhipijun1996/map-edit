# 171 / 174 / 175：按用户澄清完成

**三项均按原 regular 门槛通过，当前冻结审批清单 59/59 在各自声明范围内通过。** 本轮正式验证及接缝补测共 333 次；3 个可玩包、4 条固定回放均原生加载通过。没有修改设计网页、Module 地貌、敌人生命或原游戏物理。

| 编号 | 本轮实际修改 | 当前证据 |
| --- | --- | --- |
| 171 | 保留 42px 低顶通道；0 次跳跃、6 次真实左右交替射击，两枪之间用移动抵消反冲 | [结果与两向统计](171.json) |
| 174 | 左出口改为 ONE_WAY_PLATFORM；位置和可穿支撑不动 | [结果与接口证据](174.json) |
| 175 | 保留地貌、载台路径、3.2s 行程与原 Dock；观察载台前缘，在它从侧面推人之前起跳接乘 | [结果与统计](175.json) |

171 的修正集中在真实输入：防止同一帧连续请求六枪却只接受一枪；依据原 Controller 本帧先更新冷却再开枪的顺序调度；向敌人实际碰撞体上部瞄准，减少反冲离地后的回枪等待；在两枪之间向射击方向移动抵消反冲。触发时的第一枪只读取已声明出生点，弹丸必须在原生敌人真实生成后命中。两向固定样品均有 6 次 accepted shot，方向严格交替、两敌实际击败、跳跃计数为 0。未抬高顶板、未降低怪物血量。

174 的当前授权目标为 [174-authorized-target.json](authorization/174-authorized-target.json)，出处为本次聊天。原发布设计 JSON 不动；冻结 Module 内历史 generation.designFile 保留原人工稿来源，当前授权由 [version-bindings.json](authorization/version-bindings.json) 明确补充绑定到当前 designVersion 与 implementationVersion，不能把旧 ROCK 原稿当成当前可穿出口目标。右侧内部 staging 取原 29px 岸内的安全点；真实 Port 世界坐标未移动。

174 原主路线的校准和独立留出全部通过，原总报告因两项局部接缝夹具失败而保留 FAIL。原 +2px 初始摆放令角色脚底嵌入可穿平台下方，不能作为支持面进入状态；只将这两项改为面上方 -4px，和其余 -2/0px 初态一并覆盖。补测 2 次通过，原几何、能力、程序、原 50 次名义校准/留出及全部 seed/raw 字节保持不变。补充报告使用严格 v6 谱系，原失败不覆盖，也未重抽留出。

175 现在先在安全岸上从地面射击重启随台铃；若被载台遮挡，只进行有限次原生射击重试。落稳后观察载台前缘，合适时机原地起跳，再确认真实 support_id 为 key-carrier 后继续；不再站在扫掠区等待固定相位而被侧面推下岸。起跳、反冲、门开闭、Dock 和承载都由原生消费者执行，没有设置玩家轨迹或补资源。

正式验证仍使用原门槛，**通过不表示每次扰动都成功，也不表示真人通关率 100%**。各方向 clean/mild/moderate 的实数统计在每项 JSON 中；失败、伤害、漏接与未命中均保留。171 两向为 fresh 初态，未据此宣称同世界连续往返；镜像、未测封口配置、任意进入状态与完整 Map 均为 UNKNOWN。

原生样品、影片与复现：

- 可玩包位于 `pcg/manual_review/implementation/clarified-three-final-v1/<moduleId>/playable/`；每项结果 JSON 直接链接 manifest、参数、输入与正式证据。
- 影片 current：171 使用 v2（明确无跳跃提示），174 使用 v3（端口标注按真实可穿支撑），175 使用 v1。均为原生 60Hz、1×、未剪辑全片。**严格逐帧比较均 FAIL，按 review-only 发布并保留全部差异。**
- 174 原 case 的 trace_all 保留到 3000 tick，全片约 51 秒；另提供前 3 秒完整动作加 1 秒全画面停留的 4 秒短片，单独 manifest 标明删除的后续空闲区段；完整原片保留。
- 174 v1/v2 的旧 overlay 曾把可穿支撑误标为 ROCK：JSON 数值为 float，而 GDScript Array.has 对 int/float 类型严格比较；v3 使用显式数值比较修正显示。旧影片原件保留，不算新物理或新独立样本。
- 已实际查看当前 171/174/175 抽帧，检查角色、目标和端口可见性；未声称逐帧观看所有历史影片。

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/clarified-three-final-v1/generated-011d0a163822daaeea61e2280dbe4b26f7f48fa38d57ac30d06110da0634723b/playable/demo.tscn"
```

需要当前仓库的原游戏资源与官方 Godot 4.7.2。默认真实键鼠手玩；追加 `-- --replay` 为固定输入回放，`-- --case 1 --replay` 可选 171 反向样品。

全部原始实验归档 `pcg/archives/approved-clarified-three-v1/`：35 个运行目录，28,981 逻辑文件，1,214 去重条目，3 分片共 24,110,243 字节，整体 SHA256 `96b7a74a5da59ead36d5128ee5999cb1da986a21cfc293320306175fc0bc825f`。已校验每个分片、整体 ZIP 和每个条目。

```sh
python3 -m pcg.tools.restore_archive approved-clarified-three-v1 --verify-parts-only
python3 -m pcg.tools.restore_archive approved-clarified-three-v1 --extract
```

开发阶段的调度错误、未通过控制与后续有界修正阶段均归档，额外尝试逐阶段登记，未把驱动修正或相同条件重放算成新独立留出；每项只运行一次冻结正式方案。正式留出已观测，不应再次运行 qualifier 选择策略；复现优先恢复 raw、核 SHA 和固定回放。

`npm run check` 通过；离线谱系测试 6 项（5 通过、1 已激活场景跳过）。三个正式结果均深度重算通过，870 个原游戏保护文件 SHA 一致。当前仍为隔离候选，未自动 promote 根生产库、合并 PR 或发布站点；人工试玩与生产认可均 UNKNOWN。

入口：[index.json](index.json)、[授权](authorization/request.json)、[几何与实际动作审计](verification/geometry-and-native-audit.json)、[深度验证](verification/deep-proofs.json)、[夹具范围审计](verification/oneway-fixture-scope.json)。
