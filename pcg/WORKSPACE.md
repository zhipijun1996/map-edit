**R2真实整图里程碑**：见 [woven-region-v1](../docs/l4-mapgen/woven-region-v1.md)。固定Seed由既有R2驱动19个不同尺寸Macro、27直接接缝；25条冻结整图策略（12独立输入扰动）及全部50声明方向通过。19版本入隔离候选库，热库全复用后13条整图复验通过；配对实测两条回程节省4.90/11.35秒。四段正常速度原生录像13,822帧精确一致。仍只有一张物理拓扑，内容与空间语法有限，非最终区域规模/人类趣味/生产准入；正式游戏未改。原件与失败见 woven-region-v1 归档。

# 关卡生成工作区

## 当前任务：多口的空间选择与创意先行（2026-10-26）

用户认可上一批实现总体，同时指出多口像强加安全口；现在优先构思能服务后续地图分叉的局部空间节点，允许部分单向。环岛只是例子，不默认开始实现或批量生成。执行 [pcg-multiport-junction](../.agents/skills/pcg-multiport-junction/SKILL.md)。逐字来源/解释见`feedback/workshop/multiport-spatial-choice-feedback-v1.json`；15份现有多口的设计审查在`creative-production/curation/multiport-junction-audit-v1.json`，原技术记录不改。先读不同空间创意`creative-production/junction-ideas-v1.json`，原平台只支持两点往返，真正圆轨迹需新Cell。旧“从A有2/3出口”是当批数量/技术条件，不是新路口设计准则；UNKNOWN反向不算已证单向。此次仅审查、skill和概念输出，物理/新候选/生产准入均不增加。

## 最新交付：新增50平原Module，含7三口/4四口（2026-10-26）

见 [报告](../docs/l4-mapgen/plains50-v1.md)、[50件清单/21组审阅/运行命令](../generation/workshop/plains50-v1/README.md)。原库44→94，平原候选32→82；新增39双口/7三口/4四口，69路线逐路过原regular，所有3/4口分别有2/3真实出口。21审阅组+29有效适配不等于50新家族。8623 Harness案例含失败/接缝；留出1969/2022，未编造人类成功率。新进程原库复用、55多口矛盾需求拒绝与两零增面积接缝试件均有回执。新的平原视图`plains_workshop/catalog_v2.py`、统一手玩/回放`creative_batches/plains50_catalog.py`。归档`content-workshop-plains50-v1`保存全部新raw；旧记录不覆盖。先读最终AI审查与本批失败，D02/D03/D04/D05完整设计仍有缺口。网页当前索引包含所有94版本并能按端口筛选；main已通过PR #5发布（54d0cfc），真实公网更新94/平原82/四口4和31主审影片字节核对通过，回执`generation/workshop/plains50-v1/publication-v1.json`。人工/生产批准仍待真实反馈。共享物理/质量门槛/候选库框架未改。

## 当前续作：批次生产、AI去重、人工集中审核（2026-10-26）

执行 [批次方法](../docs/l4-mapgen/plains-batch-production-v1.md) 与 `.agents/skills/pcg-creative-producer/references/batch-production-v1.md`，续作账本 `creative-production/plains-campaign-v2.json`。每轮模型5张创意卡，缺规则/Cell就隔离实现，原Godot门槛通过后入原候选库；默认累计20个新增技术候选版本后AI按实际决策/因果分组，再给人工代表短视频。原库复用不算新增，适配不算新家族；重复仅折叠，不删除或当技术撤回。会话外不持续运行。最新反馈：D01被否决为已有基础反冲关系，停止作为新创意；D02-D05只有设计正向意见，未获试玩/生产批准。现有32平原版本做第一轮AI批次，D02进入有界实现；具体完成/失败必须读新cycle回执，计划数量不算完成。

首轮实际回执：`creative-production/plains-campaign-v2-cycle-001.json`。32版本AI分18审阅组、6适配、8折叠；18段不同代表影片有两段review-only，G06低路影片未找到。D02首版17真实案例发现岸上预停→静态跳台绕法，完整校准/留出NOT_RUN，新增入库0；先读`feedback/workshop/descending-carrier-prepark-v1.json`再修订。原库44版本保留。新失败原件用`content-workshop-plains-batch-v1`归档恢复。

## 当前优先：反冲平原与可持续配方（2026-10-26）

用户已整体正向评价新20项。见 [库现状与方法](../docs/l4-mapgen/plains-recoil-method-v1.md)、[平原视图](../generation/workshop/plains-recoil-v1/catalog.json)。共享库已归拢为44版本，平原优选32候选版本；新20里11项三能力兼容、9项高级能力留后，兼容项不全是反冲课。当前仅move/jump/shot_recoil；教学、练习、组合、奖励、同世界回程恢复分别验收。新方法首试两条旧规则×两新空间，4/4通过原门槛，新进程4/4复用0物理调用；不是方法稳定性或盲空间泛化通过。优先补安全首课和配方跨需求适应，接B现有平原流程，不继续按数量扩高级玩法。归档content-workshop-plains-method-v1提供新原件与旧15依赖闭包；旧20只需恢复results前缀，不覆盖当前源码。

## 大模型创意工坊：20种新动作关系（2026-10-25）

最新 [20种新玩法报告](../docs/l4-mapgen/content-workshop-creative20-v1.md) 与 [视频/标准Module目录](../generation/workshop/creative20-v1/README.md)。使用用户授权的当前Codex会话与子代理实际提出、实现和反驳创意，原生产循环执行参数搜索/真实Godot验证；[创意生产者skill](../.agents/skills/pcg-creative-producer/SKILL.md) 固定了可续作的方法。20种均为新关系，不计旧六家族、尺寸适配、普通电梯或Macro拆分；598/610独立留出安全稳定，沿用原regular门槛。新20原库入库及新进程检索，未编造在线API成功或无人值守服务。恢复 `content-workshop-creative20-v1` 后运行 `python3 -m pcg.prototype.creative_batches.catalog_v4 --list` / `--play 1`。人工趣味/试玩/生产准入待评，其他接口与B整图UNKNOWN。长等待双台转乘因模型视频节奏复审暂扣；撤桥下坠录像32处support_id差异严格失败，review-only，未放宽比较。

## 内容工坊续作：连续 Macro（2026-10-25）

最新 [双宝箱回程 Macro](../docs/l4-mapgen/content-workshop-macro-v1.md) 在原六家族之上交付两个三端口空间接口；4 份组成 Module 仅为版本依赖，不增加家族。450 条新留出中 444 条目的通过，原 regular 门槛不变；完整循环48/50，漏接恢复另26/26。原候选库磁盘重检索2/2，新增连接地形0。三段原生审阅录像有18帧支撑碰撞ID顺序差异，严格比较失败保持原件，不计全字段精确录像。v2已获用户整体正向视频反馈；新Macro观感、实际试玩、生产准入与B整图仍未完成。恢复 `content-workshop-macro-v1` 获取全部新源码/失败/轨迹。

## 任务 A 内容工坊入口（2026-10-25）

`prototype/workshop/` 在既有 PlainsEngine / CandidateLibrary 上增加六个因果玩法家族；每家族两种接口，另有既有 Map 100 高差需求的实际适配。**当前为 [content-workshop-v2](../docs/l4-mapgen/content-workshop-v2.md)**：旧 A2 静止登台绕法已撤回，库检索拒绝失效版本；新几何经过扩展反例与新留出。v1 原件保留。全部仍为未获人工观感/试玩/生产认可的候选。先交付 A1 的记录见 [任务 B 首次交接](../docs/l4-mapgen/task-a-first-handoff.md)。不包含 Map Director 或整图验收。

**内容驱动整图第一轮，尚未超过正式图趣味目标**：见 [content-routes-v1](../docs/l4-mapgen/content-routes-v1.md)。用户已否决上一轮“到处走”的观感，原话与版本绑定见 `feedback/woven-region-boring-v1.json`。保留19 Macro多环路骨架，15份父内容复用、4份需求适配；真实限时击铃反冲、敌人命中回充、尖刺净空与敌人死亡后的连续回程。21整图策略（8独立输入扰动）/50声明方向通过；19份热库复用后5整图复验。主线走路策略43.12%→39.03%，其他路线改善有限，不能据测试通过宣布整图更好玩。正式当前v12已重新5 Seed生成和1 live路线；生态、内容配方、地标、容错与流程仍领先。录像与三方对照在 `generation/maps/content-routes-review-v1`，全部失败/源/标准Module/候选记录恢复 `content-routes-v1`归档。人工认可0、生产准入关闭；下一步是内容配方/教学恢复/地貌共同驱动，不先扩大空地图。

**新增内容生态闭环**：见 [content-ecosystem-v1](../docs/l4-mapgen/content-ecosystem-v1.md)。`python3 -m pcg.map_directed.ecosystem.run --name fresh-ecosystem --batch` 复用既有 Director、CandidateLibrary、标准合同与真实 Harness，逐 Module 搜索/补缺/重新验整图/候选索引。固定批次生成调用 8/0/1，105 条连续整图策略通过（84 新相位），9 个候选版本；仍同一张八 Macro 双回环物理拓扑，不冒称多 Seed 探索多样性。16 个关系家族中7个仍为未实现提案；没有任意创意自主落地、生产准入或人工趣味批准。旧39 Macro压力样品仍不通过设计验收。恢复新 `content-ecosystem-v1` 获取全部失败/源/原始轨迹。

**真实整图阶段已接入，设计验收仍未通过**：见[阶段报告](../docs/l4-mapgen/full-region-spatial-stage-v1.md)。39 Macro / 55 接缝，核心90方向的12条连续巡回、两条进场和回程及12个独立相位样本已验证；6处奖励职责和16个奖励/捷径方向仍未完成，候选库拒绝入库。不能把这张薄楼板压力样品当新正式关卡。`region_scale.feedback`提供真实失败到现有端口列求解的有界反馈；`region_scale.materialize/verify`复用已有生成、标准输出和Harness。下一步是地貌/挑战先行的Macro与奖励补缺，目标并未降级。

**当前目标已升级为超过正式单图规模的完整平原**，见[目标与状态](../docs/l4-mapgen/full-region-goal-v1.md)和`map_directed/region_scale/protocol.json`。32核心探索地点、96–128 Module内容预算；不以重复/拆碎或扩大空白达标。原3个39–41地点蓝图中，Seed0已作39 Macro物理物化；另2个仍仅逻辑输出。当前设计验收未通过，不作为正式关卡交付。既有8 Module只作回归样品。人物/移动平台主要入口已改走正式安装器，`valley_complete.run --formal-style`可复现新样式验证；全游戏表现/战役迁移仍未完成。

最新完整风谷小区域：`python -m pcg.map_directed.valley_complete.run --name fresh-valley --mode full`。8个Module直接拼装，3宝箱/商人，新增空中停靠和敌人回充接力；正式native32px Tile。5整图路线、20新相位、216局部闭门策略和两个宝箱几何隔离，见[本轮报告](../docs/l4-mapgen/valley-complete-v1.md)。主游戏正式v12已另跑5 Seed及live Harness，不以旧v10代表最新状态。恢复`valley-complete-v1`归档取得完整新证据。仍是固定小区域，无Boss/战役和多Seed品质准入。

从独立研究工作区 f5daecb 迁入，布局保留以便复现；`prototype` 是可执行程序。`REPORT.md`、`COMPOSABLE-REPORT.md`、`DYNAMIC-REPORT.md`、`FACTORY-REPORT.md` 为历史阶段报告；其旧路径/提交是当时的证据，不重新盖章。

主入口：`prototype/factory/core/producer.py`。真实动作语法→运动构造→双档案变异→独立扰动/反例→人类观感评审。当前不是运行中无限生成器、完整地图或已证明的趣味库。真人试玩/正式批准仍为0；上一轮R已有1条整体正向视频反馈，原话见feedback/plains-round2-positive-v1.json。

最新开放风谷样品：`python -m pcg.map_directed.open_valley.run --name fresh-open --mode full`。7个无默认外墙的地形Module，主线三次空中击铃反冲，奖励铃联动回程平台，见[样品报告](../docs/l4-mapgen/open-valley-recoil-v1.md)。标准文档、真实接缝和整图验证继续复用原工具；先恢复`open-valley-sample-v1`取得证据和输入。当前为确定性样品与有限策略验证，未签多Seed品质/人类趣味/生产准入。

最新直接拼接Map入口：`python3 -m pcg.map_directed.direct_join.run --name fresh-direct-map --mode full`。27个不同大小Module/39处零间隙接缝，Map新增地形0；实际整图见[直接拼接报告](../docs/l4-mapgen/direct-module-contact-v1.md)。旧r2_full导航填充版被用户否决，保留原件，不再作为当前交付。候选的通用关系和生产准入仍关闭，整图有限物理见证与人类趣味认可分开。恢复`direct-module-source-and-failures-v1`及`direct-module-run-payloads-v1`取得全部新失败、冻结源及大输入；结果和媒体清单按报告链接读取。

本轮旧批次、全部冻结源和三段原生trace在 `r2-full-source-and-failures-v1`，用 `python3 pcg/tools/restore_archive.py r2-full-source-and-failures-v1 --extract` 恢复；仅校验不加extract。大量原始cases/compiled/input JSON另用 `python3 pcg/tools/restore_archive.py r2-full-run-payloads-v1 --extract` 恢复，逐文件索引见results/r2-run-payloads-index-v1.json。简要结果、库入库/复用日志、压缩物理输出及新媒体直接保留。原生AVI可重建，不入库。

历史小motif入口：`python3 -m pcg.map_directed.run`，见[旧闭环报告](../docs/l4-mapgen/map-driven-library-v1.md)。用户已反馈范围过小、安全连接过长；旧原件保留。

本轮媒体/实际试玩来源与恢复：[PUBLICATION](../generation/maps/map-directed-loop-v1/PUBLICATION.json)。`map-directed-source-and-failures-v1` 归档含各阶段冻结源和首失败；直接结果以 `results/map-directed-final-v1` 为完整新库闭环、`results/map-directed-loop-v2` 为跨进程库复用及媒体源。当前正式游戏未修改；下一步是人工评审、缩短安全连接并扩展多motif，不能把技术通过写成区域设计完成。

## 恢复与运行

在仓库根执行：

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
# 复跑历史失败轨迹实验时恢复这部分；完整旧数据仍在同一归档。
python3 pcg/tools/restore_archive.py research-results-v1 --extract --prefix results/factory-production-v1/
```

使用官方 Godot4.7.2 Standard，放到 `pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64`；官方ZIP SHA `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`，实际二进制SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。引擎来自官方Godot release4.7.2，不重传二进制或缓存。

```sh
cd pcg
python3 -m pip install -r requirements.txt
toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path prototype/godot --quit
python3 -m prototype.factory.core.producer --name new-run --tier regular
python3 -m prototype.factory.compare_landing_repairs --name guided-new-run
python3 -m unittest discover -s prototype/factory/tests -v
```

Godot素材与真实脚本由 `godot-runtime-v1` 完整保存870原件；恢复时逐SHA检查，不覆盖已更改文件。原许可证和资产来源见 `prototype/godot/asset_licenses_provenance.json` / `source_provenance.json`，归档不改变许可。

`research-results-v1` 包含4318份旧原始结果，含失败、输入输出、源快照；`review-delivery-v1` 含364份审阅录像/证据。归档分片均在本仓库，不依赖预览仓库作为唯一存储；清单列出完整ZIP及每片SHA。解压目标为本目录。旧Web导出的基础PCK/官方JS-WASM仍保留原不可变链接，不重复搬运；可重建的`.godot`缓存、原生AVI中间件与官方引擎不列为归档资产。原工作区继续保留原件。

## 接下来的范围

先比较失败轨迹指导的接收面修复与固定随机参数变异；只有多个种子/家族证据支持时才提升为默认。接入Map Notes先做显式候选导出和证据绑定，不把库里的未知能力/未评分模块默认当可通关或低难度。

当前生成物理基线12f6cb0；编辑器177参考模块来自74d8a06，不能无条件复用技术回执。迁移不改这两份历史身份。生成器未直接接正式大地图和编辑器工程回写。

## 平原的新工作入口

当前优先平原：只移动、普通单跳、反冲，以实际判断/动作链为多样性目标。`prototype/plains/{pilot,calibrate,produce}.py`执行有界离线生成；`PLAINS-REPORT.md`记录3代表/6技术候选及全部失败、原件绑定和新留出。先恢复`plains-generation-v1`再复跑；新平原worker恢复正式角色枪口，不能将旧worker的射击数据混作同一绑定。`results/plains-review-v1/playlist.json`明确每段对应哪一批验证。当前人类观感/试玩/批准为0，下一轮扩大真实机关/敌人关系与替代策略，避免仅换尺寸批量计数。

## 后续交付格式

必须执行[OUTPUT-CONTRACT.md](OUTPUT-CONTRACT.md)。plains和factory主生产器自动输出`modules/*.mapnote.json`及同版本SVG；raw review_cases仅供研究/回放，不作为地图接口。格式为现有Map Notes+generationContract；能力、难度、source.integration继续沿用旧格式。空间、端口有向对、状态、Macro组成与未知项显式表达；`assemblyInterface`默认拒绝未验证关系。

## 平原连续挑战第二轮

最新见[PLAINS-REVIEW-ROUND2.md](PLAINS-REVIEW-ROUND2.md)：6技术候选/3代表，416次正式物理验证，额外30批360案例基础设施回归0错误。3段完整原生录像及841帧精确比对随generation/videos/plains-round2公开；人工观感/试玩/批准仍0。恢复plains-review-round2-v1可取得所有新失败、校准、原始轨迹、冻结源与录像。当前等待R01/R02/R03观感审核；齿轮等待必要性未证明，不再据此增加玩法计数；自动拼装仍关闭。

## 三端口最新入口

[PLAINS-THREE-PORT-REPORT.md](PLAINS-THREE-PORT-REPORT.md)：`prototype/plains/three_port.py`生成同几何A/B/C分支；`three_port_produce.py`完成校准/独立留出。2候选，每个6有向对/7路线，正式552次物理；742帧原生视频精确匹配。新T视频待评，奖励服务/通用回程保证/接缝/拼装仍未完成。恢复plains-three-port-v1可取得完整失败与源；不是14个Module，不将参数变体算新玩法。
