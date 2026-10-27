# 当前原生 Module 包入口

当前公开编译/核验入口仍为 `pcg.migration.godot_package`，按真实内容选择 v2/v3/v4/v5 后端；不把历史 v2 的支持限制当成全库限制。v3 已适配原移动平台、钩点、敌人、荆棘/齿轮和扩展风铃关系，v4 增加原生拾取与固定能力档案，v5 增加精确原 fixture 容量和真实区域宝箱二选一。每件实际支持范围只以其 `godot-package.json`、实际加载证据及契约为准，未知机制仍拒绝。

v5 公共分发已经应用并冻结，见 [激活回执](../foundation-v1/native-v5-public-activation-v1.json) 和 [服务说明](../../../docs/l4-mapgen/native-module-services-v5.md)。各包继续绑定自己的原后端，不重标旧包。读取索引时必须保留 `requiredNativeProfile`、真实初始能力条件与未认证项。

在仓库根目录试玩一个现成的静态包（安装固定 Godot 与恢复运行依赖后）：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --path pcg/prototype/godot "$PWD/modules/game-micro-board/demo.tscn"
```

加 `-- --replay --case 0` 回放其冻结输入；这不是新的独立留出实验。A/D 移动、空格跳跃、左键松开射击；拥有钩能力时右键或 E 使用钩，W 交互、S 下穿单向平台，奖励弹窗沿用原 UI。初始资源由宿主按该包精确档案初始化一次，进入其他 Module 不补充资源。手动操作才是试玩，自动回放不计人工认可。

实例放置使用所选目录配置的真实偏移，不能忽略原 bounds 的非零起点：

```gdscript
var offset = entry.sceneOriginOffsetPixels
instance.position = Vector2(origin_block_x, origin_block_y) * entry.foundation.blockSize + Vector2(offset[0], offset[1])
```

随后按所选后端 API 绑定已有玩家、伤害策略、共享钱包与必要状态。以下保留早期 v2 的 API/实测说明；其中依赖数、支持范围和证据数量仅属于当时版本，不能代替当前包的 manifest 或整图验证。

---

# 固定 Module 数据包运行适配 v2（兼容历史 v1）

这是既有内容的离线编译和运行适配，不创作新内容，不运行生成规则、参数搜索、路线求解或第二套物理。`module.mapnote.json` 的 `objects` 是内容原件；`compiled-content.json` 是它的可重建派生数据。旧 canonical `cases.json` 逐字节保留，只为手动演示的初始位置和冻结输入回放提供资料。

## 编译和实际加载

仓库根：

```sh
python3 -m pcg.migration.godot_package \
  --module /absolute/new/module.mapnote.json \
  --cases /absolute/original/cases.json \
  --out /absolute/empty/package-directory \
  --stable-id b31-n16-west-low-east-high-interface0
```

Python 公开入口：

```python
from pcg.migration.godot_package import (
    compile_package, run_package_validation, verify_package,
)
compile_package(module_path, original_cases_path, output_dir,
                stable_id=stable_id, project_root=None)
loaded = run_package_validation(output_dir)
verified = verify_package(output_dir, require_loaded=True)
```

`PackageError.code/details` 给具体冲突。输出目录必须为空，输入通过审计后才原子写出；不覆盖既有包或实验。缺少真实冻结输入返回 `missing_frozen_replay`，不能在线解释 `control_plan` 补做一条见证。认证需要删去录像缓存时，根迁移工具另存 `physics-input-cases.json`，它与包内旧完整 `cases.json` 的差异由迁移工具核对。

包内文件：

- `module.mapnote.json`、`cases.json`：原输入字节；不改 geometry/program/证据字段。
- `compiled-content.json`：从 objects 解码的原组件定义、显式 Port 元数据和入口辅助数据。
- `module.tscn`：Node2D 内容实例，创建原 `PlatformingModule` 碰撞和美术；绑定外部玩家后创建原风铃、门、奖励服务。
- `demo.tscn`：隔离可玩宿主，使用原玩家场景、Controller、InputRouter、Motor、DamagePolicy 和现有 Context。默认手动键鼠；不调用生成规则。
- `geometry-audit.json`、`godot-package.json`：对象与每条旧 case 的精确几何/行为审计、产物 SHA 和运行依赖 SHA。

原生试玩：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --path pcg/prototype/godot /absolute/package-directory/demo.tscn
```

A/D 移动、空格跳跃、鼠标左键松开射击。附加 `-- --replay --case 0` 回放指定冻结输入。`--input-smoke` 是自动键鼠烟测，不能记为真人试玩。

## 外部游戏调用

```gdscript
var instance = load(module_scene_path).instantiate()
instance.name = stable_instance_id
instance.position = Vector2(origin_block_x, origin_block_y) * 128
world.add_child(instance)
var binding = instance.bind_player(
    player_controller, frame_damage_policy, demo_lifetime, run_wallet,
    null, stable_instance_id
)
assert(binding.ok)
```

调用者提供已初始化并注册玩家的原 `FrameDamagePolicy`、相同的有效 `DemoLifetime` 和共享 `RunWallet`。适配器不新建玩家、不移动外部玩家、不授予能力、不修改资源，也不设置存档/恢复锚。内部由 post-physics capture 检查真实落地后领取；`SimpleRoomReward` 和 `RunWallet` 仍拥有奖励事务。稳定实例 ID 给奖励来源加命名空间，避免同模板第二实例被钱包误判成重放；重复实例身份会拒绝。默认 NodePath 身份只适合当次场景，存档消费者应明确传稳定 ID。

`instance.world_port(id)` 返回元数据和变换后的世界位置；它不认证接缝。这里只允许平移，缩放、旋转和镜像绑定会拒绝。镜像、未连接 Port 封口和整图验证仍须对应认证，适配器不会补地形或恢复资源。

## 依赖与安装边界

当前绑定的物理运行项目是 `pcg/prototype/godot`，原游戏提交 `12f6cb006d7119598e3235f4ca4f7323e4c9d092`。编译先逐 SHA 核对 `source_provenance.json` 的 870 原件，再列出当前所需原有适配器及这3个运行脚本，共884个依赖；没有拷贝386MB游戏工程。依赖记录给仓库相对 `path`、SHA，以及原项目文件的 `res://` 位置。

v2 把8个仓库适配脚本按原相对目录同字节复制到 `runtime/<repo-relative>`，另复制1个 `plains_cells.gd` 作为既有相对 preload 所需的同字节别名，总9个小脚本。没有修改任何运行时源码，也没有复制870个游戏资源。两scene直接引用 `runtime/pcg/migration/runtime/{module_loader,package_demo}.gd`，所以包可以从任意深度的 staging 搬到 `modules/<stableid>`，不要求复刻安装层级或创建指向工作区的 symlink。`res://` 依赖仍来自运行项目，尤其4个原Harness适配器须按原位置安装；不能据此宣称正式主游戏已接入。

`godot-package.json` 记录 `compiler_version=foundation-data-runtime/v2`、编译器源SHA、可搬迁布局和每份同字节副本；`artifacts` 使用递归相对路径。核验会重算源依赖与包内副本SHA、完整文件集合及两scene相对引用。历史 v1 绝对引用包仍可核验，不能将v1证据改标签当成v2加载证据。

升级已存在的库包时，保留旧包及其manifest/加载证据；新建v2包，逐字节复用原内容JSON、cases和物理证据，生成新编译manifest后实际回放所有冻结case。搬目录后的独立加载证据应写在新复制品中，原包证据不覆盖。相同内容版本的编译产物更新不算新Module或新物理认证。

正式游戏安装还需把依赖按对应 `res://` 路径及现有适配器相对布局安装一次，并核对目标工程实际 SHA/类注册/资产导入；不得把不同游戏版本直接标成兼容。本轮未修改或启动正式 gunman-rush 项目。游戏调用接口已在同物理基线的隔离试件实际加载，不等于已接入正式流程。

## 证据核验

`run_package_validation` 真正启动 Godot，对包内每条冻结 case 各跑一次。`load-evidence/index.json` 以相对路径绑定每条的 `input.json`、`command.json`、`stdout.log`、Godot `receipt.json` 和实际进程 `execution.json`；原生回执还绑定 manifest/doc/cases/compiled/scene/engine SHA。失败保留，不重试选相位。

`verify_package` 不信任 `meta.godotLoad.passed`：重算所有产物、完整依赖集合、objects↔case↔compiled、Port 元数据、输入/命令/引擎/退出码和原生日志绑定，再核每帧冻结输入、生命、最后6帧真实落地稳定、奖励与无回退、全部 case 覆盖。编译 manifest 本身加载后保持不变；可将返回的 `evidence.path/sha256` 写入迁移 meta。根迁移工具负责其后来新增的认证/meta/缩略图文件绑定。

加载证据只验证本数据加载器能消费这些旧见证，不替代新地基的 Route、初始权限、封口、镜像、接缝或整图认证；`foundation_route_certification` 明确为 false。

## 当前范围和实测

支持实体/单向平台（含原 wallClimbable 标记）、原普通/限时风铃门、既有 v3 互斥双门、原返回侧接收器、原金币宝箱。旋转对象、移动平台、敌人、钩点、荆棘、齿轮及未知机制字段当前显式拒绝，不能悄悄丢弃；后续迁移时扩展映射并分别实测。

N16、N08、N17、N06、N10 的九条原 canonical 先有3049帧加载烟测，最终绑定后再有九条3049帧实测全部通过；原先281帧 N16 原型也保留，不混作新的认证。平移实例/共享钱包试件实际收到8+8币，绑定前后玩家状态相同，重复身份被拒；手动键鼠适配烟测90帧实际1跳1枪且HP5。它们不是新 Module，也不是人类趣味批准。

```sh
python3 -m unittest pcg.migration.tests.test_godot_package -v
```

规则与坏输入测试覆盖单像素篡改、重 hash 的 compiled 篡改、错误铃绑定、缺冻结输入、伪 passed 标签和防止覆盖旧包。Godot 验证预算和补充绑定验证原因见 `validation-plan-v1.json` / `validation-plan-v2.json`。


### v2 可搬迁实测

新scratch包先实际回放N16的281帧，通过HP5/8币/6稳定；再把相同包字节复制到另一处多层任意目录（不带旧load-evidence，不设pcg symlink），再次真实加载回放281帧通过。两地manifest字节相同，运行脚本均来自包内镜像副本。新旧加载日志分别保留，见 `/workspace/scratch/portable-v2-relocation/proof.json`；这些是加载器可搬迁性试件，不是新地基动作认证。13个包测试全部通过，含v1兼容、v2源字节相等、递归产物绑定及重hash副本篡改拒绝。
