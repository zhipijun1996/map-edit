# 1.1.1 迁移准备：来源、差异与回归

本轮仍使用 **1.1.0**。这里只读核对已存在的 1.1.1，不合并 PR77、不删除/恢复历史目录、不更新下游锁、不发新包。

## 三套来源不能混称

| 对象 | 实际来源 / 状态 |
|---|---|
| 当前 main | `9b712fe814ef228b368c0eb9adf660e39de29e37`，正式 catalog 82 项；PR78 是从此点的审计增量。 |
| 历史 1.1.0 | ZIP 所在提交 `47aefebe07f4f0e7471f3d1546214502a6b2aade`；包内 source.commit=`02b5cb53b06d7009225b2ecff9351f315e46b12e`；115 项，SHA `5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723`。 |
| PR77 | `production/unified-module-package`，head `c2e23fec3ec424a7b8e41552bbe2c4ed2a6c8afd`，仍 open/unmerged；含统一生产库及后续证据，不是当前 main。 |
| 已发布 1.1.1 | ZIP 所在提交 `ff235b997dbc3fdc0f7073912a97a1c4a8ac6bbc`；包内 source.commit=`5c0805e2c5055f5e458e227521ff9b3eb3123e02`，属于 PR77 分支；115 项，SHA `a806f8feb10e8a10f20014913afba49e9036be21d33c00618cfc86367ac993c6`。 |

main 与 1.1.0 的81个共同ID全部版本不同、包独有34项，沿用 [PR78 比较](../../../evidence/runtime-integration-audit-20261103/baseline-diff.json)，不重新全面审计。PR77 的统一源库/退役/设计记录变更应独立审阅，不能与消费者采用某一不可变 ZIP 混成同一动作。读取已有1.1.1不等于PR77已合并。

## 两个已发布 ZIP 的实际差异

先各自核 ZIP SHA 后比较，机器结果见 [migration-110-111.json](../../../evidence/runtime-integration-930001/migration-110-111.json)：

- 稳定 ID 集合相同，均115；没有新增/移除运行模块。仅5个 contentVersion/源SHA改变；其余110个内容版本相同。
- 115份 native compiled 的所有字段除 `source_sha256` 外逐字段相同，包括地形、敌人、奖励位置/金额、Port、world_bounds 和机制参数。5份 compiled 的源SHA随新原件重新绑定；不能沿用旧CV装新声明。
- 76份 `runtime/`、`integration/` 文件逐字节未变，含两份宿主锁；原 runtimeFingerprint 均为 `434d22271d75a3a95615209568ab6a648ae9889fa7db9faa387dbd347ab216f9`。宿主仍12f6cb0原生资格 / 5f55716 API范围，未升级到PR127。
- 26个已有文件字节改变：5组原件/compiled/包元数据/thumbnail，以及 catalog、manifest、README、portable/current-game-api报告、奖励缺口清单；新增1个紧凑领取报告。总文件从657→658（不含manifest）。缩略图变化不能误读为地形变化。
- schema仍 `map-edit/module-package/v1`、Foundation规范1.2/模型1.0、generationContract2；没有新坐标/镜像/Port协议，也没有新的spawn或封口兼容认证。
- 奖励点32个保持；缺口清单5→0，仅表示每点至少一条明确关联，不是所有路线/相位/镜像/封口都可领取。resourceProfile.status 仍 UNKNOWN，不擅自升格。

## 五项奖励关联精确变化

所有下列 Route 的 requiredRewards 由 `[]` 变为表中ID；其他关联不推断。完整旧/新版本及改动范围：

| 稳定ID / Route → reward | 1.1.0 contentVersion | 1.1.1 contentVersion | 此930001实例 |
|---|---|---|---|
| `generated-75b420621682d36fc3b7262784c347f0acea7e55422f7e0abaebbc285fa89198 / entry-to-exit → visible-cache` | `sha256:21f326887eb9d20a0f8235d8b99573db8699fd5a6961916d13a1d719115f0e65` | `sha256:daac1ddf68df5f7b7952fc5035ba233d4c5f1d1f7d8602ca05b318fa2dba9e19` | 未出现 |
| `idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-2 / A-to-B → reward` | `sha256:4cb1d54217bbeef5dcb654c58dc773a53f12bf5cd6bce24f9eb9b7b085eed468` | `sha256:3002aa99be0d31680f369d058a57653029005f68bae536de6055b1c7e7f7320e` | 未出现 |
| `idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3 / A-to-B → reward` | `sha256:c4082bd0cc390677197149e5dca2be2ee3d52d84f86f36877a3af2edb9b604cb` | `sha256:71b46e7506b58131fff70bd885f78c600d9c8c8426376ae3777dd4579bddd240` | 未出现 |
| `idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3 / A-to-B → reward` | `sha256:31c9d973eb4de9338fa4c3d05e84d8b06f508cce110b45ff5ec127a0f669169a` | `sha256:af771a45bcac3ab9bb710a54e9f4131963483231350ba82559d72fe327f17b6a` | 未出现 |
| `idea-orbit-choice-001 / A-to-C → reward` | `sha256:ee5cdeb5d7672eb1c9fbe9c502273114039a346817b8bf5ea7a7dd65045a1317` | `sha256:5fcc60e4459853b4a89229c2c0bd15f1469aada950d6705c5e7a5906f50ab9fa` | M24 |

已确认的证据仍是 PR77 冻结原生 Cells 上的三组领取后出界见证；PR78 已核15个原始输出/钱包/事件与owned Cells相等，本轮直接引用 [复核结果](../../../evidence/runtime-integration-audit-20261103/later-reward-evidence-check.json)。wall-slide 使用 wall_climb；三怪/升井上出口有外邻接应台；升井需走到x220取箱再回x192；环岛只证明开放C的A-to-C。不是PR127、任意初态或新holdout。

**本张冻结图只有 M24 命中这五个版本变化。** 1.1.1给A-to-C补关联，但当前M24只保留A-to-B/B-to-A、C已封，领取区域全被挡的几何没有变化；升级不等于修复M24。另四项未来出现在其他seed时仍需能力/外邻/取箱策略回归。

## 显式升级的前置工作与下游回归

| 责任方 | 必须完成的具体工作 |
|---|---|
| map-edit 来源/交付 | 明确消费者采用哪个固定ZIP/源提交及五项版本；保留PR77与main的区别。现有1.1.1可作为待评估输入，不为本轮再发包；若修改布局/出生/依赖则另提具体方案、内容/包版本影响与新证据。 |
| map-gen 依赖/确定性 | 在独立变更中更新module-lock/ZIP与catalog SHA，显式允许1.1.1并跑真实归档解析/协议校验；重新生成930001及已有冻结成功/失败/seed回归，区分GDScript实现指纹、map_id与布局/图/内容差异，不能只改锁而沿用1.1.0冻结SHA。 |
| map-gen 奖励/封口 | 逐项核5个新requiredRewards进入实际有向图/奖励目标，非空关联不能被过滤丢失；M24规则反例回归；其他四项以真实能力和外邻夹具检查。未测组合保持UNKNOWN。镜像仍由算法对完整内容实施。 |
| 主游戏 Provider/身份 | 显式接收新的包/内容版本与实际content字节；沿PR127分别计算generation_input_fingerprint、map_content_identity、host_load_identity，不混入session token。1.1.0旧恢复对新包应按现有identity策略拒绝，除非另设计并验证迁移；永久存档schema不在本轮改。 |
| 主游戏 机制/奖励 | 先复验M16/M18/M21旧受控切片，再对M35/M01新适配跑完整机制；五项关联不是自动发钱，必须原生落地/区域触发、实际领取ID/金额、钱包去重、后续出口、死亡/退出/恢复。reward_pair还需真实提交驱动两门状态与恢复。 |
| 主游戏 Web/算法 | 调用0.3.0运行时算法后验证旧token不提交、取消/清理、包内依赖闭包与实际PCK原字节；验证新identity，不能复用旧Web build证据签新包/新适配器。整图/Boss/手机性能继续单列。 |

拿到以上下游精确commit和新冻结输入后，再做受影响定向复验。物理等价可保留原Cells证据范围；它不能替代新宿主装载、伤害/领取、连接配置及恢复的证据。
