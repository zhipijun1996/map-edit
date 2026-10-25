# 关卡生成工作区

**当前目标已升级为超过正式单图规模的完整平原**，见[目标与状态](../docs/l4-mapgen/full-region-goal-v1.md)和`map_directed/region_scale/protocol.json`。32核心探索地点、96–128 Module内容预算；不以重复/拆碎或扩大空白达标。3个39–41地点的Director输出目前仅逻辑蓝图，实际Module=0、不可作为可玩地图交付。既有8 Module只作回归样品。人物/移动平台主要入口已改走正式安装器，`valley_complete.run --formal-style`可复现新样式验证；全游戏表现/战役迁移仍未完成。

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
