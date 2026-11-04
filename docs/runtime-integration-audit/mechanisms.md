# 少量机制接入资料

范围：1.1.0 的未镜像原始内容；单位像素/秒，Block=128，+x 向右、+y 向下。以下附件是从已核 SHA 的历史 ZIP 原样提取的完整 compiled-content，不是新增生产模块。最新主游戏需要适配现有原生类/资源路径，不需要旧演示场景。

## 精确输入

| Module | 历史 1.1.0 内容版本 | 审计基线 main 9b712fe8 内容版本 |
|---|---|---|
| `game-plains-ferry-gears` | `sha256:18e0578b0631239884f0ff9bb598b04867396bcbe3988c036b512ebe32e092b3` | `sha256:08630e9612caa0744812c7cff605f80b8d8fcc14e97c8846cf3294add8118c88` |
| `game-plains-windchime-lesson` | `sha256:b2ee44df5422a7b4dd9be1358a075c46cefb00992de802607389f6f94ecfa433` | `sha256:9e932540ae915a982f8e0f0f318d5b6b34345c4112f2243f5ab6c9c99a1350b5` |

完整文件：

- 历史载台/齿轮：[compiled JSON](../../evidence/runtime-integration-audit-20261103/samples/package-1.1.0/game-plains-ferry-gears.compiled.json)，文件 SHA-256 `a590ef1cccac757f6f6949b92048365a8a8d23ee6cf74de9619d48a90d5c3015`。
- 历史风铃/门：[compiled JSON](../../evidence/runtime-integration-audit-20261103/samples/package-1.1.0/game-plains-windchime-lesson.compiled.json)，文件 SHA-256 `ec162e3811e8cb01df6ecd20a09185bb7fcdf14e57a3e6133c2d8cc4a0d0594f`。
- main 的完整编译内容分别在 [ferry-gears](https://github.com/zhipijun1996/map-edit/blob/9b712fe814ef228b368c0eb9adf660e39de29e37/modules/game-plains-ferry-gears/compiled-content.json)、[windchime-lesson](https://github.com/zhipijun1996/map-edit/blob/9b712fe814ef228b368c0eb9adf660e39de29e37/modules/game-plains-windchime-lesson/compiled-content.json)，原件是同目录 `module.mapnote.json`；本文绑定 main `9b712fe814ef228b368c0eb9adf660e39de29e37`，不要混用这些不同内容版本。
- 历史包的原件/场景在 ZIP 内 `modules/<ID>/{module.mapnote.json,module.tscn,godot-package.json,compiled-content.json}`；共享运行时 `runtime/module_runtime/`，依赖 `runtime/host-lock.json`。包中 `integration/` 是既有安装/加载示例。

## 移动平台与环境伤害：ferry-gears

历史 bounds `[0,342,1024,768]`，偏移 `[0,-342]`。以下是**源坐标**；转占用矩形局部时只给点/矩形位置 y 减 342，尺寸/速度/位移向量不平移。

| 字段 | 实际值 / 含义 |
|---|---|
| `moving_platforms[0]` | ID `ascent_0`，中心 `[250,932]`→`[550,792]`，size `[120,24]` |
| `moving_platforms[1]` | ID `ascent_1`，中心 `[830,630]`→`[500,490]`，size `[120,24]` |
| 两者时序 | travel_duration=3，dwell_duration=1.5，initial_phase=0；完整往返周期 9 秒 |
| 时序语义 | 本地时钟 0 开始在 start 停 1.5s，线性到 finish 用 3s，停 1.5s，再用 3s 返回；phase 是周期分数，`elapsed = fposmod(clock + phase*9,9)` |
| `saws[0]` | source_id=`relay_gear`，中心 origin=`[512,710]`，travel=`[0,240]`，radius=20，period=4.8，initial_phase=0 |
| 锯轨迹 | `origin + travel*sin(TAU*(clock/period+phase))`；travel 是振幅向量，不是终点；中心 y 范围 470..950，初始先向下 |
| 锯伤害 | damage=1，contact_interval=0.7s，经宿主伤害策略处理接触、无敌与事件去重，不是每帧扣血 |
| `hazards[0]` | 静态危险矩形左上/宽高 `[44,1000,912,40]`；此列表没有自带伤害字段，原生接触发射器默认 damage=1、interval=0.7s |
| 固定地形 | `platforms` 为左上/宽高；`one_way_platform_indices=[2]` 只将第 3 块设可穿，不得把所有平台做成可穿 |

占用局部示例：第一台中心起点 `[250,590]`，锯中心 origin `[512,368]`，危险矩形 `[44,658,912,40]`。载台是带玩家的原生移动碰撞体，不能只动画画面。原生定义依据固定宿主 [ModuleMovingPlatformDefinition](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/module_moving_platform_definition.gd)、[ModuleSawDefinition](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/module_saw_definition.gd)。本轮没有更改时钟或玩家物理。

## 门控：windchime-lesson

历史 bounds `[0,76,512,384]`，偏移 `[0,-76]`。唯一 latch：

- `id=windchime_plains_windchime_lesson`，bell 源 `[170,235]`→占用局部 `[170,159]`。
- gate 源 `[320,80,24,220]`→局部 `[320,4,24,220]`，初始闭合，实际阻挡玩家。
- `open_seconds=0`：命中后持续打开，不是立即关门。`kind=safe_lesson`、prompt/link_color 是教学/展示信息，不是免除射击的通行许可。
- 使用玩家原生射击命中 `ShotLatch`，经同一 lifetime 激活并关闭门碰撞；不是宿主在玩家靠近时自动开门。玩家、弹药/后坐力、门生命周期归主游戏所有。
- 本轮原生正例三个候选射铃后通过，未射击负例被门挡住；不是仅检查场景可实例化。

## 注入服务、身份与坐标边界

包内两个样本均使用 `runtime/module_runtime/module_loader_v3-1d72f57d63dd.gd`。它创建 Module 内容，`bind_player(player, policy, lifetime, wallet, existing_scope=null, instance_id="")` 需要调用方已有的 `PlayerController`、`FrameDamagePolicy`、`DemoLifetime`、`RunWallet`，不会创建玩家、初始化全局经济或补满资源。这两个样本不需要额外 meta/region 服务，也没有原生 profile 覆盖。

| 宿主提供 | 责任 / 现有对应 |
|---|---|
| 玩家 | 原生 motor/身体、射击、动作资源、health；24×36 是本次观察配置，能力改变需要另验 |
| 伤害策略 | 注册主玩家/伤害目标，统一 request 队列、每帧结算、无敌和去重；不得并行维护第二份 HP |
| lifecycle | 同一 active/epoch/token；死亡、换图、卸载时使旧定时/事务失效，按主游戏生命周期管理 |
| wallet | 同一 grant/balance；保持奖励 stable event 去重，重复装载不能重复发奖 |
| instance_id | 来自生成结果的持久 ID，不使用 NodePath 后备值做存档身份；同一稳定 Module 可有多个实例 |
| 本地 ID | `ascent_0`、`relay_gear`、latch.id、reward.id 是实例内部对象标识；跨实例事件用实例命名空间，不是把“reward”当全图唯一 ID |

既有 loader 的锯/静态伤害使用 `module/<uri_encode(instance_id)>/<uri_encode(local_source_id)>`；奖励定义使用 `module/<instance_id>/<reward.id>`。包自带重复实例检查；卸载取消 latch。**宿主自己的完整卸载、跨实例去重、存档重载仍应在接入分支测试**，不能仅据这个接口签名宣布兼容。

坐标：仅装载未变换的源场景时，将场景放在 `mapOriginPixels + sceneOriginOffsetPixels`。已由 map-gen 物化的 Cells/Ports/Routes 加 `mapOriginPixels` 即可，不再用源 loader 重建一遍丢掉封口/镜像。原 loader 主动拒绝非单位轴的 transform；这是旧模板装载 API 的范围，并不表示 map-gen 不得统一镜像全部内容。

最新主游戏 `30e36c9…` 已将主要类移至 `game/`：例如 player → `game/player/player_controller.gd`、伤害 → `game/combat/damage/frame_damage_policy.gd`、钱包 → `game/economy/shops/run_wallet.gd`、门 → `game/world/components/shot_latch.gd`。完整文件 SHA/公开方法及路径对应见 [host-api-observations.json](../../evidence/runtime-integration-audit-20261103/host-api-observations.json)。API 名称仍在不代表旧资源路径有效；复用主游戏原生类，按目标版本显式映射依赖，不覆盖安装旧演示工程。

## 证据边界

- 包内原有资格绑定固定原生宿主/运行时 fingerprint/内容/Route/初态，UNKNOWN 继续保留。接口 face/normal 是外边界朝向；INOUT 是许可声明，并不证明任意反向动作成功；显式有向 Route 才是需要选择/核验的路线。
- main 两个样本本轮复用既有 `audit_cases`：Cells 与冻结输入相符（1031 / 179 帧记录），这是静态一致性，不是新跑 1031 帧游戏。
- 本轮新跑 Godot 的门例见 [godot-probes.json](../../evidence/runtime-integration-audit-20261103/godot-probes.json)。移动平台/锯本轮只审计数据与原生实现、保留旧验证范围，**没有在最新主游戏重新做载台承载/伤害/卸载实测**。
- 镜像、封部分 Port、任意初相、邻模块完整接缝、Boss/敌人/整图玩法均不能由这些样本推得通过。主游戏最小下一步是对这两个精确版本做承载/伤害节奏/射铃/卸载重载验收，再扩展机制，不调整玩家或经济来取得通过。
