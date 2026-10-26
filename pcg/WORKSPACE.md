**实际形状空间搜索v1，鲁棒验收未通过**：见 [real-shape-search-v1](../docs/l4-mapgen/real-shape-search-v1.md)。五张8 Macro整图、9零间隙接缝，Map补地形0；实际形状/端口/门体/齿轮扫掠/身体轨迹与落地资源条件参与有界CSP。常规30/30，独立扰动27/30，配对旧布局28/30，不能宣布稳定更优。只有4空间签名/3去镜像岸体组合/1拓扑。真实阻塞反例、三段严格原生录像、完整失败均保留。已合入main7bea81d新仓库浏览；算法冻结6479908。恢复shape-search-calibration-v1、shape-search-source-v1与shape-search-results-v1，通用关系UNKNOWN、生产准入关闭。

**R2真实整图里程碑**：见 [woven-region-v1](../docs/l4-mapgen/woven-region-v1.md)。固定Seed由既有R2驱动19个不同尺寸Macro、27直接接缝；25条冻结整图策略（12独立输入扰动）及全部50声明方向通过。19版本入隔离候选库，热库全复用后13条整图复验通过；配对实测两条回程节省4.90/11.35秒。四段正常速度原生录像13,822帧精确一致。仍只有一张物理拓扑，内容与空间语法有限，非最终区域规模/人类趣味/生产准入；正式游戏未改。原件与失败见 woven-region-v1 归档。

# 关卡生成工作区

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

## 最新 Module 库接入完整 Map（2026-10-26）

见[实验报告](../docs/l4-mapgen/latest-library-map-integration-v1.md)。已同步main54d0cfc及内容6de70fb：94版本/82平原候选，121/121源路线；三个Seed实际21原版本，整图7/12（1/4、4/4、2/4），仅一张四路线全过。没有生产/人类趣味认可、没有通用回程/路口准入。固定双分流测试图未代替既有Mission生成器。源/所有失败/原库证据在catalog-feed-source-and-runs-v1，实际截图/原生影片/公网字节核验在catalog-feed-media-v1；PCK以可精确重建的父包增量保存。


**岩井回环空间原型v1**：见[完整报告](../docs/l4-mapgen/contact-grammar-v1.md)。三Seed 12/16实例、13/18零间隙接缝，37/37（12常规、18新扰动、7回归），每图2箱48币；两段真实原生录像3187帧严格一致。仅一种有限3/4层空间文法，5父版本，尚无128网格迁移、人工趣味/正式生产准入。旧25/30及28/35失败保留；恢复contact-grammar-v1归档。

**Graph + Block128 + Module新实验**：见[分析、证据和复现](../docs/l4-mapgen/graph-block-module-v1.md)与[增量契约](../docs/l4-mapgen/graph-block-module-contract-v1.md)。真实边界中心Port、不规则连通预留形状、实体/动作/动态约束沿用原CSP、标准文档与Harness；三Seed12/16实例33/33（15常规、18新扰动），热库16/16复用后5/5重验，两片3540物理帧严格一致。Map补平台0。仍只有两种拓扑，0与1同位置，重复枢纽/水平岩体未解决。40～65是本轮新策略目标，旧96～128协议作历史保留；44节点、三种支路返回仅逻辑，真实Boss/主要道具/价值/人类分钟及任意R2图拼装未完成。源v4 4/12及hub v1 9/13全部失败在block-grid-v1归档；UNKNOWN、人工待审、生产关闭。

**同一探索图落实高崖/溪谷样图**：见[报告](../docs/l4-mapgen/same-graph-landforms-v1.md)。graph_landforms停止消费旧岩井图与位置，7个职责节点/7边逐项进入Module需求、原CSP联合选高差/跨度/轮廓及真实拼装；旧岩井0、Map补平台0。5/5校准后冻结11/11（5常规+6新扰动），11声明方向覆盖，高低两主路同世界同初始状态，landmark汇合；cliff→cache→cliff实际1箱18币。新Macro v2 20/28、v3 28/28，所有旧失败保留。三片3305物理帧严格一致。仍一张有限验收拓扑，直边/奖励阶梯与中央空腔观感待评，非完整区域/人工批准/生产准入。恢复same-graph-landforms-v1归档。
