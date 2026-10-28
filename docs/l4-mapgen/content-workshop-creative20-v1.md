# 大模型创意生产与20种新玩法 Module

本轮交付 **20种新的玩法关系、20份标准Module、20段真实Godot原生录像**。不计旧六家族、参数变体、普通升降适配、双环Macro或双环挂点适配。新内容均通过原regular技术门槛并进入持久候选库；人工趣味、实际试玩和生产认可尚未评审。视频与逐项下载见 [内容目录](../../generation/workshop/creative20-v1/README.md)，本地打开同目录 `index.html` 可按玩法和能力检索。[观感离线包](../../generation/workshop/creative20-review-v1.zip)约29 MB，解压即可看全部视频和文档；真实试玩另按下方恢复运行时。

## 创意确实由大模型产生

用户要求使用大模型，随后明确选择“使用当前codex会话，可以调用subagent。”本轮实际使用当前Codex会话及六个授权子代理：五个机制方向的设计与实现任务，以及一个独立新颖性批评任务；根会话额外实现活敌占区关系并复审视频节奏。几何、动作参数、反例和留出由程序执行。模型未公开精确版本，记录为unknown，不虚构模型名或外部API成功。

[人工原话和解释](../../pcg/creative-production/human-creative20-request-v1.json)、[真实模型任务与来源](../../pcg/creative-production/campaign-v1.json)、各方向设计卡、失败修订及冻结实现源均保留。曾实际执行独立Codex CLI，返回401；提示、事件和错误回执在归档的 `results/workshop-creative-llm-round1-v1/`。失败没有用模板假装生成成功。当前提供的是可继续执行的大模型会话工作流，未部署后台在线创作服务。

复用 [创意生产者skill](../../.agents/skills/pcg-creative-producer/SKILL.md) 和 [生产工坊skill](../../.agents/skills/pcg-module-factory/SKILL.md)。外层模型读需求、现有关系和失败账本，提出假设、辨认Cell缺口、实现隔离规则、分析反例并修订；内层原生产器做固定预算搜索和验证。没有可执行规则时返回needs_design，不能改标题、换Seed或替换普通房间继续计数。

## 20种内容

逐项玩法解释、标准JSON/SVG、完整录像、能力、精确版本、原需求、见证源和证据索引在 [发布manifest](../../generation/workshop/creative20-v1/manifest.json)。[最终模型选集](../../pcg/creative-production/novelty-review/selected20-v2.json) 保留完整独立性理由。

|编号|玩法|玩家需要处理的关系|
|---|---|---|
|M01|保留二跳越低檐|低檐压住提前上升，保留有限空中跳到开阔处|
|M02|踏空贴墙反蹬|先主动下降获得墙面，再反向蹬回高岸|
|M03|双壁绕刺越顶|对侧接触改变发射高度，避开首墙带刺段|
|M04|空中挂停主动跃出|先形成空中观察点，再主动决定离挂|
|M05|触环恢复二跳|到环前花掉二跳，真实接触恢复后再次消费|
|M06|自动弹钩后改轨|接触自动抛出，不能停留，必须处理新飞行|
|M07|诱敌发射借短门|保留视线诱导真实攻击提交，再脱离弹丸威胁穿门|
|M08|跟锯穿廊掉层|追随危险释放的空间，并离开其返程轨道|
|M09|清敌身露射铃|真实敌人吸收弹丸，清除身体才露出铃射线|
|M10|探身开锁再折返|从低通路绕过高遮挡，击中远铃后返回原门|
|M11|活敌压区维持门|击退活敌使其占区，把敌体转成暂时钥匙|
|M12|撤桥自坠|射击开桥同时撤掉自身支撑，承诺进入下层|
|M13|击退腾出落位|敌人占住实际身体安全间隙，先处理它才能着陆|
|M14|反向击铃借墙折返|同枪触发与反冲先送向墙，再借墙反向过门|
|M15|周期危险择时离挂|挂停提供观察，自主危险相位决定离挂窗口|
|M16|离台避险重接同台|离开危险载台，在安全处预测并重新截获它|
|M17|弹丸穿运动射线窗|不骑挡板，求弹丸飞行与遮挡运动的真实交会|
|M18|缓降高度预算择窗|墙滑持续损失高度，择相会消耗发射位置|
|M19|可见双目标有序事务|两目标均可见可射，操作顺序却不可交换|
|M20|先压门再取回载台|同台先作为开门钥匙，再释放作运输支撑，两用途互斥|

最初选集还包含“双台相会转乘”。根会话查看其37.45秒原速录像，发现入口等待及7秒停驻明显拖慢节奏，主动将它标为 `pacing_held`，用M07替换。旧选集和技术证据不变，也没有编造人工差评。[选择修订收据](../../pcg/creative-production/novelty-review/selection-pacing-revision-v1.json) 和 [独立审查v8](../../pcg/creative-production/novelty-review/review-v8.json) 分别保留原因。诱冲占区、双环折返、普通升降机等仍可作适配参考，但不增加本轮家族数。

## 固定生产与反驳

内层 `pcg.prototype.workshop.production_loop` 复用原WorkshopEngine、动作语法、regular质量器、标准导出和CandidateLibrary。新增callback只扩展规则编译、目的关系判定、反例生成及薄消费者；没有第二套物理模拟、候选库或Map Generator。共享Harness扩展统一实现，各方向使用隔离路径和extra_sources冻结；真实角色、承载/惯性、射击、资源、敌人伤害、跳跃恢复仍使用原组件。

每轮先写协议，再静态预检、clean及少量mild筛选、精确发布几何和相位的廉价反例、原regular完整校准、留出前固定选择与见证、独立留出。通常每接口最多4个控制候选、筛选6个mild；完整mild/moderate各12个，动态clean12个、静态clean1个。门槛不变：clean≥0.9、mild≥0.85、moderate≥0.65。实际预算、失败和选择时间以各run的protocol与selection-before-holdout为准；没有事后降低标准。新20的独立留出合计 **598/610安全稳定**，这是有限自动策略样本，不能当作真人通关率或一般必要性证明。

反例允许仍实现核心因果的替代动作。独立模型 [目的标签审计](../../pcg/creative-production/novelty-review/checker-suppression-audit-v2.json) 检查了原20及M07：没有将已知安全反例仅因不符合指定动作词而拒绝。普通长按跳、入口同步、提前地射、越顶、杀敌和同墙复位等均按机制扩搜。有限搜索未发现绕法，不等于不存在绕法。

真实失败影响了后续设计：二跳恢复旧版能用普通长按跳到环，新版提高真实环位并扩大接收距离；旧敌人落位只依赖窄目标判定，14条无射反例成功，新版用刺与敌体挤出实际身体间隙；旧落桥后反冲声明被提前射击推翻。新全局撤回通知覆盖失效版本，原件保留，库检索拒绝重用。参见 [撤回索引](../../pcg/creative-production/novelty-review/withdrawal-notices-v1.json)。合法替代不属于撤回事由。

早期通用生产试验也保留：v2冷启动330用例约96.76秒，新增2个同家族实例；warm进程约1.04秒、0物理调用，复用并跳过同源失败。它验证生产效率，不计为20个新家族；v1相位证书失配版本已撤回。

## 真正可用的入口

在仓库根执行：

需要Python 3.11+、Node.js及官方Godot4.7.2。Linux首次检出先安装引擎（已有相同SHA则跳过下载）：

```sh
mkdir -p pcg/toolchain
curl --fail -L -o pcg/toolchain/godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
printf 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  pcg/toolchain/godot.zip\n' | sha256sum -c -
python3 -m zipfile -e pcg/toolchain/godot.zip pcg/toolchain
chmod +x pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64
```

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py content-workshop-creative20-v1 --extract
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit
python3 -m pcg.prototype.creative_batches.catalog_v4 --list
python3 -m pcg.prototype.creative_batches.catalog_v4 --play 1
```

A/D移动、空格跳、左键射击、E/右键钩索；真实样品仅启用声明的能力。Retry重新开始，Replay播放实际见证。launcher使用逐项真实消费者场景与单case输入，不重写正式主游戏。官方Godot4.7.2与870份原游戏保护文件保持原SHA；新增Cell使用独立路径。带新Cell的模块必须加载对应消费者及实现源，不能仅导入通用图形就认为机关已经可用。

原生产循环可执行：

```sh
python3 -m pcg.prototype.workshop.production_loop --name fresh-production --cycles 4
```

这条命令只执行已注册规则，不独立调用大模型发明关系。继续产生新关系应使用创意skill的模型外层，查看失败并新增隔离规则，然后调用同一内层。各方向独立实现的精确重跑命令、预算和源码在其run与最终交接manifest中。

## 给任务B的接口

[统一候选目录与新进程检索](../../generation/workshop/creative20-v1/candidate-catalog.json) 使用原CandidateLibrary，并保留每条完整Map Challenge Specification、准确case、Cell消费者、版本、原生视频和生成源。20份持久候选通过原完整需求查询，从新进程检索复用，新增物理调用0；源证据、模块身份、gzip原始批次及冻结源码逐SHA核验。归档恢复后原链接有效。

标准合同仍是 `gunman-rush-level-sketch/v1 + generationContract`，不默认外边框，也不补接缝平台、传送或资源。只声明已验证的有限方向与状态；通用逆向、任意进入状态、整图和生产拼装仍UNKNOWN。需求不支持时，查询返回具体conflicts、searched_library和negotiable；改需求不能绕过UNKNOWN。

部分基底导出保留原source.path；具体创意规则的真实实现源以逐项proposal_source和物理source_binding的SHA为准，不将基底模板路径当作独立创意出处。

本轮新20各交付一个冻结的精确接口，不宣称每个新关系已有两种独立空间验证。旧六个优先家族已有双接口，既有三端口和去回程Macro保留。B的新尺寸、方向、接缝、连续资源或回程要求需要适配并重验；这里的单Module通过不代替B整图。首家族交接与接缝试件沿用 [任务A首次交接](task-a-first-handoff.md) 和 [v2交付](content-workshop-v2.md)，不新增Map Generator。

## 录像、原件与边界

20个完整原生片中19个按原record全部字段、事件、敌体/机关、奖励与资源逐帧精确通过。M12安全无伤完成、领取并稳定到出口，但32处support_id差异导致严格比较失败，标记review-only；原失败、原片、日志、trace和差异表保留，未放宽比较。录制消费者修复只发生在隔离新版本，例如在最后正式帧后完整冻结世界，避免结尾持有的原生敌人继续提交移动；原动作帧没有改动。

分组/总览是明确标注的原速节选：只剪模块间边界和稳定领取后的尾部等待。完整原片与精确比较证据始终可以逐项下载；不能把剪辑当整图连续录像。所有视频的人工观感待评。

`content-workshop-creative20-v1`归档包含本轮全部选中与落选实验、输入输出原字节/gzip、冻结源码、校准/留出/反例/失败、旧和新录像trace及真实模型调用失败回执。可重建AVI不重复入库。独立SHA清单、分片/整包SHA和验证命令与既有归档工具一致。保护编辑器的npm检查、原工坊测试、Map测试和factory测试均通过，测试不替代真实物理证据。

最新B基线 `f023a014b4442c6aa68eaf2a7555fc5aaea1a515` 已合并到任务A分支，四处文档/忽略规则/归档名单冲突均保留双方新增内容。合并后工坊、factory、Map与npm检查通过；新20再次新进程磁盘重检索20/20，0新物理调用，870保护文件无漂移。[联调检查](../../generation/workshop/creative20-v1/integration-checks/summary.json)不等于B已把新20放进整图。原ccae6f9录像和证据版本未改。
