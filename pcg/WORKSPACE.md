# 关卡生成工作区

从独立研究工作区 f5daecb 迁入，布局保留以便复现；`prototype` 是可执行程序。`REPORT.md`、`COMPOSABLE-REPORT.md`、`DYNAMIC-REPORT.md`、`FACTORY-REPORT.md` 为历史阶段报告；其旧路径/提交是当时的证据，不重新盖章。

主入口：`prototype/factory/core/producer.py`。真实动作语法→运动构造→双档案变异→独立扰动/反例→人类观感评审。当前不是运行中无限生成器、完整地图或已证明的趣味库。真人反馈仍为0。

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
