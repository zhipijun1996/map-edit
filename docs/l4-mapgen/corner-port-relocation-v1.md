# 角落 Port 换边：离线配置扩展 v2（保留 v1 历史认证）

本扩展来自用户在全量迁移任务中的追加需求，现与 `MAP_FOUNDATION` 1.2 对齐：需要时岩体可改为可穿平台，**不要求封旧开口，也不为换边额外加墙**。旧位置只撤销逻辑 Port 资格，其开放几何保留，Map 对相邻空间的实际通行影响另行验收；不据此增加连接边或授予整图资格。历史 v1 规则及真实闭口样品保留原证据，不重标为 v2。完整矩形、外边中心、surface、初始权限、有向 Route、局部封口和真实物理验证继续适用。

## 语义

角落 Block 的 Port 可申请换到**同一 Block 相邻外边中心**：

| 角落 | 换边 |
|---|---|
| `TOP_LEFT` | `LEFT ↔ TOP` |
| `TOP_RIGHT` | `RIGHT ↔ TOP` |
| `BOTTOM_LEFT` | `LEFT ↔ BOTTOM` |
| `BOTTOM_RIGHT` | `RIGHT ↔ BOTTOM` |

原口与换边口是同一逻辑 Port，ID、初始权限保持，不同时开放，不新增 Port 数或模板数。矩形不变，不旋转 Module；局部可微调接岸、平台和合法表面类型。核心挑战、奖励、恢复、原有有向路线功能及必要能力/资源要求必须保留。无损表示这些玩法功能不丢失，不表示角色运动时间和每一像素完全不变；相关差异和重新验证要记录。

`ROCK` 仍仅左右可用，转为上下方向时必须使用实际合法接口，例如真实 `ONE_WAY_PLATFORM`。底边 `AIR INPUT/INOUT` 仍非法。更改 surface 会改变可匹配对象，消费者必须读取所选配置，不能沿用原口类型。

## 每口四角属性

`ports[].cornerRelocations` 是包含四个固定键的对象。每项有：

- `applicable`：原口是否位于该角落 Block 的一条外边中心。非适用项 `allowed=false`、`profileId=null`。
- `allowed`：`true / false / "UNKNOWN"`。通过才true，实证或确定规则拒绝才false，未验证为UNKNOWN。
- `reason`：适用性、待验证条件或失败原因。
- 适用项另有 `targetFace`、`targetPosition`、`proposedSurface`、`permission`、`profileId`。提议的合法表面不是已实现/已验证表面。

旧文档缺字段时按UNKNOWN、不可换边处理，不据此否定原配置。1×1 Module 的同一边口可能同时属于两个角；每个角仍只有相邻外边那一个目标。

`pcg.migration.corners.annotate(document)` 为新准备稿写入初始属性，随后必须重绑内容版本。`assess_document(document)` 为冻结文档生成不改原件的版本绑定评估。命令：

```bash
python3 -m pcg.migration.corners
```

它扫描当前正式目录、待迁移生成来源和准备稿，写 `pcg/migration/foundation-v1/corner-port-inventory-v1.json`。评估报告不是物理认证，也不增加迁移成功数量。

## 完整配置与证据

`generationContract.portConfigurations[]` 可以记录制作阶段的**完整选择**，不是可任意组合的独立布尔开关。每项包括：

- `id`、`status`、`validationIds`；状态采用现有 `declared / verified / failed / UNKNOWN`。
- `relocations`：`[{portId, corner}]`，同一逻辑Port只能选择一次。
- `routeIds`：配置保留的全部声明路线；已认证配置必须覆盖原路线，不能删除不利方向救过。
- `configuration: {path, sha256}`：实际可加载配置工件，包含完整地貌修改、支撑、新口位置/法线/surface、对应路线和其他未连接 Port 的封口。

制作阶段的内联配置若声明已认证，结构校验要求引用的当前版本通过记录同时绑定 `coverage.portConfigurationId`、`coverage.configurationSha256` 和精确配置工件。结构校验仍不是物理认证。

**实际发布使用外部认证回执，避免认证状态变化使基础内容哈希循环失效。** 基础 `module.mapnote.json` 冻结后不再因可选配置通过而重写；配置位于 `modules/<moduleId>/port-configurations/<configurationId>/`，含完整目标doc、输入、真实Godot包及 `receipt.json`。当前回执 schema 为 `pcg/corner-port-configuration/v2`，绑定 `moduleId`、`baseContentVersion`、`baseDocumentSha256`、`configurationId`、`relocations`、精确目标doc的 `configuration {path,sha256,contentVersion}`、`physicsReport {path,sha256}` 和 `package {path,sha256}`。v2 另须 `retiredSidePolicy="preserve_geometry_no_extra_closure"` 和 `adaptation {path,sha256}`，后者绑定真实基础/目标文档SHA与选中Port/角落。消费者直接复核静态占用和材质差分：仅角落目标短支撑窗口可变为可穿平台或作必要的短外延，不能新增实体闭口墙，窗口外碰撞与机关/奖励保持。v2 不要求也不接受 `retiredOpeningReport`；v1 继续按其原闭口证据核验。`allowed=true / technicalStatus=verified` 只有重算验证真实raw、目标包实际加载以及上述身份匹配后才生效。

库索引的 `cornerConfigurationReceipts:[{path,sha256}]` 仅由 `corners.verified_receipts` 输出。它重验真实物理及原生包证据，并核对选中口是最近同Block换边、权限不扩展、未选中口不变、全部原路线及能力要求保留。网页先校验回执和基础SHA，再加载实际目标配置；不在浏览器内改地形。旧回执与当前基础版本不符时不可使用，不能由回执里的pass字段自行准入。

多口同时换边只选已经联合认证的完整配置。只认证A和只认证B不代表A+B已认证；水平镜像、封口组合也不自动继承。在线只读取已编译、已认证配置，不临时补平台、改surface或生成新路径。

## 验证范围

复用现有Godot Harness、角色身体/反冲/承载/资源和质量门槛。按受影响范围验证完整身体净空、真实支撑、进入/离开、相关原路线、初始机关权限、恢复、回程、必要接缝和廉价绕行；v2 不以封旧开口为测试目标。反例发现的新路线必须反映到实际图，不仅保留规划路线。可选换边失败不阻断原配置迁移。

报告分别统计适用、通过、拒绝和UNKNOWN，绑定来源文档SHA与版本。单独的角落评估只产生UNKNOWN候选；通过数量必须来自真实认证回执，不能把几何角落判定当成真实可用换边。

## 已有可玩认证样品

`plains50-ports-brake-branch-0` 的 `c-bottom-right-v1` 已完成真实认证：同一C口由右边 `[1024,680]` 换到底边 `[960,744]`，保持 `INOUT`，实际表面改为 `ONE_WAY_PLATFORM`。保留三条原路线和奖励/回收关系；最后岸边改为原生可穿平台，16像素共面重叠保留原站位的完整身体支撑，8像素窄岩壁关闭原右侧开口。初次128高封口被普通跳反例绕过后，修为256高，并重验。

- 正式配置与可玩场景：`modules/plains50-ports-brake-branch-0/port-configurations/c-bottom-right-v1/` 下的 `module.mapnote.json`、`module.tscn`、`demo.tscn`。
- 回执：同目录 `receipt.json`，绑定基础版本 `fd0d94da…` 和目标版本 `37e0ee44…`。
- 三条路线的校准/独立留出、全部双向接缝及连续出入、廉价反例共184输入案例通过原质量门槛；另9条原右口封闭实测通过。
- 独立Godot包实际重放三条冻结策略共530帧，HP5、稳定出口，奖励分别10/0/10。
- 完整修订历史见 `pcg/migration/foundation-v1/corner-experiment-history-v1.json`：313次Godot输入，其中301个真正步进、12个零帧资源拒绝，失败全部保留。历史总量不是新增模板数。

可从正式持久化基础内容重新准备同一目标，准备稿不会继承基础内容的技术通过标签：

```bash
python3 -m pcg.migration.corner_experiment prepare --source modules/plains50-ports-brake-branch-0 --out .cache/migration/corner-reproduction
python3 -m pcg.migration.corner_experiment validate --prepared .cache/migration/corner-reproduction --report pcg/results/foundation-corner-c-bottom-right-full-v3/migration-physics.json
python3 -m pcg.migration.corners
```

第二条命令只读核验既有真实raw，不重复声称新独立留出；新候选的`validate --name`先经过原sourceVersion的留出条件锁。额外诊断可用`preflight --prepared … --name …`和`closed --prepared … --name …`，但不增加资格。命令拒绝覆盖已有实验输出；已入库配置通过索引/查询直接复用，无需重复物理调用。样品仅认证这个完整配置，不表示所有角落都可迁移、任意多口组合可用、镜像已认证或已获得人工趣味认可。
