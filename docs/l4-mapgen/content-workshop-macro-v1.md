# 内容工坊续作：双宝箱回程 Macro v1

本轮交付 **2 个空间接口的真实局部 Macro 候选**：空中击铃穿短门取第一箱，在岩沿外反冲刹入下层取第二箱，再从下岸攀回原入口。同一角色、钱包、资源和机关时钟贯穿去回程。没有增加 Map Director、区域拓扑或接缝填充器，原六动作家族仍计为六种。

用户原话“这一次生成的都挺好的，下一步继续”已作为 **v2 整体正向视频观感**保存于 `pcg/feedback/workshop/v2-positive-video-v1.json`，绑定原视频 SHA。没有将它解释为新 Macro 的认可、实际试玩或生产批准。

交付目录：[`generation/workshop/macro-v1`](../../generation/workshop/macro-v1/README.md)。[31 秒原生录像合集](../../generation/workshop/macro-v1/videos/overview.mp4)包含 M01、M02 两个接口的完整取宝返回，以及 M03 故意漏接后的恢复重试。每段正常 60 Hz / 1 倍，末尾 1 秒冻结完成画面，段内没有剪辑。

**录像的严格比较失败，未计为全字段精确录像。** 三段共 1672 个实际物理帧；原生与批处理的 `support_id` 在两个静态碰撞体接触处出现 18 帧差异。位置、速度、输入、资源、机关和奖励事件全部一致，原生执行均真实完成且 HP=5。原比较器未放宽，失败 trace、AVI 命令及日志保留，公开 manifest 逐项列出差异。另做固定三例、零重试的单案例进程复查，仍存在此差异，不能称作已经解决。视频供观感审阅，不代替独立 Godot 技术留出。

## 内容与空间

两份新组成 Module 分别负责短门上岸与下落宝箱/下岸；各有两个具体方向的真实见证。四份标准组成文档是两个 Macro 的版本依赖，**没有独立筛选为四个可复用动作家族**，不单独计数或入库为独立挑战。尤其拆掉左侧相邻地貌后，刹车组件的替代入口尚未完成反例筛选。

| 接口 | 上岸接触面 x | 下岸接触面 x | 下层箱中心 | 已知实体范围 |
| --- | ---: | ---: | --- | --- |
| M01 | 600 | 480 | [595,632] | x=-200…1000，y=80…960 |
| M02 | 640 | 520 | [635,652] | x=-200…1000，y=80…980 |

所有岩体均归属于版本化子 Module；两处接触面的新增连接地形面积均为 0。没有默认外边框、传送或恢复资源写入。恢复靠原地面接触和实际跳跃/冷却实现。门仍为原 ShotLatch 0.55/0.65 秒与原防夹逻辑；关键穿门几何沿用 A3 的测量求解域，新的整个 Macro 再验实际击铃、24×36 身体完全过门和稳定落地。

两个宝箱分别提交原 SimpleRoomReward / RunWallet 的 12、10 金币，使用独立稳定 ID。故意漏接后返回并再取宝，账本仍只提交两个奖励事务，最终 22 金币。

每个 Macro 三个外部端口、六个有序对：A→C 为门内第一箱，C→B 为下落刹入第二箱，A→B 为两箱连续路线，B→A 为下岸攀回。**C→A、B→C 保持 UNKNOWN**。A→B 的返回声明仅绑定列明的同世界 A→C→B→A 覆盖，不能外推任意进入状态。外部接缝、通用运动/资源传递与自由变换仍 UNKNOWN，自动生产拼装未开放。

## 验证、失败和修订

原 `factory.core.quality.POLICY` regular 门槛保持不变。协议与所有失败分版本保存，不以新名字把失败改判通过。

- 第一阶段最多四轮几何校准；发现两个宝箱共用事务 ID、返回撞岩阶底部、恢复地面可一跳取第二箱等问题。后一项 4/6 条真实策略成功，旧几何拒绝。
- 冻结第四版几何后，单独固定四轮控制器修订预算。首轮完整扰动校准在源码被修改后，由原冻结保护于 324/450 条中止；保留为不完整失败，没有记为通过。后续修订解决持续 settle 控制和反冲瞄准/转向容错。
- 控制器第四轮通过原 regular 校准与首次留出，但 canonical Macro 导出发现回程在空中越过下岸接缝，没有经过声明的 E 落地端口。该版本未入库。
- `protocol-macro-port-v3.json` 因此固定一次端口策略修正、零新几何、原门槛、新校准 Seed 261025968、独立留出 Seed 261025969。先落 E、再实际步行跨 E→R，校准与解析子版本/路线/实际支撑接缝检查通过后，才执行新留出。没有从留出选种子或改几何。

新留出共 **450 条预定策略，444 条满足目的，所有路线组通过原 regular 门槛**：8 条组成方向、8 条独立 Macro 方向、2 条完整循环，每组 clean 1、mild 12、moderate 12。

| 完整 Macro 路线 | M01 clean/mild/moderate | M02 clean/mild/moderate |
| --- | --- | --- |
| A→B 两箱去程 | 1/1 · 12/12 · 12/12 | 1/1 · 12/12 · 12/12 |
| B→A 下岸返回 | 1/1 · 12/12 · 11/12 | 1/1 · 12/12 · 11/12 |
| A→C→B→A 同世界循环 | 1/1 · 12/12 · 11/12 | 1/1 · 12/12 · 11/12 |

循环合计 48/50，不能写成 50/50。另有实际省略第二枪、跌落、回原岸、再开门重取第二箱的 **26/26** 独立留出，Seed 261025970，两个接口各 clean 1 + mild 12。

反例固定 88 条：64 条同入口的普通跳、逐枪省略、提前地面射铃、越顶和不射击转向；24 条从下岸或返回岩阶的不同入口普通跳。全部没有安全稳定到达目标，不证明不存在其他解法。主体有目的动作、真实奖励、逐级返回落地以及原始无伤稳定终点检查，不靠动作词宣称机关必要。

`macro-composition-resolution-v1.json` 和公开 `proposal-feedback.json` 连接原提案、失败、选择权重从 0 到恢复、源码/协议及新候选版本。提案和可执行规则、技术候选、人类观感与生产认可继续分开。

## 需求、候选库与 B 接口

`macro_interface.generate` 接收原 Challenge Specification 格式，增加显式 `content_kind=macro`；本轮两份输入标记为 **Task A 的内容接口试件**，不冒称 B 已发出或批准。端口、能力、资源、回程、地貌职责及空间硬约束均参与匹配。不支持的家族或耦合条件返回 conflicts / searched / negotiable，不接收输入 `implemented=true` 的自我授权，也不替换成已有普通房间。

生成实际由此入口调用，再执行整个组合的 Godot 验证。两个通过版本进入**原 CandidateLibrary/candidates** 的 scoped multi-route 条目；没有第二套库。重新创建 Library 对象以及另一个 Python 进程从磁盘检索，2/2 命中，检索生成调用 0。组成依赖的 SHA、版本和解析检查随检索执行，撤回任一子版本会拒绝该 Macro。

输出继续 `gunman-rush-level-sketch/v1 + generationContract`，4 份组成 Module + 2 份 Macro JSON/SVG。`internal-seams.json` 提供两接口各两处具体接缝、真实前后快照和逐方向连接；不能据此授权镜像、缩放、移动后拼装或 B 的整图。

共享 Module 合同、Godot Harness 与 Map Director 未修改。本次只扩展隔离工坊、原候选库子类和归档白名单。B 的旧消费者仍需显式读取 reward mechanics/source 与 ShotLatch returnAccess、解析 Macro 组件；不支持时应拒绝，不能丢弃奖励或返回接收器。**B 的消费者适配及新整图验收尚未完成。**

## 复现

在 `map-edit` 工作树根目录，先恢复 v2 报告要求的原 Godot/runtime 与历史归档，再恢复本轮原件：

```sh
python3 pcg/tools/restore_archive.py content-workshop-macro-v1 --extract
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot \
  "$PWD/pcg/prototype/workshop/main.tscn" -- \
  --cases-json "$PWD/generation/workshop/macro-v1/review_cases.json"

# 新批次名称不能与已有目录重复。校准/反例通过后再执行留出和候选入库。
python3 -m pcg.prototype.workshop.macro --name workshop-my-macro-cal --stage calibration
python3 -m pcg.prototype.workshop.macro_counters --name workshop-my-macro-counters
python3 -m pcg.prototype.workshop.macro --name workshop-my-macro-held --stage holdout
python3 -m pcg.prototype.workshop.macro_retry --name workshop-my-macro-retry --holdout
python3 -m pcg.prototype.workshop.macro_publish --run workshop-my-macro-held \
  --calibration workshop-my-macro-cal --counters workshop-my-macro-counters
python3 -m pcg.prototype.workshop.library --run workshop-my-macro-held --query-only

python3 -m unittest discover -s pcg/prototype/workshop/tests -v
python3 -m unittest discover -s pcg/map_directed/tests -v
npm run check
```

本轮 26 个工坊测试、28 个 Map 测试、原编辑器检查与 43 个合同测试通过；新六份文档另经过原验证器、Macro 组件解析与原件 SHA 检查。当前仍无新 Macro 的人工观感、实际试玩或生产认可。支撑碰撞标识的跨执行模式稳定性、其他尺寸/形状/状态域、独立组件挑战筛选与整图集成是后续缺口。
