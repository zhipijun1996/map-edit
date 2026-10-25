# Task A → Task B：A1 首个家族交接

基于最新 main `b9318cf` 与实际 PR #1 `b624752`；工作分支 `content/task-a-workshop`，独立 worktree。不改 Map Director、共享合同或共享 Harness。新增隔离 runner **继承** PlainsEngine/runner_plains，原 870 物理文件不变，Godot 4.7.2 SHA 校验一致。

现在即可集成的首个家族为 **thorn-slot / 尖刺窄通道反冲**，两份空间需求分别为落点前缘 460 / 490、支撑高程 438 / 418 世界单位。真实宝箱奖励 8；无自动外框。原话见 `pcg/prototype/workshop/ideas.json`，人工创意不代表批准。

交付索引：`generation/workshop/a1-first-delivery/modules/manifest.json`。仍用 `gunman-rush-level-sketch/v1 + generationContract`，不是新 Module 格式。

| 接口 | 内容版本 | 独立留出 clean / mild / moderate |
| --- | --- | --- |
| thorn-slot/0 | `c5825cd704759634c00a9277ce0f94c9948d70d6c8bfd2c09b55b73d3c1399a8` | 1/1、12/12、10/12 |
| thorn-slot/1 | `89cc9ca617c8ebb042a28569c3eed5468c3afad843d9964cde1c19b46e855d2e` | 1/1、12/12、10/12 |

采用既有 factory regular 门槛，没有事后降级。失败全部保存。24×36 身体逐段扫掠独立检查；普通跳跃 18 策略、逐枪省略与 3 种向上越顶策略分别实跑，两接口共 44 反例未成功，不能据此证明其他绕法不存在。原伤害/回退保留，通用回程与跨 Module 接缝依然 UNKNOWN。

首段正常速度 Godot 原生录像 `generation/workshop/a1-first-delivery/thorn-slot.mp4`：91 物理帧逐字段精确一致，含 1 秒完成画面；并非人工试玩。两个候选已使用 **原 CandidateLibrary.enroll/find** 写盘后新建 Library 实例重新检索；`retrieval.json` 有真实磁盘记录，生成调用 0。候选不是生产认可。

## 复现和调用

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py plains-generation-v1 --extract --prefix prototype/godot/
python3 pcg/tools/restore_archive.py workshop-a1-first-v1 --extract
# 安装官方 Godot 4.7.2 到 WORKSPACE.md 指定路径，再导入一次。
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit
# 新一批反例与独立实验必须使用新名字，不覆盖本批。
python3 -m pcg.prototype.workshop.experiments counters --name workshop-a1-new-counters --families thorn-slot
python3 -m pcg.prototype.workshop.experiments produce --name workshop-a1-new-holdout --families thorn-slot --counters workshop-a1-new-counters
# 可操作的隔离 Godot 样品（移动、跳跃、鼠标释放射击、Retry）。
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/prototype/workshop/main.tscn" -- --cases-json "$PWD/generation/workshop/a1-first-delivery/review_cases.json"
```

程序接口：`pcg.prototype.workshop.rules.generate(spec)` 接收同版 Challenge Specification；示例输入在交付目录 `challenge-specifications.json`。注册表决定实现能力，输入 `implemented=true` 无效。超出明确的空间/端口/能力/收益域返回 `unsatisfied + conflicts + searched + negotiable`，不得替换为平台房。当前两份硬需求可执行适配，任意尺寸、镜像、旋转和通用入口状态未开放。

给 B 的集成边界：候选可用于**隔离拼装后重新实测**；共享 `assemblyInterface` 继续默认拒绝 UNKNOWN。不能据局部见证交换入口出口，不能自动补平台、传送、回满资源。随后将增加原状态连续试件；单 Module 成功不签整图通过。

其余五个家族仍在校准与反例返工，后续增量交付，不阻塞这一份集成。
