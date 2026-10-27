# Module 发布接口：Foundation 1.0 / generationContract 2

`MAP_FOUNDATION.md` 是模型依据。本文件说明当前存储与消费接口，不修改地基。
原件仍为 `gunman-rush-level-sketch/v1`；`objects` 是唯一可编辑地貌和机关来源。

## 身份与目录

`modules/catalog.json` 是当前库清单，schema 为 `map-notes/module-archive/v1`。
`modules/<id>/` 每个稳定模板只有一个当前版本。

- 清单 `id` 是 Foundation 模板 ID，与包 `stable_id`、迁移记录 `moduleId` 一致。
- 清单 `moduleId` 对应 JSON 的旧编辑器 `doc.id`，保留原设计身份；两者映射明确，不能混作第二份内容。
- `contentVersion` 是语义 SHA，`contentSha256` 是完整 JSON 字节 SHA。
- `humanReview=UNKNOWN` 允许入技术库，不代表人类认可、试玩或生产批准。
- `mapReady=false` 不授予通用 Map 资格；有限单模块与指定试件资格不能推广。

包内 `module.tscn` 是数据实例，`demo.tscn` 是带原玩家的隔离可玩宿主。
`cases.json` 是冻结的原始录像输入，`physics-input-cases.json` 是新实验证据绑定输入；
除 `recorded_frames` 缓存外必须逐字段一致。`compiled-content.json` 和包内 runtime
是离线编译产物，不能另行手改，运行时不调用配方或搜索。

## JSON 合同

`generationContract.version=2`，保留 v1 的来源、能力、难度、原状态与验证结构。

| 字段 | 当前语义 |
| --- | --- |
| `foundation` | `version:'1.0'`、`blockSize`、正整数 `widthBlocks/heightBlocks` |
| `space.bounds` | 完整矩形；`w/h` 与 Block 数精确对应；内部可不规则 |
| `ports[]` | 原 position/normal/support，加 `face/surface/permission/stagingPosition` |
| `relations[]` | 完整 N×N，包含对角线；`path/no_path/UNKNOWN`，各格独立列 routeIds |
| `routes[]` | 原 from/to/path，另有 requiredAbilities、actionTags、durationSeconds、resourceProfile、initialConditions、localDisplacementBlocks |
| `closures[]` | closedPorts、真实 objectIds、保留 routeIds、status、validationIds |
| `mirror` | status、validationIds；未认证保持 UNKNOWN |

旧 `space.blockGrid` 的稀疏占地不用于 v2。Port 必须在矩形外边的 Block 侧边中心，
face 与 normal 一致，surface 为 AIR/ROCK/ONE_WAY_PLATFORM，初始权限为
INPUT/OUTPUT/INOUT。ROCK 仅左右；底部 AIR 不接受进入。staging 是内部身体站位，
不是正式 Port；不要求身体中心恰与 Port 中心重合。

`requiredAbilities` 当前保守列出真实测试配置，不宣称最低必要能力已经证明；
原 `capabilityRequirements.status=partial` 仍保留。资源和机关状态用于离线合同，
不要求在线 Map 逐步追踪。

path 与 verified 只是引用声明；正式入库另校验真实输入、原始输出、源快照、
固定校准/留出、完整身体穿越及实际包加载。写 `implemented=true` 或 `passed=true`
不能代替这些证据。有限失败不能设置物理不可能；已发现的额外路线必须记录。

## 放置与检索

旧内容可保留局部负坐标。实例原点表示矩形左上 Block 坐标：

```text
scene_position_px = origin_block * blockSize + sceneOriginOffsetPixels
port_world_px = scene_position_px + port.position
sceneOriginOffsetPixels = -space.bounds.position
```

这只平移模板，不缩放地貌、不移动玩家、不补资源。镜像、封口与接缝只开放实际
认证的配置；当前未知组合拒绝检索，不自动生成封口或地形。

静态需求检索（从磁盘加载和核验，不是内存缓存计数）：

```bash
python3 -m pcg.migration.query pcg/migration/foundation-v1/example-demand.json --allow-scoped
python3 -m pcg.migration.query pcg/migration/foundation-v1/example-demand.json
```

前者只用于明确接受有限技术范围的离线集成；后者要求通用 Map 就绪，当前应拒绝。
支持尺寸、能力、指定方向关系、连接口子集、方向数量及镜像要求；未支持字段明确
返回冲突，不静默忽略。失败包含冲突、搜索范围和可协商条件，不制造替代模块。

## 版本与历史

结构或动作合同改变产生新 contentVersion，并重新绑定证据。仅更新离线编译包装
且 JSON 内容不变时保持 contentVersion，但新包仍需新 manifest 和实际加载证据，
旧编译包入回收归档，不留在正式目录并存。

主游戏源固定为 `879b39e` 导入并核对，不改写旧 `74d8a06` 参考历史。
当前物理与包运行验证绑定原 Harness `12f6cb0`；不将其改标为新 main 认证。
正式主游戏安装、任意相邻关系与整图验收仍是独立工作。
