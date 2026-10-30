> 最新状态见 [审批刷新 040](../review-040-v1/README.md)：累计 67/72，以下为本轮历史记录。

# 审批刷新 031：197 / 198 / 200 完成，196 设计合同冲突

同步并合入 main `d60ca5921be0fba0f824e3246db197172a2f3666`，冻结新增四项审批。本轮三项、四条路线通过原 regular 校准、独立留出、完整身体、接口与反例检查，3 个可玩包 / 4 条回放原生加载通过，正式验证共 **327 次**。累计已审批 **63 项，其中 62 项在各自声明范围内技术通过**。人工试玩、生产准入、镜像、封口组合及完整 Map 均未由这些结果授予。

| Module | 实现与验证 | 录像 |
| --- | --- | --- |
| [196](196.json) | **DESIGN_CONFLICT**；底部 AIR INOUT 被 Foundation 禁止，未运行无效模块的物理测试 | 无通过样品 |
| [197](197.json) | 原裁剪、岩唇、低铃、门、底部危险带不变。依据实际下落高度射铃并反冲落岸；69 次正式实测 | [5 秒实机](videos/197-entry-to-exit-v1/low-ray-recoil-return.mp4)，review-only |
| [198](198.json) | 原两台轨迹及 A 的 **7 秒停留**不变；实际登上两台并换乘；91 次正式实测 | [18.65 秒完整实机](videos/198-entry-to-exit-v2/carrier-rendezvous.mp4)，逐帧严格通过 |
| [200](200.json) | 同侧低口到高口：空中命中真实敌人续枪，再转向反冲；高口到低口独立验证；167 次正式实测 | [去程 3.88 秒](videos/200-entry-to-exit-v1/air-refund.mp4) / [返程 3.7 秒](videos/200-exit-to-entry-v1/air-refund.mp4)，均 review-only |

200 另有 [同世界往返实机见证](verification/200-same-world-witness.json)：固定拼接两条已冻结策略，取到 16 金币后在同一角色/世界中返回低口，没有重置、补弹或写入生命。此项是一例无扰动见证，不冒充新增独立留出或普遍的返回保证。初始夹具把同一低口重复写作原生定义的 entry/exit，13 次均在零物理帧被拒；修正夹具保留两个真实定义 Port，策略与物理未改，追加一例真实测试。所有拒绝与修正均保留。

## 196 需要设计决策

获批设计 `sha256:4856e51a…` 要求底部 `(110,818)` 为 **AIR / BOTTOM / INOUT**。现行 [MAP_FOUNDATION.md 第 3 节](../../../../MAP_FOUNDATION.md) 禁止底边 AIR INPUT/INOUT；`module-foundation.js` 拒绝该精确版本。详见 [冲突与可选改法](196-design-conflict.json) 和 [原静态错误](verification/196-static-contract-error.log)。这是接口约束冲突，未证明上攀物理不可能。

- 保持底部 AIR，改为仅出：保留四条合法有向目标，撤销两条从底口进入的目标。
- 保持六向目标：将底口改为有真实可穿支撑的 ONE_WAY_PLATFORM，几何需要重新审批，不能自行补台。
- 若坚持无支撑底口向上进入，则需先明确修订 Foundation 及对应消费者、初始运动合同和验证流程。

本轮未改变该设计、Foundation、审批意见或设计网页。196 留存的 materialization 为静态拒绝草稿，不能加载或计入认证；首次 role 格式适配错误也保留在独立失败目录。

## 测量修正、媒体与旧失败

197 原总报告 FAIL 的原因是 `ground-preopen-low-return-key` 反例：原生身体在第 4–25 帧离开审批矩形，再抵达相同奖励。此路径保留为外部空间依赖 UNKNOWN，不算内部合格解，也不能据此判定内部绕过。[限定修正测试](verification/counter-scope-tests.json) 仅作用于 197 的精确版本、该反例、唯一越界否决及健康无重置条件；其他模块、版本、伤害、重置、不同反例或没有真实越界均不适用。[原失败报告与只读重分析](197.json) 同时保留，没有修改 Module、原始输入、校准/留出或增加物理调用。

198 初版录像因未安装的可选消费者多序列化了两个空数组，严格比较失败。新版 movie consumer 对该精确 Module 不序列化未安装消费者的空快照；比较器、全部物理值和事件未变，1,054 帧严格通过；旧失败影片/trace/差异仍在 `videos/198-entry-to-exit-v1/`。其他三段录像保留全部 `support_id` 和可选快照数组差异，仍明确为 review-only。四段代表录像正常 1 倍速度、无剪辑、含 1 秒全画面尾停。AI 实际查看了五张解码抽帧，不声称看完每帧；197 在当前缩放下底部危险带视觉较淡，见 [观感记录](verification/video-observation.json)。

此前 157 顶部加一格、171 不跳而左右交替射击、174 ONE_WAY_PLATFORM 澄清及 175 择时起跳版本均保留。本轮删除明确废弃 **201 / 203 / 205**，活动库 **168 → 165**，累计删除 60 项；版本、文件数量和恢复提交见 [删除回执](deletions.json)。202、204 新修订稿待审，未实施。

## 可玩包与复核

使用完整仓库的原项目资源及官方 Godot 4.7.2，选择对应目录的 `demo.tscn`。包是可玩候选，默认手动输入；A/D 移动、空格跳跃、鼠标射击。200 的 `--case 1` 是从高口进入的独立返程。

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/review-031-final-v1/generated-769066fe5fa1b2332bd7d35c56fa814f01db2b06eb8c65ef9ecf1e586db3ca0b/playable/demo.tscn" -- --replay --case 0
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/review-031-final-v1/generated-777ce57682915e11719c9540e5c0f374c1aaef971321099e9459a34b1c3615a2/playable/demo.tscn" -- --replay --case 0
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/review-031-final-v1/generated-8df5613256e70989f6ae5795803344bdc3e636fe3232c2e35175fae612f633ba/playable/demo.tscn" -- --replay --case 1
python3 -m pcg.tools.restore_archive approved-review031-implementation-v1 --verify-parts-only
python3 -m pcg.tools.restore_archive approved-review031-implementation-v1 --extract
python3 -m pcg.manual_review.audit_review031_v1
python3 -m pcg.manual_review.audit_review031_counter_v1
```

归档覆盖本轮 **22 个运行目录、18,255 个逻辑文件、1,076 个去重条目**，2 分片共 15,190,876 字节；整体 SHA256 `7ae14a7bd61718b31559f857a9559c591cab32091e0a12b0dcc295ae5925af7e`。归档校验覆盖各分片、整体 ZIP 与每个条目。原游戏保护清单 870 文件逐一核 SHA，无修改；正式留出不因打包、录像或归因修正重抽。

完整状态见 [index.json](index.json)。公开下载核验会另行追加 commit 固定 URL 与 SHA 回执，不修改本轮物理结果。
