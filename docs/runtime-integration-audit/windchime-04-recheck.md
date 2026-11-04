# 0.4 单钟门：准备完成，待新适配commit复验

机器输入：[windchime-recheck-input.json](../../evidence/runtime-integration-actual-04/windchime-recheck-input.json)。从PR129实际七角色锁读取，不从SDK sample或旧M编号搬宿主事实。两例均锁 **1.1.0**，稳定键是 `game-plains-windchime-lesson` + **`sha256:b2ee44df5422a7b4dd9be1358a075c46cefb00992de802607389f6f94ecfa433`** + role=`start`，再核真实连接邻域。M01仅是两次实际result中的实例名。

| 实际输入 | default / 930001 | gears / 930007 |
|---|---|---|
| 指纹 | `13f7f7f480168da132e64f478919450ca8bbe179e6614b9f30b5d0ac31c65772` | `deee1d69cc42840dfc5fae6648e8fc72f016dc2a450da53c94b787d30018f485` |
| 当前真正选择 | M16/M18/M21三模块 | M35齿轮双船模块 |
| 钟门是否选择/出生 | **否**；没有其当前resolved spawn | **否**；没有其当前resolved spawn |
| 模块原点/镜像 | `[0,0]` Block，未镜像 | `[0,0]` Block，未镜像 |
| Port使用 | 只接exit；entry封口 | 只接exit；entry封口 |
| 实际邻接 | C001：exit→M02/R（idea-interface-s12-001） | C001：exit→M02/L（idea-spec02-s12-001） |
| 邻居完整新增机制 | 两船、可穿载台配置1、空怪1 | 两船、群控机制2 |

两个result SHA、profile SHA、map ID、邻居完整版本和连接原件均在机器文件中。当前Provider `runtime-map-v2-slice/2` 仍要求latches为空，所以有ShotLatch类不等于已有runtime-map适配。

## 最小内容与坐标

- 源原件SHA `0846f23881d9106d68032323b6278e4f79550e33f1cb73cf4e920323039da942`，源bounds `[0,76,512,384]`，source_affine=`[1,0,0,1,0,-76]`；actual content已是owned_rectangle_pixels，不重复应用该偏移。
- 两固定台完整保留：局部 `[0,224,480,40]`、`[480,224,32,24]`；没有敌人、奖励、伤害体、hook或移动平台。
- entry接口 `[0,192]`、旧接岸 `[24,206]`，实体封口 `[0,128,32,128]`；封口原声明 `certified=false/physical_validation=NOT_RUN` 保留。接口与旧接岸碰封口，不能直接出生。
- latch.id=`windchime_plains_windchime_lesson`，kind=safe_lesson，bell=`[170,159]`，gate=`[320,4,24,220]`，open_seconds=0（初始闭门，射铃后持续开）。
- 出生**候选** `[48,206]`、`[64,206]`、`[140,206]`，两例world坐标相同仅因原点为零。原生24×36身体在PR78旧锁定宿主中已站稳/射铃/到岸；不是0.4当前宿主的resolved bindings，不能回填为实际出生事实。
- exit几何接口 `[512,192]`，内部接岸身体中心 `[496,206]`。先验收到接岸；完整身体穿过边界/进入邻居要另验其全部机制，不能忽略邻居空怪或群控来凑通过。

## 需要观察的是真实控制事件

本Module没有reward_sites，**不存在应领取的宝箱/金币**。预期是原ShotLatch控制事件，钱包不因本模块增加：

1. 选定实际候选，使用真实PlayerController/Motor/碰撞尺寸/能力快照；保原两台、封口与门。未射击时门应阻挡，不直接写门状态或删除门体。
2. 通过原Router/原射击能力产生弹丸，命中实际bell；原生命周期/session/health/request epoch检查通过后，观察opened、open_count及门碰撞解除。不能把函数直接赋is_open当命中证据。
3. open_seconds=0保持开放；重复命中不重复开启/重复发事件，旧token/已退出/死亡后晚到弹丸或延迟提交被拒绝。暂停、恢复、取消按当前宿主原生命周期处理。
4. 实际走到exit接岸，保留位置/grounded/HP/原射击事件与门状态轨迹。跨C001另列，整图不由此通过。
5. 复用唯一现有玩家/PlayerServices、伤害、钱包、RunSession/Stage/lifetime；不创建旧演示宿主，不为这个模块补授hook或奖励。request里允许的能力不是实际授予证据。

可复用代码已只读核到PR129并与f6源向量叶SHA相同：[control-source-checks.json](../../evidence/runtime-integration-actual-04/control-source-checks.json)。`game/world/components/shot_latch.gd` 的setup:67、射击/投射物接收:133/137、提交:181、取消:217/225仍是原接口；`generated_shot_latch_encounter.gd:7` 依赖旧Manifest/RandomStageAssembler，不能直接塞runtime-map Dictionary。下一适配需做窄映射，保留真实行为，不能因为类存在而称已经接通。

## 证据与下一步依赖

PR78旧 [godot-probes.json](../../evidence/runtime-integration-audit-20261103/godot-probes.json) 绑定原生源12f6cb0、官方Godot4.7.2：三候选实际开枪到约 `[495.92,205.93]`，未射铃约x307.99被挡。其SHA已收入机器输入。它只证明这些固定条件下的旧宿主行为；当前custom4.7.2、M01新适配、存档/取消及真实邻接尚未据此通过。

当前复验状态：**PENDING_NEW_ADAPTER_COMMIT**。下游交付精确新commit、实际引擎SHA、Provider/适配版本、同次result/provenance/原指纹编码、新resolved bindings/能力快照和原生/必要Web运行收据后，复用actual-profile重新绑定并开展上述定向Godot验证。源/选择/出生改变需重新记账，不能沿用M35或旧三模块装载身份；本轮不预测或签署尚未存在的适配器。
