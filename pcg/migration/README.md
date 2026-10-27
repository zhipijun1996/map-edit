# Module 新地基迁移

规范入口：[迁移 skill](../../.agents/skills/pcg-module-migration/SKILL.md)。
本工具只处理既有内容，不创建新玩法，不调用旧 Map 生成器。

三种去向：`modules/` 是当前技术可用库；`modules-recycle/` 是迁移旧件与
明确废弃项；未迁移、失败、近似重复待审继续在原位置。
准备目录 `.cache/migration/` 是可丢弃的构建暂存，不是第三套内容库。

## 全量流程

库存固定为本仓库134个既有版本及原游戏177条登记来源，先处理本仓库，再归档原游戏。
原始版本、基础模板、组合样品和配置变体分别计数，不把准备完成算作技术入库。

```bash
# 全量修正尺寸、真实接岸和合同；不是仅筛出本来就合规的10件
python3 -m pcg.migration full --name foundation-my-batch --stage prepare
# 真实完整身体接缝、核心动作、连续进出和廉价反例预检
python3 -m pcg.migration.full_clean --prepared-root .cache/migration/foundation-my-batch --name foundation-my-clean --workers 2
# 固定校准、独立留出、实际原生加载；通过后逐项事务入库
python3 -m pcg.migration.qualify --prepared-root .cache/migration/foundation-my-batch --clean-campaign pcg/migration/foundation-v1/campaigns/foundation-my-clean.json --name foundation-my-quality
```

预检失败按实际原因执行最小修订：先保留原核心像素地貌、奖励及动作前缀，再适配局部
接岸；旧内部奖励落点保留为真实 waypoint；原始未认证方向可改为最近的自然出流方向。
`revisions`、`repair_shores`、`side_docks`、`core_preserving` 和 `boundary_runtime` 提供已实现的
针对性适配，使用同一物理 Harness。不能加长安全地板覆盖恢复路线，也不能只挪标记。

原游戏从固定提交和真实求值字典导入，Foundry使用原游戏实际输入录像，不从 poses 移动玩家。
原生金币/笔记使用原消费逻辑；初始能力档案离线匹配，Module绑定时不重设或补充资源。
具体已执行输入、命令和修订结果见 `foundation-v1` 的持久化批次清单。

## 单项复现流程

在仓库根目录运行：

```bash
python3 -m pcg.migration audit --out pcg/migration/foundation-v1/audit.json
python3 -m pcg.migration inspect <原模块目录>
python3 -m pcg.migration prepare <原模块目录> --out .cache/migration/<id>-prepared
python3 -m pcg.migration replay .cache/migration/<id>-prepared --name foundation-migration-<id>-v1
python3 -m pcg.migration certify .cache/migration/<id>-prepared --report pcg/results/foundation-migration-<id>-v1/migration-physics.json
python3 -m pcg.migration package .cache/migration/<id>-prepared --out .cache/migration/<id>-ready
python3 -m pcg.migration promote .cache/migration/<id>-ready
python3 -m pcg.migration build
npm run check
npm run check:migration
```

不要把尖括号占位符原样复制到 shell。run 名与暂存目录必须新建；同一原件已
入库时不重跑物理。`promote` 的重复调用返回已入库，不重复归档。

内容审计（只记录相似/冗余线索，不删除平台）：

```bash
python3 -c 'from pcg.migration.inspection import run; print(run())'
```

完全重复归并先计算证据，再归档；不会信任输入中的 `exact=true`：

```bash
python3 -m pcg.migration equivalence <旧目录> --primary <正式模板ID> --out pcg/migration/foundation-v1/equivalence-decision.json
python3 -m pcg.migration archive <旧目录> --reason exact_duplicate --reason-record pcg/migration/foundation-v1/equivalence-decision.json
```

比较包含真实几何、端口与路线、冻结动作输入及物理源身份；近似、镜像意图或
来源不完整时拒绝归并。全量审计发现的严格匹配先生成语义和物理来源证明；已入库项也必须通过事务和别名保留后归并。

```bash
python3 -m pcg.migration.library_audit
```

## 认证边界

迁移器实际修正完整矩形、128倍数尺寸、外边 Block 面中心 Port 与真实支撑，覆盖
静态地貌、机关、移动平台、敌人、特殊能力及 Macro。工具缺映射属于待实现工作，
不能直接把该类内容丢到失败队列。实际修正仍不成立时返回具体冲突与已搜索范围；
不缩放核心挑战、不自动加外边框、不把坏输入静默替换成普通房间。

`generationContract.version=2` 保留原可编辑 sketch/objects，新增 Foundation
合同。旧见证仍属于旧版本，新版必须实跑原因果检查、原 regular 门槛、固定校准
与独立留出。端口试件另测双向真实身体穿越、有限初始偏移及连续入口和出口。
校准失败允许预登记范围内修订，已暴露留出禁止改名或换 Seed 重试；观测器缺陷
优先对旧 raw 做明确标记的离线重分析，不冒充新的独立物理实验。
反例沿用原明确政策；多按一枪或一次跳跃本身不证明真实资源/风险成本。
邻接试件地板在模块外，明确属于测试邻居，不复制到正式模块，不允许 Map 自动补。

正式库允许 `humanReview=UNKNOWN`；这不是趣味、试玩或生产认可。
`mapReady=false` 明确表示通用 Map 接入尚未认证。未搜索有向对、镜像、封口组合、
任意进入资源与整图仍为 UNKNOWN；不把局部见证推广为任意组合。

物理输入 `physics-input-cases.json` 与录像输入 `cases.json` 分开存档：后者保留
原 `recorded_frames`。工具逐字段核对除该录像缓存外完全一致，不让视频替换动作
程序。Godot 包离线编译，运行时仅实例化已冻结数据，不运行配方或参数搜索。

每个包绑定原机制文件 SHA，当前 Harness 仍是 `12f6cb0` 物理基线。
游戏 main `879b39e` 新增换装容量与其他行为的兼容性不自动继承，见
[游戏盘点](foundation-v1/inventory-game-v1.md)。

## 历史证据与恢复

`foundation-v1/ledger.json` 保存原位置到回收归档的路径映射。用
`pcg.migration.core.resolve_artifact()` 读取历史引用，不改写原 JSON 字节或哈希。
共享原机制、raw、源快照与媒体不随模块任意搬走；目录中 `archive.json`
记录原件清单、去向和原因。新实验完整 raw 与源快照沿用现有 PCG 分片归档工具。

正式库目录由校验后构建，不能手写 `passed=true` 或只改目录索引获得准入。
网页模块选择器仅读取新版正式目录 `modules/catalog.json`；历史主游戏参考和旧工坊只能在原目录或归档中查阅。

## 静态检索与原游戏初始配置

`python3 -m pcg.migration.query <需求JSON> --allow-scoped` 读取持久化正式库。
`port_configuration_id` 可指定一个已认证完整接口配置，或以 `base` 指定原配置；
省略时按实际 Port 朝向等条件筛选原配置及已认证替代，不组合独立换边。
返回 `baseContentVersion`、`portConfigurationId`、所选 `contentVersion`、实际 Port 与场景。

原游戏 Foundry 等内容可能要求固定初始配置，能力名称相同不代表跳跃和空中射击容量相同。
需求的 `initial_profile` 只接受**精确配置 ID 字符串**，例如：

```json
{
  "abilities": ["move", "jump", "double_jump", "shot_recoil", "multi_air_shot"],
  "initial_profile": "air_chain"
}
```

该 ID 必须等于所选内容离线绑定的 `requiredNativeProfile.id`；其原始定义与
`generation.parameters.original_tuning_profile` 一致。输出的 `requiredNativeProfile`
保留完整 `overrides`、`abilities` 及 `effectiveTuning`，供消费者核对并绑定实际初始配置。
缺少 ID、`UNKNOWN`、错误 ID 或只给部分容量不能命中这类内容，即使使用 `--allow-scoped`。
本接口不接受自填 tuning 对象推断兼容性；改变配置须另外离线验证。
未声明此要求的普通 v2/v3 内容继续沿用原筛选条件，输出 `requiredNativeProfile: null`。
这是固定初始运行配置匹配，不是在线追踪 HP、速度、剩余弹药或逐步资源状态。

对于带 `INPUT` 或 `OUTPUT` 单向初始权限的接口，还须精确匹配经过验证的**可用能力集合**。
例如只在 `move + wall_climb` 下验证的顶部单向入口，不能沿用到额外拥有跳跃或反冲的玩家。
检索会交叉核对当前版本的真实物理记录、其路线对应的 `physics-input-cases.json`
（缺少时使用已绑定的 `cases.json`）以及 Port 的 `initialPermissionConditions.availableAbilitiesExact`。
仅修改证据展示字段、声明“已认证”或提供能力超集，都不能获得该单向权限。
返回 `testedInitialAbilityConfigurations` 和实际 Port 的 `initialPermissionConditions`，
供新 Map 在固定初始能力条件下选用；普通全 `INOUT` 接口不增加这项单向权限的精确集合限制。

所有路线的能力筛选还保守包含其**真实绑定物理输入**提供过的能力。
`route.requiredAbilities` 是最低需求描述，旧 `validation.capabilityConfiguration.available`
可能存在展示字段遗漏；两者都不能把拥有二段跳的见证降格为仅有一段跳也已通过。
请求须包含所选路线实际测试能力，输出 `requiredTestedAbilities` 和从真实输入得到的
`testedInitialAbilityConfigurations`。若还声明了原生配置，其 `abilities` 也须包含于请求，
不能仅给出 `initial_profile: "air_chain"` 就省略实际需要的能力。
这是保守复用已验配置；若希望更少能力即可使用，须先离线验证那个能力配置。

## 复核与试玩已入库内容

已有认证不重复消费留出池。复核当前模块使用只读命令：

```bash
python3 -m pcg.migration validate modules/plains50-ports-brake-branch-0 --certified
```

手动试玩与冻结输入回放见 [原生包运行说明](runtime/README.md)。运行的是静态
Module 数据和真实玩家机制，不调用配方或 Map 生成器；该运行项目仍是绑定的
Harness，尚不代表主游戏正式流程已经接入。

原始实验和暂存输入镜像保存在 `module-foundation-migration-v2` 分片归档。
在仓库根目录校验全部原件（不创建第二份大型 ZIP）：

```bash
python3 pcg/tools/restore_archive.py module-foundation-migration-v2 --verify-parts-only
```

按原路径恢复时使用同工具的 `--extract`。暂存输入的多个已观察字节版本另由
`python3 -m pcg.migration.snapshot_preparations --help` 提供精确 SHA 恢复；不把
迁移后保存的字节冒充早期实验输入。
