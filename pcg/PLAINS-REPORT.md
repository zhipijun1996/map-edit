# 平原：用不同判断和动作链组织生成（2026-10-24）

本轮得到6个通过既定regular技术门槛的参数候选，按真实动作链展示3个代表。不是6种新玩法；也尚未证明“有趣”、人类难度或量产能力。当前仍是离线程序生成与Godot验证，真人观感/手动试玩/批准均为0。

[下载8.7秒合集](https://zhipijun1996.github.io/map-edit/generation/videos/plains-v1/all-samples.mp4) · [观看与分段下载](https://zhipijun1996.github.io/map-edit/generation/) · [录像清单](../generation/videos/plains-v1/manifest.json)

## 生成目标与样例

|编号|需要判断什么|实际执行与压力关系|单段|
|---|---|---|---|
|P01|瞄准方向同时影响移动与机关|单跳→朝下偏左射击→反冲抬升且击钟开门→调整并稳定落地；下方荆棘|[2.2秒](https://zhipijun1996.github.io/map-edit/generation/videos/plains-v1/sample-01.mp4)|
|P02|先命中怪物补回空中射击，再选择第二次射向|单跳→向下瞄准真实哨兵→实际命中回充→第二次向后射击横移→落地；深坑荆棘|[2.6秒](https://zhipijun1996.github.io/map-edit/generation/videos/plains-v1/sample-02.mp4)|
|P03|起跳时长受低顶棚限制，落地后重新观察时机|短跳/松跳→水平反冲穿过低顶棚→落地恢复→观察移动齿轮→地面通过；顶棚及坑底荆棘|[3.9秒](https://zhipijun1996.github.io/map-edit/generation/videos/plains-v1/sample-03.mp4)|

这是小尺寸技术探针，动作较快，视频可暂停查看；不是完整正式平原段落。P02的怪物是原EnemyActor、AI攻击、伤害、接触和回充逻辑；不是固定回能图标，不改HP或赠送空中次数。它在本见证中受到1点伤害、剩余2HP，未要求击杀。

P03见证记录：第73帧落地；齿轮前有29帧实际有支撑且静止；第128帧在地面经过齿轮横坐标，当时齿轮位于平台下方。跳跃、反冲、机关开启、命中及资源变化来自逐帧记录，不由模块名字推断。这里“观察”的证据是相位条件策略与实际暂停，不代表已经模拟人的认知。

## 参考正式平原与物理基线

游戏已检查的main为`cd4989a68613e0b457cdfd5e252634dd57008505`。对`scripts/resources/scenes/config`完整递归blob树共1302文件与`12f6cb0`比较：只有production_impact配置及平原前景/表现两脚本改变，无删除；玩家、枪械、机关和敌人机制未变。证据：[source audit](research/plains-source-audit.json)。资产/文档未由截断的compare响应推断一致。

真实运行继续绑定`12f6cb006d7119598e3235f4ca4f7323e4c9d092`，官方Godot `4.7.2.stable.official.ed1daf0bf`，60Hz；二进制SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。870保护原件逐SHA一致。为原敌人动态表现补齐同一游戏提交的6份原资产，出处与SHA见[additions](research/plains-runtime-additions.json)；不改变原件。

正式关卡参考：[plains_route_recipes.gd](research/audit/scripts/generation/plains_route_recipes.gd)，尤其well_arch_phrase、low_arch、bell_deadline、gear_timing、recoil_crossing；游戏原`docs/plains_interactive_platforms.md`中的荆棘宿主、齿轮后续、远程钟与敌人落点压力。复用的是动作/压力关系和基础Cell，没有输入完整预制Module。

能力严格为`move/jump/shot_recoil`。允许普通单跳；禁用二段跳、墙跳、钩索。真实基础空中射击上限为1，命中和落地恢复由原组件处理。`resources/player/demo_ui_01/time_energy_v2.tres`实际`shooting_consumes_energy=false`；不沿用旧文档“两发空中子弹/射击耗精力”的叙述。

本轮还发现旧实验适配器强制legacy角色皮肤，但原枪口读取当前美术pivot，造成不适用的远距枪口。本轮**只在新的平原worker/录像场景恢复正式角色皮肤**，枪口和原子弹射线与游戏一致；没有修改旧worker或旧数据。因此新旧射击实验不能无条件合并统计。另将伤害目标分清：伤害敌人不判作玩家受伤；所有原伤害提交保留，玩家接触/掉血仍失败。

## 算法与实际执行

入口：[pilot.py](prototype/plains/pilot.py) → [calibrate.py](prototype/plains/calibrate.py) → [produce.py](prototype/plains/produce.py)。

1. 小型动作/压力语法提出3类关系与36个动作参数探针，动作含普通跳、松跳、不同方向射击，怪物命中后允许重复反冲。
2. 原Godot跑真实无接收面的运动；记录实际枪口、轨迹、命中与资源。按下降穿越高度计算接收面位置，按真实射线放置钟或怪物；再补低顶棚、齿轮、门和荆棘宿主。
3. 校准阶段筛选真实动作特征，同一实际序列最多选2个候选；冻结几何、策略、门槛和新holdout种子后才做最终扰动测试。
4. 档案按真实序列分组，记录无伤稳定出口、扰动容错、反例和失败；同一机制不同位置/尺寸仍算变体。P03的阶段转变另由实际落地/停留/齿轮穿越轨迹证实。

生成和测试均由Python/GDScript程序运行；没有调用LLM给关卡静态打分、在线推理或训练模型。AI在本轮承担代码实现、机制审计和失败分析。目前语法仍由研究者提出3类关系，尚不是能自动发明任意机关或动作关系的开放搜索器。已有FI/MAP-Elites架构可供下一轮扩展，但本轮不把有界枚举筛选冒称全新进化算法成果。

核心实现位置：

- [synthesis.py](prototype/plains/synthesis.py)：动作参数、真实轨迹构造、敌人/钟/地形压力关系。
- [runner_plains.gd](prototype/godot/runner_plains.gd) / [plains_cells.gd](prototype/godot/plains_cells.gd)：原控制器调度、正式枪口、原ShotLatch与EnemyActor、目标明确的伤害和逐帧证据。
- [evaluation.py](prototype/plains/evaluation.py)：真实动作链、连续空中双射、实际命中回充、扰动实例化。
- [quality.py](prototype/factory/core/quality.py)：既有regular门槛，未降低。
- [record_plains.py](tools/record_plains.py)：混合批次冻结见证的原生输入录像、物理结果交叉核对。
- [summarize_plains.py](tools/summarize_plains.py)：逐SHA原件检查、成本与阶段决策观测。

## 测试与失败记录

规则：clean动态候选12相位/敌人初始冷却样本，静态P01 clean1个确定性样本；mild12次（动作时序±1帧、瞄准±2°）；moderate12次（±3帧、±6°）。初始齿轮相位随机；敌人只改变初始idle冷却0～0.6秒，原攻击时长/伤害/速度不变。各组同一随机方案。要求HP5、完整身体无危险接触、出口稳定至少6帧、无高级能力，并真正执行目标机制。

|代表|clean|mild|moderate|结果来源|
|---|---:|---:|---:|---|
|P01|1/1（静态）|12/12|10/12|plains-production-v1，seed1240810|
|P02|12/12|12/12|10/12|同上|
|P03|12/12|12/12|9/12|plains-production-v2，**新seed83007211**|

这是有限程序策略样本，不是人类成功率或总体100%证明。每个代表另有同序列参数变体；共6个技术待人评候选、3个展示代表。门槛仍是clean≥90%、mild≥85%、moderate≥65%，各扰动至少12样本；没有失败后改名“精密难度”通过。

较便宜策略测试：两批合计不射击0/32通过，延长普通跳且不射击0/32，钟方案改成朝左瞄准0/8，怪物方案保持双射但移除怪物0/8。均为有限反例策略，不是穷尽所有人类路线。**P03不观察相位也有通过样本**：改进两变体合计6/8无伤；等待帮助构成低风险策略，但不能宣称是唯一必需操作。后续应比较更广策略的风险/速度选择，不能靠标签声称必要性。

完整失败轨迹与源快照均保留：

- pilot-v1：36次Definition拒绝，探针出口错误放在边界外；不是36条真实运动证据。
- pilot-v2：56次返回，10个低顶棚候选被原出口/齿轮安全约束拒绝；修正出口关系，未关闭约束。
- pilot-v3：54次、6个名义成功；calibration-v2：66次。calibration-v1在12次输出后因资源退出ERROR被拒，未当成功证据。
- production-v1：266次、23批；4候选通过、2个低顶棚候选误差容错失败。保留失败，不能把本批拿来重新调参后仍称独立留出。
- 返工将低顶棚后的空中/齿轮耦合改成有支撑恢复带与第二次时机选择。pilot-v4：54次、12个名义成功；calibration-v3：138次；按原规则冻结2个low_arch候选后，production-v2：96次、8批，独立新种子验证，2个通过。旧钟/怪物通过证据原样复用，不重新抽幸运种子。

production-v1总墙钟39.38秒、production-v2为14.43秒；这是本机整批筛选/扰动/反例预算，**不是单个全新Module端到端量产耗时**。Godot子进程统计峰值RSS约295～363MiB（run累计最大值，不是逐候选独立内存）。包含发现/校准、工程修复和人评的量产成本尚不能由这两批外推。详细逐运行成本见[review audit](results/plains-review-v1/audit.json)。

录像与冻结验证逐项一致：caseID、Module SHA、最终帧数/位置（误差<0.001）、原跳跃/射击/高级能力计数、全部机关/敌人事件。仅原伤害source中的进程本地Godot ObjectID后缀归一化，时间/伤害/HP/命中/枪口仍逐项比较。首次录像比对因ObjectID不同失败的日志也保留，修正比对后复核同一原片，无轨迹改写。正常60Hz/1倍播放，单段连续保留动作与等待；合集仅按P01～P03拼接原片。

编辑器`npm run check`、原factory26项测试、新平原9项合同测试通过。原生录像3段均通过与真实headless见证交叉核对；它们证明有限策略可行，不替代真人趣味评价。

## 恢复与复跑

先按[WORKSPACE.md](WORKSPACE.md)恢复godot-runtime-v1并安装精确引擎，再恢复本轮（不会覆盖不一致文件）：

```sh
python3 pcg/tools/restore_archive.py plains-generation-v1 --extract
cd pcg
toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path prototype/godot --quit
python3 -m prototype.plains.pilot --name plains-pilot-new
python3 -m prototype.plains.calibrate --pilot plains-pilot-new --name plains-calibration-new
python3 -m prototype.plains.produce --calibration plains-calibration-new --name plains-production-new --holdout-seed 9300421
python3 -m unittest discover -s prototype/plains/tests -v
```

旧阶段必须从各自`source_snapshot`复现；当前代码包含低顶棚返工，不能用它冒充重跑v1。原始输入输出gzip、执行命令/失败日志、阶段源快照、视频及运行清单在`archives/plains-generation-v1`逐文件SHA归档；AVI和导入缓存可重建，不上传。公开视频独立位于`generation/videos/plains-v1`。

## 下一轮生产目标

先扩大“需要不同判断”的覆盖，优先原平原已有能力：同一枪既救位移又操作钟；按顺序/限时击钟；射击启停渡船；齿轮前等待、跳过或走高路；敌人作为威胁与空中资源的冲突；低风险主路和高难奖励路汇合。

将这些关系写成可组合动作/压力合同，允许重复、多个Cell和真实落地重置。新增可选策略与跨策略评估：能否不消耗反冲/不命中/绕开机关；选择的速度、风险和操作要求有何差别。再用实际轨迹的动作顺序、瞄准切换、落点选择、等待/恢复分布维护质量档案；外观与参数变体单独计数。人类用P编号和视频反馈节奏/可读性后定向返工，新版本重验。

通过多轮相互独立的数据和真实观感后再离线批量生产。游戏运行中先从已验证档案按区域、难度、入口出口和资源状态抽取/拼接；运行中创造未知新Module需要另测性能与快速验证，不在本轮承诺。Map Notes下一步显示这些机制、轨迹、质量和视频绑定，不把研究候选自动加入正式可用库。
